from dataclasses import dataclass
from typing import Annotated

from .. import message as m

PROJECTILE_TYPE_SPELL = 6
PROJECTILE_TYPE_SPELL_CUSTOM_PATH = 7

MESSAGE_SIZE_ATTACK_RESULT = 4
MESSAGE_SIZE_DAMAGE_ROLL = 9


@dataclass(kw_only=True)
class _ProjectileNonSpell:
    projectile_path: m.Byte
    base_item_id: m.Byte
    attack_result: m.Byte


@dataclass(kw_only=True)
class _ProjectileSpell:
    spell_id: m.Dword


@dataclass(kw_only=True)
class _ProjectileSpellCustomPath:
    spell_id: m.Dword
    projectile_path: m.Byte


@dataclass(kw_only=True)
class SafeProjectileSpawn(m.Message):
    MAJOR = 0x22
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    originator: m.ObjectId
    target: m.ObjectId
    origin_location: m.Vec3
    target_location: m.Vec3
    delta_time: m.Dword
    projectile: Annotated[
        _ProjectileNonSpell | _ProjectileSpell | _ProjectileSpellCustomPath,
        m.Tagged(
            m.MessageType.BYTE,
            {
                0: _ProjectileNonSpell,
                1: _ProjectileNonSpell,
                2: _ProjectileNonSpell,
                3: _ProjectileNonSpell,
                4: _ProjectileNonSpell,
                5: _ProjectileNonSpell,
                PROJECTILE_TYPE_SPELL: _ProjectileSpell,
                PROJECTILE_TYPE_SPELL_CUSTOM_PATH: _ProjectileSpellCustomPath,
            },
        ),
    ]


@dataclass(kw_only=True)
class _WhirlwindAttackEntry:
    hit: m.Bool
    target: Annotated[m.ObjectId, m.IfEq("hit", False)]
    reaction_animation: Annotated[m.Word, m.IfEq("hit", False)]
    reaction_animation_length: Annotated[m.Word, m.IfEq("hit", False)]
    attack_result: Annotated[
        m.Byte, m.IfEq("hit", False), m.Bits(MESSAGE_SIZE_ATTACK_RESULT)
    ]
    weapon_attack_type: Annotated[m.Byte, m.IfEq("hit", False)]


@dataclass(kw_only=True)
class SafeWhirlwindAttack(m.Message):
    MAJOR = 0x22
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    attacker: m.ObjectId
    improved_whirlwind: m.Bool
    attacks: Annotated[list[_WhirlwindAttackEntry], m.SizePrefix.BYTE]


@dataclass(kw_only=True)
class _WhirlwindDamageEntry:
    target: m.ObjectId
    reaction_animation: m.Word
    reaction_animation_length: m.Word
    attack_result: Annotated[m.Byte, m.Bits(MESSAGE_SIZE_ATTACK_RESULT)]
    damage: Annotated[m.Word, m.Bits(MESSAGE_SIZE_DAMAGE_ROLL)]
    killing_blow: m.Bool
    weapon_attack_type: m.Byte


@dataclass(kw_only=True)
class SafeWhirlwindDamage(m.Message):
    MAJOR = 0x22
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    attacker: m.ObjectId
    improved_whirlwind: m.Bool
    attacks: Annotated[list[_WhirlwindDamageEntry], m.SizePrefix.BYTE]
