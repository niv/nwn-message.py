from typing import Annotated, Self
from dataclasses import dataclass, field
from enum import IntFlag, IntEnum
import logging

from ..context import Context
from .. import message as m

logger = logging.getLogger(__name__)

CNWSPELL_NUM_LEVELS = 10
NWACTION_MOVETOPOINT = 0
NWACTION_DROPITEM = 2
NWACTION_CASTSPELL = 4
NWACTION_SETTRAP = 12
NWACTION_ITEMCASTSPELL = 19

_VECTOR_ACTIONS = {
    NWACTION_MOVETOPOINT,
    NWACTION_CASTSPELL,
    NWACTION_ITEMCASTSPELL,
    NWACTION_DROPITEM,
    NWACTION_SETTRAP,
}
_SPELL_ACTIONS = {NWACTION_CASTSPELL, NWACTION_ITEMCASTSPELL}
_NO_TARGET_ACTIONS = {NWACTION_MOVETOPOINT, NWACTION_DROPITEM}


class UpdatePlayerCreatureFlags(IntFlag):
    AC_GOLD_WEIGHT_LEVELUP = 0x00000001
    GUISKILL = 0x00000002
    FEAT = 0x00000004
    STATE = 0x00000008
    GUIKNOWNSPELL = 0x00000010
    GUIMEMORIZEDSPELL = 0x00000020
    GUIKNOWNSPELLUSES = 0x00000040
    GUINUMBERMEMORIZEDSPELLS = 0x00000080
    ACTION_QUEUE = 0x00000100
    AUTOMAP = 0x00000200
    EFFECT_ICONS = 0x00000400
    ABILITY_SCORES = 0x00000800
    NEWOBJECT = 0x00001000
    PERCEPTION = 0x00002000
    SPELLLIKEABILITY = 0x00004000
    POLYMORPHSPELL = 0x00008000


F = UpdatePlayerCreatureFlags


@dataclass(kw_only=True)
class LevelUpInfo:
    skill_pts: m.Word
    skill_ranks: Annotated[list[m.Char], m.TwoDARowCountHint("skills")]
    familiar_type: m.Int
    familiar_name: m.String
    companion_type: m.Int
    companion_name: m.String
    starting_package_new: m.Dword
    starting_package_old: m.Byte
    multiclass_level: m.Byte


@dataclass(kw_only=True)
class AcGoldWeightLevelUp:
    ac: m.Short
    gold: m.Dword
    weight: m.Int
    can_level_up: m.Bool
    level_up_info: Annotated[LevelUpInfo, m.IfEq("can_level_up", True)]


@dataclass(kw_only=True)
class PolymorphSpells:
    spell_id_1: m.Int
    spell_id_2: m.Int
    spell_id_3: m.Int


@dataclass(kw_only=True)
class SpellSlotClassUpdate:
    # Both GUINUMBERMEMORIZEDSPELLS and GUIKNOWNSPELLUSES share this wire format
    class_index: m.Byte
    level_flag: Annotated[int, m.MessageType.WORD]
    level_0: Annotated[m.Byte, m.IfFlag("level_flag", 1 << 0)]
    level_1: Annotated[m.Byte, m.IfFlag("level_flag", 1 << 1)]
    level_2: Annotated[m.Byte, m.IfFlag("level_flag", 1 << 2)]
    level_3: Annotated[m.Byte, m.IfFlag("level_flag", 1 << 3)]
    level_4: Annotated[m.Byte, m.IfFlag("level_flag", 1 << 4)]
    level_5: Annotated[m.Byte, m.IfFlag("level_flag", 1 << 5)]
    level_6: Annotated[m.Byte, m.IfFlag("level_flag", 1 << 6)]
    level_7: Annotated[m.Byte, m.IfFlag("level_flag", 1 << 7)]
    level_8: Annotated[m.Byte, m.IfFlag("level_flag", 1 << 8)]
    level_9: Annotated[m.Byte, m.IfFlag("level_flag", 1 << 9)]


@dataclass(kw_only=True)
class KnownSpellClassUpdate:
    spells_to_delete: Annotated[list[m.Dword], m.SizePrefix.WORD]
    spells_to_add: Annotated[list[m.Dword], m.SizePrefix.WORD]


@dataclass(kw_only=True)
class MemorizedSpellDelete:
    spell_level: m.Byte
    spell_slot: m.Byte


@dataclass(kw_only=True)
class MemorizedSpellAdd:
    spell_id: m.Dword
    spell_slot: m.Byte
    spell_level: m.Byte
    readied: m.Bool
    domain_spell: m.Bool
    meta_type: m.Byte


@dataclass(kw_only=True)
class MemorizedSpellClassUpdate:
    spells_to_delete: Annotated[list[MemorizedSpellDelete], m.SizePrefix.WORD]
    spells_to_add: Annotated[list[MemorizedSpellAdd], m.SizePrefix.WORD]


