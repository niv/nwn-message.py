from dataclasses import dataclass
from typing import Annotated

from .. import message as m


@dataclass(kw_only=True)
class DebugInfoCreature(m.Message):
    MAJOR = 0x21
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    oid: m.ObjectId
    tag: m.String
    faction_name: m.String
    dialog_resref: m.ResRef
    hp_current: m.Short
    hp_max: m.Short
    armor_class: m.Short
    ai_level: m.Int
    challenge_rating: m.Float
    area_tag: m.String
    equipped_item_tags: Annotated[
        list[m.String],
        m.BitmaskConditionedList(m.MessageType.STRING, m.SizePrefix.DWORD, 18),
    ]
    repository_item_tags: Annotated[list[m.String], m.SizePrefix.DWORD]


@dataclass(kw_only=True)
class DebugInfoItem(m.Message):
    MAJOR = 0x21
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    oid: m.ObjectId
    tag: m.String
    passive_property_ids: Annotated[list[m.Word], m.SizePrefix.INT]


@dataclass(kw_only=True)
class DebugInfoPlaceable(m.Message):
    MAJOR = 0x21
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    oid: m.ObjectId
    first_name: m.LocStr
    tag: m.String
    hardness: m.Byte
    hp_current: m.Short
    fort_save: m.Byte
    reflex_save: m.Byte
    will_save: m.Byte
    template_resref: m.ResRef
    faction_name: m.String


@dataclass(kw_only=True)
class DebugInfoArea(m.Message):
    MAJOR = 0x21
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    oid: m.ObjectId
    tag: m.String


@dataclass(kw_only=True)
class DebugInfoString(m.Message):
    MAJOR = 0x21
    MINOR = 0x05
    DIRECTION = m.Direction.S2C

    debug_string: m.String


@dataclass(kw_only=True)
class DebugInfoDoor(m.Message):
    MAJOR = 0x21
    MINOR = 0x06
    DIRECTION = m.Direction.S2C

    oid: m.ObjectId
    first_name: m.LocStr
    tag: m.String
    hardness: m.Byte
    hp_current: m.Short
    fort_save: m.Byte
    reflex_save: m.Byte
    will_save: m.Byte
    template_resref: m.ResRef
    faction_name: m.String
    key_name: m.String


@dataclass(kw_only=True)
class DebugInfoTrigger(m.Message):
    MAJOR = 0x21
    MINOR = 0x07
    DIRECTION = m.Direction.S2C

    oid: m.ObjectId
    first_name: m.LocStr
    tag: m.String
