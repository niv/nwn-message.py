import logging
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Annotated, Self

from .. import message as m
from ..context import Context
from ..net_types import VisualTransformData
from ..types import ObjectType

logger = logging.getLogger(__name__)

CNWITEM_ARMORPART_NUM = 19
CNWITEM_NUM_LAYEREDTEXTURECOLORS = 6

MODELTYPE_SIMPLE = 0
MODELTYPE_LAYERED = 1
MODELTYPE_COMPOSITE = 2
MODELTYPE_ARMOR = 3

CNWITEM_BASEITEM_ARMOR = 16


@dataclass(kw_only=True)
class SimpleModel:
    part1: m.Word


@dataclass(kw_only=True)
class CompositeModel:
    part1: m.Word
    part2: m.Word
    part3: m.Word
    vis_effect: m.Byte


@dataclass(kw_only=True)
class LayeredModel:
    part1: m.Word
    palette: Annotated[list[m.Byte], m.FixedSizeHint(CNWITEM_NUM_LAYEREDTEXTURECOLORS)]


@dataclass(kw_only=True)
class ArmorModel:
    parts: Annotated[list[m.Word], m.FixedSizeHint(CNWITEM_ARMORPART_NUM)]
    palette: Annotated[list[m.Byte], m.FixedSizeHint(CNWITEM_NUM_LAYEREDTEXTURECOLORS)]
    palette_per_part: Annotated[
        list[
            Annotated[
                list[m.Byte],
                m.FixedSizeHint(CNWITEM_NUM_LAYEREDTEXTURECOLORS),
            ]
        ],
        m.FixedSizeHint(CNWITEM_ARMORPART_NUM),
    ]


ItemModelData = SimpleModel | CompositeModel | LayeredModel | ArmorModel


# [TODO] surely this must be doable in a cleaner fashion


@dataclass
class OriginalCreatureName:
    first: m.LocStr
    last: m.LocStr


@dataclass
class DisplayCreatureName:
    name: m.String


CreatureName = Annotated[
    OriginalCreatureName | DisplayCreatureName,
    m.Tagged(
        m.MessageType.BOOL,
        {True: OriginalCreatureName, False: DisplayCreatureName},
    ),
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
        {True: OriginalItemName, False: DisplayItemName},
    ),
]


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
class SoundsetInfo:
    soundset: m.Word
    footstep_type: m.Int


@dataclass(kw_only=True)
class CreaturePartInfo:
    # We just store the full list of parts, and reconstruct the sparse
    # representation on write, and reconstruct the full representation on read.
    # We hide the needless 1990s overoptimisation away from the poor API user.
    #
    # This list must always have length CNWITEM_ARMORPART_NUM.
    parts: list[m.Word]

    @classmethod
    def read(cls, rd: m.Reader, context: Context) -> Self:
        n = rd.read_byte()
        if n == 0:
            return cls(parts=[0] * CNWITEM_ARMORPART_NUM)
        if n < 10:
            sparse = {}
            for _ in range(n):
                idx = rd.read_byte()
                sparse[idx] = rd.read_word()
            return cls(parts=[sparse.get(i, 0) for i in range(CNWITEM_ARMORPART_NUM)])
        else:
            return cls(parts=[rd.read_word() for _ in range(CNWITEM_ARMORPART_NUM)])

    def write(self, wr: m.Writer, context: Context) -> None:
        if len(self.parts) != CNWITEM_ARMORPART_NUM:
            raise ValueError(f"parts list must have length {CNWITEM_ARMORPART_NUM}")
        non_zero = [(i, v) for i, v in enumerate(self.parts) if v != 0]
        n = len(non_zero)
        if n == 0:
            wr.write_byte(0)
        elif n < 10:
            wr.write_byte(n)
            for idx, val in non_zero:
                wr.write_byte(idx)
                wr.write_word(val)
        else:
            wr.write_byte(CNWITEM_ARMORPART_NUM)
            for val in self.parts:
                wr.write_word(val)


