from dataclasses import dataclass
from enum import Enum
from types import NoneType
from typing import Annotated, Any, Callable, NamedTuple, Union, get_args, get_origin

from ..context import Context
from ._io import MessageType


@dataclass
class FixedSizeHint:
    """
    A fixed size hint for lists, where the size is known ahead of time and
    static.
    """

    size: int


@dataclass
class ComputedMultiplySizeHint:
    """
    A computed size hint for lists, where the size is determined by multiplying
    the values of two preceding fields. This is useful for cases where the size of a list is
    not fixed, but can be calculated based on other fields in the message.

    Computed data is NOT written out to the message; this is just a read hint.
    """

    field1: str
    field2: str


@dataclass
class ComputedAddSizeHint:
    """
    A computed size hint for lists, where the size is determined by adding
    the values of two preceding fields. This is useful for cases where the size of a list is
    not fixed, but can be calculated based on other fields in the message.

    Computed data is NOT written out to the message; this is just a read hint.
    """

    field1: str
    field2: str


@dataclass
class TwoDARowCountHint:
    """
    A size hint for lists whose length equals the number of rows in a 2DA file.
    Looks up the row count of `twoda_name`.2da at parse time via context.twoda_row_count().
    """

    twoda_name: str


@dataclass
class BuildSizeHint:
    """
    A build-version-dependent fixed size hint for lists.
    Resolves to `new` when context.satisfies(build, patch, postfix), else `old`.
    """

    new: int
    old: int
    build: int
    patch: int
    postfix: int


@dataclass
class BoolPrefix:
    """
    A boolean prefix for optional types; a preceding boolean indicates whether
    the value is present.

    The bool prefix is consumed and written as part of the field it annotates,
    and is not a separate field in the dataclass.
    """


class SizePrefix(Enum):
    """
    Size prefix for any type that accepts a size prefix.
    """

    BYTE = MessageType.BYTE
    WORD = MessageType.WORD
    INT = MessageType.INT
    DWORD = MessageType.DWORD


@dataclass(frozen=True)
class Bits:
    """
    A bit-constrain modifier that limits the bit width of the type.

    This annotation is currently informational only.

    Behaviour when exceeding the bit width of the underlying type is undefined.
    """

    bits: int


class If:
    """
    Base conditional for message fields.
    Be careful with using this annotation:
    Custom lambdas cannot be codegen'd. If at all possible, use one of
    the specialised subclasses, which can be dealt with correctly in codegen.
    """

    def __init__(self, cb: Callable[[Context], Any]):
        self.cb = cb


class IfFlag(If):
    """
    Only accept this field if a specific flag is set in another field.
    This will only work for fields that preceede this one in the message.
    """

    def __init__(self, field: str, flag: Any):
        super().__init__(lambda context: context.fields[field] & flag)


class IfEq(If):
    """
    Only accept this field if another field equals a specific value.
    This will only work for fields that preceede this one in the message.
    """

    def __init__(self, field: str, eq: Any):
        super().__init__(lambda context: context.fields[field] == eq)


class IfNotEq(If):
    """
    Only accept this field if another field does not equal a specific value.
    This will only work for fields that precede this one in the message.
    """

    def __init__(self, field: str, ne: Any):
        super().__init__(lambda context: context.fields.get(field) != ne)


class IfGt(If):
    """
    Only accept this field if another field is greater than a specific value.
    This will only work for fields that precede this one in the message.
    """

    def __init__(self, field: str, gt: Any):
        super().__init__(
            lambda context: (v := context.fields.get(field)) is not None and v > gt
        )


class IfBuild(If):
    """
    Conditional based on the NWN build version; this is analogous to the native
    nwMsg->Satisfies function group.
    """

    def __init__(self, build: int, patch: int, postfix: int):
        super().__init__(lambda context: context.peer.satisfies(build, patch, postfix))


class IfTwoDA(If):
    """
    Only accept this field if a 2DA lookup on another field matches one of the
    given values.
    """

    def __init__(self, field: str, twoda: str, column: str, values: set[str]):
        super().__init__(
            lambda context: (
                context.twoda(twoda, context.fields[field], column) in values
            )
        )


