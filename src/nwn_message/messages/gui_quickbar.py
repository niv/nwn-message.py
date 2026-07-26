from typing import Annotated
from dataclasses import dataclass
from enum import IntEnum

from .. import message as m
from .game_obj_update_appearance import ItemAppearanceAndProps


class ButtonObjectType(IntEnum):
    EMPTY = 0
    ITEM = 1
    SPELL = 2
    SKILL = 3
    FEAT = 4
    SCRIPT = 5  # defined but never sent on the wire
    DIALOG = 6
    ATTACK = 7
    EMOTE = 8
    ITEM_PROPERTY_CASTSPELL = 9  # server sends it, client code is commented out
    MODE_TOGGLE = 10
    DM_CREATE_CREATURE = 11
    DM_CREATE_ITEM = 12
    DM_CREATE_ENCOUNTER = 13
    DM_CREATE_WAYPOINT = 14
    DM_CREATE_TRIGGER = 15
    DM_CREATE_PORTAL = 16
    DM_CREATE_PLACEABLE = 17
    COMMAND_LINE = 18
    DM_MAKEINVULNERABLE = 19
    DM_FORCEREST = 20
    DM_GOTO = 21
    DM_HEAL = 22
    DM_KILL = 23
    DM_POSSESS = 24
    DM_IMPERSONATE = 25
    # 26 is unused
    DM_GIVEGOLD = 27
    DM_TAKEGOLD = 28
    DM_GIVEITEM = 29
    DM_TAKEITEM = 30
    DM_GIVEXP = 31
    DM_TAKEXP = 32
    DM_GIVELEVEL = 33
    DM_TAKELEVEL = 34
    DM_LIMBO = 35
    DM_TOGGLEAI = 36
    ROLLDIE = 37
    POSSESS_FAMILIAR = 38
    ASSOCIATE_COMMAND = 39
    EXAMINE = 40
    BARTER = 41
    QUICK_CHAT = 42
    CANCELPOLYMORPH = 43
    SPELLLIKEABILITY = 44
    DM_GIVEGOOD = 45
    DM_GIVEEVIL = 46
    DM_GIVELAWFUL = 47
    DM_GIVECHAOTIC = 48


@dataclass(kw_only=True)
class ButtonEmpty: ...


@dataclass(kw_only=True)
class ButtonItem:
    @dataclass(kw_only=True)
    class PrimaryItem:
        object_id: m.ObjectId
        property_id: m.Int
        item: ItemAppearanceAndProps

    @dataclass(kw_only=True)
    class SecondaryItem:
        object_id: m.ObjectId
        item: ItemAppearanceAndProps

    primary: Annotated[PrimaryItem, m.BoolPrefix()]
    secondary: Annotated[SecondaryItem, m.BoolPrefix()]


@dataclass(kw_only=True)
class ButtonSpell:
    multi_class: m.Byte
    spell_id: m.Dword
    meta_type: m.Byte
    domain_level: m.Byte


@dataclass(kw_only=True)
class ButtonSkill:
    skill_id: m.Int


@dataclass(kw_only=True)
class ButtonFeat:
    feat_id: m.Int


@dataclass(kw_only=True)
class ButtonDialog: ...


@dataclass(kw_only=True)
class ButtonAttack: ...


@dataclass(kw_only=True)
class ButtonEmote:
    emote_id: m.Int


@dataclass(kw_only=True)
class ButtonModeToggle:
    mode: m.Int


@dataclass(kw_only=True)
class ButtonDMCreateCreature:
    resref: m.ResRef
    tooltip: m.String


@dataclass(kw_only=True)
class ButtonDMCreateItem:
    resref: m.ResRef
    tooltip: m.String


@dataclass(kw_only=True)
class ButtonDMCreateEncounter:
    resref: m.ResRef
    tooltip: m.String


@dataclass(kw_only=True)
class ButtonDMCreateWaypoint:
    resref: m.ResRef
    tooltip: m.String


@dataclass(kw_only=True)
class ButtonDMCreateTrigger:
    resref: m.ResRef
    tooltip: m.String


@dataclass(kw_only=True)
class ButtonDMCreatePortal:
    resref: m.ResRef
    tooltip: m.String


@dataclass(kw_only=True)
class ButtonDMCreatePlaceable:
    resref: m.ResRef
    tooltip: m.String


