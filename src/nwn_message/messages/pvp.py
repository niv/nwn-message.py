from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class PVPListAdd(m.Message):
    MAJOR = 0x29
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    player_id: m.Dword


@dataclass(kw_only=True)
class PVPListRemove(m.Message):
    MAJOR = 0x29
    MINOR = 0x02
    DIRECTION = m.Direction.C2S

    player_id: m.Dword


@dataclass(kw_only=True)
class PVPAttitudeChangeC2S(m.Message):
    MAJOR = 0x29
    MINOR = 0x03
    DIRECTION = m.Direction.C2S

    target_oid: m.ObjectId
    attitude: m.Bool


@dataclass(kw_only=True)
class PVPAttitudeChangeS2C(m.Message):
    MAJOR = 0x29
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    # "me" (the message recipient) and "the other party"
    player_id: m.Dword
    other_player_id: m.Dword
    attitude: m.Bool
    is_source: m.Bool  # True if I am the one expressing the attitude


@dataclass(kw_only=True)
class PVPDifficultyChange(m.Message):
    MAJOR = 0x29
    MINOR = 0x04
    DIRECTION = m.Direction.C2S

    difficulty: m.Int
