import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Self

from nwn.environ import get_codepage, get_language
from nwn.types import Language, Platform

from .context import Context
from .packet import Packet, PacketReader, PacketWriter
from .types import ConnectionType, PVPSetting
from .util import detect_platform

logger = logging.getLogger(__name__)

# pylint: disable=unused-argument, too-many-instance-attributes, too-many-locals


@dataclass(kw_only=True)
class GNHI(Packet, head=b"GNHI"):
    protocol_version: int = 1
    caps: int = 0

    @classmethod
    def parse(cls, reader: PacketReader, context: Context) -> Self:
        protocol_version = reader.read_u8()
        caps = reader.read_u64()
        return cls(protocol_version=protocol_version, caps=caps)

    def dump(self, context: Context) -> bytes:
        wr = PacketWriter(self.HEAD)
        wr.write_u8(self.protocol_version)
        wr.write_u64(self.caps)
        return wr.getvalue()


class EnumerateType(IntEnum):
    NONE = 0
    HISTORY = 1
    FAVORITES = 2
    BUDDIES = 3
    INTERNET = 4


@dataclass(kw_only=True)
class NWSyncManifest:
    flags: int
    language_id: int
    hash: str


@dataclass(kw_only=True)
class BNES(Packet, head=b"BNES"):
    port_number: int = 5121
    enumerate_type: EnumerateType = EnumerateType.NONE

    @classmethod
    def parse(cls, reader: PacketReader, context: Context) -> Self:
        port_number = reader.read_u16()
        enumerate_type = EnumerateType(reader.read_u8())
        return cls(port_number=port_number, enumerate_type=enumerate_type)

    def dump(self, context: Context) -> bytes:
        wr = PacketWriter(self.HEAD)
        wr.write_u16(self.port_number)
        wr.write_u8(self.enumerate_type.value)
        return wr.getvalue()


@dataclass(kw_only=True)
class BNER(Packet, head=b"BNER"):
    enumerate_type: EnumerateType
    session_name: str

    @classmethod
    def parse(cls, reader: PacketReader, context: Context) -> Self:
        _always_u = reader.read_bytes(1)
        if _always_u != b"U":
            raise ValueError(f"Expected 'U' at start of BNER packet, got {_always_u!r}")
        _port = reader.read_u16()
        enumerate_type = EnumerateType(reader.read_u8())
        session_name = reader.read_lp8()
        return cls(
            enumerate_type=enumerate_type,
            session_name=session_name.decode(get_codepage()).strip("\x00"),
        )

    def dump(self, context: Context) -> bytes:
        wr = PacketWriter(self.HEAD)
        wr.write_bytes(b"U")
        wr.write_u16(5121)
        wr.write_u8(self.enumerate_type.value)
        wr.write_str_lp8(self.session_name)
        return wr.getvalue()


@dataclass(kw_only=True)
class BNXI(Packet, head=b"BNXI"):
    player_name: str
    public_key: str
    legacy_public_key: str = ""
    language: Language = get_language()
    connection_type: ConnectionType
    platform: Platform = detect_platform()
    build_number: str = ""
    build_revision: str = ""
    build_postfix: str = ""
    build_git_commit: str = ""

    @classmethod
    def parse(cls, reader: PacketReader, context: Context) -> Self:
        _port = reader.read_u16()
        player_name = reader.read_lp8()
        public_key = reader.read_lp8()
        legacy_public_key = reader.read_lp8()
        language = Language(reader.read_u8())
        connection_type = ConnectionType(reader.read_u8())
        platform = Platform(reader.read_u8())
        build_number = reader.read_lp8()
        build_revision = reader.read_lp8()
        build_postfix = reader.read_lp8()
        build_git_commit = reader.read_lp8()
        return cls(
            player_name=player_name.decode(get_codepage()).strip("\x00"),
            public_key=public_key.decode(get_codepage()).strip("\x00"),
            legacy_public_key=legacy_public_key.decode(get_codepage()).strip("\x00"),
            language=language,
            connection_type=connection_type,
            platform=platform,
            build_number=build_number.decode(get_codepage()).strip("\x00"),
            build_revision=build_revision.decode(get_codepage()).strip("\x00"),
            build_postfix=build_postfix.decode(get_codepage()).strip("\x00"),
            build_git_commit=build_git_commit.decode(get_codepage()).strip("\x00"),
        )

    def dump(self, context: Context) -> bytes:
        wr = PacketWriter(self.HEAD)
        wr.write_u16(5121)
        wr.write_str_lp8(self.player_name)
        wr.write_str_lp8(self.public_key)
        wr.write_str_lp8(self.legacy_public_key)
        wr.write_u8(self.language.value)
        wr.write_u8(self.connection_type.value)
        wr.write_u8(self.platform.value)
        wr.write_str_lp8(self.build_number or str(context.peer.our_version.build))
        wr.write_str_lp8(self.build_revision or str(context.peer.our_version.patch))
        wr.write_str_lp8(self.build_postfix or str(context.peer.our_version.postfix))
        wr.write_str_lp8(self.build_git_commit)
        return wr.getvalue()


