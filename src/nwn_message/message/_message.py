from __future__ import annotations

import logging
import struct
from dataclasses import is_dataclass
from enum import Enum
from typing import Annotated, Any, ClassVar, Self, Type, get_args, get_origin

from nwn_message.context import Context
from nwn_message.errors import ReadOverrunError, UnknownHeaderError
from nwn_message.types import LocStr

from ._annotation import (
    BuildSizeHint,
    ComputedAddSizeHint,
    ComputedMultiplySizeHint,
    FixedSizeHint,
    MessageType,
    SizePrefix,
    Tagged,
    TwoDARowCountHint,
    TwoDATagged,
    validate_annotation,
)
from ._io import Reader, Writer

logger = logging.getLogger(__name__)


def _resolve_bitmask_valueish(
    value: int | str | TwoDARowCountHint, context: Context
) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if value not in context.fields:
            raise ValueError(f"Field {value} not in context")
        return int(context.fields[value])
    if isinstance(value, TwoDARowCountHint):
        return context.twoda_row_count(value.twoda_name)
    raise TypeError(f"Unsupported BitmaskConditionedList count value: {value!r}")


class MessagePrefix(Enum):
    PLAYER_CLIENT_TO_SERVER = b"p"
    PLAYER_SERVER_TO_CLIENT = b"P"


class Direction(Enum):
    BOTH = "both"
    C2S = "c2s"
    S2C = "s2c"


_PREFIX_TO_DIRECTION: dict[bytes, Direction] = {
    b"p": Direction.C2S,
    b"P": Direction.S2C,
}


REGISTRY: dict[tuple[int, int, Direction], type[Message]] = {}


class SubMessage:
    """
    SubMessage base class for nested messages split out for convenience.

    Event listeners can subscribe to SubMessage types for less painful handling
    of only the specific sub-events they care about (eg. inside GameObjectUpdate).

    Unlike top-level Message classes, SubMessages are intentionally NOT registered
    in the global message registry. They inherit the parent message's MAJOR/MINOR
    and are distinguished by a discriminator byte or field during parsing.
    """


class Message:
    prefix: MessagePrefix
    MAJOR: ClassVar[int]
    MINOR: ClassVar[int]
    DIRECTION: ClassVar[Direction] = Direction.BOTH

    def __init_subclass__(cls) -> None:
        if cls.DIRECTION == Direction.BOTH:
            for d in (Direction.C2S, Direction.S2C):
                if (cls.MAJOR, cls.MINOR, d) in REGISTRY:
                    raise ValueError(
                        f"Duplicate message class for {cls.MAJOR:02x} "
                        f"{cls.MINOR:02x} ({d.value})"
                    )
                REGISTRY[cls.MAJOR, cls.MINOR, d] = cls
        else:
            if (cls.MAJOR, cls.MINOR, cls.DIRECTION) in REGISTRY:
                raise ValueError(
                    f"Duplicate message class for {cls.MAJOR:02x} "
                    f"{cls.MINOR:02x} ({cls.DIRECTION.value})"
                )
            REGISTRY[cls.MAJOR, cls.MINOR, cls.DIRECTION] = cls

        return super().__init_subclass__()

    def iter_submessages(self) -> tuple:
        """Return nested submessages to emit after top-level dispatch."""
        return ()

    @classmethod
    def parse(cls, data: bytes | bytearray | memoryview, context: Context) -> Self:
        with Reader(data, context) as reader:
            if hasattr(cls, "read") and callable(fn := getattr(cls, "read")):
                obj = fn(reader, context)
            else:
                obj = read_dataclass(cls, reader, context)

            if not reader.at_end:
                logger.warning(
                    f"{cls.__name__}: not fully read; {reader.len() - reader.tell()} bytes remain"
                )

        assert isinstance(obj, cls)
        return obj

    def dump(self, prefix: MessagePrefix, context: Context) -> bytes:
        if self.DIRECTION != Direction.BOTH:
            expected = _PREFIX_TO_DIRECTION.get(prefix.value)
            if expected != self.DIRECTION:
                logger.warning(
                    f"{self.__class__.__name__}: dumping with {prefix} but message "
                    f"direction is {self.DIRECTION.value}"
                )
        out = Writer(context)
        if hasattr(self, "write") and callable(fn := getattr(self, "write")):
            fn(out, context)
        else:
            write_dataclass(self, out, context)

        return (
            prefix.value + struct.pack("<BB", self.MAJOR, self.MINOR) + out.getvalue()
        )


