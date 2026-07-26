from dataclasses import dataclass

import nwn_message.message as m


@dataclass(kw_only=True)
class SetShaderUniformFloat(m.Message):
    MAJOR = 0x38
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    index: m.Byte
    value: m.Float


@dataclass(kw_only=True)
class SetShaderUniformInt(m.Message):
    MAJOR = 0x38
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    index: m.Byte
    value: m.Int


@dataclass(kw_only=True)
class SetShaderUniformVec(m.Message):
    MAJOR = 0x38
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    index: m.Byte
    x: m.Float
    y: m.Float
    z: m.Float
    w: m.Float
