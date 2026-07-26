"""
Wire format hierarchy:
  'G' (consumed by ObjListEntry Tagged)
     └─ CHAR element_type
            ├─ 'I'/'i' → CHAR op ('A','D','U')
            ├─ 'R'/'r'/'B'/'A' → CHAR op ('A','D','U','M')
            ├─ 'C'/'c' → CHAR op ('P','A','D','U','M')
            ├─ 'M' → CHAR op ('P','A','D','U')
            ├─ 'S' → ObjectId, DWORD flags, conditional fields
            └─ 'Q' → BYTE count, per-button data

Canonical exported class names follow the pattern:
    GameObjUpdateObjListGui<Panel><Operation>
"""

from typing import Annotated
from dataclasses import dataclass
from enum import IntFlag
import logging

from .. import message as m
from .game_obj_update_appearance import ItemAppearanceAndProps
from .game_obj_update_playerinfo import EffectIconsUpdate

logger = logging.getLogger(__name__)


# MESSAGE_SIZE_* bit-width constants (from msgplayermessages.h)

MESSAGE_SIZE_BASE_NUM_ATTACKS = 3
MESSAGE_SIZE_ARCANE_SPELL_FAIL = 7
MESSAGE_SIZE_ARMOR_CHECK_PEN = 5
MESSAGE_SIZE_DAMAGE_DICE = 5
MESSAGE_SIZE_DAMAGE_DIE = 5
MESSAGE_SIZE_CRIT_HIT_RANGE = 4
MESSAGE_SIZE_CRIT_HIT_MULT = 3
MESSAGE_SIZE_DAMAGE_TYPE = 5
MESSAGE_SIZE_WEAPON_WIELD = 3
MESSAGE_SIZE_VERSUS_LAWCHAOS = 2
MESSAGE_SIZE_VERSUS_GOODEVIL = 3

CRULES_NUM_CREATURE_WEAPONS = 3


@dataclass(kw_only=True)
class _GuiRepoItemAddShape(m.SubMessage):
    x: m.Byte
    y: m.Byte
    item_id: m.ObjectId
    item: ItemAppearanceAndProps


@dataclass(kw_only=True)
class _GuiRepoItemUpdateShape(m.SubMessage):
    item_id: m.ObjectId
    stack_size: m.Dword
    cost: m.Dword


@dataclass(kw_only=True)
class _GuiRepoItemDeleteShape(m.SubMessage):
    item_id: m.ObjectId


@dataclass(kw_only=True)
class _GuiRepoItemMoveShape(m.SubMessage):
    x: m.Byte
    y: m.Byte
    item_id: m.ObjectId


@dataclass(kw_only=True)
class GuiInventorySlotAdd(m.SubMessage):
    slot: m.Dword
    item_id: m.ObjectId
    item: ItemAppearanceAndProps


@dataclass(kw_only=True)
class GuiInventorySlotDelete(m.SubMessage):
    slot: m.Dword


@dataclass(kw_only=True)
class GuiInventorySlotUpdate(m.SubMessage):
    weight: m.Int
    ac: m.Short
    str_val: m.Byte


GuiInventoryEntry = (
    GuiInventorySlotAdd | GuiInventorySlotDelete | GuiInventorySlotUpdate
)


@dataclass(kw_only=True)
class GuiRepositoryItemAdd(_GuiRepoItemAddShape):
    pass


@dataclass(kw_only=True)
class GuiRepositoryItemDelete(_GuiRepoItemDeleteShape):
    pass


@dataclass(kw_only=True)
class GuiRepositoryItemUpdate(_GuiRepoItemUpdateShape):
    pass


@dataclass(kw_only=True)
class GuiRepositoryItemMove(_GuiRepoItemMoveShape):
    pass


GuiRepositoryEntry = (
    GuiRepositoryItemAdd
    | GuiRepositoryItemDelete
    | GuiRepositoryItemUpdate
    | GuiRepositoryItemMove
)


@dataclass(kw_only=True)
class GuiContainerPages(m.SubMessage):
    num_pages: m.Byte


@dataclass(kw_only=True)
class GuiContainerItemAdd(_GuiRepoItemAddShape):
    pass


@dataclass(kw_only=True)
class GuiContainerItemDelete(_GuiRepoItemDeleteShape):
    pass


@dataclass(kw_only=True)
class GuiContainerItemUpdate(_GuiRepoItemUpdateShape):
    pass


@dataclass(kw_only=True)
class GuiContainerItemMove(_GuiRepoItemMoveShape):
    pass


GuiContainerEntry = (
    GuiContainerPages
    | GuiContainerItemAdd
    | GuiContainerItemDelete
    | GuiContainerItemUpdate
    | GuiContainerItemMove
)


@dataclass(kw_only=True)
class GuiStorePages(m.SubMessage):
    num_panels: m.Byte
    current_page: m.Byte


@dataclass(kw_only=True)
class GuiStoreReposition(m.SubMessage):
    x: m.Byte
    y: m.Byte
    item_id: m.ObjectId


