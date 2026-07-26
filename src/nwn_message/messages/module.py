from dataclasses import dataclass, field
from typing import Annotated
from enum import IntFlag, IntEnum

from .. import message as m


class CampaignIndicator(IntEnum):
    NONE = 0
    NWN = 1
    XP1 = 2
    XP2 = 3


@dataclass(kw_only=True)
class ModuleInfo(m.Message):
    MAJOR = 0x03
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    @dataclass(kw_only=True)
    class Area:
        object_id: m.ObjectId
        name: m.String

    resource_name: m.String
    module_name: m.LocStr
    minutes_per_hour: m.Byte = 5
    start_movie: m.ResRef = ""
    areas: Annotated[list[Area], m.SizePrefix.DWORD]
    campaign_indicator: Annotated[CampaignIndicator, m.MessageType.BYTE] = (
        CampaignIndicator.NONE
    )
    use_max_hitpoints: m.Bool = False
    hide_hitpoints_gained: m.Bool = False
    player_party_control: m.Bool = False
    show_player_join_messages: m.Bool = False


@dataclass(kw_only=True)
class ModuleLoaded(m.Message):
    MAJOR = 0x03
    MINOR = 0x02
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class ModuleTime(m.Message):
    MAJOR = 0x03
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    class _F(IntFlag):
        STATE = 0x01
        HOUR = 0x02
        DAY = 0x04
        MONTH = 0x08
        YEAR = 0x10

    flags: Annotated[_F, m.MessageType.BYTE]
    hour: Annotated[m.Byte, m.IfFlag("flags", _F.HOUR)]
    day: Annotated[m.Byte, m.IfFlag("flags", _F.DAY)]
    month: Annotated[m.Byte, m.IfFlag("flags", _F.MONTH)]
    year: Annotated[m.Dword, m.IfFlag("flags", _F.YEAR)]


@dataclass(kw_only=True)
class ModuleSaveGame(m.Message):
    MAJOR = 0x03
    MINOR = 0x04
    DIRECTION = m.Direction.C2S

    slot: m.Dword
    save_name: m.String
    module_name: m.String
    overwrite_name: m.String


@dataclass(kw_only=True)
class ModuleLoadGame(m.Message):
    MAJOR = 0x03
    MINOR = 0x05
    DIRECTION = m.Direction.C2S

    slot: m.Dword
    save_name: m.String
    module_name: m.String
    import_char: m.Bool


@dataclass(kw_only=True)
class ModuleLoading(m.Message):
    MAJOR = 0x03
    MINOR = 0x06
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class ModuleRunModule(m.Message):
    MAJOR = 0x03
    MINOR = 0x07
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class ModuleDumpPlayer(m.Message):
    MAJOR = 0x03
    MINOR = 0x08
    DIRECTION = m.Direction.S2C


class PauseState(IntEnum):
    NONE = 0
    TIMESTOP = 1
    PAUSED = 2


@dataclass(kw_only=True)
class ModuleSetPauseState(m.Message):
    MAJOR = 0x03
    MINOR = 0x09
    DIRECTION = m.Direction.S2C

    state: Annotated[PauseState, m.MessageType.BYTE, m.Bits(2)]
    pause: m.Bool
    excluded_objects: Annotated[list[m.ObjectId], m.SizePrefix.WORD]


@dataclass(kw_only=True)
class ModuleExportReply(m.Message):
    MAJOR = 0x03
    MINOR = 0x0A
    DIRECTION = m.Direction.S2C

    first_name: m.LocStr
    last_name: m.LocStr
    character_data: m.Void = field(repr=False)


@dataclass(kw_only=True)
class ModuleStartStartNewModule(m.Message):
    MAJOR = 0x03
    MINOR = 0x0B
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class ModuleEndStartNewModule(m.Message):
    MAJOR = 0x03
    MINOR = 0x0C
    DIRECTION = m.Direction.S2C

    success: m.Bool


class SaveGameStatus(IntEnum):
    START = 1
    SUCCESS = 2


@dataclass(kw_only=True)
class ModuleSaveGameStatus(m.Message):
    MAJOR = 0x03
    MINOR = 0x0D
    DIRECTION = m.Direction.S2C

    status: Annotated[SaveGameStatus, m.Byte]


@dataclass(kw_only=True)
class ModuleEndGame(m.Message):
    MAJOR = 0x03
    MINOR = 0x0E
    DIRECTION = m.Direction.S2C

    movie_name: m.String
    nwsync_manifest: m.String = ""
