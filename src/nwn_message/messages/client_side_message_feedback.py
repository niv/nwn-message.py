from dataclasses import dataclass
from enum import IntEnum
from typing import Annotated

from .. import message as m


@dataclass(kw_only=True)
class ClientSideMessageFeedbackString(m.Message):
    MAJOR = 0x12
    MINOR = 0x12
    DIRECTION = m.Direction.S2C

    message: m.String


class FeedbackType(IntEnum):
    # Skill Feedback Messages
    SKILL_CANT_USE = 0
    SKILL_CANT_USE_TIMER = 1
    SKILL_ANIMALEMPATHY_VALID_TARGETS = 2
    SKILL_TAUNT_VALID_TARGETS = 3
    SKILL_TAUNT_TARGET_IMMUNE = 223
    SKILL_PICKPOCKET_STOLE_ITEM = 4
    SKILL_PICKPOCKET_STOLE_GOLD = 5
    SKILL_PICKPOCKET_ATTEMPTING_TO_STEAL = 46
    SKILL_PICKPOCKET_ATTEMPT_DETECTED = 150
    SKILL_PICKPOCKET_STOLE_ITEM_TARGET = 47
    SKILL_PICKPOCKET_STOLE_GOLD_TARGET = 48
    SKILL_PICKPOCKET_TARGET_BROKE = 57
    SKILL_HEAL_TARGET_NOT_DISPSND = 55
    SKILL_HEAL_VALID_TARGETS = 56
    SKILL_STEALTH_IN_COMBAT = 60

    # Miscellaneous Targetting Messages
    TARGET_UNAWARE = 6
    ACTION_NOT_POSSIBLE_STATUS = 7
    ACTION_NOT_POSSIBLE_PVP = 187
    ACTION_CANT_REACH_TARGET = 218
    ACTION_NO_LOOT = 247

    # Miscellaneous Feedback Messages
    WEIGHT_TOO_ENCUMBERED_TO_RUN = 8
    WEIGHT_TOO_ENCUMBERED_WALK_SLOW = 9
    WEIGHT_TOO_ENCUMBERED_CANT_PICKUP = 10
    STATS_LEVELUP = 11
    INVENTORY_FULL = 12
    CONTAINER_FULL = 212
    TRAP_TRIGGERED = 82
    DAMAGE_HEALED = 151
    EXPERIENCE_GAINNED = 182
    EXPERIENCE_LOST = 183
    JOURNALUPDATED = 184
    BARTER_CANCELLED = 185

    # Mode activation/deactivation Messages
    DETECT_MODE_ACTIVATED = 83
    DETECT_MODE_DEACTIVATED = 84
    STEALTH_MODE_ACTIVATED = 85
    STEALTH_MODE_DEACTIVATED = 86
    PARRY_MODE_ACTIVATED = 87
    PARRY_MODE_DEACTIVATED = 88
    POWER_ATTACK_MODE_ACTIVATED = 89
    POWER_ATTACK_MODE_DEACTIVATED = 90
    IMPROVED_POWER_ATTACK_MODE_ACTIVATED = 91
    IMPROVED_POWER_ATTACK_MODE_DEACTIVATED = 92
    RAPID_SHOT_MODE_ACTIVATED = 166
    RAPID_SHOT_MODE_DEACTIVATED = 167
    FLURRY_OF_BLOWS_MODE_ACTIVATED = 168
    FLURRY_OF_BLOWS_MODE_DEACTIVATED = 169
    EXPERTISE_MODE_ACTIVATED = 227
    EXPERTISE_MODE_DEACTIVATED = 228
    IMPROVED_EXPERTISE_MODE_ACTIVATED = 229
    IMPROVED_EXPERTISE_MODE_DEACTIVATED = 230
    DEFENSIVE_CAST_MODE_ACTIVATED = 231
    DEFENSIVE_CAST_MODE_DEACTIVATED = 232
    MODE_CANNOT_USE_WEAPONS = 188
    DIRTY_FIGHTING_MODE_ACTIVATED = 237
    DIRTY_FIGHTING_MODE_DEACTIVATED = 238

    DEFENSIVE_STANCE_MODE_ACTIVATED = 252
    DEFENSIVE_STANCE_MODE_DEACTIVATED = 253
    COUNTERSPELL_MODE_ACTIVATED = 262
    COUNTERSPELL_MODE_DEACTIVATED = 263

    # Equipping Feedback Messages
    EQUIP_SKILL_SPELL_MODIFIERS = 71
    EQUIP_UNIDENTIFIED = 76
    EQUIP_MONK_ABILITIES = 77
    EQUIP_INSUFFICIENT_LEVEL = 98
    EQUIP_PROFICIENCIES = 119
    EQUIP_WEAPON_TOO_LARGE = 120
    EQUIP_WEAPON_TOO_SMALL = 260
    EQUIP_ONE_HANDED_WEAPON = 121
    EQUIP_TWO_HANDED_WEAPON = 122
    EQUIP_WEAPON_SWAPPED_OUT = 123
    EQUIP_ONE_CHAIN_WEAPON = 124
    EQUIP_NATURAL_AC_NO_STACK = 189
    EQUIP_ARMOUR_AC_NO_STACK = 190
    EQUIP_SHIELD_AC_NO_STACK = 191
    EQUIP_DEFLECTION_AC_NO_STACK = 192
    EQUIP_NO_ARMOR_COMBAT = 193
    EQUIP_RANGER_ABILITIES = 200
    EQUIP_ALIGNMENT = 207
    EQUIP_CLASS = 208
    EQUIP_RACE = 209
    UNEQUIP_NO_ARMOR_COMBAT = 194

    # Action Feedback Messages
    OBJECT_LOCKED = 13
    OBJECT_NOT_LOCKED = 14
    OBJECT_SPECIAL_KEY = 15
    OBJECT_USED_KEY = 16
    REST_EXCITED_CANT_REST = 17
    REST_BEGINNING_REST = 18
    REST_FINISHED_REST = 19
    REST_CANCEL_REST = 20
    REST_NOT_ALLOWED_IN_AREA = 54
    REST_NOT_ALLOWED_BY_POSSESSED_FAMILIAR = 153
    REST_NOT_ALLOWED_ENEMIES = 186
    REST_CANT_UNDER_THIS_EFFECT = 213
    CAST_LOST_TARGET = 21
    CAST_CANT_CAST = 22
    CAST_CNTRSPELL_TARGET_LOST_TARGET = 52
    CAST_ARCANE_SPELL_FAILURE = 61
    CAST_CNTRSPELL_TARGET_ARCANE_SPELL_FAILURE = 118
    CAST_ENTANGLE_CONCENTRATION_FAILURE = 65
    CAST_CNTRSPELL_TARGET_ENTANGLE_CONCENTRATION_FAILURE = 147
    CAST_SPELL_INTERRUPTED = 72
    CAST_EFFECT_SPELL_FAILURE = 236
    CAST_CANT_CAST_WHILE_POLYMORPHED = 107
    CAST_USE_HANDS = 210
    CAST_USE_MOUTH = 211
    CAST_DEFCAST_CONCENTRATION_FAILURE = 233
    CAST_DEFCAST_CONCENTRATION_SUCCESS = 240
    USEITEM_CANT_USE = 23
    CONVERSATION_TOOFAR = 58
    CONVERSATION_BUSY = 59
    CONVERSATION_IN_COMBAT = 152
    CHARACTER_INTRANSIT = 74
    CHARACTER_OUTTRANSIT = 75
    USEITEM_NOT_EQUIPPED = 244
    DROPITEM_CANT_DROP = 245
    DROPITEM_CANT_GIVE = 246
    CLIENT_SERVER_SPELL_MISMATCH = 259

    # Combat feedback messages
    COMBAT_RUNNING_OUT_OF_AMMO = 24
    COMBAT_OUT_OF_AMMO = 25
    COMBAT_HENCHMAN_OUT_OF_AMMO = 241
    COMBAT_DAMAGE_IMMUNITY = 62
    COMBAT_SPELL_IMMUNITY = 68
    COMBAT_DAMAGE_RESISTANCE = 63
    COMBAT_DAMAGE_RESISTANCE_REMAINING = 66
    COMBAT_DAMAGE_REDUCTION = 64
    COMBAT_DAMAGE_REDUCTION_REMAINING = 67
    COMBAT_SPELL_LEVEL_ABSORPTION = 69
    COMBAT_SPELL_LEVEL_ABSORPTION_REMAINING = 70
    COMBAT_WEAPON_NOT_EFFECTIVE = 117
    COMBAT_EPIC_DODGE_ATTACK_EVADED = 234
    COMBAT_MASSIVE_DAMAGE = 235
    COMBAT_SAVED_VS_MASSIVE_DAMAGE = 254
    COMBAT_SAVED_VS_DEVASTATING_CRITICAL = 257

    # Feat Feedback Messages
    FEAT_SAP_VALID_TARGETS = 26
    FEAT_KNOCKDOWN_VALID_TARGETS = 27
    FEAT_IMPKNOCKDOWN_VALID_TARGETS = 28
    FEAT_CALLED_SHOT_NO_LEGS = 29
    FEAT_CALLED_SHOT_NO_ARMS = 30
    FEAT_SMITE_GOOD_TARGET_NOT_GOOD = 239
    FEAT_SMITE_EVIL_TARGET_NOT_EVIL = 53
    FEAT_QUIVERING_PALM_HIGHER_LEVEL = 73
    FEAT_KEEN_SENSE_DETECT = 195
    FEAT_USE_UNARMED = 198
    FEAT_USES = 199
    FEAT_USE_WEAPON_OF_CHOICE = 243

    # Party Feedback Messages
    PARTY_NEW_LEADER = 31
    PARTY_MEMBER_KICKED = 32
    PARTY_KICKED_YOU = 33
    PARTY_ALREADY_CONSIDERING = 34
    PARTY_ALREADY_INVOLVED = 35
    PARTY_SENT_INVITATION = 36
    PARTY_RECEIVED_INVITATION = 37
    PARTY_JOINED = 38
    PARTY_INVITATION_IGNORED = 39
    PARTY_YOU_IGNORED_INVITATION = 40
    PARTY_INVITATION_REJECTED = 41
    PARTY_YOU_REJECTED_INVITATION = 42
    PARTY_INVITATION_EXPIRED = 43
    PARTY_LEFT_PARTY = 44
    PARTY_YOU_LEFT = 45
    PARTY_HENCHMAN_LIMIT = 49
    PARTY_CANNOT_LEAVE_THE_ONE_PARTY = 196
    PARTY_CANNOT_KICK_FROM_THE_ONE_PARTY = 197
    PARTY_YOU_INVITED_NON_SINGLETON = 202
    PVP_REACTION_DISLIKESYOU = 203

    # Item Feedback Messages
    ITEM_RECEIVED = 50
    ITEM_LOST = 51
    ITEM_EJECTED = 96
    ITEM_USE_UNIDENTIFIED = 97
    ITEM_GOLD_GAINED = 148
    ITEM_GOLD_LOST = 149

    # Spell Scroll Learning
    LEARN_SCROLL_NOT_SCROLL = 78
    LEARN_SCROLL_CANT_LEARN_CLASS = 79
    LEARN_SCROLL_CANT_LEARN_LEVEL = 80
    LEARN_SCROLL_CANT_LEARN_ABILITY = 81
    LEARN_SCROLL_CANT_LEARN_OPPOSITION = 219
    LEARN_SCROLL_CANT_LEARN_POSSESS = 220
    LEARN_SCROLL_CANT_LEARN_KNOWN = 221
    LEARN_SCROLL_CANT_LEARN_DIVINE = 224
    LEARN_SCROLL_SUCCESS = 222

    # Floaty text feedback
    FLOATY_TEXT_STRREF = 93
    FLOATY_TEXT_STRING = 94

    # store feedback
    CANNOT_SELL_PLOT_ITEM = 99
    CANNOT_SELL_CONTAINER = 100
    CANNOT_SELL_ITEM = 101
    NOT_ENOUGH_GOLD = 102
    TRANSACTION_SUCCEEDED = 103
    PRICE_TOO_HIGH = 248
    STORE_NOT_ENOUGH_GOLD = 249
    CANNOT_SELL_STOLEN_ITEM = 250
    CANNOT_SELL_RESTRICTED_ITEM = 251

    # Portal control feedback
    PORTAL_TIMEDOUT = 104
    PORTAL_INVALID = 105

    # Chat feedback
    CHAT_TELL_PLAYER_NOT_FOUND = 106

    # Alignment Feedback
    ALIGNMENT_SHIFT = 108
    ALIGNMENT_PARTY_SHIFT = 111
    ALIGNMENT_CHANGE = 109
    ALIGNMENT_RESTRICTED_BY_CLASS_LOST = 110
    ALIGNMENT_RESTRICTED_BY_CLASS_GAIN = 115
    ALIGNMENT_RESTRICTED_WARNING_LOSS = 116
    ALIGNMENT_RESTRICTED_WARNING_GAIN = 112
    ALIGNMENT_EPITOME_GAINED = 113
    ALIGNMENT_EPITOME_LOST = 114

    # Immunity Feedback
    IMMUNITY_DISEASE = 125
    IMMUNITY_CRITICAL_HIT = 126
    IMMUNITY_DEATH_MAGIC = 127
    IMMUNITY_FEAR = 128
    IMMUNITY_KNOCKDOWN = 129
    IMMUNITY_PARALYSIS = 130
    IMMUNITY_NEGATIVE_LEVEL = 131
    IMMUNITY_MIND_SPELLS = 132
    IMMUNITY_POISON = 133
    IMMUNITY_SNEAK_ATTACK = 134
    IMMUNITY_SLEEP = 135
    IMMUNITY_DAZE = 136
    IMMUNITY_CONFUSION = 137
    IMMUNITY_STUN = 138
    IMMUNITY_BLINDNESS = 139
    IMMUNITY_DEAFNESS = 140
    IMMUNITY_CURSE = 141
    IMMUNITY_CHARM = 142
    IMMUNITY_DOMINATE = 143
    IMMUNITY_ENTANGLE = 144
    IMMUNITY_SILENCE = 145
    IMMUNITY_SLOW = 146

    # Associates
    ASSOCIATE_SUMMONED = 154
    ASSOCIATE_UNSUMMONING = 155
    ASSOCIATE_UNSUMMONING_BECAUSE_REST = 156
    ASSOCIATE_UNSUMMONING_BECAUSE_DIED = 157
    ASSOCIATE_DOMINATED = 158
    ASSOCIATE_DOMINATION_ENDED = 159
    ASSOCIATE_POSSESSED_CANNOT_RECOVER_TRAP = 170
    ASSOCIATE_POSSESSED_CANNOT_BARTER = 171
    ASSOCIATE_POSSESSED_CANNOT_EQUIP = 172
    ASSOCIATE_POSSESSED_CANNOT_REPOSITORY_MOVE = 173
    ASSOCIATE_POSSESSED_CANNOT_PICK_UP = 174
    ASSOCIATE_POSSESSED_CANNOT_DROP = 175
    ASSOCIATE_POSSESSED_CANNOT_UNEQUIP = 176
    ASSOCIATE_POSSESSED_CANNOT_REST = 177
    ASSOCIATE_POSSESSED_CANNOT_DIALOGUE = 178
    ASSOCIATE_POSSESSED_CANNOT_GIVE_ITEM = 179
    ASSOCIATE_POSSESSED_CANNOT_TAKE_ITEM = 180
    ASSOCIATE_POSSESSED_CANNOT_USE_CONTAINER = 181

    SCRIPT_ERROR = 160
    ACTION_LIST_OVERFLOW = 161
    EFFECT_LIST_OVERFLOW = 162
    AI_UPDATE_TIME_OVERFLOW = 163
    ACTION_LIST_WIPE_OVERFLOW = 164
    EFFECT_LIST_WIPE_OVERFLOW = 165
    SEND_MESSAGE_TO_PC = 204
    SEND_MESSAGE_TO_PC_STRREF = 242

    # Misc GUI feedback
    GUI_ONLY_PARTY_LEADER_MAY_CLICK = 201
    PAUSED = 205
    UNPAUSED = 206
    REST_YOU_MAY_NOT_AT_THIS_TIME = 214
    GUI_CHAR_EXPORT_REQUEST_SENT = 215
    GUI_CHAR_EXPORTED_SUCCESSFULLY = 216
    GUI_ERROR_CHAR_NOT_EXPORTED = 217
    CAMERA_BG = 255
    CAMERA_EQ = 256
    CAMERA_CHASECAM = 258

    SAVING = 225
    SAVE_COMPLETE = 226

    CANNOT_LEVELUP_WHILE_POLYMORPHED = 261


