from dataclasses import dataclass
from typing import Annotated

from .. import message as m


@dataclass(kw_only=True)
class LoginLocalCharacter(m.Message):
    MAJOR = 0x02
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    character_data: m.Void


@dataclass(kw_only=True)
class LoginServerCharacter(m.Message):
    MAJOR = 0x02
    MINOR = 0x02
    DIRECTION = m.Direction.C2S

    resref: m.ResRef


@dataclass(kw_only=True)
class LoginVaultCharacter(m.Message):
    MAJOR = 0x02
    MINOR = 0x03
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class LoginDMCharacter(m.Message):
    MAJOR = 0x02
    MINOR = 0x04
    DIRECTION = m.Direction.C2S

    character_data: m.Void


@dataclass(kw_only=True)
class LoginConfirm(m.Message):
    MAJOR = 0x02
    MINOR = 0x05
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class LoginDeny(m.Message):
    MAJOR = 0x02
    MINOR = 0x06
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class LoginCharacterQuery(m.Message):
    MAJOR = 0x02
    MINOR = 0x0A
    DIRECTION = m.Direction.S2C

    classes: Annotated[list[tuple[m.Int, m.Byte]], m.SizePrefix.BYTE]
    xp: m.Dword


@dataclass(kw_only=True)
class LoginCharacterResponse(m.Message):
    MAJOR = 0x02
    MINOR = 0x0B
    DIRECTION = m.Direction.C2S

    use_save_game_character: m.Bool


@dataclass(kw_only=True)
class LoginGetWaypoint(m.Message):
    MAJOR = 0x02
    MINOR = 0x0C
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class LoginWaypointResponse(m.Message):
    MAJOR = 0x02
    MINOR = 0x0D
    DIRECTION = m.Direction.C2S

    waypoint: m.String


@dataclass(kw_only=True)
class LoginServerSaveGameCharacter(m.Message):
    MAJOR = 0x02
    MINOR = 0x0E
    DIRECTION = m.Direction.C2S

    resref: m.ResRef


@dataclass(kw_only=True)
class LoginIFOCharacter(m.Message):
    MAJOR = 0x02
    MINOR = 0x0F
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class LoginNeedCharacter(m.Message):
    MAJOR = 0x02
    MINOR = 0x10
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class LoginServerSubDirCharacter(m.Message):
    MAJOR = 0x02
    MINOR = 0x11
    DIRECTION = m.Direction.C2S

    resref: m.ResRef


@dataclass(kw_only=True)
class LoginCharacterFail(m.Message):
    MAJOR = 0x02
    MINOR = 0x12
    DIRECTION = m.Direction.S2C

    reason: m.Dword


@dataclass(kw_only=True)
class LoginNewServerCharacter(m.Message):
    MAJOR = 0x02
    MINOR = 0x13
    DIRECTION = m.Direction.C2S

    character_data: m.Void
