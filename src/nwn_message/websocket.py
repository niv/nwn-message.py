import asyncio
import hashlib
import logging
from typing import Callable

import websockets

from nwn_message import errors, packets
from nwn_message.cdkey import CDKey
from nwn_message.context import Context
from nwn_message.peer import Peer, PeerOwner
from nwn_message.types import ConnectionType, ServerSettings, Version
from nwn_message.util import apply_fields_from

logger = logging.getLogger(__name__)


class WebsocketClient(Peer, PeerOwner):
    """
    A websocket client that connects to a NWN server.
    """

    websocket: websockets.ClientConnection | None

    player_name: str
    cd_key: CDKey
    host: str
    port: int
    connection_type: ConnectionType
    password: str

    def __init__(
        self,
        *,
        context_factory: Callable[[Peer], Context],
        player_name: str,
        cd_key: CDKey,
        host: str,
        port: int = 5121,
        connection_type: ConnectionType = ConnectionType.PLAYER,
        password: str = "",
    ):
        # This may look convoluted; but consider this will also be used by a
        # server implementation, which will have a different context per conn.
        context = context_factory(self)
        super().__init__(owner=self, context=context)

        self.websocket = None

        self.player_name = player_name
        self.cd_key = cd_key
        self.host = host
        self.port = port
        self.connection_type = connection_type
        self.password = password

    def __str__(self):
        return f"WebsocketClient({self.player_name}@{self.host}:{self.port})"

    async def send_bytes(self, data: bytes):
        assert self.websocket
        await self.websocket.send(data)

    async def _login(self):
        gnhi = await self.send_and_await(
            packets.GNHI(),
            packets.GNHI,
        )

        if gnhi.protocol_version != 1:
            raise ValueError(f"Unsupported protocol version: {gnhi.protocol_version}")

        if gnhi.caps != 0x0:
            raise ValueError(f"Unsupported protocol caps: {gnhi.caps}")

        bner = await self.send_and_await(
            packets.BNES(),
            packets.BNER,
        )
        bnxr = await self.send_and_await(
            packets.BNXI(
                player_name=self.player_name,
                public_key=self.cd_key.public_key(),
                connection_type=self.connection_type,
            ),
            packets.BNXR,
        )
        bndr = await self.send_and_await(packets.BNDS(), packets.BNDR)

        apply_fields_from(self.server_settings, bner)
        apply_fields_from(self.server_settings, bnxr)
        apply_fields_from(self.server_settings, bndr)

        bncr = await self.send_and_await(
            packets.BNCS(
                connection_type=self.connection_type,
                player_name=self.player_name,
                cd_key=self.cd_key.public_key(),
            ),
            packets.BNCR,
        )

        if bncr.status == packets.BNCRStatus.REJECTED:
            raise errors.AuthenticationError(bncr.rejection_reason.name)

        cdkey_response = self.cd_key.public_key().encode("ascii") + hashlib.md5(
            self.cd_key.full_key().encode("ascii") + bncr.cd_key_challenge
        ).hexdigest().encode("ascii")

        if bncr.status == packets.BNCRStatus.PASSWORD_REQUIRED:
            if not self.password:
                raise errors.AuthenticationError("Password required but not provided")
            game_response = (
                hashlib.md5(
                    self.password.encode("ascii") + bncr.game_password_challenge
                )
                .hexdigest()
                .encode("ascii")
            )
        else:
            game_response = b""

        bnvr = await self.send_and_await(
            packets.BNVS(
                cd_key_response=cdkey_response,
                game_password_response=(
                    game_response
                    if bncr.status == packets.BNCRStatus.PASSWORD_REQUIRED
                    else b""
                ),
                master_password_response=hashlib.md5(
                    b"" + bncr.master_password_challenge
                )
                .hexdigest()
                .encode("ascii"),
            ),
            packets.BNVR,
        )

        if bnvr.connection_status != packets.BNVRConnectionStatus.ACCEPTED:
            raise errors.AuthenticationError(bnvr.rejection_reason.name)

        self.their_version = Version(
            bnvr.server_build, bnvr.server_patch, bnvr.server_postfix
        )

        if self.their_version != self.our_version:
            raise errors.VersionMismatchError(
                f"Version mismatch: server is {self.their_version}, "
                f"but client is {self.our_version}"
            )

        await self.on_peer_authenticated.send_async(self, peer=self)

    async def disconnect(self, reason="User disconnect"):
        if self.websocket:
            await self.websocket.close(reason=reason)

    async def _handle_incoming(self, data: bytes):
        if data.startswith(b"P"):
            await self._handle_message(data)

        elif data.startswith((b"B", b"G")):
            await self._handle_pre_window(data)

        else:
            logger.error(f"Unknown data received: {data}")

    async def run(self):
        """
        Run the client, automatically log in with the configured credentials.
        This function will only return if the connection is closed or an error occurs.

        Raises:
            DisconnectedError: If the client disconnected, with the reason provided.
        """

        uri = f"ws://{self.host}:{self.port}?proto_flags=0x100"

        self.server_settings = ServerSettings()

        async def _recv_loop(websocket):
            async for data in websocket:
                await self._handle_incoming(data)

        async with websockets.connect(
            uri,
            ping_interval=10,
            ping_timeout=60,
        ) as websocket:
            self.websocket = websocket
            await self.on_peer_connected.send_async(self, peer=self)

            try:
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(_recv_loop(websocket))
                    await self._login()
            except* errors.DisconnectedError as eg:
                raise eg.exceptions[0]  # pylint: disable=no-member
            except* asyncio.CancelledError:
                await websocket.close()
        self.websocket = None
