from dataclasses import dataclass

import nwn_message.message as m


@dataclass(kw_only=True)
class TargetingDataSpell(m.Message):
    MAJOR = 0x39
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    spell_id: m.Int
    shape: m.Int
    size_x: m.Float
    size_y: m.Float
    flags: m.Int


@dataclass(kw_only=True)
class TargetingDataEnterTargetMode(m.Message):
    MAJOR = 0x39
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    shape: m.Int
    size_x: m.Float
    size_y: m.Float
    flags: m.Int
    spell_range: m.Float
    spell_id: m.Int
    feat_id: m.Int
