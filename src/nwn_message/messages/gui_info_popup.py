from dataclasses import dataclass
from typing import Annotated

from .. import message as m

INVALID_OBJECT_ID = 0x7F000000


@dataclass(kw_only=True)
class LocDescription:
    text: m.LocStr


@dataclass(kw_only=True)
class StringDescription:
    text: m.String


DescriptionText = Annotated[
    LocDescription | StringDescription,
    m.Tagged(
        m.MessageType.BOOL,
        {
            False: LocDescription,
            True: StringDescription,
        },
    ),
]


@dataclass(kw_only=True)
class OriginalCreatureName:
    first: m.LocStr
    last: m.LocStr


@dataclass(kw_only=True)
class DisplayCreatureName:
    name: m.String


CreatureName = Annotated[
    OriginalCreatureName | DisplayCreatureName,
    m.Tagged(
        m.MessageType.BOOL,
        {
            True: OriginalCreatureName,
            False: DisplayCreatureName,
        },
    ),
]


@dataclass(kw_only=True)
class EffectIcons:
    icons: Annotated[list[m.Word], m.SizePrefix.WORD]


@dataclass(kw_only=True)
class ExamineItemProperty:
    name: m.Word
    subtype: m.Word
    cost_table_value: m.Word
    param1: m.Byte
    temporary: m.Bool


@dataclass(kw_only=True)
class GuiInfoPopupExamineItemData(m.Message):
    MAJOR = 0x1B
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    creature: Annotated[m.ObjectId, m.IfNotEq("item", INVALID_OBJECT_ID)]
    identified: Annotated[m.Bool, m.IfNotEq("item", INVALID_OBJECT_ID)]
    useable: Annotated[
        m.Bool, m.IfEq("identified", True), m.IfNotEq("item", INVALID_OBJECT_ID)
    ]
    description: Annotated[DescriptionText, m.IfNotEq("item", INVALID_OBJECT_ID)]
    can_equip: Annotated[m.Bool, m.IfNotEq("item", INVALID_OBJECT_ID)]
    min_level: Annotated[
        m.Byte, m.IfEq("can_equip", False), m.IfNotEq("item", INVALID_OBJECT_ID)
    ]
    num_charges: Annotated[m.Int, m.IfNotEq("item", INVALID_OBJECT_ID)]
    weight: Annotated[m.Int, m.IfNotEq("item", INVALID_OBJECT_ID)]
    dm_examine: Annotated[m.Bool, m.IfNotEq("item", INVALID_OBJECT_ID)]
    cost: Annotated[
        m.Dword, m.IfEq("dm_examine", True), m.IfNotEq("item", INVALID_OBJECT_ID)
    ]
    properties: Annotated[
        list[ExamineItemProperty],
        m.SizePrefix.WORD,
        m.IfEq("identified", True),
        m.IfNotEq("item", INVALID_OBJECT_ID),
    ]


@dataclass(kw_only=True)
class GuiInfoPopupExamineCreatureData(m.Message):
    MAJOR = 0x1B
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    creature: m.ObjectId
    description: DescriptionText
    full_message: m.Bool
    name: Annotated[CreatureName, m.IfEq("full_message", True)]
    portrait_id: Annotated[m.Word, m.IfEq("full_message", True)]
    portrait_resref: Annotated[
        m.ResRef, m.IfGt("portrait_id", 0xFFFD), m.IfEq("full_message", True)
    ]
    damage_level: Annotated[m.Byte, m.IfEq("full_message", True)]
    ai_state_reaction: Annotated[m.Byte, m.IfEq("full_message", True)]
    display_challenge_rating: Annotated[m.Bool, m.IfEq("full_message", True)]
    challenge_rating: Annotated[
        m.Float, m.IfEq("display_challenge_rating", True), m.IfEq("full_message", True)
    ]
    display_effects: Annotated[m.Bool, m.IfEq("full_message", True)]
    effects: Annotated[
        EffectIcons, m.IfEq("display_effects", True), m.IfEq("full_message", True)
    ]
    dm_examine: Annotated[m.Bool, m.IfEq("full_message", True)]
    experience: Annotated[
        m.Int, m.IfEq("dm_examine", True), m.IfEq("full_message", True)
    ]
    gold: Annotated[m.Dword, m.IfEq("dm_examine", True), m.IfEq("full_message", True)]


@dataclass(kw_only=True)
class GuiInfoPopupExaminePlaceableData(m.Message):
    MAJOR = 0x1B
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    placeable: m.ObjectId
    description: DescriptionText


@dataclass(kw_only=True)
class GuiInfoPopupExamineTrapData(m.Message):
    MAJOR = 0x1B
    MINOR = 0x05
    DIRECTION = m.Direction.S2C

    trap: m.ObjectId
    success: m.Bool
    has_description_override: m.Bool
    description_override: Annotated[m.String, m.IfEq("has_description_override", True)]
    base_type: m.Byte
    trap_difficulty: m.Byte


@dataclass(kw_only=True)
class GuiInfoPopupExamineDoorData(m.Message):
    MAJOR = 0x1B
    MINOR = 0x06
    DIRECTION = m.Direction.S2C

    door: m.ObjectId
    description: DescriptionText