@dataclass(kw_only=True)
class ButtonCommandLine:
    label: m.String
    cmd: m.String


@dataclass(kw_only=True)
class ButtonDMMakeInvulnerable: ...


@dataclass(kw_only=True)
class ButtonDMForceRest: ...


@dataclass(kw_only=True)
class ButtonDMGoto: ...


@dataclass(kw_only=True)
class ButtonDMHeal: ...


@dataclass(kw_only=True)
class ButtonDMKill: ...


@dataclass(kw_only=True)
class ButtonDMPossess: ...


@dataclass(kw_only=True)
class ButtonDMImpersonate: ...


@dataclass(kw_only=True)
class ButtonDMGiveGold:
    amount: m.Int


@dataclass(kw_only=True)
class ButtonDMTakeGold:
    amount: m.Int


@dataclass(kw_only=True)
class ButtonDMGiveItem:
    resref: m.ResRef


@dataclass(kw_only=True)
class ButtonDMTakeItem:
    resref: m.ResRef


@dataclass(kw_only=True)
class ButtonDMGiveXP:
    amount: m.Int


@dataclass(kw_only=True)
class ButtonDMTakeXP:
    amount: m.Int


@dataclass(kw_only=True)
class ButtonDMGiveLevel:
    amount: m.Int


@dataclass(kw_only=True)
class ButtonDMTakeLevel:
    amount: m.Int


@dataclass(kw_only=True)
class ButtonDMLimbo: ...


@dataclass(kw_only=True)
class ButtonDMToggleAI: ...


@dataclass(kw_only=True)
class ButtonRollDie:
    num_sides: m.Int


@dataclass(kw_only=True)
class ButtonPossessFamiliar: ...


@dataclass(kw_only=True)
class ButtonAssociateCommand:
    command: m.Int
    associate_type: m.Word
    associate_id: m.ObjectId


@dataclass(kw_only=True)
class ButtonExamine: ...


@dataclass(kw_only=True)
class ButtonBarter: ...


@dataclass(kw_only=True)
class ButtonQuickChat:
    quick_chat_id: m.Int


@dataclass(kw_only=True)
class ButtonCancelPolymorph:
    # The parameter will indicate what feat this quickbar button should
    # change back into once polymorph has been cancelled.
    # If it's -1, the slot will just clear itself.
    revert_feat_id: m.Int


@dataclass(kw_only=True)
class ButtonSpellLikeAbility:
    spell_id: m.Dword
    caster_level: m.Byte


@dataclass(kw_only=True)
class ButtonDMGiveGood:
    amount: m.Int


@dataclass(kw_only=True)
class ButtonDMGiveEvil:
    amount: m.Int


@dataclass(kw_only=True)
class ButtonDMGiveLawful:
    amount: m.Int


@dataclass(kw_only=True)
class ButtonDMGiveChaotic:
    amount: m.Int


_ALL_BUTTON_CLASSES = (
    ButtonEmpty
    | ButtonItem
    | ButtonSpell
    | ButtonDialog
    | ButtonAttack
    | ButtonEmote
    | ButtonModeToggle
    | ButtonDMCreateCreature
    | ButtonDMCreateItem
    | ButtonDMCreateEncounter
    | ButtonDMCreateWaypoint
    | ButtonDMCreateTrigger
    | ButtonDMCreatePortal
    | ButtonDMCreatePlaceable
    | ButtonCommandLine
    | ButtonDMMakeInvulnerable
    | ButtonDMForceRest
    | ButtonDMGoto
    | ButtonDMHeal
    | ButtonDMKill
    | ButtonDMPossess
    | ButtonDMImpersonate
    | ButtonDMGiveGold
    | ButtonDMTakeGold
    | ButtonDMGiveItem
    | ButtonDMTakeItem
    | ButtonDMGiveXP
    | ButtonDMTakeXP
    | ButtonDMGiveLevel
    | ButtonDMTakeLevel
    | ButtonDMLimbo
    | ButtonDMToggleAI
    | ButtonRollDie
    | ButtonPossessFamiliar
    | ButtonAssociateCommand
    | ButtonExamine
    | ButtonBarter
    | ButtonQuickChat
    | ButtonCancelPolymorph
    | ButtonSpellLikeAbility
    | ButtonDMGiveGood
    | ButtonDMGiveEvil
    | ButtonDMGiveLawful
    | ButtonDMGiveChaotic
)

