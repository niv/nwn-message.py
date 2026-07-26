import logging
import struct
from typing import Self, Any
from enum import IntEnum
import json

from nwn.environ import get_codepage
from nwn.types import Gender

from nwn_message.context import Context
from nwn_message.types import LocStr, STRREF_NONE

logger = logging.getLogger(__name__)


class MessageType(IntEnum):
    BITS = 1  # not used in WS wire format
    BOOL = 2
    BYTE = 3
    CHAR = 4
    WORD = 5
    SHORT = 6
    DWORD = 7
    INT = 8
    DWORD64 = 9
    INT64 = 10
    FLOAT = 11
    DOUBLE = 12
    RESREF = 13
    STRING = 14
    VOIDPTR = 15
    JSON = 16
    OBJECT_ID = 17  # uint32, distinct type tag from DWORD
    LOCSTRING = 18  # bool(is_strref) + [gender:u8 + strref:u32] | [len:u32 + bytes]


class Reader:
    """
    Deserialises the WSNetLayer wire format.

    The routing prefix is NOT expected here; the caller is responsible.
    """

    def __init__(self, data: bytes | bytearray, context: Context):
        self._buf = memoryview(data)
        self._pos = 0
        self.context = context

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args):
        pass

    def more(self) -> bool:
        return self._pos < len(self._buf)

    def tell(self) -> int:
        return self._pos

    def seek(self, pos: int) -> None:
        self._pos = pos

    @property
    def at_end(self) -> bool:
        return self._pos >= len(self._buf)

    def len(self) -> int:
        return len(self._buf)

    def _need(self, n: int):
        if self._pos + n > len(self._buf):
            raise EOFError(
                f"Message truncated: need {n} bytes at pos {self._pos}, "
                f"have {len(self._buf) - self._pos}"
            )

    def _u8(self) -> int:
        self._need(1)
        v = self._buf[self._pos]
        self._pos += 1
        return v

    def _u16(self) -> int:
        self._need(2)
        (v,) = struct.unpack_from("<H", self._buf, self._pos)
        self._pos += 2
        return v

    def _u32(self) -> int:
        self._need(4)
        (v,) = struct.unpack_from("<I", self._buf, self._pos)
        self._pos += 4
        return v

    def _u64(self) -> int:
        self._need(8)
        (v,) = struct.unpack_from("<Q", self._buf, self._pos)
        self._pos += 8
        return v

    def _bytes(self, n: int) -> bytes:
        self._need(n)
        v = bytes(self._buf[self._pos : self._pos + n])
        self._pos += n
        return v

    def _read_canary(self, expected: MessageType):
        ty = MessageType(self._u8())
        if ty != expected:
            raise ValueError(f"Type mismatch: expected {expected.name}, got {ty.name}")

    def read_typed(self, ty: MessageType, **_) -> Any:
        match ty:
            case MessageType.BOOL:
                return self.read_bool()
            case MessageType.BYTE:
                return self.read_byte()
            case MessageType.CHAR:
                return self.read_char()
            case MessageType.WORD:
                return self.read_word()
            case MessageType.SHORT:
                return self.read_short()
            case MessageType.DWORD:
                return self.read_dword()
            case MessageType.INT:
                return self.read_int()
            case MessageType.DWORD64:
                return self.read_dword64()
            case MessageType.INT64:
                return self.read_int64()
            case MessageType.FLOAT:
                return self.read_float()
            case MessageType.DOUBLE:
                return self.read_double()
            case MessageType.RESREF:
                return self.read_resref()
            case MessageType.STRING:
                return self.read_str()
            case MessageType.VOIDPTR:
                return self.read_voidptr()
            case MessageType.JSON:
                return self.read_json()
            case MessageType.OBJECT_ID:
                return self.read_object_id()
            case MessageType.LOCSTRING:
                return self.read_locstr()
            case _:
                raise NotImplementedError(ty)

    def read_bool(self, **_) -> bool:
        self._read_canary(MessageType.BOOL)
        return bool(self._u8() & 1)

    def read_byte(self, **_) -> int:
        self._read_canary(MessageType.BYTE)
        return self._u8()

    def read_char(self, **_) -> int:
        self._read_canary(MessageType.CHAR)
        v = self._u8()
        return v if v < 128 else v - 256

    def read_word(self, **_) -> int:
        self._read_canary(MessageType.WORD)
        return self._u16()

    def read_short(self, **_) -> int:
        self._read_canary(MessageType.SHORT)
        self._need(2)
        (v,) = struct.unpack_from("<h", self._buf, self._pos)
        self._pos += 2
        return v

    def read_dword(self, **_) -> int:
        self._read_canary(MessageType.DWORD)
        return self._u32()

    def read_int(self, **_) -> int:
        self._read_canary(MessageType.INT)
        self._need(4)
        (v,) = struct.unpack_from("<i", self._buf, self._pos)
        self._pos += 4
        return v

    def read_dword64(self, **_) -> int:
        self._read_canary(MessageType.DWORD64)
        return self._u64()

    def read_int64(self, **_) -> int:
        self._read_canary(MessageType.INT64)
        self._need(8)
        (v,) = struct.unpack_from("<q", self._buf, self._pos)
        self._pos += 8
        return v

    def read_float(self, **_) -> float:
        self._read_canary(MessageType.FLOAT)
        self._need(4)
        (v,) = struct.unpack_from("<f", self._buf, self._pos)
        self._pos += 4
        return v

    # Server already clamped; receive the full-precision float directly.
    def read_float_lim(self, mn: float, mx: float, **_) -> float:
        self._read_canary(MessageType.FLOAT)
        return self.read_float()

    def read_double(self, **_) -> float:
        self._read_canary(MessageType.DOUBLE)
        self._need(8)
        (v,) = struct.unpack_from("<d", self._buf, self._pos)
        self._pos += 8
        return v

    def read_double_lim(self, mn: float, mx: float, **_) -> float:
        self._read_canary(MessageType.DOUBLE)
        return self.read_double()

    def read_resref(self, **_) -> str:
        self._read_canary(MessageType.RESREF)
        slen = self._u8()
        return self._bytes(slen).decode(get_codepage())

    def read_str(self, **_) -> str:
        self._read_canary(MessageType.STRING)
        slen = self._u32()
        return self._bytes(slen).decode(get_codepage())

    def read_voidptr(self, **_) -> bytes:
        self._read_canary(MessageType.VOIDPTR)
        slen = self._u32()
        return self._bytes(slen)

    def read_json(self, **_):
        self._read_canary(MessageType.JSON)
        return json.loads(self.read_str())

    def read_object_id(self, **_) -> int:
        self._read_canary(MessageType.OBJECT_ID)
        return self._u32()

    def read_locstr(self, **_) -> LocStr:
        self._read_canary(MessageType.LOCSTRING)
        is_strref = self._u8()
        if is_strref:
            gender = Gender(self._u8())
            strref = self._u32()
            return self.context.tlk(strref, gender=gender)
        slen = self._u32()
        text = self._bytes(slen).decode(get_codepage())
        return LocStr(text)