@dataclass(kw_only=True)
class BNXR(Packet, head=b"BNXR"):
    passworded: bool = False
    min_level: int = 0  # or 0xFF if no server info
    max_level: int = 40  # or 0xFF if no server info
    current_players: int = 0  # or 0x00
    max_players: int = 0xFF
    allow_localvault: bool = True
    pvp_setting: PVPSetting = PVPSetting.NONE
    pause_and_play: bool = False
    one_party_only: bool = True
    elc: bool = True
    ilr: bool = False
    expansion_pack: int = 0
    module_name: str = ""
    nwsync_url: str = ""
    nwsync_primary_manifest: str = ""
    nwsync_additional_manifests: list[NWSyncManifest] = field(default_factory=list)
    advanced_version: str = ""

    @classmethod
    def parse(cls, reader: PacketReader, context: Context) -> Self:
        _port = reader.read_u16()
        version_number = reader.read_u8()
        if version_number != 0xFD:
            raise ValueError(
                f"Expected version number 0xFD in BNXR packet, got {version_number:#x}"
            )

        passworded = bool(reader.read_u8())
        min_level = reader.read_u8()
        max_level = reader.read_u8()
        current_players = reader.read_u8()
        max_players = reader.read_u8()
        allow_localvault = bool(reader.read_u8())
        pvp_setting = PVPSetting(reader.read_u8())
        pause_and_play = bool(reader.read_u8())
        one_party_only = bool(reader.read_u8())
        elc = bool(reader.read_u8())
        ilr = bool(reader.read_u8())
        expansion_pack = reader.read_u8()

        module_name = reader.read_lp8().decode(get_codepage())

        nwsync_url = ""
        nwsync_primary_manifest = ""
        nwsync_additional_manifests: list[NWSyncManifest] = []

        if not reader.at_end:
            nwsync_version = reader.read_u8()
            if nwsync_version == 2 and not reader.at_end:
                nwsync_present = bool(reader.read_u8())
                if nwsync_present:
                    nwsync_url = reader.read_lp8().decode(get_codepage())
                    nwsync_primary_manifest = reader.read_lp8().decode(get_codepage())
                    additional_count = reader.read_u8()
                    for _ in range(additional_count):
                        flags = reader.read_u8()
                        language_id = reader.read_u8()
                        hash_value = reader.read_lp8().decode(get_codepage())
                        nwsync_additional_manifests.append(
                            NWSyncManifest(
                                flags=flags,
                                language_id=language_id,
                                hash=hash_value,
                            )
                        )

        advanced_version = ""
        if not reader.at_end:
            advanced_version = reader.read_lp16().decode(get_codepage())

        return cls(
            passworded=passworded,
            min_level=min_level,
            max_level=max_level,
            current_players=current_players,
            max_players=max_players,
            allow_localvault=allow_localvault,
            pvp_setting=pvp_setting,
            pause_and_play=pause_and_play,
            one_party_only=one_party_only,
            elc=elc,
            ilr=ilr,
            expansion_pack=expansion_pack,
            module_name=module_name.strip("\x00"),
            nwsync_url=nwsync_url.strip("\x00"),
            nwsync_primary_manifest=nwsync_primary_manifest.strip("\x00"),
            nwsync_additional_manifests=nwsync_additional_manifests,
            advanced_version=advanced_version.strip("\x00"),
        )

    def dump(self, context: Context) -> bytes:
        wr = PacketWriter(self.HEAD)
        wr.write_bytes(b"\x00\x00")  # fake port for now
        wr.write_bytes(b"\xfd")
        wr.write_u8(1 if self.passworded else 0)
        wr.write_u8(self.min_level)
        wr.write_u8(self.max_level)
        wr.write_u8(self.current_players)
        wr.write_u8(self.max_players)
        wr.write_u8(1 if self.allow_localvault else 0)
        wr.write_u8(self.pvp_setting)
        wr.write_u8(1 if self.pause_and_play else 0)
        wr.write_u8(1 if self.one_party_only else 0)
        wr.write_u8(1 if self.elc else 0)
        wr.write_u8(1 if self.ilr else 0)
        wr.write_u8(self.expansion_pack)
        wr.write_str_lp8(self.module_name)
        # NWSync wire format version 2.
        if not self.nwsync_url and not self.nwsync_primary_manifest:
            wr.write_bytes(b"\x02\x00")
        else:
            wr.write_bytes(b"\x02\x01")
            wr.write_str_lp8(self.nwsync_url)
            wr.write_str_lp8(self.nwsync_primary_manifest)
            wr.write_u8(len(self.nwsync_additional_manifests))
            for manifest in self.nwsync_additional_manifests:
                wr.write_u8(manifest.flags)
                wr.write_u8(manifest.language_id)
                wr.write_str_lp8(manifest.hash)
        wr.write_str_lp16(self.advanced_version)
        return wr.getvalue()


