"""Language-agnostic models for the codegen pipeline.

These replace GDScript-specific render objects (TypeRender, ClassRender,
MessageRenderContext) with a clean intermediate representation that any
language backend can consume.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum as StdlibEnum
from typing import Any

from nwn_message.message import (
    BuildType,
    Direction,
    MessageType,
    QuantFloat,
    RangeFloat,
    SizePrefix,
    TwoDARowCountHint,
)


class FieldKind(StdlibEnum):
    """Language-agnostic classification of a serialised field."""

    PRIMITIVE = "primitive"
    ENUM = "enum"
    DATACLASS = "dataclass"
    BYTES = "bytes"
    LOCSTRING = "locstring"
    TUPLE = "tuple"
    LIST = "list"
    TAGGED = "tagged"
    BITMASK_LIST = "bitmask_list"


@dataclass(slots=True)
class ConditionInfo:
    """A single conditional guard for a field, language-agnostic.

    ``op`` is one of ``"eq"``, ``"ne"``, ``"gt"``, ``"flag"``, ``"in"``,
    ``"not_in"``, ``"twoda"``, ``"build"``, ``"not_build"``.
    """

    op: str
    field: str
    value: Any


@dataclass(slots=True)
class TaggedVariantRef:
    """One variant in a tagged union, language-agnostic."""

    key: str  # string representation of the discriminator key
    field: AgnosticField  # body field tree for this variant


@dataclass(slots=True)
class AgnosticField:
    """Complete description of one message- or dataclass-field.

    This is the language-agnostic replacement for ``TypeRender``.  Every
    language backend consumes this tree to emit its own read/write code.
    """

    # -- identity -----------------------------------------------------------
    name: str  # original Python field name
    kind: FieldKind

    # -- wire metadata ------------------------------------------------------
    wire_type: MessageType | None = None
    bits: int | None = None
    float_bits: QuantFloat | RangeFloat | None = None
    size_hint: Any | None = None  # one of the ``SizeHint`` subclasses
    bool_prefix: bool = False
    conditionals: list[ConditionInfo] = field(default_factory=list)
    build_type: BuildType | None = None

    # -- type reference for shared / external types -------------------------
    # Python qualname, e.g. ``"nwn_net.net_types.Vec3"`` or
    # ``"AreaVisualEffect.VisualTransformData"``.  The backend maps this to
    # its own naming convention.
    type_ref: str | None = None

    # -- compound fields ----------------------------------------------------
    element: AgnosticField | None = None  # list / tuple element
    elements: list[AgnosticField] | None = None  # tuple element list

    # -- tagged union -------------------------------------------------------
    tagged_variants: list[TaggedVariantRef] | None = None
    tagged_discriminator_type: MessageType | None = None
    tagged_discriminator_bits: int | None = None
    tagged_twoda_field: str | None = None
    tagged_twoda_name: str | None = None
    tagged_twoda_column: str | None = None

    # -- bitmask-conditioned list -------------------------------------------
    bitmask_element: AgnosticField | None = None
    bitmask_size_prefix: SizePrefix | None = None
    bitmask_max_slots: int | str | TwoDARowCountHint | None = None
    bitmask_bit_count: int | str | TwoDARowCountHint | None = None


@dataclass(slots=True)
class EnumDef:
    """Language-agnostic enum definition."""

    name: str  # ``_qualname(t)`` e.g. ``"nwn_net.messages.area.AreaWeather.AreaWeatherType"``
    py_type: type  # original Python enum type, for naming
    values: list[tuple[str, int]]


@dataclass(slots=True)
class HelperClass:
    """Language-agnostic inner dataclass definition."""

    name: str  # ``_qualname(t)`` e.g. ``"nwn_net.messages.area.AreaVisualEffect.VisualTransformData"``
    py_type: type  # original Python dataclass type, for naming
    fields: list[AgnosticField]
    custom_io: bool = False


@dataclass(slots=True)
class ResolvedMessage:
    """Completely resolved message ready for rendering.

    This replaces ``MessageRenderContext`` and ``ClassRender``.  A per-language
    backend receives this and emits source code.
    """

    source_class: str
    source_module: str
    major: int
    minor: int
    direction: Direction
    enums: list[EnumDef] = field(default_factory=list)
    helpers: list[HelperClass] = field(default_factory=list)
    fields: list[AgnosticField] = field(default_factory=list)
    custom_io: bool = False


@dataclass(slots=True)
class TypeRegistry:
    """Language-agnostic shared/global type registry.

    Maps Python types to their Python qualnames.  Backends use this to
    generate appropriate type references / imports.
    """

    shared_types: dict[type, str] = field(default_factory=dict)
    shared_enums: dict[type, str] = field(default_factory=dict)

    def get(self, cls: type) -> str | None:
        return self.shared_types.get(cls) or self.shared_enums.get(cls)

    def has_type(self, cls: type) -> bool:
        return cls in self.shared_types

    def has_enum(self, cls: type) -> bool:
        return cls in self.shared_enums
