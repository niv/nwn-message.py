from dataclasses import dataclass
from typing import Annotated
from enum import IntEnum

from .. import message as m


@dataclass(kw_only=True)
class ClientSideMessageSimpleAdjective(m.Message):
    MAJOR = 0x12
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    target: m.ObjectId
    adjective_strref: m.Dword


@dataclass(kw_only=True)
class ClientSideMessageUseSkill(m.Message):
    MAJOR = 0x12
    MINOR = 0x09
    DIRECTION = m.Direction.S2C

    MESSAGE_SIZE_DIE_ROLL = 5
    MESSAGE_SIZE_DIFFICULTY_CLASS = 7

    target: m.ObjectId
    skill_strref: m.Dword
    die_roll: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_DIE_ROLL)]
    modifier: m.Char
    difficulty_class: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_DIFFICULTY_CLASS)]
    is_take20: m.Bool
    result: m.Byte


@dataclass(kw_only=True)
class ClientSideMessagePolymorph(m.Message):
    MAJOR = 0x12
    MINOR = 0x11
    DIRECTION = m.Direction.S2C

    morpher: m.ObjectId
    is_polymorphed: m.Bool
    allow_cancel: m.Bool


@dataclass(kw_only=True)
class ClientSideMessageVibrate(m.Message):
    MAJOR = 0x12
    MINOR = 0x13
    DIRECTION = m.Direction.S2C

    motor: m.Int
    strength: m.Float
    duration: m.Float


@dataclass(kw_only=True)
class ClientSideMessageUnlockAchievement(m.Message):
    MAJOR = 0x12
    MINOR = 0x14
    DIRECTION = m.Direction.S2C

    achievement_id: m.String
    last_value: m.Int
    current_value: m.Int
    maximum_value: m.Int


@dataclass(kw_only=True)
class ClientSideMessageEnterTargetingMode(m.Message):
    MAJOR = 0x12
    MINOR = 0x17
    DIRECTION = m.Direction.S2C

    valid_object_types: m.Int
    mouse_cursor_id: m.Int
    bad_target_cursor_id: m.Int


@dataclass(kw_only=True)
class ClientSideMessageCastSpell(m.Message):
    MAJOR = 0x12
    MINOR = 0x08
    DIRECTION = m.Direction.S2C

    target: m.ObjectId
    spell_id: m.Dword
    display: m.Bool
    casting: m.Bool
    is_item_cast: m.Bool
    # When is_item_cast and display: item name is sent
    is_loc_name: Annotated[
        m.Bool, m.IfEq("is_item_cast", True), m.IfEq("display", True)
    ]
    item_loc_name: Annotated[
        m.LocStr,
        m.IfEq("is_item_cast", True),
        m.IfEq("display", True),
        m.IfEq("is_loc_name", True),
    ]
    item_display_name: Annotated[
        m.String,
        m.IfEq("is_item_cast", True),
        m.IfEq("display", True),
        m.IfEq("is_loc_name", False),
    ]
    # When is_item_cast and not display: base item id is sent
    base_item_id: Annotated[
        m.Byte, m.IfEq("is_item_cast", True), m.IfEq("display", False)
    ]


@dataclass(kw_only=True)
class ClientSideMessageModifySelection(m.Message):
    MAJOR = 0x12
    MINOR = 0x18
    DIRECTION = m.Direction.S2C

    class ModifySelectionAction(IntEnum):
        CLEAR = ord("C")
        ADD = ord("A")
        TOGGLE = ord("T")
        REMOVE = ord("R")

    action: Annotated[ModifySelectionAction, m.MessageType.BYTE]
    _empty_size: Annotated[m.Dword, m.IfEq("action", ModifySelectionAction.CLEAR)]
    objects: Annotated[
        list[m.ObjectId],
        m.SizePrefix.DWORD,
        m.IfNotEq("action", ModifySelectionAction.CLEAR),
    ]