@dataclass(kw_only=True)
class BNLM(Packet, head=b"BNLM"):
    port: int
    message_no: int
    session_id: int

    @classmethod
    def parse(cls, reader: PacketReader, context: Context) -> Self:
        port = reader.read_u16()
        message_no = reader.read_u8()
        session_id = reader.read_u32()
        return cls(
            port=port,
            message_no=message_no,
            session_id=session_id,
        )

    def dump(self, context: Context) -> bytes:
        wr = PacketWriter(self.HEAD)
        wr.write_u16(self.port)
        wr.write_u8(self.message_no)
        wr.write_u32(self.session_id)
        return wr.getvalue()


@dataclass(kw_only=True)
class BNLR(Packet, head=b"BNLR"):
    port: int = 5121  # unused
    message_no: int
    session_id: int

    @classmethod
    def parse(cls, reader: PacketReader, context: Context) -> Self:
        port = reader.read_u16()
        message_no = reader.read_u8()
        session_id = reader.read_u32()
        return cls(port=port, message_no=message_no, session_id=session_id)

    def dump(self, context: Context) -> bytes:
        wr = PacketWriter(self.HEAD)
        wr.write_u16(self.port)
        wr.write_u8(self.message_no)
        wr.write_u32(self.session_id)
        return wr.getvalue()


@dataclass(kw_only=True)
class BNDS(Packet, head=b"BNDS"):
    port_number: int = 5121

    @classmethod
    def parse(cls, reader: PacketReader, context: Context) -> Self:
        return cls(port_number=reader.read_u16())

    def dump(self, context: Context) -> bytes:
        wr = PacketWriter(self.HEAD)
        wr.write_u16(self.port_number)
        return wr.getvalue()


@dataclass(kw_only=True)
class BNDR(Packet, head=b"BNDR"):
    port_number: int = 5121
    game_details: str
    module_description: str
    build: str | None = None
    game_type: int = 0  # unused

    @classmethod
    def parse(cls, reader: PacketReader, context: Context) -> Self:
        port_number = reader.read_u16()
        game_details = reader.read_lp32()
        module_description = reader.read_lp32()
        build = reader.read_lp32()
        game_type = reader.read_i16()
        return cls(
            port_number=port_number,
            game_details=game_details.decode(get_codepage()).strip("\x00"),
            module_description=module_description.decode(get_codepage()).strip("\x00"),
            build=build.decode(get_codepage()).strip("\x00"),
            game_type=game_type,
        )

    def dump(self, context: Context) -> bytes:
        wr = PacketWriter(self.HEAD)
        wr.write_u16(self.port_number)
        wr.write_str_lp32(self.game_details)
        wr.write_str_lp32(self.module_description)
        wr.write_str_lp32(self.build or context.peer.our_version.build)
        wr.write_i16(self.game_type)
        return wr.getvalue()


