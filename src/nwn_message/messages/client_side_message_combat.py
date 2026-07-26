from dataclasses import dataclass
from typing import Annotated

from .. import message as m

MESSAGE_SIZE_DIE_ROLL = 5
MESSAGE_SIZE_ATTACK_RESULT = 4
MESSAGE_SIZE_ATTACK_MODE = 4
MESSAGE_SIZE_CONCEALMENT = 7
MESSAGE_SIZE_DIFFICULTY_CLASS = 7
MESSAGE_SIZE_DAMAGE = 14
DAMAGE_TYPE_MAX = 32
DAMAGE_TYPE_MAX_PRE_35 = 13

ATTACK_RESULT_ATTACKER_MISS_CHANCE = 9
ATTACK_RESULT_TARGET_CONCEALED = 8
_CONCEALMENT_RESULTS = {
    ATTACK_RESULT_ATTACKER_MISS_CHANCE,
    ATTACK_RESULT_TARGET_CONCEALED,
}


@dataclass(kw_only=True)
class ClientSideMessageComplexDeath(m.Message):
    MAJOR = 0x12
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    killer: m.ObjectId
    victim: m.ObjectId


@dataclass(kw_only=True)
class ClientSideMessageSpellResistance(m.Message):
    MAJOR = 0x12
    MINOR = 0x0A
    DIRECTION = m.Direction.S2C

    target: m.ObjectId
    result: m.Byte


@dataclass(kw_only=True)
class ClientSideMessageInitiative(m.Message):
    MAJOR = 0x12
    MINOR = 0x0E
    DIRECTION = m.Direction.S2C

    target: m.ObjectId
    die_roll: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_DIE_ROLL)]
    modifier: m.Char


@dataclass(kw_only=True)
class ClientSideMessageCounterspell(m.Message):
    MAJOR = 0x12
    MINOR = 0x0C
    DIRECTION = m.Direction.S2C

    caster: m.ObjectId
    target: m.ObjectId
    spell_id: m.Dword
    countered_spell_id: m.Dword
    success: m.Bool


@dataclass(kw_only=True)
class _DamageEntry:
    has_damage: m.Bool
    damage: Annotated[m.Word, m.Bits(MESSAGE_SIZE_DAMAGE), m.IfEq("has_damage", True)]


@dataclass(kw_only=True)
class ClientSideMessageComplexDamage(m.Message):
    MAJOR = 0x12
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    effector: m.ObjectId
    target: m.ObjectId
    damages: Annotated[list[_DamageEntry], m.FixedSizeHint(DAMAGE_TYPE_MAX)]
    combat_debugging: m.Bool
    debug_string: Annotated[m.String, m.IfEq("combat_debugging", True)]


@dataclass(kw_only=True)
class ClientSideMessageComplexAttack(m.Message):
    MAJOR = 0x12
    MINOR = 0x05
    DIRECTION = m.Direction.S2C

    effector: m.ObjectId
    target: m.ObjectId
    to_hit_mod: m.Char
    to_hit_roll: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_DIE_ROLL)]
    attack_result: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_ATTACK_RESULT)]
    attack_mode: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_ATTACK_MODE)]
    is_offhand: m.Bool
    sneak_attack: m.Bool
    death_attack: m.Bool
    attack_of_opportunity: m.Bool
    coup_de_grace: m.Bool
    critical_threat: m.Bool
    threat_roll: Annotated[
        m.Byte, m.Bits(MESSAGE_SIZE_DIE_ROLL), m.IfEq("critical_threat", True)
    ]
    concealment: Annotated[
        m.Byte,
        m.Bits(MESSAGE_SIZE_CONCEALMENT),
        m.IfIn("attack_result", _CONCEALMENT_RESULTS),
    ]
    combat_debugging: m.Bool
    debug_string: Annotated[m.String, m.IfEq("combat_debugging", True)]


@dataclass(kw_only=True)
class ClientSideMessageSpecialAttack(m.Message):
    MAJOR = 0x12
    MINOR = 0x06
    DIRECTION = m.Direction.S2C

    effector: m.ObjectId
    target: m.ObjectId
    to_hit_mod: m.Char
    to_hit_roll: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_DIE_ROLL)]
    attack_result: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_ATTACK_RESULT)]
    attack_type: m.Word
    attack_mode: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_ATTACK_MODE)]
    is_offhand: m.Bool
    sneak_attack: m.Bool
    death_attack: m.Bool
    critical_threat: m.Bool
    threat_roll: Annotated[
        m.Byte, m.Bits(MESSAGE_SIZE_DIE_ROLL), m.IfEq("critical_threat", True)
    ]
    concealment: Annotated[
        m.Byte,
        m.Bits(MESSAGE_SIZE_CONCEALMENT),
        m.IfIn("attack_result", _CONCEALMENT_RESULTS),
    ]
    combat_debugging: m.Bool
    debug_string: Annotated[m.String, m.IfEq("combat_debugging", True)]


@dataclass(kw_only=True)
class ClientSideMessageSavingThrow(m.Message):
    MAJOR = 0x12
    MINOR = 0x07
    DIRECTION = m.Direction.S2C

    target: m.ObjectId
    difficulty_class: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_DIFFICULTY_CLASS)]
    modifier: m.Char
    die_roll: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_DIE_ROLL)]
    auto_fail_on_1: Annotated[m.Bool, m.IfEq("die_roll", 1)]
    save_type: m.Byte
    save_specific_type: m.Byte
    has_feat: m.Bool
    feat: Annotated[m.Word, m.IfEq("has_feat", True)]


@dataclass(kw_only=True)
class ClientSideMessageTouchAttack(m.Message):
    MAJOR = 0x12
    MINOR = 0x0D
    DIRECTION = m.Direction.S2C

    attacker: m.ObjectId
    target: m.ObjectId
    to_hit_mod: m.Char
    to_hit_roll: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_DIE_ROLL)]
    attack_result: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_ATTACK_RESULT)]
    is_melee: m.Bool
    has_concealment: m.Bool
    concealment: Annotated[
        m.Byte, m.Bits(MESSAGE_SIZE_CONCEALMENT), m.IfEq("has_concealment", True)
    ]


@dataclass(kw_only=True)
class _DispelledSpell:
    spell_id: Annotated[m.Word, m.Bits(11)]


@dataclass(kw_only=True)
class ClientSideMessageDispelMagic(m.Message):
    MAJOR = 0x12
    MINOR = 0x0F
    DIRECTION = m.Direction.S2C

    target: m.ObjectId
    dispelled_spells: Annotated[list[_DispelledSpell], m.SizePrefix.BYTE]