@dataclass(kw_only=True)
class EffectIconAdd:
    icon: m.Word
    flashing: m.Bool


@dataclass(kw_only=True)
class EffectIconsUpdate:
    remove: Annotated[list[m.Word], m.SizePrefix.WORD]
    add: Annotated[list[EffectIconAdd], m.SizePrefix.WORD]


class FeatChangeType(IntEnum):
    ADD = ord("A")
    DELETE = ord("D")
    BONUS_ADD = ord("B")
    BONUS_DELETE = ord("X")


@dataclass(kw_only=True)
class FeatChange:
    change_type: Annotated[int, m.MessageType.CHAR]
    feat_id: m.Word


@dataclass(kw_only=True)
class FeatUse:
    feat_id: m.Word
    uses_remaining: m.Byte


@dataclass(kw_only=True)
class FeatUpdate:
    changes: Annotated[list[FeatChange], m.SizePrefix.WORD]
    uses: Annotated[list[FeatUse], m.SizePrefix.WORD]


@dataclass(kw_only=True)
class AutoMapUpdate:
    """
    Three encoding strategies selected by two BOOL flags.

    Strategy 1 (explore_all=True, bitstream=False): >=90% tiles changed.
      DWORD count; if 0 all explored, else count×(BYTE x, BYTE y) explored tiles.
    Strategy 2 (explore_all=False, bitstream=False): <10% tiles changed.
      DWORD count; count×(BOOL explored, BYTE x, BYTE y) sparse updates.
    Strategy 3 (explore_all=False, bitstream=True): 10-90% tiles changed.
      BYTE num_bytes; num_bytes×BYTE raw tile bitstream.

    This remains imperative because the wire format multiplexes three
    incompatible encodings behind two leading BOOLs; BitmaskConditionedList
    only models the sparse-bitmask variant of list presence.
    """

    explore_all: bool
    bitstream: bool
    tile_coords: list
    raw_bytes: bytes | None = None

    @classmethod
    def read(cls, rd: m.Reader, context: Context) -> Self:
        explore_all = rd.read_bool()
        bitstream = rd.read_bool()

        if explore_all and not bitstream:
            count = rd.read_dword()
            tiles = [(rd.read_byte(), rd.read_byte()) for _ in range(count)]
            return cls(explore_all=True, bitstream=False, tile_coords=tiles)
        elif not explore_all and not bitstream:
            count = rd.read_dword()
            tiles = [
                (rd.read_bool(), rd.read_byte(), rd.read_byte()) for _ in range(count)
            ]
            return cls(explore_all=False, bitstream=False, tile_coords=tiles)
        else:
            num_bytes = rd.read_byte()
            raw = bytes(rd.read_byte() for _ in range(num_bytes))
            return cls(
                explore_all=False,
                bitstream=True,
                tile_coords=[],
                raw_bytes=raw,
            )

    def write(self, wr: m.Writer, context: Context) -> None:
        wr.write_bool(self.explore_all)
        wr.write_bool(self.bitstream)

        if self.explore_all and not self.bitstream:
            wr.write_dword(len(self.tile_coords))
            for x, y in self.tile_coords:
                wr.write_byte(x)
                wr.write_byte(y)
        elif not self.explore_all and not self.bitstream:
            wr.write_dword(len(self.tile_coords))
            for explored, x, y in self.tile_coords:
                wr.write_bool(explored)
                wr.write_byte(x)
                wr.write_byte(y)
        else:
            raw_bytes = self.raw_bytes or b""
            wr.write_byte(len(raw_bytes))
            for b in raw_bytes:
                wr.write_byte(b)


@dataclass(kw_only=True)
class ActionQueueDelete:
    id: m.Word
    group_id: m.Word


@dataclass(kw_only=True)
class ActionQueueSpecialAttack:
    special_attack_id: m.Word
    group_id: m.Word
    target: m.ObjectId


@dataclass(kw_only=True)
class ActionQueueAdd:
    action_id: m.Word
    group_id: m.Word
    target_object_id: Annotated[m.ObjectId, m.IfNotIn("action_id", _NO_TARGET_ACTIONS)]
    target_position: Annotated[m.Vec3, m.IfIn("action_id", _VECTOR_ACTIONS)]
    spell_id: Annotated[m.Dword, m.IfIn("action_id", _SPELL_ACTIONS)]


@dataclass(kw_only=True)
class ActionQueueEntryUpdate:
    action_id: m.Word
    group_id: m.Word
    target: m.ObjectId


ActionQueueEntry = Annotated[
    ActionQueueDelete
    | ActionQueueSpecialAttack
    | ActionQueueAdd
    | ActionQueueEntryUpdate,
    m.Tagged(
        m.MessageType.CHAR,
        {
            ord("D"): ActionQueueDelete,
            ord("S"): ActionQueueSpecialAttack,
            ord("A"): ActionQueueAdd,
            ord("U"): ActionQueueEntryUpdate,
        },
    ),
]