@dataclass(kw_only=True)
class ItemAppearanceAndProps:
    base_item_id: m.Dword
    model_data: Annotated[
        ItemModelData,
        m.TwoDATagged(
            field="base_item_id",
            twoda="baseitems",
            column="ModelType",
            lut={
                MODELTYPE_SIMPLE: SimpleModel,
                MODELTYPE_LAYERED: LayeredModel,
                MODELTYPE_COMPOSITE: CompositeModel,
                MODELTYPE_ARMOR: ArmorModel,
            },
        ),
    ]
    vt: VisualTransformData

    armor_value: Annotated[m.Short, m.IfEq("base_item_id", CNWITEM_BASEITEM_ARMOR)]
    name: ItemName
    identified: m.Bool
    cost: m.Dword
    stack_size: m.Dword
    useable: m.Bool
    stolen: m.Bool
    cursed: m.Bool
    hidden: m.Bool
    text_bubble_type: m.Int
    text_bubble_text: m.String
    properties: Annotated[list[ItemPropertyEntry], m.SizePrefix.BYTE]
    uses_left: ItemUsesLeft


class UpdateCreatureAppearanceFlags(IntEnum):
    RACE = 0x0001
    PHENOTYPE = 0x0002
    GENDER = 0x0004
    SKIN_COLOR = 0x0008
    HAIR_COLOR = 0x0010
    TATTOO1 = 0x0020
    TATTOO2 = 0x0040
    HEAD_VARIATION = 0x0080
    PART_INFO = 0x0100
    ITEM_INFO = 0x0200
    NAME = 0x0400
    TAIL_VARIATION = 0x0800
    WING_VARIATION = 0x1000
    SOUNDSET = 0x2000
    WALK_ANIMATION = 0x4000
    ALL = 0xFFFF


F = UpdateCreatureAppearanceFlags


@dataclass(kw_only=True)
class EquippedItemAdd:
    oid: m.ObjectId
    slot: m.Dword
    item: ItemAppearanceAndProps


@dataclass(kw_only=True)
class EquippedItemUpdate:
    oid: m.ObjectId
    slot: m.Dword
    vis_effect: m.Byte
    vt: VisualTransformData


@dataclass(kw_only=True)
class EquippedItemDelete:
    oid: m.ObjectId
    slot: m.Dword


EquippedItem = Annotated[
    EquippedItemAdd | EquippedItemUpdate | EquippedItemDelete,
    m.Tagged(
        m.MessageType.CHAR,
        {
            ord("A"): EquippedItemAdd,
            ord("U"): EquippedItemUpdate,
            ord("D"): EquippedItemDelete,
        },
    ),
]


@dataclass(kw_only=True)
class GameObjUpdateObjListAppearanceCreature(m.SubMessage):
    object_type: Annotated[ObjectType, m.MessageType.BYTE]
    object_id: m.ObjectId
    flags: Annotated[UpdateCreatureAppearanceFlags, m.MessageType.WORD]

    name: Annotated[CreatureName, m.IfFlag("flags", F.NAME)]
    race: Annotated[m.Word, m.IfFlag("flags", F.RACE)] = 0
    phenotype: Annotated[m.Byte, m.IfFlag("flags", F.PHENOTYPE)] = 0
    gender: Annotated[m.Byte, m.IfFlag("flags", F.GENDER)] = 0
    head_variation: Annotated[m.Word, m.IfFlag("flags", F.HEAD_VARIATION)] = 0
    tail_variation: Annotated[m.Dword, m.IfFlag("flags", F.TAIL_VARIATION)] = 0
    wing_variation: Annotated[m.Dword, m.IfFlag("flags", F.WING_VARIATION)] = 0
    skin_color: Annotated[m.Byte, m.IfFlag("flags", F.SKIN_COLOR)] = 0
    hair_color: Annotated[m.Byte, m.IfFlag("flags", F.HAIR_COLOR)] = 0
    tattoo1: Annotated[m.Byte, m.IfFlag("flags", F.TATTOO1)] = 0
    tattoo2: Annotated[m.Byte, m.IfFlag("flags", F.TATTOO2)] = 0
    part_info: Annotated[CreaturePartInfo | None, m.IfFlag("flags", F.PART_INFO)] = None
    soundset_info: Annotated[SoundsetInfo | None, m.IfFlag("flags", F.SOUNDSET)] = None
    walk_animation: Annotated[m.Byte, m.IfFlag("flags", F.WALK_ANIMATION)] = 0
    equipped_items: Annotated[
        list[EquippedItem], m.SizePrefix.BYTE, m.IfFlag("flags", F.ITEM_INFO)
    ] = field(default_factory=list)