def read(data: bytes | bytearray | memoryview, context: Context) -> Message:
    """
    Attempts to read a message from the given data.
    This is a shorthand to look up the correct message type
    and call its parse method.

    Args:
        data: The raw bytes of the message; including the prefix, major,
            and minor bytes.

    Returns:
        An instance of the appropriate Message subclass.

    Raises:
        UnknownHeaderError if the message type is unknown.
        ReadOverrunError if parsing fails because too much data was read.
        Any other exception is passed on.
    """

    try:
        prefix = data[0:1]
        major = data[1]
        minor = data[2]
        direction = _PREFIX_TO_DIRECTION.get(prefix, Direction.C2S)
        message_cls = REGISTRY[(major, minor, direction)]
    except KeyError as e:
        raise UnknownHeaderError(f"Unknown message: {data[0:3]}") from e

    try:
        obj = message_cls.parse(data[3:], context)
        obj.prefix = MessagePrefix(prefix)
        return obj
    except struct.error as e:
        raise ReadOverrunError(f"Failed to read message: {e}") from e


Bool = Annotated[bool, MessageType.BOOL]
Byte = Annotated[int, MessageType.BYTE]
Char = Annotated[int, MessageType.CHAR]
Word = Annotated[int, MessageType.WORD]
Short = Annotated[int, MessageType.SHORT]
Dword = Annotated[int, MessageType.DWORD]
Int = Annotated[int, MessageType.INT]
Dword64 = Annotated[int, MessageType.DWORD64]
Int64 = Annotated[int, MessageType.INT64]
Float = Annotated[float, MessageType.FLOAT]
Double = Annotated[float, MessageType.DOUBLE]
ResRef = Annotated[str, MessageType.RESREF]
String = Annotated[str, MessageType.STRING]
Void = Annotated[bytes, MessageType.VOIDPTR, SizePrefix.DWORD]
# [TODO] Json = Annotated[str, MessageType.JSON]


ObjectId = Annotated[int, MessageType.OBJECT_ID]
PlayerId = Annotated[int, MessageType.DWORD]
SHA1 = Annotated[bytes, MessageType.VOIDPTR, FixedSizeHint(20)]

Vec3 = tuple[Float, Float, Float]
Vec3i = tuple[Int, Int, Int]


