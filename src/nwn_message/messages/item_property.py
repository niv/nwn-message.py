from typing import Annotated
from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class ItemPropertyEntry:
    name: m.Word
    subtype: m.Word
    cost_table_value: m.Word
    param1: m.Byte


@dataclass(kw_only=True)
class ItemUsesLeft:
    useable_properties: m.Byte
    uses: Annotated[
        list[m.Byte],
        m.BitmaskConditionedList(m.MessageType.BYTE, m.SizePrefix.BYTE, 8),
    ]


@dataclass(kw_only=True)
class OriginalItemName:
    name: m.LocStr


@dataclass(kw_only=True)
class DisplayItemName:
    name: m.String


ItemName = Annotated[
    OriginalItemName | DisplayItemName,
    m.Tagged(
        m.MessageType.BOOL,
        {
            True: OriginalItemName,
            False: DisplayItemName,
        },
    ),
]


@dataclass(kw_only=True)
class ItemPropertyUpdateUses(m.Message):
    MAJOR = 0x18
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    uses_left: ItemUsesLeft


@dataclass(kw_only=True)
class ItemPropertyUpdateProps(m.Message):
    MAJOR = 0x18
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    properties: Annotated[list[ItemPropertyEntry], m.SizePrefix.BYTE]
    uses_left: ItemUsesLeft


@dataclass(kw_only=True)
class ItemPropertyUpdateName(m.Message):
    MAJOR = 0x18
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    name: ItemName


@dataclass(kw_only=True)
class ItemPropertyUpdateHidden(m.Message):
    MAJOR = 0x18
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    hidden: m.Bool


@dataclass(kw_only=True)
class ItemPropertyUpdateTextBubbleOverride(m.Message):
    MAJOR = 0x18
    MINOR = 0x05
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    text_bubble_type: m.Int
    text_bubble_text: m.String
