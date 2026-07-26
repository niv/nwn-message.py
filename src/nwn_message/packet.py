from __future__ import annotations

import logging
import struct
from dataclasses import dataclass, fields
from typing import ClassVar, Self

from nwn.environ import get_codepage

from .context import Context
from .errors import ReadOverrunError, UnknownHeaderError

logger = logging.getLogger(__name__)

_REGISTRY: dict[bytes, type[Packet]] = {}


class PacketReader:
    """Simple sequential reader over raw bytes for packet parsing."""

    __slots__ = ("_data", "_pos")

    def __init__(self, data: bytes | bytearray | memoryview) -> None:
        self._data = memoryview(data) if not isinstance(data, memoryview) else data
        self._pos = 0

    @property
    def at_end(self) -> bool:
        return self._pos >= len(self._data)

    @property
    def remaining(self) -> int:
        return len(self._data) - self._pos

    def read_u8(self) -> int:
        (val,) = struct.unpack_from("B", self._data, self._pos)
        self._pos += 1
        return val

    def read_u16(self) -> int:
        (val,) = struct.unpack_from("<H", self._data, self._pos)
        self._pos += 2
        return val

    def read_i16(self) -> int:
        (val,) = struct.unpack_from("<h", self._data, self._pos)
        self._pos += 2
        return val

    def read_u32(self) -> int:
        (val,) = struct.unpack_from("<I", self._data, self._pos)
        self._pos += 4
        return val

    def read_i32(self) -> int:
        (val,) = struct.unpack_from("<i", self._data, self._pos)
        self._pos += 4
        return val

    def read_u64(self) -> int:
        (val,) = struct.unpack_from("<Q", self._data, self._pos)
        self._pos += 8
        return val

    def read_i64(self) -> int:
        (val,) = struct.unpack_from("<q", self._data, self._pos)
        self._pos += 8
        return val

    def read_bytes(self, n: int) -> bytes:
        val = bytes(self._data[self._pos : self._pos + n])
        self._pos += n
        return val

    def read_lp8(self) -> bytes:
        return self.read_bytes(self.read_u8())

    def read_lp16(self) -> bytes:
        return self.read_bytes(self.read_u16())

    def read_lp32(self) -> bytes:
        return self.read_bytes(self.read_u32())


class PacketWriter:
    """Simple sequential writer for packet serialization."""

    __slots__ = ("_buf",)

    def __init__(self, head: bytes = b"") -> None:
        self._buf = bytearray(head)

    def write_u8(self, val: int) -> None:
        self._buf += struct.pack("B", val)

    def write_u16(self, val: int) -> None:
        self._buf += struct.pack("<H", val)

    def write_i16(self, val: int) -> None:
        self._buf += struct.pack("<h", val)

    def write_u32(self, val: int) -> None:
        self._buf += struct.pack("<I", val)

    def write_i32(self, val: int) -> None:
        self._buf += struct.pack("<i", val)

    def write_u64(self, val: int) -> None:
        self._buf += struct.pack("<Q", val)

    def write_i64(self, val: int) -> None:
        self._buf += struct.pack("<q", val)

    def write_bytes(self, data: bytes) -> None:
        self._buf += data

    def write_lp8(self, data: bytes) -> None:
        self._buf += struct.pack("B", len(data))
        self._buf += data

    def write_lp16(self, data: bytes) -> None:
        self._buf += struct.pack("<H", len(data))
        self._buf += data

    def write_lp32(self, data: bytes) -> None:
        self._buf += struct.pack("<I", len(data))
        self._buf += data

    def write_str_lp8(self, s: str) -> None:
        self.write_lp8(s.encode(get_codepage()))

    def write_str_lp16(self, s: str) -> None:
        self.write_lp16(s.encode(get_codepage()))

    def write_str_lp32(self, s: str) -> None:
        self.write_lp32(s.encode(get_codepage()))

    def getvalue(self) -> bytes:
        return bytes(self._buf)


@dataclass
class Packet:
    HEAD: ClassVar[bytes]

    def __str__(self) -> str:
        return repr(self)

    def __init_subclass__(cls, head: bytes) -> None:
        super().__init_subclass__()
        cls.HEAD = head
        if head in _REGISTRY:
            raise ValueError(f"Duplicate packet head registration: {head!r}")
        _REGISTRY[cls.HEAD] = cls

    @classmethod
    def parse(cls, _reader: PacketReader, _context: Context) -> Self:
        # This is a base implementation; subclasses with fields must override it
        if len(fields(cls)) == 0:
            return cls()
        raise NotImplementedError(f"Packet {cls.HEAD} must implement parse()")

    def dump(self, _context: Context) -> bytes:
        # This is a base implementation; subclasses with fields must override it
        if len(fields(self)) == 0:
            return self.HEAD
        raise NotImplementedError(f"Packet {self.HEAD} must implement dump()")


def read(data: bytes | bytearray | memoryview, context: Context) -> Packet:
    """
    Read the given bytes as a Packet; tries to identify and parse it.

    Returns:
        An instance of the appropriate Packet subclass.

    Raises:
        UnknownHeaderError if the packet type is unknown.
        ReadOverrunError if parsing fails because too much data was read.
    """
    raw = bytes(data) if not isinstance(data, bytes) else data
    for head, packet_cls in _REGISTRY.items():
        if raw.startswith(head):
            reader = PacketReader(raw[len(head) :])
            try:
                result = packet_cls.parse(reader, context)
            except struct.error as e:
                raise ReadOverrunError from e
            if not reader.at_end:
                logger.warning(
                    "%s: %d byte(s) not consumed after parse",
                    packet_cls.__name__,
                    reader.remaining,
                )
            return result
    raise UnknownHeaderError(f"Unknown packet head: {raw[:4]!r}")
