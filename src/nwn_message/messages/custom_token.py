from dataclasses import dataclass
from typing import Annotated

from .. import message as m


@dataclass(kw_only=True)
class CustomTokenSingle(m.Message):
    MAJOR = 0x32
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    token_number: m.Int
    token_value: m.String


@dataclass(kw_only=True)
class CustomTokenListEntry:
    token_number: m.Int
    token_value: m.String


@dataclass(kw_only=True)
class CustomTokenList(m.Message):
    MAJOR = 0x32
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    tokens: Annotated[list[CustomTokenListEntry], m.SizePrefix.DWORD]
