import abc
import asyncio
import logging
import secrets
from collections import defaultdict
from typing import TypeVar

from blinker import Signal

from nwn_message import message, messages, packet, packets
from nwn_message.context import Context
from nwn_message.errors import UnknownHeaderError
from nwn_message.types import ServerSettings, Version

logger = logging.getLogger(__name__)


Sendable = message.Message | packet.Packet
Subscribable = message.Message | message.SubMessage | packet.Packet
SubscribableT = TypeVar("SubscribableT", bound=Subscribable)


class PeerOwner:
    """
    A PeerOwner is an object that owns one or more Peers, and is responsible for
    managing their lifecycle.

    This object is laying the groundwork for a future server implementation.
    """

    app_id: int
    """
    A per-run, unique 32-bit unsigned integer value for use in app_id fields
    during game operation; mostly immaterial for NWN:EE.
    """

    server_settings: ServerSettings
    """
    The server settings, either from the runtime config (for servers) or from
    the server itself (for clients).
    """

    on_peer_connected: Signal
    on_peer_authenticated: Signal

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app_id = secrets.randbelow(0xFFFFFFFF)
        self.server_settings = ServerSettings()
        self._on_signals = defaultdict(Signal)
        self.on_peer_connected = Signal("Peer connected to the remote")
        self.on_peer_authenticated = Signal("Peer authenticated with the remote")

    def on(self, data_class: type[Subscribable]) -> Signal:
        """
        Get the signal for a specific message or packet payload class.

        These signals are sent by the Peer when a message or packet of the
        corresponding type is received, with the sender as the Peer and a
        `data` keyword argument containing the parsed message or packet.

        All signals are sent out async.
        """
        return self._on_signals[data_class]

    async def _dispatch(self, peer, data: Subscribable, **kwargs):
        """
        Called by the Peer when it receives a message.

        All signals are sent out async.
        """
        if signal := self._on_signals.get(type(data)):
            await signal.send_async(self, peer=peer, data=data, **kwargs)


class Peer(abc.ABC):
    """
    A Peer represents a connection to a NWN server or client.
    It can send and receive messages and packets.
    """

    owner: PeerOwner
    context: Context
    our_version: Version
    their_version: Version | None

    def __init__(self, owner: PeerOwner, context: Context, **kwargs):
        super().__init__(**kwargs)
        self._request_lock = asyncio.Lock()

        self.owner = owner
        self.context = context
        self.context.peer = self
        self.our_version = Version(8193, 37, 17)
        self.their_version = None

    @abc.abstractmethod
    async def send_bytes(self, data: bytes):
        """
        Send raw bytes to the remote peer.
        """

    async def send(self, data: Sendable):
        """
        Send a message or packet to the remote peer, transparently encoding
        and compressing as needed.
        """
        logger.debug(f"~> {self}: {data!r}")

        if isinstance(data, packet.Packet):
            payload = data.dump(self.context)
        elif isinstance(data, message.Message):
            payload = data.dump(
                message.MessagePrefix.PLAYER_CLIENT_TO_SERVER, self.context
            )
        else:
            raise ValueError(f"Unsupported payload type: {type(data)}")
        await self.send_bytes(payload)

    @abc.abstractmethod
    async def disconnect(self):
        """
        Disconnect this peer from the remote.

        This exits the closes the connection and exits the run loop.

        If the remote peer disconnects *us*, the run loop also ends and
        throws a DisconnectedError with the reason provided by the remote.
        """

    @abc.abstractmethod
    async def run(self):
        """
        Run the mainloop/processing for this peer; this is where incoming
        messages/packets are processed and dispatched. It should only return when
        the connection is closed or an error occurs.

        The transport-specific implementation of this is left to the concrete class,
        including the login/authentication process, if applicable.

        It should never return unless an error occurs.

        To break out of the loop, call `disconnect()`.
        """

    def satisfies(self, build: int, patch: int, postfix: int) -> bool:
        """
        Check if the *remote* peer's version is compatible with the given version.

        This is used by the message parser/generator to ensure compatibility.

        Returns True if compatible, False otherwise.
        """
        if not self.their_version:
            raise ValueError(f"Peer {self} does not have a version set")
        return self.their_version.satisfies(Version(build, patch, postfix))

    async def send_and_await(
        self, data: Sendable, expect: type[SubscribableT], timeout: float = 5.0
    ) -> SubscribableT:
        """
        Send a message or packet to the remote peer, and wait for a specific
        response message or packet.

        The response is identified by the `expect` parameter, which is a message
        or packet class. The function will wait until a message or packet of the
        expected type is received, and return it.

        If a timeout occurs before the expected message or packet is received,
        a TimeoutError is raised. The sender for the received message or packet
        will be this peer.

        Note: This function is currently strictly serialising, as the network
            protocol does not have a request/response RPC mechanism.

        This is most useful for pre-window communication to make the authentication
        flow easier.

        Args:
            payload: The message or packet to send.
            expect: The type of message or packet to wait for in response.
            timeout: The maximum time to wait for the expected message or packet.

        Returns:
            The received message or packet of the expected type.

        Raises:
            TimeoutError: If the expected message or packet is not received within
                the timeout period.
        """
        async with self._request_lock:
            fut = asyncio.get_event_loop().create_future()

            async def handler(_sender, **kw):
                fut.set_result(kw["data"])
                self.owner.on(expect).disconnect(handler)

            self.owner.on(expect).connect(handler, weak=False)
            try:
                await self.send(data)
                return await asyncio.wait_for(fut, timeout)
            finally:
                self.owner.on(expect).disconnect(handler)

    async def _handle_message(self, payload: bytes):
        try:
            msg = message.read(payload, self.context)
        except UnknownHeaderError as e:
            logger.error(f"Unknown message type from {self}: {e}")
            return
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(f"Error reading message from {self}: {payload=}: {e}")
            return

        logger.debug(f"<~ {self}: {msg!r}")

        await self.owner._dispatch(self, msg)

        for submsg in msg.iter_submessages():
            await self.owner._dispatch(self, data=submsg, parent=msg)

        if isinstance(msg, messages.device.DeviceEchoRequest):
            await self.send(messages.device.DeviceEchoResponse(data=msg.data))

    async def _handle_pre_window(self, payload: bytes):
        data = packet.read(payload, self.context)

        logger.debug(f"<~ {self}: {data!r}")

        await self.owner._dispatch(self, data=data)

        if isinstance(data, packets.BNLM):
            await self.send(
                packets.BNLR(message_no=data.message_no, session_id=data.session_id)
            )
