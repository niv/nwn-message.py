"""Walk Python Message types and produce language-agnostic ``ResolvedMessage`` trees.

This is where the heavy lifting happens: validating annotations, resolving
external type references (shared / global registries), collecting helpers
and enums, and producing a tree of ``AgnosticField`` objects that a
per-language backend can render.
"""

from __future__ import annotations

import inspect
from collections import Counter
from dataclasses import fields, is_dataclass
from enum import Enum
from types import UnionType
from typing import Annotated, Any, Union, get_args, get_origin

from nwn_message.message import (
    BuildSizeHint,
    Direction,
    If,
    IfBuild,
    IfEq,
    IfFlag,
    IfGt,
    IfIn,
    IfNotBuild,
    IfNotEq,
    IfNotIn,
    IfTwoDA,
    Message,
    MessageType,
    Tagged,
    TwoDATagged,
    validate_annotation,
)
from nwn_message.types import LocStr

from ._analysis import (
    collect_message_type_dependencies,
    collect_type_dependencies,
    transitive_closure,
)
from ._models import (
    AgnosticField,
    ConditionInfo,
    EnumDef,
    FieldKind,
    HelperClass,
    ResolvedMessage,
    TaggedVariantRef,
    TypeRegistry,
)

# Modules whose types are globally shared across all messages.
GLOBAL_SHARED_MODULES = {"nwn_net.net_types"}

_SUPPORTED_CONDITIONS: tuple[type[If], ...] = (
    IfEq,
    IfNotEq,
    IfFlag,
    IfGt,
    IfIn,
    IfNotIn,
    IfTwoDA,
    IfBuild,
    IfNotBuild,
)

# Errors


class UnsupportedMessageError(RuntimeError):
    pass


# -- registry building (language-agnostic) -----------------------------------


def _qualname(cls: type) -> str:
    return f"{cls.__module__}.{cls.__qualname__}"


def _type_sort_key(t: type) -> tuple:
    return (0 if issubclass(t, Enum) else 1, t.__name__)


def build_global_shared_types(
    all_messages: list[type[Message]],
) -> TypeRegistry | None:
    """Find all types from global shared modules used by any message."""
    global_types: set[type] = set()
    global_enums: set[type[Enum]] = set()

    for msg_cls in all_messages:
        deps = collect_message_type_dependencies(msg_cls)
        for t in deps:
            if t.__module__ in GLOBAL_SHARED_MODULES:
                if isinstance(t, type) and issubclass(t, Enum):
                    global_enums.add(t)
                else:
                    global_types.add(t)

    # Transitive closure.
    all_global_deps: set[type] = set(global_types) | set(global_enums)
    changed = True
    while changed:
        changed = False
        for t in list(all_global_deps):
            if is_dataclass(t):
                for dc_field in fields(t):
                    field_deps = collect_type_dependencies(dc_field.type, set())
                    for dep in field_deps:
                        if (
                            dep.__module__ in GLOBAL_SHARED_MODULES
                            and dep not in all_global_deps
                        ):
                            all_global_deps.add(dep)
                            changed = True
                            if isinstance(dep, type) and issubclass(dep, Enum):
                                global_enums.add(dep)
                            else:
                                global_types.add(dep)

    if not all_global_deps:
        return None

    return TypeRegistry(
        shared_types={
            t: _qualname(t) for t in sorted(global_types, key=_type_sort_key)
        },
        shared_enums={
            t: _qualname(t) for t in sorted(global_enums, key=_type_sort_key)
        },
    )