@dataclass(kw_only=True)
class ActionQueueChanges:
    entries: Annotated[list[ActionQueueEntry], m.SizePrefix.BYTE]


@dataclass(kw_only=True)
class PerceptionAdd:
    creature_id: m.ObjectId
    heard: m.Bool
    seen: m.Bool
    invisible: m.Bool


@dataclass(kw_only=True)
class PerceptionUpdate:
    deletes: Annotated[list[m.ObjectId], m.SizePrefix.DWORD]
    adds: Annotated[list[PerceptionAdd], m.SizePrefix.DWORD]


@dataclass(kw_only=True)
class AbilityScoreValues:
    str_base: m.Byte
    dex_base: m.Byte
    con_base: m.Byte
    int_base: m.Byte
    wis_base: m.Byte
    cha_base: m.Byte
    str_final: m.Byte
    dex_final: m.Byte
    con_final: m.Byte
    int_final: m.Byte
    wis_final: m.Byte
    cha_final: m.Byte


@dataclass(kw_only=True)
class AbilityScoresUpdate:
    values: Annotated[AbilityScoreValues, m.BoolPrefix()]


@dataclass(kw_only=True)
class SpellLikeAbilityResize:
    new_size: m.Word


@dataclass(kw_only=True)
class SpellLikeAbilityEntryUpdate:
    index: m.Word
    readied: m.Bool
    caster_level: m.Byte
    spell_id: m.Word


SpellLikeAbilityChange = Annotated[
    SpellLikeAbilityResize | SpellLikeAbilityEntryUpdate,
    m.Tagged(
        m.MessageType.BYTE,
        {
            ord("S"): SpellLikeAbilityResize,
            ord("U"): SpellLikeAbilityEntryUpdate,
        },
    ),
]


@dataclass(kw_only=True)
class GameObjUpdateObjListPlayerInfo(m.SubMessage):
    object_id: m.ObjectId
    flags: Annotated[UpdatePlayerCreatureFlags, m.MessageType.WORD] = (
        UpdatePlayerCreatureFlags(0)
    )

    # NEWOBJECT (0x1000) — no wire data; check flags & F.NEWOBJECT directly.

    ac_gold_weight_levelup: Annotated[
        AcGoldWeightLevelUp | None, m.IfFlag("flags", F.AC_GOLD_WEIGHT_LEVELUP)
    ] = None

    gui_skill_useable: Annotated[m.Dword, m.IfFlag("flags", F.GUISKILL)] = 0

    player_state: Annotated[m.Dword, m.IfFlag("flags", F.STATE)] = 0

    polymorph_spells: Annotated[
        PolymorphSpells | None, m.IfFlag("flags", F.POLYMORPHSPELL)
    ] = None

    num_memorized_spell_slots: Annotated[
        list[SpellSlotClassUpdate],
        m.SizePrefix.BYTE,
        m.IfFlag("flags", F.GUINUMBERMEMORIZEDSPELLS),
    ] = field(default_factory=list)

    known_spells: Annotated[
        list[KnownSpellClassUpdate],
        m.FixedSizeHint(8),
        m.IfFlag("flags", F.GUIKNOWNSPELL),
    ] = field(default_factory=list)

    memorized_spells: Annotated[
        list[MemorizedSpellClassUpdate],
        m.FixedSizeHint(8),
        m.IfFlag("flags", F.GUIMEMORIZEDSPELL),
    ] = field(default_factory=list)

    known_spell_uses: Annotated[
        list[SpellSlotClassUpdate],
        m.SizePrefix.BYTE,
        m.IfFlag("flags", F.GUIKNOWNSPELLUSES),
    ] = field(default_factory=list)

    effect_icons: Annotated[
        EffectIconsUpdate | None, m.IfFlag("flags", F.EFFECT_ICONS)
    ] = None

    feats: Annotated[FeatUpdate | None, m.IfFlag("flags", F.FEAT)] = None

    automap: Annotated[AutoMapUpdate | None, m.IfFlag("flags", F.AUTOMAP)] = None

    action_queue: Annotated[
        ActionQueueChanges | None, m.IfFlag("flags", F.ACTION_QUEUE)
    ] = None

    perception: Annotated[PerceptionUpdate | None, m.IfFlag("flags", F.PERCEPTION)] = (
        None
    )

    ability_scores: Annotated[
        AbilityScoresUpdate | None, m.IfFlag("flags", F.ABILITY_SCORES)
    ] = None

    spell_like_abilities: Annotated[
        list[SpellLikeAbilityChange],
        m.SizePrefix.WORD,
        m.IfFlag("flags", F.SPELLLIKEABILITY),
    ] = field(default_factory=list)