class IfNotBuild(If):
    """
    Inverse of IfBuild — only accept this field when the server does NOT satisfy
    the given build version (i.e. older clients/servers).
    """

    def __init__(self, build: int, patch: int, postfix: int):
        super().__init__(
            lambda context: not context.peer.satisfies(build, patch, postfix)
        )


class IfIn(If):
    """
    Only accept this field if another field's value is a member of the given set.
    This will only work for fields that precede this one in the message.
    """

    def __init__(self, field: str, values: set):
        super().__init__(lambda context: context.fields.get(field) in values)


class IfNotIn(If):
    """
    Only accept this field if another field's value is NOT a member of the given set.
    This will only work for fields that precede this one in the message.
    """

    def __init__(self, field: str, values: set):
        super().__init__(lambda context: context.fields.get(field) not in values)


@dataclass
class Tagged:
    """
    Tagged-union dispatch: reads a discriminator value using `discriminator_type`,
    then dispatches to the matching dataclass in `lut`.

    The discriminator is consumed and is NOT a field in the dataclass itself.
    Multiple lut keys may map to the same class (shared wire formats).
    """

    discriminator_type: MessageType
    lut: dict[int, Any]


@dataclass
class TwoDATagged:
    """
    Tagged-union dispatch where the discriminator is derived from a 2DA lookup
    of another field, rather than read from the wire.
    """

    field: str
    twoda: str
    column: str
    lut: dict[int, type]


@dataclass(frozen=True)
class BuildType:
    """
    Conditional message type override based on server build.
    """

    default: MessageType
    if_build: tuple[int, int, int]
    then: MessageType


@dataclass(frozen=True)
class QuantFloat:
    """
    Multiplier-quantized float: stored as round(value * multiplier) in `bits` unsigned bits.
    Corresponds to C++ WriteFLOAT(value, MULTIPLIER, PRECISION).
    """

    multiplier: float
    bits: int


@dataclass(frozen=True)
class RangeFloat:
    """
    Range-quantized float: maps [min, max] linearly onto an unsigned `bits`-bit integer.
    Corresponds to C++ WriteFLOAT(value, MIN, MAX, PRECISION).
    """

    min: float
    max: float
    bits: int


@dataclass(frozen=True)
class BitmaskConditionedList:
    """
    A list where presence is controlled by a bitmask (of SizePrefix flags) and
    each set bit indicates an element at that position should be read/written.

    Used for sparse slot patterns like equipped item tags.

    The field value should be a sparse list where index i corresponds to bit i.

    max_slots may be:
    - int: fixed slot count
    - str: name of a previously read field in context.fields
    - TwoDARowCountHint: row count from a 2DA table

    bit_count controls the number of bits used for the bitmap flags.
    This is currently advisory only; omission defaults to the native size.
    """

    element_type: MessageType
    size_prefix: SizePrefix
    max_slots: int | str | TwoDARowCountHint
    bit_count: int | str | TwoDARowCountHint | None = None


class MessageField(NamedTuple):
    # native type, e.g. int, str, dataclass, LocStr, tuple, list, etc
    real_type: type

    message_type: MessageType | None = None

    size_hint: (
        SizePrefix
        | FixedSizeHint
        | ComputedMultiplySizeHint
        | ComputedAddSizeHint
        | TwoDARowCountHint
        | BuildSizeHint
        | None
    ) = None

    # True if this field is only valid if a bool prefix is set true.
    # When READING; the inner type is skipped when the bool prefix is false.
    # When WRITING; the bool prefix is written out if the inner type evaluates
    #   true-ish; this only makes sense for nested dataclasses or similar.
    bool_prefix: bool = False

    # Conditionals are all AND'ed together when evaluating them.
    # Overriding previous conditionals does not remove them, so you can only
    # ever constrain MORE. This is currently fine as the only usecase for this
    # is annotation "inheritance" for prefab types.
    # IMPORTANT: any failing conditional makes the field read return None, even
    #   if the underlying real type does NOT option to None. This is on you, the
    #   message author, to clarify in type hints.
    conditionals: list[If] = []  # list of If*

    # For bitwidth-constrained fields
    # This parameter is informational and not enforced. Exceeding the limits is
    # undefined behaviour.
    bits: int | None = None

    # For compressed float types, the quantization parameters
    # This parameter is informational and not enforced. Exceeding the limits is
    # undefined behaviour.
    float_bits: QuantFloat | RangeFloat | None = None

    # for tagged-union fields; this can either read/write a wire discriminator
    # (Tagged) or derive one from a 2DA indirection (TwoDATagged)
    tagged: Tagged | TwoDATagged | None = None

    # for bitmask-conditioned list fields; enables sparse, fixed-slot encoding
    bitmask_conditioned_list: BitmaskConditionedList | None = None

    # conditionally resolves message_type based on context.satisfies(...)
    build_type: BuildType | None = None