def build_module_shared_types(
    module_messages: list[type[Message]],
    global_registry: TypeRegistry | None = None,
) -> TypeRegistry | None:
    """Determine which types are shared across multiple messages in a module.

    Returns ``None`` if there are no shared types (e.g., a single-message module).
    """
    if len(module_messages) <= 1:
        return None

    deps_per_message: dict[type[Message], set[type]] = {}
    for msg_cls in module_messages:
        deps_per_message[msg_cls] = collect_message_type_dependencies(msg_cls)

    all_deps: list[type] = []
    for deps in deps_per_message.values():
        all_deps.extend(deps)
    type_counts = Counter(all_deps)

    root_shared = {t for t, count in type_counts.items() if count >= 2}

    if global_registry is not None:
        root_shared = {
            t
            for t in root_shared
            if not global_registry.has_type(t) and not global_registry.has_enum(t)
        }

    if not root_shared:
        return None

    all_shared = transitive_closure(root_shared)

    if global_registry is not None:
        all_shared = {
            t
            for t in all_shared
            if not global_registry.has_type(t) and not global_registry.has_enum(t)
        }

    if not all_shared:
        return None

    return TypeRegistry(
        shared_types={
            t: _qualname(t)
            for t in sorted(all_shared, key=_type_sort_key)
            if not (isinstance(t, type) and issubclass(t, Enum))
        },
        shared_enums={
            t: _qualname(t)
            for t in sorted(all_shared, key=_type_sort_key)
            if isinstance(t, type) and issubclass(t, Enum)
        },
    )


# -- type resolver -----------------------------------------------------------