@dataclass(kw_only=True)
class BNCS(Packet, head=b"BNCS"):
    connection_type: ConnectionType
    # expansion_pack_info: int
    player_language: Language = get_language()
    player_name: str
    cd_key: str
    app_id: int = 0
    version_number: int = 0
    patch_revision: int = 0
    patch_postfix: int = 0
    git_commit: str = ""
    legacy_cd_key: str = ""
    psid: str = field(repr=False, default="")
    platform: Platform = detect_platform()

    @classmethod
    def parse(cls, reader: PacketReader, context: Context) -> Self:
        _port = reader.read_u16()
        connection_type = ConnectionType(reader.read_u8())
        version_number = reader.read_u32()
        _always_ffff = reader.read_u16()
        player_language = Language(reader.read_u8())
        app_id = reader.read_u32()
        player_name = reader.read_lp8()
        cd_key = reader.read_lp8()
        legacy_cd_key = reader.read_lp8()
        platform = Platform(reader.read_u8())
        psid = reader.read_lp8()
        patch_revision = reader.read_i32()
        git_commit = reader.read_lp8()
        patch_postfix = reader.read_i32()
        return cls(
            connection_type=connection_type,
            player_language=player_language,
            player_name=player_name.decode(get_codepage()).strip("\x00"),
            cd_key=cd_key.decode(get_codepage()).strip("\x00"),
            legacy_cd_key=legacy_cd_key.decode(get_codepage()).strip("\x00"),
            app_id=app_id,
            version_number=version_number,
            patch_revision=patch_revision,
            patch_postfix=patch_postfix,
            git_commit=git_commit.decode(get_codepage()).strip("\x00"),
            psid=psid.decode(get_codepage()).strip("\x00"),
            platform=platform,
        )

    def dump(self, context: Context) -> bytes:
        app_id = self.app_id or int(datetime.datetime.now().timestamp())
        wr = PacketWriter(self.HEAD)
        wr.write_u16(5121)
        wr.write_u8(self.connection_type.value)
        wr.write_u32(self.version_number or context.peer.our_version.build)
        wr.write_u16(0xFFFF)
        wr.write_u8(self.player_language.value)
        wr.write_u32(app_id)
        wr.write_str_lp8(self.player_name)
        wr.write_str_lp8(self.cd_key)
        wr.write_str_lp8(self.legacy_cd_key)
        wr.write_u8(self.platform.value)
        wr.write_str_lp8(self.psid)
        wr.write_i32(self.patch_revision or context.peer.our_version.patch)
        wr.write_str_lp8(self.git_commit or context.peer.our_version.git_commit)
        wr.write_i32(self.patch_postfix or context.peer.our_version.postfix)
        return wr.getvalue()


class BNCRStatus(Enum):
    REJECTED = b"R"
    PASSWORD_REQUIRED = b"P"
    ACCEPTED = b"V"


class AuthenticationResult(IntEnum):
    OK = 0
    UNKNOWN = 1
    SERVER_VERSIONMISMATCH = 2
    PASSWORD_INCORRECT = 3
    SERVER_NOT_MULTIPLAYER = 4
    SERVER_FULL = 5
    PLAYER_NAME_IN_USE = 6
    REPLY_TIMEOUT = 7
    PLAYER_NAME_REFUSED = 8
    CD_KEY_IN_USE = 9
    BANNED = 10
    EXPANSION_PACK_WRONG = 11
    CDKEY_UNAUTHORIZED = 12
    DM_CONNECTION_REFUSED = 13
    ADMIN_CONNECTION_REFUSED = 14
    LANGUAGE_VERSIONMISMATCH = 15
    MASTERSERVER_CD_IN_USE = 16
    LOGIN_DENIED_MASTERSERVER_NOT_RESPONDING = 17
    DEFAULT_PLAYER_NAME_MISSING = 18
    CRYPTO_HANDSHAKE_FAILED = 19


@dataclass(kw_only=True)
class BNCR(Packet, head=b"BNCR"):
    status: BNCRStatus
    game_password_challenge: bytes = field(repr=False, default=b"")
    cd_key_challenge: bytes = field(repr=False, default=b"")
    master_password_challenge: bytes = field(repr=False, default=b"")  # Unused
    rejection_reason: AuthenticationResult = AuthenticationResult.OK

    @classmethod
    def parse(cls, reader: PacketReader, context: Context) -> Self:
        _port = reader.read_u16()
        status = BNCRStatus(reader.read_bytes(1))
        if status == BNCRStatus.REJECTED:
            rejection_reason = AuthenticationResult(reader.read_u8())
            return cls(status=status, rejection_reason=rejection_reason)
        game_password_challenge = b""
        if status == BNCRStatus.PASSWORD_REQUIRED:
            game_password_challenge = reader.read_lp8()
        cd_key_challenge = reader.read_lp8()
        master_password_challenge = reader.read_lp8()
        return cls(
            status=status,
            game_password_challenge=game_password_challenge,
            cd_key_challenge=cd_key_challenge,
            master_password_challenge=master_password_challenge,
        )

    def dump(self, context: Context) -> bytes:
        wr = PacketWriter(self.HEAD)
        wr.write_bytes(b"\x00\x00")  # port, unused
        if self.status == BNCRStatus.REJECTED:
            wr.write_bytes(b"R")
            wr.write_u8(self.rejection_reason.value)
            return wr.getvalue()
        wr.write_bytes(b"P" if self.status == BNCRStatus.PASSWORD_REQUIRED else b"V")
        if self.status == BNCRStatus.PASSWORD_REQUIRED:
            wr.write_lp8(self.game_password_challenge)
        wr.write_lp8(self.cd_key_challenge)
        wr.write_lp8(self.master_password_challenge)
        return wr.getvalue()