@dataclass(kw_only=True)
class GuiStoreItemAdd(_GuiRepoItemAddShape):
    pass


@dataclass(kw_only=True)
class GuiStoreItemDelete(_GuiRepoItemDeleteShape):
    pass


GuiStoreEntry = (
    GuiStorePages | GuiStoreItemAdd | GuiStoreItemDelete | GuiStoreReposition
)


# Canonical names for flat ObjList GUI entries.
GameObjUpdateObjListGuiInventoryAdd = GuiInventorySlotAdd
GameObjUpdateObjListGuiInventoryDelete = GuiInventorySlotDelete
GameObjUpdateObjListGuiInventoryUpdate = GuiInventorySlotUpdate

GameObjUpdateObjListGuiRepositoryAdd = GuiRepositoryItemAdd
GameObjUpdateObjListGuiRepositoryDelete = GuiRepositoryItemDelete
GameObjUpdateObjListGuiRepositoryUpdate = GuiRepositoryItemUpdate
GameObjUpdateObjListGuiRepositoryMove = GuiRepositoryItemMove

GameObjUpdateObjListGuiContainerPages = GuiContainerPages
GameObjUpdateObjListGuiContainerAdd = GuiContainerItemAdd
GameObjUpdateObjListGuiContainerDelete = GuiContainerItemDelete
GameObjUpdateObjListGuiContainerUpdate = GuiContainerItemUpdate
GameObjUpdateObjListGuiContainerMove = GuiContainerItemMove

GameObjUpdateObjListGuiStorePages = GuiStorePages
GameObjUpdateObjListGuiStoreAdd = GuiStoreItemAdd
GameObjUpdateObjListGuiStoreDelete = GuiStoreItemDelete
GameObjUpdateObjListGuiStoreReposition = GuiStoreReposition


@dataclass(kw_only=True)
class QuickbarButtonUpdate:
    button_index: m.Byte
    object_type: m.Byte
    item_id: m.ObjectId
    property_index: m.Byte
    uses: m.Word


@dataclass(kw_only=True)
class GuiQuickbarUseCount(m.SubMessage):
    buttons: Annotated[list[QuickbarButtonUpdate], m.SizePrefix.BYTE]


class CharacterSheetFlags(IntFlag):
    ABILITIES = 0x00000001
    FORTSAVE = 0x00000002
    WILLSAVE = 0x00000004
    REFLEXSAVE = 0x00000008
    CURRENTXP = 0x00000010
    BASEATTACK = 0x00000020
    COMBAT_INFORMATION = 0x00000040
    SKILLS = 0x00000080
    EFFECTICONS = 0x00000100
    FEATS = 0x00000200
    AC = 0x00000400
    HITPOINTS = 0x00000800
    NEGATIVE_LEVEL = 0x00001000
    BASE_FORTSAVE = 0x00002000
    BASE_WILLSAVE = 0x00004000
    BASE_REFLEXSAVE = 0x00008000


F = CharacterSheetFlags


@dataclass(kw_only=True)
class CharSheetAbilities:
    str_stat: m.Byte
    dex_stat: m.Byte
    con_stat: m.Byte
    int_stat: m.Byte
    wis_stat: m.Byte
    cha_stat: m.Byte
    str_bonus: m.Char
    dex_bonus: m.Char
    con_bonus: m.Char
    int_bonus: m.Char
    wis_bonus: m.Char
    cha_bonus: m.Char
    str_base: m.Char
    dex_base: m.Char
    con_base: m.Char
    int_base: m.Char
    wis_base: m.Char
    cha_base: m.Char
    dex_ac_mod: m.Char


@dataclass(kw_only=True)
class CharSheetBaseAttack:
    base_attack: m.Byte
    use_monk_tables: m.Bool


@dataclass(kw_only=True)
class CharSheetHitPoints:
    current_hp: m.Short
    max_hp: m.Short


@dataclass(kw_only=True)
class CharSheetFeats:
    feats: Annotated[list[m.Word], m.SizePrefix.WORD]
    bonus_feats: Annotated[list[m.Word], m.SizePrefix.WORD]


@dataclass(kw_only=True)
class CharSheetNegativeLevels:
    levels: Annotated[list[m.Byte], m.SizePrefix.BYTE]


@dataclass(kw_only=True)
class AttackMod:
    modifier: m.Char
    weapon_wield: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_WEAPON_WIELD)]
    versus_race: Annotated[m.Byte, m.BoolPrefix()]
    versus_lawchaos: m.Annotated[m.Byte, m.Bits(2), m.BoolPrefix()]
    versus_goodevil: m.Annotated[m.Byte, m.Bits(3), m.BoolPrefix()]