Button = Annotated[
    _ALL_BUTTON_CLASSES,
    m.Tagged(
        m.MessageType.BYTE,
        {
            ButtonObjectType.EMPTY: ButtonEmpty,
            ButtonObjectType.ITEM: ButtonItem,
            ButtonObjectType.SPELL: ButtonSpell,
            ButtonObjectType.SKILL: ButtonSkill,
            ButtonObjectType.FEAT: ButtonFeat,
            ButtonObjectType.DIALOG: ButtonDialog,
            ButtonObjectType.ATTACK: ButtonAttack,
            ButtonObjectType.EMOTE: ButtonEmote,
            ButtonObjectType.MODE_TOGGLE: ButtonModeToggle,
            ButtonObjectType.DM_CREATE_CREATURE: ButtonDMCreateCreature,
            ButtonObjectType.DM_CREATE_ITEM: ButtonDMCreateItem,
            ButtonObjectType.DM_CREATE_ENCOUNTER: ButtonDMCreateEncounter,
            ButtonObjectType.DM_CREATE_WAYPOINT: ButtonDMCreateWaypoint,
            ButtonObjectType.DM_CREATE_TRIGGER: ButtonDMCreateTrigger,
            ButtonObjectType.DM_CREATE_PORTAL: ButtonDMCreatePortal,
            ButtonObjectType.DM_CREATE_PLACEABLE: ButtonDMCreatePlaceable,
            ButtonObjectType.COMMAND_LINE: ButtonCommandLine,
            ButtonObjectType.DM_MAKEINVULNERABLE: ButtonDMMakeInvulnerable,
            ButtonObjectType.DM_FORCEREST: ButtonDMForceRest,
            ButtonObjectType.DM_GOTO: ButtonDMGoto,
            ButtonObjectType.DM_HEAL: ButtonDMHeal,
            ButtonObjectType.DM_KILL: ButtonDMKill,
            ButtonObjectType.DM_POSSESS: ButtonDMPossess,
            ButtonObjectType.DM_IMPERSONATE: ButtonDMImpersonate,
            ButtonObjectType.DM_GIVEGOLD: ButtonDMGiveGold,
            ButtonObjectType.DM_TAKEGOLD: ButtonDMTakeGold,
            ButtonObjectType.DM_GIVEITEM: ButtonDMGiveItem,
            ButtonObjectType.DM_TAKEITEM: ButtonDMTakeItem,
            ButtonObjectType.DM_GIVEXP: ButtonDMGiveXP,
            ButtonObjectType.DM_TAKEXP: ButtonDMTakeXP,
            ButtonObjectType.DM_GIVELEVEL: ButtonDMGiveLevel,
            ButtonObjectType.DM_TAKELEVEL: ButtonDMTakeLevel,
            ButtonObjectType.DM_LIMBO: ButtonDMLimbo,
            ButtonObjectType.DM_TOGGLEAI: ButtonDMToggleAI,
            ButtonObjectType.ROLLDIE: ButtonRollDie,
            ButtonObjectType.POSSESS_FAMILIAR: ButtonPossessFamiliar,
            ButtonObjectType.ASSOCIATE_COMMAND: ButtonAssociateCommand,
            ButtonObjectType.EXAMINE: ButtonExamine,
            ButtonObjectType.BARTER: ButtonBarter,
            ButtonObjectType.QUICK_CHAT: ButtonQuickChat,
            ButtonObjectType.CANCELPOLYMORPH: ButtonCancelPolymorph,
            ButtonObjectType.SPELLLIKEABILITY: ButtonSpellLikeAbility,
            ButtonObjectType.DM_GIVEGOOD: ButtonDMGiveGood,
            ButtonObjectType.DM_GIVEEVIL: ButtonDMGiveEvil,
            ButtonObjectType.DM_GIVELAWFUL: ButtonDMGiveLawful,
            ButtonObjectType.DM_GIVECHAOTIC: ButtonDMGiveChaotic,
        },
    ),
]


@dataclass(kw_only=True)
class GuiQuickbarSetAllButtons(m.Message):
    MAJOR = 0x1E
    MINOR = 0x01

    slots: Annotated[list[Button], m.FixedSizeHint(36)]


@dataclass(kw_only=True)
class GuiQuickbarSetButton(m.Message):
    MAJOR = 0x1E
    MINOR = 0x02

    button: m.Byte
    slot: Button