class BNVSResponseType(Enum):
    PASSWORD_REQUIRED = b"P"
    OK = b"V"


@dataclass(kw_only=True)
class BNVS(Packet, head=b"BNVS"):
    cd_key_response: bytes = field(repr=False)
    master_password_response: bytes = field(repr=False, default=b"")
    game_password_response: bytes = field(repr=False, default=b"")

    @classmethod
    def parse(cls, reader: PacketReader, context: Context) -> Self:
        status = BNVSResponseType(reader.read_bytes(1))
        num_cd_keys = reader.read_u8()

        cd_key_response = b""
        if num_cd_keys == 1:
            cd_key_response = reader.read_lp8()

        master_password_response = reader.read_lp8()
        game_password_response = b""
        if status == BNVSResponseType.PASSWORD_REQUIRED:
            game_password_response = reader.read_lp8()

        return cls(
            cd_key_response=cd_key_response,
            master_password_response=master_password_response,
            game_password_response=game_password_response,
        )

    def dump(self, context: Context) -> bytes:
        wr = PacketWriter(self.HEAD)
        wr.write_bytes(b"P" if self.game_password_response else b"V")
        wr.write_u8(1 if self.cd_key_response else 0)
        if self.cd_key_response:
            wr.write_lp8(self.cd_key_response)
        wr.write_lp8(self.master_password_response)
        if self.game_password_response:
            wr.write_lp8(self.game_password_response)
        return wr.getvalue()


class BNVRConnectionStatus(Enum):
    REJECTED = b"R"
    ACCEPTED = b"A"


@dataclass(kw_only=True)
class BNVR(Packet, head=b"BNVR"):
    connection_status: BNVRConnectionStatus
    rejection_reason: AuthenticationResult = AuthenticationResult.OK

    app_id: int = 0

    server_build: int = 0
    server_patch: int = 0
    server_postfix: int = 0

    @classmethod
    def parse(cls, reader: PacketReader, context: Context) -> Self:
        status = BNVRConnectionStatus(reader.read_bytes(1))
        if status == BNVRConnectionStatus.REJECTED:
            rejection_reason = AuthenticationResult(reader.read_u8())
            return cls(
                connection_status=BNVRConnectionStatus.REJECTED,
                rejection_reason=rejection_reason,
            )
        app_id = reader.read_u32()
        server_build = 0
        server_patch = 0
        server_postfix = 0
        if not reader.at_end:
            server_build = reader.read_u32()  # 8193.14+
        if not reader.at_end:
            server_patch = reader.read_u32()  # 8193.14+
        if not reader.at_end:
            server_postfix = reader.read_u32()  # 8193.36.1+

        return cls(
            connection_status=BNVRConnectionStatus.ACCEPTED,
            rejection_reason=AuthenticationResult.OK,
            app_id=app_id,
            server_build=server_build,
            server_patch=server_patch,
            server_postfix=server_postfix,
        )

    def dump(self, context: Context) -> bytes:
        wr = PacketWriter(self.HEAD)
        if self.connection_status == BNVRConnectionStatus.REJECTED:
            wr.write_bytes(b"R")
            wr.write_u8(self.rejection_reason.value)
            return wr.getvalue()
        wr.write_bytes(b"A")
        wr.write_u32(self.app_id)
        if self.server_build is not None:
            wr.write_u32(self.server_build)
        if self.server_patch is not None:
            wr.write_u32(self.server_patch)
        if self.server_postfix is not None:
            wr.write_u32(self.server_postfix)
        return wr.getvalue()