@dataclass(kw_only=True)
class ItemData:
    identified: m.Bool
    name: Annotated[
        m.LocStr | m.String,
        m.IfEq("identified", True),
        m.Tagged(
            m.MessageType.BOOL,  # use_original_name
            {
                True: m.LocStr,
                int(False): m.String,
            },
        ),
    ]
    base_item_id: Annotated[m.Dword, m.IfEq("identified", False)]


@dataclass(kw_only=True)
class FeedbackSkillCantUse(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackSkillCantUseTimer(m.SubMessage):
    time_remaining: m.Int


@dataclass(kw_only=True)
class FeedbackSkillAnimalEmpathyValidTargets(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackSkillTauntValidTargets(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackSkillTauntTargetImmune(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackSkillPickpocketStoleItem(m.SubMessage):
    target: m.ObjectId
    item: ItemData


@dataclass(kw_only=True)
class FeedbackSkillPickpocketStoleGold(m.SubMessage):
    target: m.ObjectId
    gold_amount: m.Int


@dataclass(kw_only=True)
class FeedbackSkillPickpocketAttemptingToSteal(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackSkillPickpocketAttemptDetected(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackSkillPickpocketStoleItemTarget(m.SubMessage):
    thief: m.ObjectId
    item: ItemData


@dataclass(kw_only=True)
class FeedbackSkillPickpocketStoleGoldTarget(m.SubMessage):
    thief: m.ObjectId


@dataclass(kw_only=True)
class FeedbackSkillPickpocketTargetBroke(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackSkillHealTargetNotDispsnd(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackSkillHealValidTargets(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackSkillStealthInCombat(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackTargetUnaware(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackActionNotPossibleStatus(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackActionNotPossiblePvp(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackActionCantReachTarget(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackActionNoLoot(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackWeightTooEncumberedToRun(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackWeightTooEncumberedWalkSlow(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackWeightTooEncumberedCantPickup(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackStatsLevelUp(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackInventoryFull(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackContainerFull(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackTrapTriggered(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackDamageHealed(m.SubMessage):
    target: m.ObjectId
    amount: m.Int


@dataclass(kw_only=True)
class FeedbackExperienceGained(m.SubMessage):
    experience: m.Int


@dataclass(kw_only=True)
class FeedbackExperienceLost(m.SubMessage):
    experience: m.Int


@dataclass(kw_only=True)
class FeedbackJournalUpdated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackBarterCancelled(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackDetectModeActivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackDetectModeDeactivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackStealthModeActivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackStealthModeDeactivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackParryModeActivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackParryModeDeactivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackPowerAttackModeActivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackPowerAttackModeDeactivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackImprovedPowerAttackModeActivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackImprovedPowerAttackModeDeactivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackRapidShotModeActivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackRapidShotModeDeactivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackFlurryOfBlowsModeActivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackFlurryOfBlowsModeDeactivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackExpertiseModeActivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackExpertiseModeDeactivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackImprovedExpertiseModeActivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackImprovedExpertiseModeDeactivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackDefensiveCastModeActivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackDefensiveCastModeDeactivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackModeCannotUseWeapons(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackDirtyFightingModeActivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackDirtyFightingModeDeactivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackDefensiveStanceModeActivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackDefensiveStanceModeDeactivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCounterspellModeActivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCounterspellModeDeactivated(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipSkillSpellModifiers(m.SubMessage):
    arcane_spell_failure: m.Int
    skill_check_penalty: m.Int


@dataclass(kw_only=True)
class FeedbackEquipUnidentified(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipMonkAbilities(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipInsufficientLevel(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipProficiencies(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipWeaponTooLarge(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipWeaponTooSmall(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipOneHandedWeapon(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipTwoHandedWeapon(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipWeaponSwappedOut(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipOneChainWeapon(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipNaturalAcNoStack(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipArmourAcNoStack(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipShieldAcNoStack(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipDeflectionAcNoStack(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipNoArmorCombat(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipRangerAbilities(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipAlignment(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipClass(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackEquipRace(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackUnequipNoArmorCombat(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackObjectLocked(m.SubMessage):
    locked_object: m.ObjectId


@dataclass(kw_only=True)
class FeedbackObjectNotLocked(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackObjectSpecialKey(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackObjectUsedKey(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackRestExcitedCantRest(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackRestBeginningRest(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackRestFinishedRest(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackRestCancelRest(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackRestNotAllowedInArea(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackRestNotAllowedByPossessedFamiliar(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackRestNotAllowedEnemies(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackRestCantUnderThisEffect(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCastLostTarget(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCastCantCast(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCastCntrspellTargetLostTarget(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCastArcaneSpellFailure(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCastCntrspellTargetArcaneSpellFailure(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCastEntangleConcentrationFailure(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCastCntrspellTargetEntangleConcentrationFailure(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCastSpellInterrupted(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCastEffectSpellFailure(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCastCantCastWhilePolymorphed(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCastUseHands(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCastUseMouth(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCastDefcastConcentrationFailure(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCastDefcastConcentrationSuccess(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackUseItemCantUse(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackConversationTooFar(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackConversationBusy(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackConversationInCombat(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCharacterInTransit(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCharacterOutTransit(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackUseItemNotEquipped(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackDropItemCantDrop(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackDropItemCantGive(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackClientServerSpellMismatch(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCombatRunningOutOfAmmo(m.SubMessage):
    ammo_remaining: m.Int


@dataclass(kw_only=True)
class FeedbackCombatOutOfAmmo(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCombatHenchmanOutOfAmmo(m.SubMessage):
    henchman: m.ObjectId


@dataclass(kw_only=True)
class FeedbackCombatDamageImmunity(m.SubMessage):
    target: m.ObjectId
    absorbed_amount: m.Int
    damage_flags: m.Int


@dataclass(kw_only=True)
class FeedbackCombatSpellImmunity(m.SubMessage):
    target: m.ObjectId
    spell_id: m.Int


@dataclass(kw_only=True)
class FeedbackCombatDamageResistance(m.SubMessage):
    target: m.ObjectId
    absorbed_amount: m.Int


@dataclass(kw_only=True)
class FeedbackCombatDamageResistanceRemaining(m.SubMessage):
    target: m.ObjectId
    absorbed_amount: m.Int
    remaining_amount: m.Int


@dataclass(kw_only=True)
class FeedbackCombatDamageReduction(m.SubMessage):
    target: m.ObjectId
    absorbed_amount: m.Int


@dataclass(kw_only=True)
class FeedbackCombatDamageReductionRemaining(m.SubMessage):
    target: m.ObjectId
    absorbed_amount: m.Int
    remaining_amount: m.Int


@dataclass(kw_only=True)
class FeedbackCombatSpellLevelAbsorption(m.SubMessage):
    target: m.ObjectId
    absorbed_spell_levels: m.Int


@dataclass(kw_only=True)
class FeedbackCombatSpellLevelAbsorptionRemaining(m.SubMessage):
    target: m.ObjectId
    absorbed_spell_levels: m.Int
    remaining_spell_levels: m.Int


@dataclass(kw_only=True)
class FeedbackCombatWeaponNotEffective(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCombatEpicDodgeAttackEvaded(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackCombatMassiveDamage(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackCombatSavedVsMassiveDamage(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackCombatSavedVsDevastatingCritical(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackFeatSapValidTargets(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackFeatKnockdownValidTargets(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackFeatImpknockdownValidTargets(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackFeatCalledShotNoLegs(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackFeatCalledShotNoArms(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackFeatSmiteGoodTargetNotGood(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackFeatSmiteEvilTargetNotEvil(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackFeatQuiveringPalmHigherLevel(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackFeatKeenSenseDetect(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackFeatUseUnarmed(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackFeatUses(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackFeatUseWeaponOfChoice(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackPartyNewLeader(m.SubMessage):
    leader: m.ObjectId


@dataclass(kw_only=True)
class FeedbackPartyMemberKicked(m.SubMessage):
    member: m.ObjectId


@dataclass(kw_only=True)
class FeedbackPartyKickedYou(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackPartyAlreadyConsidering(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackPartyAlreadyInvolved(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackPartySentInvitation(m.SubMessage):
    invitee: m.ObjectId


@dataclass(kw_only=True)
class FeedbackPartyReceivedInvitation(m.SubMessage):
    inviter: m.ObjectId


@dataclass(kw_only=True)
class FeedbackPartyJoined(m.SubMessage):
    member: m.ObjectId


@dataclass(kw_only=True)
class FeedbackPartyInvitationIgnored(m.SubMessage):
    invitee: m.ObjectId


@dataclass(kw_only=True)
class FeedbackPartyYouIgnoredInvitation(m.SubMessage):
    inviter: m.ObjectId


@dataclass(kw_only=True)
class FeedbackPartyInvitationRejected(m.SubMessage):
    invitee: m.ObjectId


@dataclass(kw_only=True)
class FeedbackPartyYouRejectedInvitation(m.SubMessage):
    inviter: m.ObjectId


@dataclass(kw_only=True)
class FeedbackPartyInvitationExpired(m.SubMessage):
    invitee: m.ObjectId


@dataclass(kw_only=True)
class FeedbackPartyLeftParty(m.SubMessage):
    member: m.ObjectId


@dataclass(kw_only=True)
class FeedbackPartyYouLeft(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackPartyHenchmanLimit(m.SubMessage):
    henchman_limit: m.Int


@dataclass(kw_only=True)
class FeedbackPartyCannotLeaveTheOneParty(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackPartyCannotKickFromTheOneParty(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackPartyYouInvitedNonSingleton(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackPvpReactionDislikesYou(m.SubMessage):
    creature: m.ObjectId


@dataclass(kw_only=True)
class FeedbackItemReceived(m.SubMessage):
    item: ItemData


@dataclass(kw_only=True)
class FeedbackItemLost(m.SubMessage):
    item: ItemData


@dataclass(kw_only=True)
class FeedbackItemEjected(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackItemUseUnidentified(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackItemGoldGained(m.SubMessage):
    gold_amount: m.Int


@dataclass(kw_only=True)
class FeedbackItemGoldLost(m.SubMessage):
    gold_amount: m.Int


@dataclass(kw_only=True)
class FeedbackLearnScrollNotScroll(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackLearnScrollCantLearnClass(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackLearnScrollCantLearnLevel(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackLearnScrollCantLearnAbility(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackLearnScrollCantLearnOpposition(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackLearnScrollCantLearnPossess(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackLearnScrollCantLearnKnown(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackLearnScrollCantLearnDivine(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackLearnScrollSuccess(m.SubMessage):
    spell_id: m.Int


@dataclass(kw_only=True)
class FeedbackFloatyTextStrref(m.SubMessage):
    target: m.ObjectId
    strref: m.Int
    chat_log: m.Bool


@dataclass(kw_only=True)
class FeedbackFloatyTextString(m.SubMessage):
    target: m.ObjectId
    text: m.String
    chat_log: m.Bool


@dataclass(kw_only=True)
class FeedbackCannotSellPlotItem(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCannotSellContainer(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCannotSellItem(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackNotEnoughGold(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackTransactionSucceeded(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackPriceTooHigh(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackStoreNotEnoughGold(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCannotSellStolenItem(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCannotSellRestrictedItem(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackPortalTimedOut(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackPortalInvalid(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackChatTellPlayerNotFound(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackAlignmentShift(m.SubMessage):
    alignment_axis: m.Int
    shift_amount: m.Int


@dataclass(kw_only=True)
class FeedbackAlignmentPartyShift(m.SubMessage):
    shifter: m.ObjectId
    alignment_axis: m.Int
    shift_amount: m.Int


@dataclass(kw_only=True)
class FeedbackAlignmentChange(m.SubMessage):
    law_chaos_alignment: m.Int
    good_evil_alignment: m.Int


@dataclass(kw_only=True)
class FeedbackAlignmentRestrictedByClassLost(m.SubMessage):
    class_index: m.Int


@dataclass(kw_only=True)
class FeedbackAlignmentRestrictedByClassGain(m.SubMessage):
    class_index: m.Int


@dataclass(kw_only=True)
class FeedbackAlignmentRestrictedWarningLoss(m.SubMessage):
    class_index: m.Int


@dataclass(kw_only=True)
class FeedbackAlignmentRestrictedWarningGain(m.SubMessage):
    class_index: m.Int


@dataclass(kw_only=True)
class FeedbackAlignmentEpitomeGained(m.SubMessage):
    law_chaos_alignment: m.Int
    good_evil_alignment: m.Int


@dataclass(kw_only=True)
class FeedbackAlignmentEpitomeLost(m.SubMessage):
    law_chaos_alignment: m.Int
    good_evil_alignment: m.Int


@dataclass(kw_only=True)
class FeedbackImmunityDisease(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityCriticalHit(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityDeathMagic(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityFear(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityKnockdown(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityParalysis(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityNegativeLevel(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityMindSpells(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityPoison(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunitySneakAttack(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunitySleep(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityDaze(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityConfusion(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityStun(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityBlindness(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityDeafness(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityCurse(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityCharm(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityDominate(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunityEntangle(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunitySilence(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackImmunitySlow(m.SubMessage):
    target: m.ObjectId


@dataclass(kw_only=True)
class FeedbackAssociateSummoned(m.SubMessage):
    associate: m.ObjectId


@dataclass(kw_only=True)
class FeedbackAssociateUnsummoning(m.SubMessage):
    associate: m.ObjectId


@dataclass(kw_only=True)
class FeedbackAssociateUnsummoningBecauseRest(m.SubMessage):
    associate: m.ObjectId


@dataclass(kw_only=True)
class FeedbackAssociateUnsummoningBecauseDied(m.SubMessage):
    associate: m.ObjectId


@dataclass(kw_only=True)
class FeedbackAssociateDominated(m.SubMessage):
    associate: m.ObjectId


@dataclass(kw_only=True)
class FeedbackAssociateDominationEnded(m.SubMessage):
    associate: m.ObjectId


@dataclass(kw_only=True)
class FeedbackAssociatePossessedCannotRecoverTrap(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackAssociatePossessedCannotBarter(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackAssociatePossessedCannotEquip(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackAssociatePossessedCannotRepositoryMove(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackAssociatePossessedCannotPickUp(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackAssociatePossessedCannotDrop(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackAssociatePossessedCannotUnequip(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackAssociatePossessedCannotRest(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackAssociatePossessedCannotDialogue(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackAssociatePossessedCannotGiveItem(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackAssociatePossessedCannotTakeItem(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackAssociatePossessedCannotUseContainer(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackScriptError(m.SubMessage):
    object_id: m.ObjectId
    filename: m.String
    code: m.String
    line_number: m.Int
    error_context: m.String


@dataclass(kw_only=True)
class FeedbackActionListOverflow(m.SubMessage):
    object_id: m.ObjectId
    tag_name: m.String
    action_count: m.Int
    action_limit: m.Int


@dataclass(kw_only=True)
class FeedbackEffectListOverflow(m.SubMessage):
    object_id: m.ObjectId
    tag_name: m.String
    effect_count: m.Int
    effect_limit: m.Int


@dataclass(kw_only=True)
class FeedbackAIUpdateTimeOverflow(m.SubMessage):
    object_id: m.ObjectId
    tag_name: m.String
    ai_update_time: m.Int
    ai_update_limit: m.Int
    scripts: m.String
    current_action: m.Int
    flags: m.Int


@dataclass(kw_only=True)
class FeedbackActionListWipeOverflow(m.SubMessage):
    object_id: m.ObjectId
    tag_name: m.String
    action_count: m.Int
    action_limit: m.Int


@dataclass(kw_only=True)
class FeedbackEffectListWipeOverflow(m.SubMessage):
    object_id: m.ObjectId
    tag_name: m.String
    effect_count: m.Int
    effect_limit: m.Int


@dataclass(kw_only=True)
class FeedbackSendMessageToPc(m.SubMessage):
    message: m.String


@dataclass(kw_only=True)
class FeedbackSendMessageToPcStrref(m.SubMessage):
    strref: m.Int


@dataclass(kw_only=True)
class FeedbackGuiOnlyPartyLeaderMayClick(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackPaused(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackUnpaused(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackRestYouMayNotAtThisTime(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackGuiCharExportRequestSent(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackGuiCharExportedSuccessfully(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackGuiErrorCharNotExported(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCameraBg(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCameraEq(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCameraChasecam(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackSaving(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackSaveComplete(m.SubMessage): ...


@dataclass(kw_only=True)
class FeedbackCannotLevelupWhilePolymorphed(m.SubMessage): ...


_FEEDBACK_CLASSES_0 = (
    FeedbackSkillCantUse
    | FeedbackSkillCantUseTimer
    | FeedbackSkillAnimalEmpathyValidTargets
    | FeedbackSkillTauntValidTargets
    | FeedbackSkillTauntTargetImmune
    | FeedbackSkillPickpocketStoleItem
    | FeedbackSkillPickpocketStoleGold
    | FeedbackSkillPickpocketAttemptingToSteal
    | FeedbackSkillPickpocketAttemptDetected
    | FeedbackSkillPickpocketStoleItemTarget
    | FeedbackSkillPickpocketStoleGoldTarget
    | FeedbackSkillPickpocketTargetBroke
    | FeedbackSkillHealTargetNotDispsnd
    | FeedbackSkillHealValidTargets
    | FeedbackSkillStealthInCombat
    | FeedbackTargetUnaware
    | FeedbackActionNotPossibleStatus
    | FeedbackActionNotPossiblePvp
    | FeedbackActionCantReachTarget
    | FeedbackActionNoLoot
    | FeedbackWeightTooEncumberedToRun
    | FeedbackWeightTooEncumberedWalkSlow
    | FeedbackWeightTooEncumberedCantPickup
    | FeedbackStatsLevelUp
    | FeedbackInventoryFull
    | FeedbackContainerFull
    | FeedbackTrapTriggered
    | FeedbackDamageHealed
    | FeedbackExperienceGained
    | FeedbackExperienceLost
    | FeedbackJournalUpdated
    | FeedbackBarterCancelled
    | FeedbackDetectModeActivated
    | FeedbackDetectModeDeactivated
    | FeedbackStealthModeActivated
    | FeedbackStealthModeDeactivated
    | FeedbackParryModeActivated
    | FeedbackParryModeDeactivated
    | FeedbackPowerAttackModeActivated
    | FeedbackPowerAttackModeDeactivated
    | FeedbackImprovedPowerAttackModeActivated
    | FeedbackImprovedPowerAttackModeDeactivated
    | FeedbackRapidShotModeActivated
    | FeedbackRapidShotModeDeactivated
    | FeedbackFlurryOfBlowsModeActivated
    | FeedbackFlurryOfBlowsModeDeactivated
    | FeedbackExpertiseModeActivated
    | FeedbackExpertiseModeDeactivated
    | FeedbackImprovedExpertiseModeActivated
    | FeedbackImprovedExpertiseModeDeactivated
    | FeedbackDefensiveCastModeActivated
    | FeedbackDefensiveCastModeDeactivated
    | FeedbackModeCannotUseWeapons
    | FeedbackDirtyFightingModeActivated
    | FeedbackDirtyFightingModeDeactivated
    | FeedbackDefensiveStanceModeActivated
    | FeedbackDefensiveStanceModeDeactivated
    | FeedbackCounterspellModeActivated
    | FeedbackCounterspellModeDeactivated
)


_FEEDBACK_CLASSES_1 = (
    FeedbackEquipSkillSpellModifiers
    | FeedbackEquipUnidentified
    | FeedbackEquipMonkAbilities
    | FeedbackEquipInsufficientLevel
    | FeedbackEquipProficiencies
    | FeedbackEquipWeaponTooLarge
    | FeedbackEquipWeaponTooSmall
    | FeedbackEquipOneHandedWeapon
    | FeedbackEquipTwoHandedWeapon
    | FeedbackEquipWeaponSwappedOut
    | FeedbackEquipOneChainWeapon
    | FeedbackEquipNaturalAcNoStack
    | FeedbackEquipArmourAcNoStack
    | FeedbackEquipShieldAcNoStack
    | FeedbackEquipDeflectionAcNoStack
    | FeedbackEquipNoArmorCombat
    | FeedbackEquipRangerAbilities
    | FeedbackEquipAlignment
    | FeedbackEquipClass
    | FeedbackEquipRace
    | FeedbackUnequipNoArmorCombat
    | FeedbackObjectLocked
    | FeedbackObjectNotLocked
    | FeedbackObjectSpecialKey
    | FeedbackObjectUsedKey
    | FeedbackRestExcitedCantRest
    | FeedbackRestBeginningRest
    | FeedbackRestFinishedRest
    | FeedbackRestCancelRest
    | FeedbackRestNotAllowedInArea
    | FeedbackRestNotAllowedByPossessedFamiliar
    | FeedbackRestNotAllowedEnemies
    | FeedbackRestCantUnderThisEffect
    | FeedbackCastLostTarget
    | FeedbackCastCantCast
    | FeedbackCastCntrspellTargetLostTarget
    | FeedbackCastArcaneSpellFailure
    | FeedbackCastCntrspellTargetArcaneSpellFailure
    | FeedbackCastEntangleConcentrationFailure
    | FeedbackCastCntrspellTargetEntangleConcentrationFailure
    | FeedbackCastSpellInterrupted
    | FeedbackCastEffectSpellFailure
    | FeedbackCastCantCastWhilePolymorphed
    | FeedbackCastUseHands
    | FeedbackCastUseMouth
    | FeedbackCastDefcastConcentrationFailure
    | FeedbackCastDefcastConcentrationSuccess
    | FeedbackUseItemCantUse
    | FeedbackConversationTooFar
    | FeedbackConversationBusy
    | FeedbackConversationInCombat
    | FeedbackCharacterInTransit
    | FeedbackCharacterOutTransit
    | FeedbackUseItemNotEquipped
    | FeedbackDropItemCantDrop
    | FeedbackDropItemCantGive
    | FeedbackClientServerSpellMismatch
    | FeedbackCombatRunningOutOfAmmo
    | FeedbackCombatOutOfAmmo
    | FeedbackCombatHenchmanOutOfAmmo
    | FeedbackCombatDamageImmunity
    | FeedbackCombatSpellImmunity
    | FeedbackCombatDamageResistance
    | FeedbackCombatDamageResistanceRemaining
    | FeedbackCombatDamageReduction
    | FeedbackCombatDamageReductionRemaining
    | FeedbackCombatSpellLevelAbsorption
    | FeedbackCombatSpellLevelAbsorptionRemaining
    | FeedbackCombatWeaponNotEffective
    | FeedbackCombatEpicDodgeAttackEvaded
    | FeedbackCombatMassiveDamage
    | FeedbackCombatSavedVsMassiveDamage
    | FeedbackCombatSavedVsDevastatingCritical
    | FeedbackFeatSapValidTargets
    | FeedbackFeatKnockdownValidTargets
    | FeedbackFeatImpknockdownValidTargets
    | FeedbackFeatCalledShotNoLegs
    | FeedbackFeatCalledShotNoArms
    | FeedbackFeatSmiteGoodTargetNotGood
    | FeedbackFeatSmiteEvilTargetNotEvil
    | FeedbackFeatQuiveringPalmHigherLevel
    | FeedbackFeatKeenSenseDetect
    | FeedbackFeatUseUnarmed
    | FeedbackFeatUses
    | FeedbackFeatUseWeaponOfChoice
)


_FEEDBACK_CLASSES_2 = (
    FeedbackPartyNewLeader
    | FeedbackPartyMemberKicked
    | FeedbackPartyKickedYou
    | FeedbackPartyAlreadyConsidering
    | FeedbackPartyAlreadyInvolved
    | FeedbackPartySentInvitation
    | FeedbackPartyReceivedInvitation
    | FeedbackPartyJoined
    | FeedbackPartyInvitationIgnored
    | FeedbackPartyYouIgnoredInvitation
    | FeedbackPartyInvitationRejected
    | FeedbackPartyYouRejectedInvitation
    | FeedbackPartyInvitationExpired
    | FeedbackPartyLeftParty
    | FeedbackPartyYouLeft
    | FeedbackPartyHenchmanLimit
    | FeedbackPartyCannotLeaveTheOneParty
    | FeedbackPartyCannotKickFromTheOneParty
    | FeedbackPartyYouInvitedNonSingleton
    | FeedbackPvpReactionDislikesYou
    | FeedbackItemReceived
    | FeedbackItemLost
    | FeedbackItemEjected
    | FeedbackItemUseUnidentified
    | FeedbackItemGoldGained
    | FeedbackItemGoldLost
    | FeedbackLearnScrollNotScroll
    | FeedbackLearnScrollCantLearnClass
    | FeedbackLearnScrollCantLearnLevel
    | FeedbackLearnScrollCantLearnAbility
    | FeedbackLearnScrollCantLearnOpposition
    | FeedbackLearnScrollCantLearnPossess
    | FeedbackLearnScrollCantLearnKnown
    | FeedbackLearnScrollCantLearnDivine
    | FeedbackLearnScrollSuccess
    | FeedbackFloatyTextStrref
    | FeedbackFloatyTextString
    | FeedbackCannotSellPlotItem
    | FeedbackCannotSellContainer
    | FeedbackCannotSellItem
    | FeedbackNotEnoughGold
    | FeedbackTransactionSucceeded
    | FeedbackPriceTooHigh
    | FeedbackStoreNotEnoughGold
    | FeedbackCannotSellStolenItem
    | FeedbackCannotSellRestrictedItem
    | FeedbackPortalTimedOut
    | FeedbackPortalInvalid
    | FeedbackChatTellPlayerNotFound
    | FeedbackAlignmentShift
    | FeedbackAlignmentPartyShift
    | FeedbackAlignmentChange
    | FeedbackAlignmentRestrictedByClassLost
    | FeedbackAlignmentRestrictedByClassGain
    | FeedbackAlignmentRestrictedWarningLoss
    | FeedbackAlignmentRestrictedWarningGain
    | FeedbackAlignmentEpitomeGained
    | FeedbackAlignmentEpitomeLost
    | FeedbackImmunityDisease
    | FeedbackImmunityCriticalHit
    | FeedbackImmunityDeathMagic
    | FeedbackImmunityFear
    | FeedbackImmunityKnockdown
    | FeedbackImmunityParalysis
    | FeedbackImmunityNegativeLevel
    | FeedbackImmunityMindSpells
    | FeedbackImmunityPoison
    | FeedbackImmunitySneakAttack
    | FeedbackImmunitySleep
    | FeedbackImmunityDaze
    | FeedbackImmunityConfusion
    | FeedbackImmunityStun
    | FeedbackImmunityBlindness
    | FeedbackImmunityDeafness
    | FeedbackImmunityCurse
    | FeedbackImmunityCharm
    | FeedbackImmunityDominate
    | FeedbackImmunityEntangle
    | FeedbackImmunitySilence
    | FeedbackImmunitySlow
)


_FEEDBACK_CLASSES_3 = (
    FeedbackAssociateSummoned
    | FeedbackAssociateUnsummoning
    | FeedbackAssociateUnsummoningBecauseRest
    | FeedbackAssociateUnsummoningBecauseDied
    | FeedbackAssociateDominated
    | FeedbackAssociateDominationEnded
    | FeedbackAssociatePossessedCannotRecoverTrap
    | FeedbackAssociatePossessedCannotBarter
    | FeedbackAssociatePossessedCannotEquip
    | FeedbackAssociatePossessedCannotRepositoryMove
    | FeedbackAssociatePossessedCannotPickUp
    | FeedbackAssociatePossessedCannotDrop
    | FeedbackAssociatePossessedCannotUnequip
    | FeedbackAssociatePossessedCannotRest
    | FeedbackAssociatePossessedCannotDialogue
    | FeedbackAssociatePossessedCannotGiveItem
    | FeedbackAssociatePossessedCannotTakeItem
    | FeedbackAssociatePossessedCannotUseContainer
    | FeedbackScriptError
    | FeedbackActionListOverflow
    | FeedbackEffectListOverflow
    | FeedbackAIUpdateTimeOverflow
    | FeedbackActionListWipeOverflow
    | FeedbackEffectListWipeOverflow
    | FeedbackSendMessageToPc
    | FeedbackSendMessageToPcStrref
    | FeedbackGuiOnlyPartyLeaderMayClick
    | FeedbackPaused
    | FeedbackUnpaused
    | FeedbackRestYouMayNotAtThisTime
    | FeedbackGuiCharExportRequestSent
    | FeedbackGuiCharExportedSuccessfully
    | FeedbackGuiErrorCharNotExported
    | FeedbackCameraBg
    | FeedbackCameraEq
    | FeedbackCameraChasecam
    | FeedbackSaving
    | FeedbackSaveComplete
    | FeedbackCannotLevelupWhilePolymorphed
)


_ALL_FEEDBACK_CLASSES = (
    _FEEDBACK_CLASSES_0
    | _FEEDBACK_CLASSES_1
    | _FEEDBACK_CLASSES_2
    | _FEEDBACK_CLASSES_3
)


FeedbackPayload = Annotated[
    _ALL_FEEDBACK_CLASSES,
    m.Tagged(
        m.MessageType.WORD,
        {
            FeedbackType.SKILL_CANT_USE: FeedbackSkillCantUse,
            FeedbackType.SKILL_CANT_USE_TIMER: FeedbackSkillCantUseTimer,
            FeedbackType.SKILL_ANIMALEMPATHY_VALID_TARGETS: FeedbackSkillAnimalEmpathyValidTargets,
            FeedbackType.SKILL_TAUNT_VALID_TARGETS: FeedbackSkillTauntValidTargets,
            FeedbackType.SKILL_TAUNT_TARGET_IMMUNE: FeedbackSkillTauntTargetImmune,
            FeedbackType.SKILL_PICKPOCKET_STOLE_ITEM: FeedbackSkillPickpocketStoleItem,
            FeedbackType.SKILL_PICKPOCKET_STOLE_GOLD: FeedbackSkillPickpocketStoleGold,
            FeedbackType.SKILL_PICKPOCKET_ATTEMPTING_TO_STEAL: FeedbackSkillPickpocketAttemptingToSteal,
            FeedbackType.SKILL_PICKPOCKET_ATTEMPT_DETECTED: FeedbackSkillPickpocketAttemptDetected,
            FeedbackType.SKILL_PICKPOCKET_STOLE_ITEM_TARGET: FeedbackSkillPickpocketStoleItemTarget,
            FeedbackType.SKILL_PICKPOCKET_STOLE_GOLD_TARGET: FeedbackSkillPickpocketStoleGoldTarget,
            FeedbackType.SKILL_PICKPOCKET_TARGET_BROKE: FeedbackSkillPickpocketTargetBroke,
            FeedbackType.SKILL_HEAL_TARGET_NOT_DISPSND: FeedbackSkillHealTargetNotDispsnd,
            FeedbackType.SKILL_HEAL_VALID_TARGETS: FeedbackSkillHealValidTargets,
            FeedbackType.SKILL_STEALTH_IN_COMBAT: FeedbackSkillStealthInCombat,
            FeedbackType.TARGET_UNAWARE: FeedbackTargetUnaware,
            FeedbackType.ACTION_NOT_POSSIBLE_STATUS: FeedbackActionNotPossibleStatus,
            FeedbackType.ACTION_NOT_POSSIBLE_PVP: FeedbackActionNotPossiblePvp,
            FeedbackType.ACTION_CANT_REACH_TARGET: FeedbackActionCantReachTarget,
            FeedbackType.ACTION_NO_LOOT: FeedbackActionNoLoot,
            FeedbackType.WEIGHT_TOO_ENCUMBERED_TO_RUN: FeedbackWeightTooEncumberedToRun,
            FeedbackType.WEIGHT_TOO_ENCUMBERED_WALK_SLOW: FeedbackWeightTooEncumberedWalkSlow,
            FeedbackType.WEIGHT_TOO_ENCUMBERED_CANT_PICKUP: FeedbackWeightTooEncumberedCantPickup,
            FeedbackType.STATS_LEVELUP: FeedbackStatsLevelUp,
            FeedbackType.INVENTORY_FULL: FeedbackInventoryFull,
            FeedbackType.CONTAINER_FULL: FeedbackContainerFull,
            FeedbackType.TRAP_TRIGGERED: FeedbackTrapTriggered,
            FeedbackType.DAMAGE_HEALED: FeedbackDamageHealed,
            FeedbackType.EXPERIENCE_GAINNED: FeedbackExperienceGained,
            FeedbackType.EXPERIENCE_LOST: FeedbackExperienceLost,
            FeedbackType.JOURNALUPDATED: FeedbackJournalUpdated,
            FeedbackType.BARTER_CANCELLED: FeedbackBarterCancelled,
            FeedbackType.DETECT_MODE_ACTIVATED: FeedbackDetectModeActivated,
            FeedbackType.DETECT_MODE_DEACTIVATED: FeedbackDetectModeDeactivated,
            FeedbackType.STEALTH_MODE_ACTIVATED: FeedbackStealthModeActivated,
            FeedbackType.STEALTH_MODE_DEACTIVATED: FeedbackStealthModeDeactivated,
            FeedbackType.PARRY_MODE_ACTIVATED: FeedbackParryModeActivated,
            FeedbackType.PARRY_MODE_DEACTIVATED: FeedbackParryModeDeactivated,
            FeedbackType.POWER_ATTACK_MODE_ACTIVATED: FeedbackPowerAttackModeActivated,
            FeedbackType.POWER_ATTACK_MODE_DEACTIVATED: FeedbackPowerAttackModeDeactivated,
            FeedbackType.IMPROVED_POWER_ATTACK_MODE_ACTIVATED: FeedbackImprovedPowerAttackModeActivated,
            FeedbackType.IMPROVED_POWER_ATTACK_MODE_DEACTIVATED: FeedbackImprovedPowerAttackModeDeactivated,
            FeedbackType.RAPID_SHOT_MODE_ACTIVATED: FeedbackRapidShotModeActivated,
            FeedbackType.RAPID_SHOT_MODE_DEACTIVATED: FeedbackRapidShotModeDeactivated,
            FeedbackType.FLURRY_OF_BLOWS_MODE_ACTIVATED: FeedbackFlurryOfBlowsModeActivated,
            FeedbackType.FLURRY_OF_BLOWS_MODE_DEACTIVATED: FeedbackFlurryOfBlowsModeDeactivated,
            FeedbackType.EXPERTISE_MODE_ACTIVATED: FeedbackExpertiseModeActivated,
            FeedbackType.EXPERTISE_MODE_DEACTIVATED: FeedbackExpertiseModeDeactivated,
            FeedbackType.IMPROVED_EXPERTISE_MODE_ACTIVATED: FeedbackImprovedExpertiseModeActivated,
            FeedbackType.IMPROVED_EXPERTISE_MODE_DEACTIVATED: FeedbackImprovedExpertiseModeDeactivated,
            FeedbackType.DEFENSIVE_CAST_MODE_ACTIVATED: FeedbackDefensiveCastModeActivated,
            FeedbackType.DEFENSIVE_CAST_MODE_DEACTIVATED: FeedbackDefensiveCastModeDeactivated,
            FeedbackType.MODE_CANNOT_USE_WEAPONS: FeedbackModeCannotUseWeapons,
            FeedbackType.DIRTY_FIGHTING_MODE_ACTIVATED: FeedbackDirtyFightingModeActivated,
            FeedbackType.DIRTY_FIGHTING_MODE_DEACTIVATED: FeedbackDirtyFightingModeDeactivated,
            FeedbackType.DEFENSIVE_STANCE_MODE_ACTIVATED: FeedbackDefensiveStanceModeActivated,
            FeedbackType.DEFENSIVE_STANCE_MODE_DEACTIVATED: FeedbackDefensiveStanceModeDeactivated,
            FeedbackType.COUNTERSPELL_MODE_ACTIVATED: FeedbackCounterspellModeActivated,
            FeedbackType.COUNTERSPELL_MODE_DEACTIVATED: FeedbackCounterspellModeDeactivated,
            FeedbackType.EQUIP_SKILL_SPELL_MODIFIERS: FeedbackEquipSkillSpellModifiers,
            FeedbackType.EQUIP_UNIDENTIFIED: FeedbackEquipUnidentified,
            FeedbackType.EQUIP_MONK_ABILITIES: FeedbackEquipMonkAbilities,
            FeedbackType.EQUIP_INSUFFICIENT_LEVEL: FeedbackEquipInsufficientLevel,
            FeedbackType.EQUIP_PROFICIENCIES: FeedbackEquipProficiencies,
            FeedbackType.EQUIP_WEAPON_TOO_LARGE: FeedbackEquipWeaponTooLarge,
            FeedbackType.EQUIP_WEAPON_TOO_SMALL: FeedbackEquipWeaponTooSmall,
            FeedbackType.EQUIP_ONE_HANDED_WEAPON: FeedbackEquipOneHandedWeapon,
            FeedbackType.EQUIP_TWO_HANDED_WEAPON: FeedbackEquipTwoHandedWeapon,
            FeedbackType.EQUIP_WEAPON_SWAPPED_OUT: FeedbackEquipWeaponSwappedOut,
            FeedbackType.EQUIP_ONE_CHAIN_WEAPON: FeedbackEquipOneChainWeapon,
            FeedbackType.EQUIP_NATURAL_AC_NO_STACK: FeedbackEquipNaturalAcNoStack,
            FeedbackType.EQUIP_ARMOUR_AC_NO_STACK: FeedbackEquipArmourAcNoStack,
            FeedbackType.EQUIP_SHIELD_AC_NO_STACK: FeedbackEquipShieldAcNoStack,
            FeedbackType.EQUIP_DEFLECTION_AC_NO_STACK: FeedbackEquipDeflectionAcNoStack,
            FeedbackType.EQUIP_NO_ARMOR_COMBAT: FeedbackEquipNoArmorCombat,
            FeedbackType.EQUIP_RANGER_ABILITIES: FeedbackEquipRangerAbilities,
            FeedbackType.EQUIP_ALIGNMENT: FeedbackEquipAlignment,
            FeedbackType.EQUIP_CLASS: FeedbackEquipClass,
            FeedbackType.EQUIP_RACE: FeedbackEquipRace,
            FeedbackType.UNEQUIP_NO_ARMOR_COMBAT: FeedbackUnequipNoArmorCombat,
            FeedbackType.OBJECT_LOCKED: FeedbackObjectLocked,
            FeedbackType.OBJECT_NOT_LOCKED: FeedbackObjectNotLocked,
            FeedbackType.OBJECT_SPECIAL_KEY: FeedbackObjectSpecialKey,
            FeedbackType.OBJECT_USED_KEY: FeedbackObjectUsedKey,
            FeedbackType.REST_EXCITED_CANT_REST: FeedbackRestExcitedCantRest,
            FeedbackType.REST_BEGINNING_REST: FeedbackRestBeginningRest,
            FeedbackType.REST_FINISHED_REST: FeedbackRestFinishedRest,
            FeedbackType.REST_CANCEL_REST: FeedbackRestCancelRest,
            FeedbackType.REST_NOT_ALLOWED_IN_AREA: FeedbackRestNotAllowedInArea,
            FeedbackType.REST_NOT_ALLOWED_BY_POSSESSED_FAMILIAR: FeedbackRestNotAllowedByPossessedFamiliar,
            FeedbackType.REST_NOT_ALLOWED_ENEMIES: FeedbackRestNotAllowedEnemies,
            FeedbackType.REST_CANT_UNDER_THIS_EFFECT: FeedbackRestCantUnderThisEffect,
            FeedbackType.CAST_LOST_TARGET: FeedbackCastLostTarget,
            FeedbackType.CAST_CANT_CAST: FeedbackCastCantCast,
            FeedbackType.CAST_CNTRSPELL_TARGET_LOST_TARGET: FeedbackCastCntrspellTargetLostTarget,
            FeedbackType.CAST_ARCANE_SPELL_FAILURE: FeedbackCastArcaneSpellFailure,
            FeedbackType.CAST_CNTRSPELL_TARGET_ARCANE_SPELL_FAILURE: FeedbackCastCntrspellTargetArcaneSpellFailure,
            FeedbackType.CAST_ENTANGLE_CONCENTRATION_FAILURE: FeedbackCastEntangleConcentrationFailure,
            FeedbackType.CAST_CNTRSPELL_TARGET_ENTANGLE_CONCENTRATION_FAILURE: FeedbackCastCntrspellTargetEntangleConcentrationFailure,
            FeedbackType.CAST_SPELL_INTERRUPTED: FeedbackCastSpellInterrupted,
            FeedbackType.CAST_EFFECT_SPELL_FAILURE: FeedbackCastEffectSpellFailure,
            FeedbackType.CAST_CANT_CAST_WHILE_POLYMORPHED: FeedbackCastCantCastWhilePolymorphed,
            FeedbackType.CAST_USE_HANDS: FeedbackCastUseHands,
            FeedbackType.CAST_USE_MOUTH: FeedbackCastUseMouth,
            FeedbackType.CAST_DEFCAST_CONCENTRATION_FAILURE: FeedbackCastDefcastConcentrationFailure,
            FeedbackType.CAST_DEFCAST_CONCENTRATION_SUCCESS: FeedbackCastDefcastConcentrationSuccess,
            FeedbackType.USEITEM_CANT_USE: FeedbackUseItemCantUse,
            FeedbackType.CONVERSATION_TOOFAR: FeedbackConversationTooFar,
            FeedbackType.CONVERSATION_BUSY: FeedbackConversationBusy,
            FeedbackType.CONVERSATION_IN_COMBAT: FeedbackConversationInCombat,
            FeedbackType.CHARACTER_INTRANSIT: FeedbackCharacterInTransit,
            FeedbackType.CHARACTER_OUTTRANSIT: FeedbackCharacterOutTransit,
            FeedbackType.USEITEM_NOT_EQUIPPED: FeedbackUseItemNotEquipped,
            FeedbackType.DROPITEM_CANT_DROP: FeedbackDropItemCantDrop,
            FeedbackType.DROPITEM_CANT_GIVE: FeedbackDropItemCantGive,
            FeedbackType.CLIENT_SERVER_SPELL_MISMATCH: FeedbackClientServerSpellMismatch,
            FeedbackType.COMBAT_RUNNING_OUT_OF_AMMO: FeedbackCombatRunningOutOfAmmo,
            FeedbackType.COMBAT_OUT_OF_AMMO: FeedbackCombatOutOfAmmo,
            FeedbackType.COMBAT_HENCHMAN_OUT_OF_AMMO: FeedbackCombatHenchmanOutOfAmmo,
            FeedbackType.COMBAT_DAMAGE_IMMUNITY: FeedbackCombatDamageImmunity,
            FeedbackType.COMBAT_SPELL_IMMUNITY: FeedbackCombatSpellImmunity,
            FeedbackType.COMBAT_DAMAGE_RESISTANCE: FeedbackCombatDamageResistance,
            FeedbackType.COMBAT_DAMAGE_RESISTANCE_REMAINING: FeedbackCombatDamageResistanceRemaining,
            FeedbackType.COMBAT_DAMAGE_REDUCTION: FeedbackCombatDamageReduction,
            FeedbackType.COMBAT_DAMAGE_REDUCTION_REMAINING: FeedbackCombatDamageReductionRemaining,
            FeedbackType.COMBAT_SPELL_LEVEL_ABSORPTION: FeedbackCombatSpellLevelAbsorption,
            FeedbackType.COMBAT_SPELL_LEVEL_ABSORPTION_REMAINING: FeedbackCombatSpellLevelAbsorptionRemaining,
            FeedbackType.COMBAT_WEAPON_NOT_EFFECTIVE: FeedbackCombatWeaponNotEffective,
            FeedbackType.COMBAT_EPIC_DODGE_ATTACK_EVADED: FeedbackCombatEpicDodgeAttackEvaded,
            FeedbackType.COMBAT_MASSIVE_DAMAGE: FeedbackCombatMassiveDamage,
            FeedbackType.COMBAT_SAVED_VS_MASSIVE_DAMAGE: FeedbackCombatSavedVsMassiveDamage,
            FeedbackType.COMBAT_SAVED_VS_DEVASTATING_CRITICAL: FeedbackCombatSavedVsDevastatingCritical,
            FeedbackType.FEAT_SAP_VALID_TARGETS: FeedbackFeatSapValidTargets,
            FeedbackType.FEAT_KNOCKDOWN_VALID_TARGETS: FeedbackFeatKnockdownValidTargets,
            FeedbackType.FEAT_IMPKNOCKDOWN_VALID_TARGETS: FeedbackFeatImpknockdownValidTargets,
            FeedbackType.FEAT_CALLED_SHOT_NO_LEGS: FeedbackFeatCalledShotNoLegs,
            FeedbackType.FEAT_CALLED_SHOT_NO_ARMS: FeedbackFeatCalledShotNoArms,
            FeedbackType.FEAT_SMITE_GOOD_TARGET_NOT_GOOD: FeedbackFeatSmiteGoodTargetNotGood,
            FeedbackType.FEAT_SMITE_EVIL_TARGET_NOT_EVIL: FeedbackFeatSmiteEvilTargetNotEvil,
            FeedbackType.FEAT_QUIVERING_PALM_HIGHER_LEVEL: FeedbackFeatQuiveringPalmHigherLevel,
            FeedbackType.FEAT_KEEN_SENSE_DETECT: FeedbackFeatKeenSenseDetect,
            FeedbackType.FEAT_USE_UNARMED: FeedbackFeatUseUnarmed,
            FeedbackType.FEAT_USES: FeedbackFeatUses,
            FeedbackType.FEAT_USE_WEAPON_OF_CHOICE: FeedbackFeatUseWeaponOfChoice,
            FeedbackType.PARTY_NEW_LEADER: FeedbackPartyNewLeader,
            FeedbackType.PARTY_MEMBER_KICKED: FeedbackPartyMemberKicked,
            FeedbackType.PARTY_KICKED_YOU: FeedbackPartyKickedYou,
            FeedbackType.PARTY_ALREADY_CONSIDERING: FeedbackPartyAlreadyConsidering,
            FeedbackType.PARTY_ALREADY_INVOLVED: FeedbackPartyAlreadyInvolved,
            FeedbackType.PARTY_SENT_INVITATION: FeedbackPartySentInvitation,
            FeedbackType.PARTY_RECEIVED_INVITATION: FeedbackPartyReceivedInvitation,
            FeedbackType.PARTY_JOINED: FeedbackPartyJoined,
            FeedbackType.PARTY_INVITATION_IGNORED: FeedbackPartyInvitationIgnored,
            FeedbackType.PARTY_YOU_IGNORED_INVITATION: FeedbackPartyYouIgnoredInvitation,
            FeedbackType.PARTY_INVITATION_REJECTED: FeedbackPartyInvitationRejected,
            FeedbackType.PARTY_YOU_REJECTED_INVITATION: FeedbackPartyYouRejectedInvitation,
            FeedbackType.PARTY_INVITATION_EXPIRED: FeedbackPartyInvitationExpired,
            FeedbackType.PARTY_LEFT_PARTY: FeedbackPartyLeftParty,
            FeedbackType.PARTY_YOU_LEFT: FeedbackPartyYouLeft,
            FeedbackType.PARTY_HENCHMAN_LIMIT: FeedbackPartyHenchmanLimit,
            FeedbackType.PARTY_CANNOT_LEAVE_THE_ONE_PARTY: FeedbackPartyCannotLeaveTheOneParty,
            FeedbackType.PARTY_CANNOT_KICK_FROM_THE_ONE_PARTY: FeedbackPartyCannotKickFromTheOneParty,
            FeedbackType.PARTY_YOU_INVITED_NON_SINGLETON: FeedbackPartyYouInvitedNonSingleton,
            FeedbackType.PVP_REACTION_DISLIKESYOU: FeedbackPvpReactionDislikesYou,
            FeedbackType.ITEM_RECEIVED: FeedbackItemReceived,
            FeedbackType.ITEM_LOST: FeedbackItemLost,
            FeedbackType.ITEM_EJECTED: FeedbackItemEjected,
            FeedbackType.ITEM_USE_UNIDENTIFIED: FeedbackItemUseUnidentified,
            FeedbackType.ITEM_GOLD_GAINED: FeedbackItemGoldGained,
            FeedbackType.ITEM_GOLD_LOST: FeedbackItemGoldLost,
            FeedbackType.LEARN_SCROLL_NOT_SCROLL: FeedbackLearnScrollNotScroll,
            FeedbackType.LEARN_SCROLL_CANT_LEARN_CLASS: FeedbackLearnScrollCantLearnClass,
            FeedbackType.LEARN_SCROLL_CANT_LEARN_LEVEL: FeedbackLearnScrollCantLearnLevel,
            FeedbackType.LEARN_SCROLL_CANT_LEARN_ABILITY: FeedbackLearnScrollCantLearnAbility,
            FeedbackType.LEARN_SCROLL_CANT_LEARN_OPPOSITION: FeedbackLearnScrollCantLearnOpposition,
            FeedbackType.LEARN_SCROLL_CANT_LEARN_POSSESS: FeedbackLearnScrollCantLearnPossess,
            FeedbackType.LEARN_SCROLL_CANT_LEARN_KNOWN: FeedbackLearnScrollCantLearnKnown,
            FeedbackType.LEARN_SCROLL_CANT_LEARN_DIVINE: FeedbackLearnScrollCantLearnDivine,
            FeedbackType.LEARN_SCROLL_SUCCESS: FeedbackLearnScrollSuccess,
            FeedbackType.FLOATY_TEXT_STRREF: FeedbackFloatyTextStrref,
            FeedbackType.FLOATY_TEXT_STRING: FeedbackFloatyTextString,
            FeedbackType.CANNOT_SELL_PLOT_ITEM: FeedbackCannotSellPlotItem,
            FeedbackType.CANNOT_SELL_CONTAINER: FeedbackCannotSellContainer,
            FeedbackType.CANNOT_SELL_ITEM: FeedbackCannotSellItem,
            FeedbackType.NOT_ENOUGH_GOLD: FeedbackNotEnoughGold,
            FeedbackType.TRANSACTION_SUCCEEDED: FeedbackTransactionSucceeded,
            FeedbackType.PRICE_TOO_HIGH: FeedbackPriceTooHigh,
            FeedbackType.STORE_NOT_ENOUGH_GOLD: FeedbackStoreNotEnoughGold,
            FeedbackType.CANNOT_SELL_STOLEN_ITEM: FeedbackCannotSellStolenItem,
            FeedbackType.CANNOT_SELL_RESTRICTED_ITEM: FeedbackCannotSellRestrictedItem,
            FeedbackType.PORTAL_TIMEDOUT: FeedbackPortalTimedOut,
            FeedbackType.PORTAL_INVALID: FeedbackPortalInvalid,
            FeedbackType.CHAT_TELL_PLAYER_NOT_FOUND: FeedbackChatTellPlayerNotFound,
            FeedbackType.ALIGNMENT_SHIFT: FeedbackAlignmentShift,
            FeedbackType.ALIGNMENT_PARTY_SHIFT: FeedbackAlignmentPartyShift,
            FeedbackType.ALIGNMENT_CHANGE: FeedbackAlignmentChange,
            FeedbackType.ALIGNMENT_RESTRICTED_BY_CLASS_LOST: FeedbackAlignmentRestrictedByClassLost,
            FeedbackType.ALIGNMENT_RESTRICTED_BY_CLASS_GAIN: FeedbackAlignmentRestrictedByClassGain,
            FeedbackType.ALIGNMENT_RESTRICTED_WARNING_LOSS: FeedbackAlignmentRestrictedWarningLoss,
            FeedbackType.ALIGNMENT_RESTRICTED_WARNING_GAIN: FeedbackAlignmentRestrictedWarningGain,
            FeedbackType.ALIGNMENT_EPITOME_GAINED: FeedbackAlignmentEpitomeGained,
            FeedbackType.ALIGNMENT_EPITOME_LOST: FeedbackAlignmentEpitomeLost,
            FeedbackType.IMMUNITY_DISEASE: FeedbackImmunityDisease,
            FeedbackType.IMMUNITY_CRITICAL_HIT: FeedbackImmunityCriticalHit,
            FeedbackType.IMMUNITY_DEATH_MAGIC: FeedbackImmunityDeathMagic,
            FeedbackType.IMMUNITY_FEAR: FeedbackImmunityFear,
            FeedbackType.IMMUNITY_KNOCKDOWN: FeedbackImmunityKnockdown,
            FeedbackType.IMMUNITY_PARALYSIS: FeedbackImmunityParalysis,
            FeedbackType.IMMUNITY_NEGATIVE_LEVEL: FeedbackImmunityNegativeLevel,
            FeedbackType.IMMUNITY_MIND_SPELLS: FeedbackImmunityMindSpells,
            FeedbackType.IMMUNITY_POISON: FeedbackImmunityPoison,
            FeedbackType.IMMUNITY_SNEAK_ATTACK: FeedbackImmunitySneakAttack,
            FeedbackType.IMMUNITY_SLEEP: FeedbackImmunitySleep,
            FeedbackType.IMMUNITY_DAZE: FeedbackImmunityDaze,
            FeedbackType.IMMUNITY_CONFUSION: FeedbackImmunityConfusion,
            FeedbackType.IMMUNITY_STUN: FeedbackImmunityStun,
            FeedbackType.IMMUNITY_BLINDNESS: FeedbackImmunityBlindness,
            FeedbackType.IMMUNITY_DEAFNESS: FeedbackImmunityDeafness,
            FeedbackType.IMMUNITY_CURSE: FeedbackImmunityCurse,
            FeedbackType.IMMUNITY_CHARM: FeedbackImmunityCharm,
            FeedbackType.IMMUNITY_DOMINATE: FeedbackImmunityDominate,
            FeedbackType.IMMUNITY_ENTANGLE: FeedbackImmunityEntangle,
            FeedbackType.IMMUNITY_SILENCE: FeedbackImmunitySilence,
            FeedbackType.IMMUNITY_SLOW: FeedbackImmunitySlow,
            FeedbackType.ASSOCIATE_SUMMONED: FeedbackAssociateSummoned,
            FeedbackType.ASSOCIATE_UNSUMMONING: FeedbackAssociateUnsummoning,
            FeedbackType.ASSOCIATE_UNSUMMONING_BECAUSE_REST: FeedbackAssociateUnsummoningBecauseRest,
            FeedbackType.ASSOCIATE_UNSUMMONING_BECAUSE_DIED: FeedbackAssociateUnsummoningBecauseDied,
            FeedbackType.ASSOCIATE_DOMINATED: FeedbackAssociateDominated,
            FeedbackType.ASSOCIATE_DOMINATION_ENDED: FeedbackAssociateDominationEnded,
            FeedbackType.ASSOCIATE_POSSESSED_CANNOT_RECOVER_TRAP: FeedbackAssociatePossessedCannotRecoverTrap,
            FeedbackType.ASSOCIATE_POSSESSED_CANNOT_BARTER: FeedbackAssociatePossessedCannotBarter,
            FeedbackType.ASSOCIATE_POSSESSED_CANNOT_EQUIP: FeedbackAssociatePossessedCannotEquip,
            FeedbackType.ASSOCIATE_POSSESSED_CANNOT_REPOSITORY_MOVE: FeedbackAssociatePossessedCannotRepositoryMove,
            FeedbackType.ASSOCIATE_POSSESSED_CANNOT_PICK_UP: FeedbackAssociatePossessedCannotPickUp,
            FeedbackType.ASSOCIATE_POSSESSED_CANNOT_DROP: FeedbackAssociatePossessedCannotDrop,
            FeedbackType.ASSOCIATE_POSSESSED_CANNOT_UNEQUIP: FeedbackAssociatePossessedCannotUnequip,
            FeedbackType.ASSOCIATE_POSSESSED_CANNOT_REST: FeedbackAssociatePossessedCannotRest,
            FeedbackType.ASSOCIATE_POSSESSED_CANNOT_DIALOGUE: FeedbackAssociatePossessedCannotDialogue,
            FeedbackType.ASSOCIATE_POSSESSED_CANNOT_GIVE_ITEM: FeedbackAssociatePossessedCannotGiveItem,
            FeedbackType.ASSOCIATE_POSSESSED_CANNOT_TAKE_ITEM: FeedbackAssociatePossessedCannotTakeItem,
            FeedbackType.ASSOCIATE_POSSESSED_CANNOT_USE_CONTAINER: FeedbackAssociatePossessedCannotUseContainer,
            FeedbackType.SCRIPT_ERROR: FeedbackScriptError,
            FeedbackType.ACTION_LIST_OVERFLOW: FeedbackActionListOverflow,
            FeedbackType.EFFECT_LIST_OVERFLOW: FeedbackEffectListOverflow,
            FeedbackType.AI_UPDATE_TIME_OVERFLOW: FeedbackAIUpdateTimeOverflow,
            FeedbackType.ACTION_LIST_WIPE_OVERFLOW: FeedbackActionListWipeOverflow,
            FeedbackType.EFFECT_LIST_WIPE_OVERFLOW: FeedbackEffectListWipeOverflow,
            FeedbackType.SEND_MESSAGE_TO_PC: FeedbackSendMessageToPc,
            FeedbackType.SEND_MESSAGE_TO_PC_STRREF: FeedbackSendMessageToPcStrref,
            FeedbackType.GUI_ONLY_PARTY_LEADER_MAY_CLICK: FeedbackGuiOnlyPartyLeaderMayClick,
            FeedbackType.PAUSED: FeedbackPaused,
            FeedbackType.UNPAUSED: FeedbackUnpaused,
            FeedbackType.REST_YOU_MAY_NOT_AT_THIS_TIME: FeedbackRestYouMayNotAtThisTime,
            FeedbackType.GUI_CHAR_EXPORT_REQUEST_SENT: FeedbackGuiCharExportRequestSent,
            FeedbackType.GUI_CHAR_EXPORTED_SUCCESSFULLY: FeedbackGuiCharExportedSuccessfully,
            FeedbackType.GUI_ERROR_CHAR_NOT_EXPORTED: FeedbackGuiErrorCharNotExported,
            FeedbackType.CAMERA_BG: FeedbackCameraBg,
            FeedbackType.CAMERA_EQ: FeedbackCameraEq,
            FeedbackType.CAMERA_CHASECAM: FeedbackCameraChasecam,
            FeedbackType.SAVING: FeedbackSaving,
            FeedbackType.SAVE_COMPLETE: FeedbackSaveComplete,
            FeedbackType.CANNOT_LEVELUP_WHILE_POLYMORPHED: FeedbackCannotLevelupWhilePolymorphed,
        },
    ),
]


@dataclass(kw_only=True)
class ClientSideMessageFeedback(m.Message):
    MAJOR = 0x12
    MINOR = 0x0B
    DIRECTION = m.Direction.S2C

    payload: FeedbackPayload