def read_annotated_value(ty, rd: Reader, context: Context, if_missing: Any) -> Any:
    anno = validate_annotation(ty)

    for cond in anno.conditionals:
        if not cond.cb(context):
            return if_missing

    if anno.bool_prefix:
        if not rd.read_bool():
            return if_missing

    effective_message_type = anno.message_type
    if anno.build_type is not None:
        build, patch, postfix = anno.build_type.if_build
        if context.satisfies(build, patch, postfix):
            effective_message_type = anno.build_type.then
        else:
            effective_message_type = anno.build_type.default

    if isinstance(anno.size_hint, SizePrefix):
        size_hint_value = rd.read_typed(anno.size_hint.value)
    elif isinstance(anno.size_hint, FixedSizeHint):
        size_hint_value = anno.size_hint.size
    elif isinstance(anno.size_hint, TwoDARowCountHint):
        size_hint_value = context.twoda_row_count(anno.size_hint.twoda_name)
    elif isinstance(anno.size_hint, BuildSizeHint):
        sh = anno.size_hint
        size_hint_value = (
            sh.new if context.satisfies(sh.build, sh.patch, sh.postfix) else sh.old
        )
    elif isinstance(anno.size_hint, ComputedMultiplySizeHint):
        if (
            anno.size_hint.field1 not in context.fields
            or anno.size_hint.field2 not in context.fields
        ):
            raise ValueError(
                f"Fields {anno.size_hint.field1} and {anno.size_hint.field2} "
                "must be present in context for ComputedMultiplySizeHint"
            )

        size_hint_value = (
            context.fields[anno.size_hint.field1]
            * context.fields[anno.size_hint.field2]
        )
    elif isinstance(anno.size_hint, ComputedAddSizeHint):
        if (
            anno.size_hint.field1 not in context.fields
            or anno.size_hint.field2 not in context.fields
        ):
            raise ValueError(
                f"Fields {anno.size_hint.field1} and {anno.size_hint.field2} "
                "must be present in context for ComputedAddSizeHint"
            )

        size_hint_value = (
            context.fields[anno.size_hint.field1]
            + context.fields[anno.size_hint.field2]
        )
    else:
        size_hint_value = None

    if anno.bitmask_conditioned_list is not None:
        max_slots = _resolve_bitmask_valueish(
            anno.bitmask_conditioned_list.max_slots, context
        )
        flags = rd.read_typed(anno.bitmask_conditioned_list.size_prefix.value)
        result = []
        nested_type = get_args(anno.real_type)[0]
        for i in range(max_slots):
            if flags & (1 << i):
                result.append(
                    read_annotated_value(nested_type, rd, context, if_missing=None)
                )
            else:
                result.append(None)
        return result

    if anno.tagged is not None:
        if isinstance(anno.tagged, TwoDATagged):
            if anno.tagged.field not in context.fields:
                raise ValueError(
                    f"Field {anno.tagged.field} must be present in context for {ty}"
                )
            raw = int(
                context.twoda(
                    anno.tagged.twoda,
                    context.fields[anno.tagged.field],
                    anno.tagged.column,
                )
            )
        else:
            raw = rd.read_typed(anno.tagged.discriminator_type)
        cls = anno.tagged.lut.get(raw)
        if cls is None:
            raise ValueError(f"Unknown tagged discriminator {raw} for {ty}")
        return read_annotated_value(cls, rd, context, if_missing=None)

    if get_origin(anno.real_type) is tuple:
        args = get_args(anno.real_type)
        return tuple(
            read_annotated_value(t, rd, context, if_missing=None) for t in args
        )

    if isinstance(anno.real_type, type) and issubclass(anno.real_type, Enum):
        if effective_message_type is None:
            raise NotImplementedError(f"Enum without message type: {ty}")
        raw = rd.read_typed(effective_message_type)
        return anno.real_type(raw)

    if get_origin(anno.real_type) is list:
        assert size_hint_value is not None
        nested_type = get_args(anno.real_type)[0]
        return [
            read_annotated_value(nested_type, rd, context, if_missing=None)
            for _ in range(size_hint_value)
        ]

    if is_dataclass(anno.real_type):
        return read_dataclass(anno.real_type, rd, context)

    if anno.real_type is LocStr:
        return rd.read_locstr()

    if anno.real_type is bytes:
        return rd.read_voidptr()

    if effective_message_type is None:
        raise NotImplementedError(f"No message type specified for {ty}")

    return rd.read_typed(effective_message_type)