def validate_annotation(annotation: type) -> MessageField:
    """
    Explodes an annotated type into it's real underlying type and
    components.

    If a type is not annotated, returns the type as-is with no metadata.
    """

    if get_origin(annotation) is not Annotated:
        return MessageField(annotation)

    args = get_args(annotation)

    real_type = args[0]
    is_optional = False
    if get_origin(real_type) is Union and NoneType in get_args(real_type):
        real_type = get_args(real_type)[0]
        is_optional = True

    # We parse from the BACK: the last-specified annotation (including when nesting them
    #  overrides all earlier ones. This is useful for annotation inheritance/stacking.
    args = list(reversed(args[1:]))
    message_type = next((a for a in args if isinstance(a, MessageType)), None)
    bool_prefix = next((a for a in args if isinstance(a, BoolPrefix)), None)

    # We cannot have more than one size hint active.
    size_hint = next(
        (
            a
            for a in args
            if isinstance(
                a,
                (
                    FixedSizeHint,
                    SizePrefix,
                    ComputedMultiplySizeHint,
                    ComputedAddSizeHint,
                    TwoDARowCountHint,
                    BuildSizeHint,
                ),
            )
        ),
        None,
    )

    conditionals = [a for a in args if isinstance(a, If)]

    if (conditionals or bool_prefix) and not is_optional:
        # [TODO] this is not super useful yet. Future improvement could be
        # to use the type checker for this (if possible?).
        # For now, we just strip/ignore it.
        ...

    bits = next((a.bits for a in args if isinstance(a, Bits)), None)

    float_bits = next(
        (a for a in args if isinstance(a, (QuantFloat, RangeFloat))), None
    )

    tagged = next((a for a in args if isinstance(a, (Tagged, TwoDATagged))), None)
    build_type = next((a for a in args if isinstance(a, BuildType)), None)
    bitmask_conditioned_list = next(
        (a for a in args if isinstance(a, BitmaskConditionedList)), None
    )

    candidate_message_types = []
    if message_type is not None:
        candidate_message_types.append(message_type)
    if build_type is not None:
        candidate_message_types.extend([build_type.default, build_type.then])

    type_map = {
        str: [MessageType.STRING, MessageType.RESREF],
        int: [
            MessageType.CHAR,
            MessageType.BYTE,
            MessageType.WORD,
            MessageType.SHORT,
            MessageType.DWORD,
            MessageType.INT,
            MessageType.DWORD64,
            MessageType.INT64,
            MessageType.OBJECT_ID,
        ],
        float: [MessageType.FLOAT, MessageType.DOUBLE],
        bool: [MessageType.BOOL],
        bytes: [MessageType.VOIDPTR],
    }

    if (
        isinstance(real_type, type)
        and real_type in type_map
        and any(ty not in type_map[real_type] for ty in candidate_message_types)
    ):
        raise TypeError(f"Type {real_type} invalid {message_type=}")

    if message_type == MessageType.VOIDPTR and size_hint is None:
        raise TypeError(f"VOIDPTR must have SizeHint: {annotation}")

    if real_type is list and size_hint is None and bitmask_conditioned_list is None:
        raise TypeError(
            f"List must have SizeHint or BitmaskConditionedList: {annotation}"
        )

    if float_bits and any(ty != MessageType.FLOAT for ty in candidate_message_types):
        raise TypeError(
            f"Quant/RangeFloat can only be applied to FLOAT fields: {annotation}"
        )

    return MessageField(
        real_type=real_type,
        message_type=message_type,
        size_hint=size_hint,
        bool_prefix=bool_prefix is not None,
        conditionals=conditionals,
        bits=bits,
        float_bits=float_bits,
        tagged=tagged,
        bitmask_conditioned_list=bitmask_conditioned_list,
        build_type=build_type,
    )