@dataclass(kw_only=True)
class CombatMod:
    modifier: m.Char
    # warning: we no longer support <35 here
    modifier_type: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_DAMAGE_TYPE)]
    weapon_wield: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_WEAPON_WIELD)]
    versus_race: Annotated[m.Byte, m.BoolPrefix()]
    versus_lawchaos: m.Annotated[m.Byte, m.Bits(2), m.BoolPrefix()]
    versus_goodevil: m.Annotated[m.Byte, m.Bits(3), m.BoolPrefix()]


@dataclass(kw_only=True)
class CharSheetCombatInfo:
    num_attacks: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_BASE_NUM_ATTACKS)]
    on_hand_attack_mod: m.Char
    on_hand_damage_mod: m.Char
    spell_resistance: m.Char
    arcane_spell_failure: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_ARCANE_SPELL_FAIL)]
    armor_check_penalty: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_ARMOR_CHECK_PEN)]
    unarmed_damage_dice: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_DAMAGE_DICE)]
    unarmed_damage_die: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_DAMAGE_DIE)]
    creature_weapons: Annotated[
        list[
            tuple[
                Annotated[m.Byte, m.Bits(MESSAGE_SIZE_DAMAGE_DICE)],
                Annotated[m.Byte, m.Bits(MESSAGE_SIZE_DAMAGE_DIE)],
                m.Char,
            ]
        ],
        m.FixedSizeHint(CRULES_NUM_CREATURE_WEAPONS),
    ]
    on_hand_crit_range: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_CRIT_HIT_RANGE)]
    on_hand_crit_mult: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_CRIT_HIT_MULT)]
    off_hand_equipped: m.Bool
    off_hand_attack_mod: Annotated[m.Char, m.IfEq("off_hand_equipped", True)]
    off_hand_damage_mod: Annotated[m.Char, m.IfEq("off_hand_equipped", True)]
    off_hand_crit_range: Annotated[
        m.Byte, m.Bits(MESSAGE_SIZE_CRIT_HIT_RANGE), m.IfEq("off_hand_equipped", True)
    ]
    off_hand_crit_mult: Annotated[
        m.Byte, m.Bits(MESSAGE_SIZE_CRIT_HIT_MULT), m.IfEq("off_hand_equipped", True)
    ]
    attack_mods: Annotated[list[AttackMod], m.SizePrefix.BYTE]
    damage_mods: Annotated[list[CombatMod], m.SizePrefix.BYTE]


@dataclass(kw_only=True)
class CharSheetSkills:
    ranks: Annotated[
        list[tuple[m.Char, m.Bool]],
        m.BitmaskConditionedList(
            m.MessageType.CHAR,
            m.SizePrefix.DWORD,
            m.TwoDARowCountHint("skills"),
            m.TwoDARowCountHint("skills"),
        ),
    ]


@dataclass(kw_only=True)
class GuiCharacterSheet(m.SubMessage):
    object_id: m.ObjectId
    flags: Annotated[CharacterSheetFlags, m.MessageType.DWORD]

    abilities: Annotated[CharSheetAbilities, m.IfFlag("flags", F.ABILITIES)]
    fort_save: Annotated[m.Char, m.IfFlag("flags", F.FORTSAVE)]
    will_save: Annotated[m.Char, m.IfFlag("flags", F.WILLSAVE)]
    reflex_save: Annotated[m.Char, m.IfFlag("flags", F.REFLEXSAVE)]
    base_fort_save: Annotated[m.Char, m.IfFlag("flags", F.BASE_FORTSAVE)]
    base_will_save: Annotated[m.Char, m.IfFlag("flags", F.BASE_WILLSAVE)]
    base_reflex_save: Annotated[m.Char, m.IfFlag("flags", F.BASE_REFLEXSAVE)]
    experience: Annotated[m.Dword, m.IfFlag("flags", F.CURRENTXP)]
    base_attack: Annotated[CharSheetBaseAttack, m.IfFlag("flags", F.BASEATTACK)]
    combat_info: Annotated[CharSheetCombatInfo, m.IfFlag("flags", F.COMBAT_INFORMATION)]
    ac: Annotated[m.Short, m.IfFlag("flags", F.AC)]
    hit_points: Annotated[CharSheetHitPoints, m.IfFlag("flags", F.HITPOINTS)]
    skills: Annotated[CharSheetSkills, m.IfFlag("flags", F.SKILLS)]
    effect_icons: Annotated[EffectIconsUpdate, m.IfFlag("flags", F.EFFECTICONS)]
    feats: Annotated[CharSheetFeats, m.IfFlag("flags", F.FEATS)]
    negative_levels: Annotated[
        CharSheetNegativeLevels, m.IfFlag("flags", F.NEGATIVE_LEVEL)
    ]


GameObjUpdateObjListGuiCharacterSheet = GuiCharacterSheet
GameObjUpdateObjListGuiQuickbarUseCount = GuiQuickbarUseCount


GuiElementPayload = (
    GuiInventoryEntry
    | GuiRepositoryEntry
    | GuiContainerEntry
    | GuiStoreEntry
    | GuiCharacterSheet
    | GuiQuickbarUseCount
)