class TypeResolver:
    """Resolve a message class (or shared type collection) into
    language-agnostic :class:`ResolvedMessage` trees.
    """

    def __init__(
        self,
        shared_types: TypeRegistry | None = None,
        global_types: TypeRegistry | None = None,
    ):
        self.shared_types = shared_types
        self.global_types = global_types

        # Accumulators populated during resolution.
        # ``_helpers`` / ``_enums`` map all types (both inline and external)
        # to their qualnames.  The ``_inline_*`` sets only contain types
        # that should be *declared* in the output (not referenced).
        self._helpers: dict[type, str] = {}
        self._enums: dict[type[Enum], str] = {}
        self._inline_helpers: set[type] = set()
        self._inline_enums: set[type[Enum]] = set()
        self._custom_io: set[type] = set()

    # -- public API ----------------------------------------------------------

    def resolve_message(self, cls: type[Message]) -> ResolvedMessage:
        """Resolve a ``Message`` subclass into a ``ResolvedMessage``."""
        self._resolve_dataclass(cls)
        # Only inline (non-external) helpers and enums are emitted in the
        # message file; external ones are referenced by name.
        inline_helpers = [t for t in self._inline_helpers if t is not cls]
        return ResolvedMessage(
            source_class=cls.__name__,
            source_module=cls.__module__,
            major=cls.MAJOR,
            minor=cls.MINOR,
            direction=cls.DIRECTION,
            enums=[self._build_enum_def(e_cls) for e_cls in self._inline_enums],
            helpers=[self.resolve_dataclass(h_cls) for h_cls in inline_helpers],
            fields=[self.resolve_field(f.type, f.name) for f in fields(cls)],  # pyright: ignore[reportArgumentType]
            custom_io=cls in self._custom_io,
        )

    def resolve_dataclass(self, cls: type) -> HelperClass:
        """Resolve a dataclass (helper) into a ``HelperClass``."""
        return HelperClass(
            name=_qualname(cls),
            py_type=cls,
            fields=[self.resolve_field(f.type, f.name) for f in fields(cls)],
            custom_io=cls in self._custom_io,
        )

    def resolve_field(self, annotation: Any, field_name: str) -> AgnosticField:
        """Resolve a single field annotation into an ``AgnosticField``."""
        anno = validate_annotation(annotation)
        self._validate_annotation(annotation, anno)

        conditions = self._build_condition_info(anno.conditionals)

        if anno.tagged is not None:
            result = self._resolve_tagged(annotation, anno, field_name)
            result.conditionals = conditions
            return result

        real_type = anno.real_type
        effective_mt = self._effective_message_type(annotation, anno)

        # Peel Annotated wrappers.
        if get_origin(real_type) is Annotated:
            result = self.resolve_field(real_type, field_name)
            result.conditionals = conditions
            return result

        origin = get_origin(real_type)

        # Tuple
        if origin is tuple:
            elements = [
                self.resolve_field(arg, f"{field_name}_{i}")
                for i, arg in enumerate(get_args(real_type))
            ]
            return AgnosticField(
                name=field_name,
                kind=FieldKind.TUPLE,
                elements=elements,
                conditionals=conditions,
            )

        # List
        if origin is list:
            item_field = self.resolve_field(
                get_args(real_type)[0], f"{field_name}_item"
            )
            if anno.bitmask_conditioned_list is not None:
                bcl = anno.bitmask_conditioned_list
                return AgnosticField(
                    name=field_name,
                    kind=FieldKind.BITMASK_LIST,
                    element=item_field,
                    bitmask_element=item_field,
                    bitmask_size_prefix=bcl.size_prefix,
                    bitmask_max_slots=bcl.max_slots,
                    bitmask_bit_count=bcl.bit_count,
                    size_hint=anno.size_hint,
                    conditionals=conditions,
                )
            return AgnosticField(
                name=field_name,
                kind=FieldKind.LIST,
                element=item_field,
                size_hint=anno.size_hint,
                conditionals=conditions,
            )

        # Bytes
        if real_type is bytes:
            return AgnosticField(
                name=field_name,
                kind=FieldKind.BYTES,
                size_hint=anno.size_hint,
                conditionals=conditions,
            )

        # LocStr
        if real_type is LocStr:
            return AgnosticField(
                name=field_name,
                kind=FieldKind.LOCSTRING,
                conditionals=conditions,
            )

        # Dataclass (inner helper or external shared type)
        if is_dataclass(real_type):
            self._resolve_dataclass(real_type)
            return AgnosticField(
                name=field_name,
                kind=FieldKind.DATACLASS,
                type_ref=self._helpers[real_type],
                conditionals=conditions,
            )

        # Enum
        if isinstance(real_type, type) and issubclass(real_type, Enum):
            self._register_enum(real_type)
            return AgnosticField(
                name=field_name,
                kind=FieldKind.ENUM,
                wire_type=effective_mt,
                bits=anno.bits,
                type_ref=self._enums[real_type],
                build_type=anno.build_type,
                conditionals=conditions,
            )

        # Primitive
        return AgnosticField(
            name=field_name,
            kind=FieldKind.PRIMITIVE,
            wire_type=effective_mt,
            bits=anno.bits,
            float_bits=anno.float_bits,
            size_hint=anno.size_hint,
            bool_prefix=anno.bool_prefix,
            conditionals=conditions,
            build_type=anno.build_type,
        )

    # -- internal: tagged union resolution -----------------------------------

    def _resolve_tagged(self, annotation: Any, anno, field_name: str) -> AgnosticField:
        tagged = anno.tagged
        variants = [
            TaggedVariantRef(
                key=self._render_literal(raw_key),
                field=self.resolve_field(variant_annotation, f"{field_name}_variant"),
            )
            for raw_key, variant_annotation in tagged.lut.items()
        ]

        # Register discriminator-key enums.
        for raw_value in tagged.lut.keys():
            if isinstance(raw_value, Enum):
                self._register_enum(type(raw_value))

        return AgnosticField(
            name=field_name,
            kind=FieldKind.TAGGED,
            tagged_variants=variants,
            tagged_discriminator_type=(
                tagged.discriminator_type if isinstance(tagged, Tagged) else None
            ),
            tagged_discriminator_bits=(
                anno.bits if isinstance(tagged, Tagged) else None
            ),
            tagged_twoda_field=(
                tagged.field if isinstance(tagged, TwoDATagged) else None
            ),
            tagged_twoda_name=(
                tagged.twoda if isinstance(tagged, TwoDATagged) else None
            ),
            tagged_twoda_column=(
                tagged.column if isinstance(tagged, TwoDATagged) else None
            ),
        )

    # -- internal: collection ------------------------------------------------

    def _resolve_dataclass(self, cls: type) -> None:
        """Walk a dataclass and register its field types."""
        if cls in self._helpers:
            return

        # External type — reference only, don't inline its definition.
        qualified = self._resolve_type_ref(cls)
        if qualified is not None:
            self._helpers[cls] = qualified
            return

        self._helpers[cls] = _qualname(cls)
        self._inline_helpers.add(cls)
        if self._has_custom_io(cls):
            self._custom_io.add(cls)

        for f in fields(cls):  # pyright: ignore[reportArgumentType]
            self._collect_annotation(f.type)

    def _collect_annotation(self, annotation: Any) -> None:
        """Walk a type annotation and register dataclass/enum types found."""
        anno = validate_annotation(annotation)

        if anno.tagged is not None:
            for variant_annotation in anno.tagged.lut.values():
                self._collect_annotation(variant_annotation)
            for raw_value in anno.tagged.lut.keys():
                if isinstance(raw_value, Enum):
                    self._register_enum(type(raw_value))
            return

        real_type = anno.real_type
        if get_origin(real_type) is Annotated:
            self._collect_annotation(real_type)
            return

        origin = get_origin(real_type)

        if origin in {Union, UnionType}:
            for nested in get_args(real_type):
                self._collect_annotation(nested)
            return

        if origin is tuple:
            for nested in get_args(real_type):
                self._collect_annotation(nested)
            return

        if origin is list:
            self._collect_annotation(get_args(real_type)[0])
            return

        if is_dataclass(real_type):
            qualified = self._resolve_type_ref(real_type)
            if qualified is not None:
                self._helpers[real_type] = qualified
                return
            self._resolve_dataclass(real_type)
            return

        if isinstance(real_type, type) and issubclass(real_type, Enum):
            self._register_enum(real_type)

    def _register_enum(self, enum_cls: type[Enum]) -> None:
        if enum_cls in self._enums:
            return
        qualified = self._resolve_type_ref(enum_cls)
        if qualified is not None:
            self._enums[enum_cls] = qualified  # external — reference only
            return
        self._enums[enum_cls] = _qualname(enum_cls)
        self._inline_enums.add(enum_cls)

    # -- internal: helpers ---------------------------------------------------

    def _resolve_type_ref(self, cls: type) -> str | None:
        for registry in (self.global_types, self.shared_types):
            if registry is not None:
                qualname = registry.get(cls)
                if qualname is not None:
                    return qualname
        return None

    @staticmethod
    def _has_custom_io(typ: Any) -> bool:
        return any(
            "read" in base.__dict__ or "write" in base.__dict__ for base in typ.__mro__
        )

    def _effective_message_type(self, annotation: Any, anno) -> MessageType | None:
        if anno.build_type is not None:
            return anno.build_type.default
        if anno.message_type is not None:
            return anno.message_type
        if get_origin(anno.real_type) is Annotated:
            return self._effective_message_type(
                anno.real_type, validate_annotation(anno.real_type)
            )
        if get_origin(annotation) is not Annotated:
            return None
        for meta in get_args(annotation)[1:]:
            if get_origin(meta) is Annotated:
                nested = validate_annotation(meta)
                nested_mt = self._effective_message_type(meta, nested)
                if nested_mt is not None:
                    return nested_mt
        return None

    @staticmethod
    def _validate_annotation(annotation: Any, anno) -> None:
        effective_mt = anno.message_type or (
            anno.build_type.default if anno.build_type else None
        )
        for cond in anno.conditionals:
            if not isinstance(cond, _SUPPORTED_CONDITIONS):
                raise UnsupportedMessageError(
                    f"unsupported conditional {type(cond).__name__}"
                )

        if get_origin(anno.real_type) is Annotated:
            TypeResolver._validate_annotation(
                anno.real_type, validate_annotation(anno.real_type)
            )

        if anno.size_hint is not None and isinstance(anno.size_hint, BuildSizeHint):
            if get_origin(anno.real_type) is not list and anno.real_type is not bytes:
                raise UnsupportedMessageError(
                    "BuildSizeHint currently only supports list or byte payload fields"
                )

        if anno.tagged is not None and isinstance(anno.tagged, Tagged):
            TypeResolver._assert_message_type_supported(anno.tagged.discriminator_type)

        if anno.build_type is not None:
            TypeResolver._assert_message_type_supported(anno.build_type.default)
            TypeResolver._assert_message_type_supported(anno.build_type.then)

        if effective_mt is not None:
            TypeResolver._assert_message_type_supported(effective_mt)

    @staticmethod
    def _assert_message_type_supported(mt: MessageType) -> None:
        if mt == MessageType.BITS:
            raise UnsupportedMessageError("BITS is not a supported wire message type")

    @staticmethod
    def _build_condition_info(conditions: list[If]) -> list[ConditionInfo]:
        result = []
        for cond in conditions:
            closure = inspect.getclosurevars(cond.cb).nonlocals
            if isinstance(cond, IfFlag):
                result.append(
                    ConditionInfo(
                        op="flag", field=closure["field"], value=closure["flag"]
                    )
                )
            elif isinstance(cond, IfEq):
                result.append(
                    ConditionInfo(op="eq", field=closure["field"], value=closure["eq"])
                )
            elif isinstance(cond, IfNotEq):
                result.append(
                    ConditionInfo(op="ne", field=closure["field"], value=closure["ne"])
                )
            elif isinstance(cond, IfGt):
                result.append(
                    ConditionInfo(op="gt", field=closure["field"], value=closure["gt"])
                )
            elif isinstance(cond, IfIn):
                result.append(
                    ConditionInfo(
                        op="in", field=closure["field"], value=closure["values"]
                    )
                )
            elif isinstance(cond, IfNotIn):
                result.append(
                    ConditionInfo(
                        op="not_in", field=closure["field"], value=closure["values"]
                    )
                )
            elif isinstance(cond, IfTwoDA):
                result.append(
                    ConditionInfo(
                        op="twoda",
                        field=closure["field"],
                        value=(
                            closure["twoda"],
                            closure["column"],
                            closure["values"],
                        ),
                    )
                )
            elif isinstance(cond, IfBuild):
                result.append(
                    ConditionInfo(
                        op="build",
                        field="",
                        value=(
                            closure["build"],
                            closure["patch"],
                            closure["postfix"],
                        ),
                    )
                )
            elif isinstance(cond, IfNotBuild):
                result.append(
                    ConditionInfo(
                        op="not_build",
                        field="",
                        value=(
                            closure["build"],
                            closure["patch"],
                            closure["postfix"],
                        ),
                    )
                )
        return result

    def _render_literal(self, value: Any) -> str:
        if isinstance(value, Enum):
            self._register_enum(type(value))
            return f"{_qualname(type(value))}.{value.name}"
        if isinstance(value, str):
            return repr(value)
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return "null"
        return str(value)

    def resolve_registry(
        self,
        registry: TypeRegistry,
        source_module: str,
    ) -> ResolvedMessage:
        """Collect all types from a shared/global *registry* and produce
        a ``ResolvedMessage`` suitable for rendering as a shared-types file."""
        for cls in registry.shared_types:
            self._resolve_dataclass(cls)
        for enum_cls in registry.shared_enums:
            self._register_enum(enum_cls)
        return ResolvedMessage(
            source_class="",
            source_module=source_module,
            major=0,
            minor=0,
            direction=Direction.BOTH,
            enums=[self._build_enum_def(e_cls) for e_cls in self._inline_enums],
            helpers=[self.resolve_dataclass(h_cls) for h_cls in self._inline_helpers],
        )

    def _build_enum_def(self, enum_cls: type[Enum]) -> EnumDef:
        return EnumDef(
            name=_qualname(enum_cls),
            py_type=enum_cls,
            values=[(item.name, int(item.value)) for item in enum_cls],
        )
