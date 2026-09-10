"""
Animation-related dataclasses for the GameObjUpdate 'U' (update) sub-message.

The ANIMATION_FLAG data is split across three non-contiguous reads,
interleaved with other flag reads:
- Block 1: anim_speed (float)
- Block 2: AnimTypeData  (animation type + optional attack/cast payloads)
- Block 3: AnimPathData  (client path number + optional waypoints)
Between block 2 and block 3, the visual-effect flag data is read.
"""

from typing import Annotated
from dataclasses import dataclass

from ..context import Context
from .. import message as m
from ..message._annotation import IfEq, MessageType, Bits

ANIM_CONJURE_1: int = 15
ANIM_CONJURE_2: int = 16
ANIM_CAST_1: int = 17
ANIM_CAST_2: int = 18
ANIM_CAST_3: int = 19
ANIM_CAST_4: int = 20
ANIM_CAST_5: int = 61
ANIM_ATTACK: int = 9

_CAST_ANIMS = frozenset(
    {ANIM_CAST_1, ANIM_CAST_2, ANIM_CAST_3, ANIM_CAST_4, ANIM_CAST_5}
)
_CONJURE_CAST_ANIMS = frozenset({ANIM_CONJURE_1, ANIM_CONJURE_2}) | _CAST_ANIMS


@dataclass(kw_only=True)
class AttackRecord:
    target_id: m.ObjectId
    react_anim: m.Word
    react_anim_len: m.Word
    anim_len: m.Word
    result: Annotated[int, MessageType.BYTE, Bits(4)]
    attack_type: m.Word
    damage: Annotated[int, MessageType.WORD, Bits(9)]
    ranged: m.Bool
    killing: m.Bool
    weapon_attack_type: Annotated[int, MessageType.BYTE, Bits(4)]


@dataclass(kw_only=True)
class CastAnimData:
    """Spell data written for CONJURE and CAST animations."""

    spell_id: m.Dword
    cast_item_id: m.ObjectId
    silent: m.Bool


@dataclass(kw_only=True)
class CastTargetData:
    """
    Projectile target data, only appended for CAST_1-5 animations.
    target_type: 1 = object target, 2 = position target.
    """

    target_type: m.Byte
    target_oid: Annotated[int, IfEq("target_type", 1), MessageType.OBJECT_ID]
    target_position: Annotated[m.Vec3, IfEq("target_type", 2)]
    projectile_time: m.Dword = 0


@dataclass(kw_only=True)
class AnimTypeData:
    """
    Animation type word plus optional attack or cast payload.
    Always read as the second part of an ANIMATION_FLAG block.
    Custom read() because the payload type depends on anim_type.
    """

    anim_type: int
    attacks: list[AttackRecord]  # ATTACK anim only
    spell: CastAnimData | None  # CONJURE or CAST anims
    cast_target: CastTargetData | None  # CAST_1-5 only

    @classmethod
    def read(cls, rd: m.Reader, context: Context) -> "AnimTypeData":
        anim_type = rd.read_word()
        attacks, spell, cast_target = [], None, None

        if anim_type == ANIM_ATTACK:
            n = rd.read_byte()  # bits=2
            attacks = [m.read_dataclass(AttackRecord, rd, context) for _ in range(n)]

        if anim_type in _CONJURE_CAST_ANIMS:
            spell = m.read_dataclass(CastAnimData, rd, context)

        if anim_type in _CAST_ANIMS:
            cast_target = m.read_dataclass(CastTargetData, rd, context)

        return cls(
            anim_type=anim_type, attacks=attacks, spell=spell, cast_target=cast_target
        )

    def write(self, wr: m.Writer, context: Context) -> None:
        wr.write_word(self.anim_type)

        if self.anim_type == ANIM_ATTACK and self.attacks is not None:
            wr.write_byte(len(self.attacks))  # bits=2
            for atk in self.attacks:
                m.write_dataclass(atk, wr, context)

        if self.anim_type in _CONJURE_CAST_ANIMS and self.spell is not None:
            m.write_dataclass(self.spell, wr, context)

        if self.anim_type in _CAST_ANIMS and self.cast_target is not None:
            m.write_dataclass(self.cast_target, wr, context)


@dataclass(kw_only=True)
class AnimPathData:
    """
    Path / waypoint data at the end of an ANIMATION_FLAG block.
    Custom read() because the waypoint list length is runtime-determined.
    """

    client_path_number: int
    waypoints: list[tuple[float, float]]
    drive_mode: bool = False
    drive_slide_factor: float = 1.0

    @classmethod
    def read(cls, rd: m.Reader, context: Context) -> "AnimPathData":
        path_num = rd.read_byte()
        num_wp = rd.read_word()
        drive = False
        slide = 1.0
        wps: list[tuple[float, float]] = []

        if num_wp > 0:
            drive = rd.read_bool()
            if drive:
                slide = rd.read_float()
            for _ in range(num_wp):
                x = rd.read_float()
                y = rd.read_float()
                wps.append((x, y))

        return cls(
            client_path_number=path_num,
            waypoints=wps,
            drive_mode=drive,
            drive_slide_factor=slide,
        )