class Writer:
    """
    Serialises the WSNetLayer wire format.

    Call getvalue() to retrieve the fully assembled bytes to send.
    The routing prefix is NOT added here; the caller is responsible.
    """

    def __init__(self, context: Context):
        self.context = context
        self._buf = bytearray()

    def getvalue(self) -> bytes:
        return bytes(self._buf)

    def _u8(self, v: int):
        self._buf.append(v & 0xFF)

    def _u16(self, v: int):
        self._buf += struct.pack("<H", v & 0xFFFF)

    def _u32(self, v: int):
        self._buf += struct.pack("<I", v & 0xFFFFFFFF)

    def _u64(self, v: int):
        self._buf += struct.pack("<Q", v & 0xFFFFFFFFFFFFFFFF)

    def _write_canary(self, ty: MessageType):
        self._u8(ty.value)

    def write_typed(self, val: Any, ty: MessageType, **_) -> None:
        match ty:
            case MessageType.BOOL:
                return self.write_bool(val)
            case MessageType.BYTE:
                return self.write_byte(val)
            case MessageType.CHAR:
                return self.write_char(val)
            case MessageType.WORD:
                return self.write_word(val)
            case MessageType.SHORT:
                return self.write_short(val)
            case MessageType.DWORD:
                return self.write_dword(val)
            case MessageType.INT:
                return self.write_int(val)
            case MessageType.DWORD64:
                return self.write_dword64(val)
            case MessageType.INT64:
                return self.write_int64(val)
            case MessageType.FLOAT:
                return self.write_float(val)
            case MessageType.DOUBLE:
                return self.write_double(val)
            case MessageType.RESREF:
                return self.write_resref(val)
            case MessageType.STRING:
                return self.write_str(val)
            case MessageType.VOIDPTR:
                return self.write_voidptr(val)
            case MessageType.JSON:
                return self.write_json(val)
            case MessageType.OBJECT_ID:
                return self.write_object_id(val)
            case MessageType.LOCSTRING:
                return self.write_locstr(val)
            case _:
                raise NotImplementedError(ty)

    def write_bool(self, value: bool, **_):
        self._write_canary(MessageType.BOOL)
        self._u8(1 if value else 0)

    def write_byte(self, value: int, **_):
        self._write_canary(MessageType.BYTE)
        self._u8(value)

    def write_char(self, value: int, **_):
        self._write_canary(MessageType.CHAR)
        self._u8(value & 0xFF)

    def write_word(self, value: int, **_):
        self._write_canary(MessageType.WORD)
        self._u16(value)

    def write_short(self, value: int, **_):
        self._write_canary(MessageType.SHORT)
        self._buf += struct.pack("<h", value)

    def write_dword(self, value: int, **_):
        self._write_canary(MessageType.DWORD)
        self._u32(value)

    def write_int(self, value: int, **_):
        self._write_canary(MessageType.INT)
        self._buf += struct.pack("<i", value)

    def write_dword64(self, value: int, **_):
        self._write_canary(MessageType.DWORD64)
        self._u64(value)

    def write_int64(self, value: int, **_):
        self._write_canary(MessageType.INT64)
        self._buf += struct.pack("<q", value)

    def write_float(self, value: float, **_):
        self._write_canary(MessageType.FLOAT)
        self._buf += struct.pack("<f", value)

    # Ranged: clamp to [mn, mx] before writing; full IEEE 754 on wire.
    def write_float_lim(self, value: float, mn: float, mx: float, **_):
        self._write_canary(MessageType.FLOAT)
        self.write_float(max(mn, min(mx, value)))

    def write_double(self, value: float, **_):
        self._write_canary(MessageType.DOUBLE)
        self._buf += struct.pack("<d", value)

    def write_double_lim(self, value: float, mn: float, mx: float, **_):
        self._write_canary(MessageType.DOUBLE)
        self.write_double(max(mn, min(mx, value)))

    def write_resref(self, value: str, **_):
        self._write_canary(MessageType.RESREF)
        encoded = value.encode(get_codepage())
        assert len(encoded) <= 16, f"ResRef too long: {value!r}"
        self._u8(len(encoded))
        self._buf += encoded

    def write_str(self, value: str, **_):
        self._write_canary(MessageType.STRING)
        encoded = value.encode(get_codepage())
        self._u32(len(encoded))
        self._buf += encoded

    def write_voidptr(self, value: bytes, **_):
        self._write_canary(MessageType.VOIDPTR)
        assert isinstance(value, (bytes, bytearray))
        self._u32(len(value))
        self._buf += value

    def write_json(self, value, **_):
        self._write_canary(MessageType.JSON)
        self.write_str(json.dumps(value))

    def write_object_id(self, value: int, **_):
        self._write_canary(MessageType.OBJECT_ID)
        self._u32(value)

    def write_locstr(self, value: "LocStr | str | int", **_):
        self._write_canary(MessageType.LOCSTRING)
        if isinstance(value, LocStr) and value.str_ref != STRREF_NONE:
            self._u8(1)  # is_strref
            self._u8(value.gender.value)
            self._u32(value.str_ref)
        elif isinstance(value, str):
            self._u8(0)  # is_strref = false
            self.write_str(value)
        elif isinstance(value, int):
            self._u8(1)  # is_strref
            self._u8(Gender.MALE.value)
            self._u32(value)
        else:
            raise NotImplementedError(type(value))