def write_annotated_value(val: Any, ty: Type, wr: Writer, context: Context) -> None:
    anno = validate_annotation(ty)

    for cond in anno.conditionals:
        if not cond.cb(context):
            return

    if anno.bool_prefix:
        has_value = bool(val)
        wr.write_bool(has_value)
        if not has_value:
            return

    effective_message_type = anno.message_type
    if anno.build_type is not None:
        build, patch, postfix = anno.build_type.if_build
        if context.satisfies(build, patch, postfix):
            effective_message_type = anno.build_type.then
        else:
            effective_message_type = anno.build_type.default

    size_hint_value = None
    if isinstance(anno.size_hint, SizePrefix):
        if val is None:
            raise ValueError(f"Size-prefixed field cannot be None: {ty}")
        size_hint_value = len(val)
        wr.write_typed(size_hint_value, anno.size_hint.value)
    elif isinstance(anno.size_hint, FixedSizeHint):
        size_hint_value = anno.size_hint.size
        if val is None:
            raise ValueError(f"Fixed-size field cannot be None: {ty}")
        assert (
            len(val) == size_hint_value
        ), f"Expected fixed size {size_hint_value}, got {len(val)}"
    elif isinstance(anno.size_hint, TwoDARowCountHint):
        size_hint_value = context.twoda_row_count(anno.size_hint.twoda_name)
        if val is None:
            raise ValueError(f"TwoDA-row-count-sized field cannot be None: {ty}")
        assert (
            len(val) == size_hint_value
        ), f"Expected TwoDA row count {size_hint_value}, got {len(val)}"
    elif isinstance(anno.size_hint, BuildSizeHint):
        sh = anno.size_hint
        size_hint_value = (
            sh.new if context.satisfies(sh.build, sh.patch, sh.postfix) else sh.old
        )
        if val is None:
            raise ValueError(f"Build-size-hinted field cannot be None: {ty}")
        assert (
            len(val) == size_hint_value
        ), f"Expected build-dependent size {size_hint_value}, got {len(val)}"
    elif isinstance(anno.size_hint, (ComputedMultiplySizeHint, ComputedAddSizeHint)):
        if (
            anno.size_hint.field1 not in context.fields
            or anno.size_hint.field2 not in context.fields
        ):
            raise ValueError(
                f"Fields {anno.size_hint.field1} and {anno.size_hint.field2} "
                f"must be present in context for {type(anno.size_hint).__name__}"
            )
        size_hint_value = None

    if anno.bitmask_conditioned_list is not None:
        max_slots = _resolve_bitmask_valueish(
            anno.bitmask_conditioned_list.max_slots, context
        )
        if len(val) > max_slots:
            raise ValueError(
                f"BitmaskConditionedList has {len(val)} entries, exceeds max_slots {max_slots}"
            )
        flags = 0
        for i in range(max_slots):
            item = val[i] if i < len(val) else None
            if item is not None:
                flags |= 1 << i
        wr.write_typed(flags, anno.bitmask_conditioned_list.size_prefix.value)
        nested_type = get_args(anno.real_type)[0]
        for i in range(max_slots):
            item = val[i] if i < len(val) else None
            if item is not None:
                write_annotated_value(item, nested_type, wr, context)
        return

    if anno.tagged is not None:
        # Reverse-lookup: find discriminator key from the value's type
        val_type = type(val)
        match = next(
            ((k, v) for k, v in anno.tagged.lut.items() if v is val_type),
            None,
        )
        if match is None:
            raise ValueError(
                f"Cannot write tagged union: type {val_type} not in lut for {ty}"
            )
        key, tagged_cls = match
        if isinstance(anno.tagged, Tagged):
            wr.write_typed(key, anno.tagged.discriminator_type)
        write_annotated_value(val, tagged_cls, wr, context)
        return

    if get_origin(anno.real_type) is tuple:
        args = get_args(anno.real_type)
        assert len(args) == len(val)
        for v, nested_type in zip(val, args):
            write_annotated_value(v, nested_type, wr, context)
        return

    if isinstance(anno.real_type, type) and issubclass(anno.real_type, Enum):
        if effective_message_type is None:
            raise NotImplementedError(f"Enum without message type: {ty}")
        wr.write_typed(val.value, effective_message_type)
        return

    if get_origin(anno.real_type) is list:
        nested_type = get_args(anno.real_type)[0]
        for item in val:
            write_annotated_value(item, nested_type, wr, context)
        return

    if is_dataclass(anno.real_type):
        write_dataclass(val, wr, context)
        return

    if anno.real_type is LocStr:
        wr.write_locstr(val)
        return

    if anno.real_type is bytes:
        if size_hint_value is None:
            raise NotImplementedError(f"VOIDPtr without size hint: {ty}")
        wr.write_voidptr(val)
        return

    if effective_message_type is None:
        raise NotImplementedError(f"No message type specified for {ty}")

    wr.write_typed(val, effective_message_type)


def read_dataclass(cls, rd: Reader, context: Context) -> Any:
    if "read" in cls.__dict__:
        return cls.read(rd, context)

    fields = {}
    for k, v in cls.__dataclass_fields__.items():
        t = v.type
        context.fields = fields
        try:
            if_missing = getattr(cls, k, None)
            fields[k] = read_annotated_value(t, rd, context, if_missing=if_missing)
        except Exception as e:
            logger.error(f"Error reading field {k} in {cls.__name__}: {e}")
            raise

        value_repr = repr(fields[k])
        value_repr = value_repr if len(value_repr) <= 20 else value_repr[:20] + "..."

    return cls(**fields)


def write_dataclass(obj: Any, wr: Writer, context: Context) -> None:
    if hasattr(obj, "write") and callable(fn := getattr(obj, "write")):
        fn(wr, context)
        return

    fields = {}
    for k, v in obj.__dataclass_fields__.items():
        t = v.type
        field_val = getattr(obj, k)
        context.fields = fields
        try:
            write_annotated_value(field_val, t, wr, context)
        except Exception as e:
            logger.error(f"Error writing field {k} in {type(obj).__name__}: {e}")
            raise
        fields[k] = field_val
        continue
