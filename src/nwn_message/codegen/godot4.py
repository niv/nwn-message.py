"""GDScript codegen backend.

Consumes the language-agnostic ``ResolvedMessage`` / ``AgnosticField`` /
``HelperClass`` trees produced by ``_resolve.py`` and emits GDScript source
code.
"""

from __future__ import annotations

import json

# ---------------------------------------------------------------------------
# Public constants (preserved for compatibility)
# ---------------------------------------------------------------------------
import os
from dataclasses import fields as dc_fields
from typing import Any

from nwn_message.message import (
    BuildSizeHint,
    BuildType,
    ComputedAddSizeHint,
    ComputedMultiplySizeHint,
    Direction,
    FixedSizeHint,
    MessageType,
    QuantFloat,
    SizePrefix,
    TwoDARowCountHint,
)

from ._models import (
    AgnosticField,
    ConditionInfo,
    EnumDef,
    FieldKind,
    HelperClass,
    ResolvedMessage,
    TypeRegistry,
)
from ._resolve import UnsupportedMessageError

HELPER_FILE_NAME = "net_message_util.gd"
_HELPER_DIR = os.path.dirname(__file__)
HELPER_FILE_SOURCE = open(
    os.path.join(_HELPER_DIR, HELPER_FILE_NAME), encoding="utf-8"
).read()

# ---------------------------------------------------------------------------
# GDScript-specific name configuration
# ---------------------------------------------------------------------------

CLASS_NAME_PREFIX = "NetMessage"
CLASS_NAME_OVERRIDES = {
    "Resource": "ResourceEntry",
    "TileData": "TileInfo",
    "NWSync": "NWSyncData",
}
FIELD_NAME_OVERRIDES = {
    "hash": "sha1",
}

_PRIMITIVE_FULL_WIDTHS: dict[MessageType, int] = {
    MessageType.BOOL: 1,
    MessageType.BYTE: 8,
    MessageType.CHAR: 8,
    MessageType.WORD: 16,
    MessageType.SHORT: 16,
    MessageType.DWORD: 32,
    MessageType.INT: 32,
    MessageType.DWORD64: 64,
    MessageType.INT64: 64,
    MessageType.FLOAT: 32,
    MessageType.DOUBLE: 64,
    MessageType.OBJECT_ID: 32,
}

_PRIMITIVE_GDSCRIPT_TYPES: dict[MessageType, str] = {
    MessageType.BOOL: "bool",
    MessageType.BYTE: "int",
    MessageType.CHAR: "int",
    MessageType.WORD: "int",
    MessageType.SHORT: "int",
    MessageType.DWORD: "int",
    MessageType.INT: "int",
    MessageType.DWORD64: "int",
    MessageType.INT64: "int",
    MessageType.FLOAT: "float",
    MessageType.DOUBLE: "float",
    MessageType.STRING: "String",
    MessageType.RESREF: "String",
    MessageType.OBJECT_ID: "int",
}


# ---------------------------------------------------------------------------
# Direction helpers
# ---------------------------------------------------------------------------


def _direction_constant(direction: Direction) -> str:
    if direction == Direction.S2C:
        return "NetTypes.Direction.SERVER_TO_CLIENT"
    if direction == Direction.C2S:
        return "NetTypes.Direction.CLIENT_TO_SERVER"
    if direction == Direction.BOTH:
        return "NetTypes.Direction.BOTH"
    raise UnsupportedMessageError(f"unsupported direction {direction}")


# ---------------------------------------------------------------------------
# GDScript renderer
# ---------------------------------------------------------------------------


class _GodotRenderer:
    """Produces GDScript source from resolved message / shared-type trees."""

    def __init__(
        self,
        global_registry: TypeRegistry | None = None,
        module_registry: TypeRegistry | None = None,
    ):
        self._global_registry = global_registry
        self._module_registry = module_registry

        # Accumulators reset per render call
        self._name_map: dict[str, str] = {}  # Python qualname → GDScript name
        self._used_names: set[str] = set()
        self._temp_counter: int = 0
        self._msg_class_qualname: str = ""  # message's qualname for prefix stripping

    # -- public render entry points -----------------------------------------

    def render_message(self, resolved: ResolvedMessage) -> str:
        """Render a single message file."""
        self._reset(resolved)

        msg_name = f"{CLASS_NAME_PREFIX}{resolved.source_class}"
        sections: list[list[str]] = [
            [
                f"class_name {msg_name}",
                "extends NetMessageBase",
                "",
                f"const MAJOR: int = 0x{resolved.major:02X}",
                f"const MINOR: int = 0x{resolved.minor:02X}",
                f"const DIRECTION: NetTypes.Direction = {_direction_constant(resolved.direction)}",
                "",
                f'static var received := create_static_signal({msg_name}, "received")',
            ]
        ]

        sections.extend(self._render_enum(e) for e in resolved.enums)
        sections.extend(self._render_helper(h) for h in resolved.helpers)

        if resolved.fields:
            sections.append(self._field_declarations(resolved.fields))

        sections.append(self._message_read_block(resolved, msg_name))
        sections.append(self._message_write_block(resolved))

        return self._join(sections)

    def render_shared(self, resolved: ResolvedMessage, module: str) -> str:
        """Render a shared-types file."""
        self._reset(resolved)
        class_name = self._module_class_name(module)

        sections: list[list[str]] = [[f"class_name {class_name}", "extends RefCounted"]]
        sections.extend(self._render_enum(e) for e in resolved.enums)
        sections.extend(self._render_helper(h) for h in resolved.helpers)
        return self._join(sections)

    def render_custom(self, resolved: ResolvedMessage) -> str:
        """Render the custom-io companion stub file."""
        self._reset(resolved)
        msg_name = f"{CLASS_NAME_PREFIX}{resolved.source_class}"
        custom_name = f"{msg_name}Custom"

        sections: list[list[str]] = [
            [f"class_name {custom_name}", "extends RefCounted"]
        ]

        for h in resolved.helpers:
            if not h.custom_io:
                continue
            gd_name = self._resolve_name(h.name)
            stub_base = self._custom_io_base_name(h.py_type)
            sections.append(
                self._custom_hook_block(
                    gd_name,
                    f"{stub_base}_read",
                    f"{stub_base}_write",
                    is_message=False,
                    custom_name=custom_name,
                )
            )

        if resolved.custom_io:
            sections.append(
                self._custom_hook_block(
                    msg_name,
                    "read",
                    "write",
                    is_message=True,
                    custom_name=custom_name,
                )
            )

        return self._join(sections)

    def _custom_io_base_name(self, py_type: type) -> str:
        """Derive the stub-name prefix for a custom-io helper class."""
        import re

        qualname = re.sub(r"[^0-9A-Za-z_]", "_", py_type.__qualname__.replace(".", "_"))
        msg_qn = re.sub(r"[^0-9A-Za-z_]", "_", self._msg_class_qualname)
        if qualname.startswith(f"{msg_qn}_") or qualname == msg_qn:
            return f"fn_{qualname}"
        return f"fn_{msg_qn}_{qualname}"

    # -- name preparation ---------------------------------------------------

    def _reset(self, resolved: ResolvedMessage) -> None:
        self._name_map.clear()
        self._used_names.clear()
        self._temp_counter = 0
        self._msg_class_qualname = resolved.source_class

        # Build qualname → GDScript name map

        # 1. External types from registries
        if self._global_registry is not None:
            for cls, qn in self._global_registry.shared_types.items():
                short = self._safe_class_name(cls.__qualname__.rsplit(".", 1)[-1])
                self._name_map[qn] = f"NetGlobalTypes.{short}"
                self._used_names.add(short)
            for cls, qn in self._global_registry.shared_enums.items():
                short = cls.__qualname__.rsplit(".", 1)[-1]
                self._name_map[qn] = f"NetGlobalTypes.{short}"
                self._used_names.add(short)

        if self._module_registry is not None:
            module_prefix = self._module_class_name(resolved.source_module)
            for cls, qn in self._module_registry.shared_types.items():
                short = self._safe_class_name(cls.__qualname__.rsplit(".", 1)[-1])
                deduped = self._dedupe(short)
                self._name_map[qn] = f"{module_prefix}.{deduped}"
            for cls, qn in self._module_registry.shared_enums.items():
                short = cls.__qualname__.rsplit(".", 1)[-1]
                deduped = self._dedupe(short)
                self._name_map[qn] = f"{module_prefix}.{deduped}"

        # 2. Internal helpers (inline dataclasses)
        for h in resolved.helpers:
            if h.name in self._name_map:
                continue
            short = self._short_name(h.py_type)
            deduped = self._dedupe(short)
            self._name_map[h.name] = deduped

        # 3. Internal enums
        for e in resolved.enums:
            if e.name in self._name_map:
                continue
            short = e.py_type.__qualname__.rsplit(".", 1)[-1]
            deduped = self._dedupe(short)
            self._name_map[e.name] = deduped

    def _resolve_name(self, qualname: str) -> str:
        """Map a Python qualname to its GDScript name."""
        return self._name_map.get(qualname, qualname)

    def _short_name(self, py_type: type) -> str:
        """Derive a short GDScript name for an inline helper."""
        qn = py_type.__qualname__.replace(".", "")
        if qn.startswith(self._msg_class_qualname):
            qn = qn[len(self._msg_class_qualname) :] or py_type.__name__
        return self._safe_class_name(qn)

    @staticmethod
    def _safe_class_name(name: str) -> str:
        return CLASS_NAME_OVERRIDES.get(name, name)

    @staticmethod
    def _safe_field_name(name: str) -> str:
        return FIELD_NAME_OVERRIDES.get(name, name)

    def _dedupe(self, name: str) -> str:
        candidate = name
        suffix = 2
        while candidate in self._used_names:
            candidate = f"{name}{suffix}"
            suffix += 1
        self._used_names.add(candidate)
        return candidate

    @staticmethod
    def _module_class_name(module: str) -> str:
        base = module.rsplit(".", 1)[-1]
        title = "".join(p[0].upper() + p[1:] for p in base.split("_"))
        return f"Net{title}Types"

    # -- structural blocks --------------------------------------------------

    def _render_enum(self, enum_def: EnumDef) -> list[str]:
        gd_name = self._resolve_name(enum_def.name)
        lines = [f"enum {gd_name} {{"]
        for name, value in enum_def.values:
            lines.append(f"    {name} = {value},")
        lines.append("}")
        return lines

    def _render_helper(self, helper: HelperClass) -> list[str]:
        gd_name = self._resolve_name(helper.name)
        lines = [f"class {gd_name}:"]

        if helper.fields:
            for field in helper.fields:
                lines.append(f"    {self._render_field_decl(field)}")
        else:
            lines.append("    pass")

        lines.append("")
        lines.extend(self._indent(self._helper_read_block(helper), prefix="    "))
        lines.append("")
        lines.extend(self._indent(self._helper_write_block(helper), prefix="    "))
        if not helper.custom_io:
            lines.append("")
            lines.extend(
                [
                    "    func _to_string() -> String:",
                    f"        return NetMessageBase.format_object(self, {json.dumps(gd_name)})",
                ]
            )
        return lines

    def _field_declarations(self, fields: list[AgnosticField]) -> list[str]:
        return [self._render_field_decl(f) for f in fields]

    @staticmethod
    def _render_field_decl(field: AgnosticField) -> str:
        gd_type = None
        default = field_default(field)
        if field.kind == FieldKind.PRIMITIVE and field.wire_type is not None:
            gd_type = _PRIMITIVE_GDSCRIPT_TYPES.get(field.wire_type)
        elif field.kind == FieldKind.ENUM:
            gd_type = "int"
        elif field.kind == FieldKind.BYTES:
            gd_type = "PackedByteArray"
        elif field.kind == FieldKind.LIST:
            gd_type = "Array"
        elif field.kind == FieldKind.TUPLE:
            gd_type = "Array"

        name = FIELD_NAME_OVERRIDES.get(field.name, field.name)
        prefix = f"var {name}"
        if gd_type:
            prefix += f": {gd_type}"
        return f"{prefix} = {default}"

    def _message_read_block(
        self, resolved: ResolvedMessage, msg_name: str
    ) -> list[str]:
        lines = [f"static func read(reader, context: NetContext) -> {msg_name}:"]
        if resolved.custom_io:
            custom_name = f"{msg_name}Custom"
            lines.append(f"    return {custom_name}.read(reader, context)")
            return lines

        lines.append(f"    var msg = {msg_name}.new()")
        lines.append("    var obj = msg")
        for field in resolved.fields:
            for line in self._emit_read_field(field, "obj"):
                lines.append(f"    {line}")
        lines.append("    return msg")
        return lines

    def _message_write_block(self, resolved: ResolvedMessage) -> list[str]:
        lines = ["func write(writer, context):"]
        if resolved.custom_io:
            custom_name = f"{CLASS_NAME_PREFIX}{resolved.source_class}Custom"
            lines.append(f"    {custom_name}.write(self, writer, context)")
            return lines

        for field in resolved.fields:
            for line in self._emit_write_field(field, "self"):
                lines.append(f"    {line}")
        if not resolved.fields:
            lines.append("    pass")
        return lines

    def _helper_read_block(self, helper: HelperClass) -> list[str]:
        gd_name = self._resolve_name(helper.name)
        lines = [f"static func read(reader, context: NetContext) -> {gd_name}:"]
        if helper.custom_io:
            custom_name = f"{CLASS_NAME_PREFIX}{self._msg_class_qualname}Custom"
            stub_base = self._custom_io_base_name(helper.py_type)
            lines.append(f"    return {custom_name}.{stub_base}_read(reader, context)")
            return lines

        lines.append(f"    var obj = {gd_name}.new()")
        for field in helper.fields:
            for line in self._emit_read_field(field, "obj"):
                lines.append(f"    {line}")
        lines.append("    return obj")
        return lines

    def _helper_write_block(self, helper: HelperClass) -> list[str]:
        lines = ["func write(writer, context: NetContext) -> void:"]
        if helper.custom_io:
            custom_name = f"{CLASS_NAME_PREFIX}{self._msg_class_qualname}Custom"
            stub_base = self._custom_io_base_name(helper.py_type)
            lines.append(f"    {custom_name}.{stub_base}_write(self, writer, context)")
            return lines

        for field in helper.fields:
            for line in self._emit_write_field(field, "self"):
                lines.append(f"    {line}")
        return lines

    @staticmethod
    def _custom_hook_block(
        target_name: str,
        read_name: str,
        write_name: str,
        is_message: bool,
        custom_name: str = "",
    ) -> list[str]:
        cls_name = custom_name or f"{target_name}Custom"
        if is_message:
            return [
                f"static func {read_name}(reader, context: NetContext) -> {target_name}:",
                f'    push_error("{cls_name}.{read_name} is not implemented")',
                f"    return {target_name}.new()",
                "",
                f"static func {write_name}(message, writer, context: NetContext) -> void:",
                f'    push_error("{cls_name}.{write_name} is not implemented")',
            ]
        return [
            f"static func {read_name}(reader, context: NetContext):",
            f'    push_error("{cls_name}.{read_name} is not implemented")',
            "    return null",
            "",
            f"static func {write_name}(value, writer, context: NetContext) -> void:",
            f'    push_error("{cls_name}.{write_name} is not implemented")',
        ]

    # -- read / write body emission -----------------------------------------

    def _emit_read_field(self, field: AgnosticField, receiver: str) -> list[str]:
        conditions = [self._render_condition(c, receiver) for c in field.conditionals]
        body = self._emit_field_read_body(field, receiver)
        return self._wrap_conditions(body, conditions)

    def _emit_write_field(self, field: AgnosticField, receiver: str) -> list[str]:
        conditions = [self._render_condition(c, receiver) for c in field.conditionals]
        body = self._emit_field_write_body(field, receiver)
        return self._wrap_conditions(body, conditions)

    def _emit_field_read_body(self, field: AgnosticField, receiver: str) -> list[str]:
        target = self._safe_field_ref(receiver, field.name)
        body = self._emit_read_assignment(target, field, receiver)
        if field.bool_prefix:
            body = ["if reader.read_bool():"] + [f"    {line}" for line in body]
        return body

    def _emit_field_write_body(self, field: AgnosticField, receiver: str) -> list[str]:
        source = self._safe_field_ref(receiver, field.name)
        body = self._emit_write_assignment(source, field, receiver)
        if field.bool_prefix:
            has_var = self._new_temp("has")
            body = [
                f"var {has_var} = NetMessageUtil.is_truthy({source})",
                f"writer.write_bool({has_var})",
                f"if {has_var}:",
            ] + [f"    {line}" for line in body]
        return body

    def _emit_read_assignment(
        self, target: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        kind = field.kind
        if kind == FieldKind.PRIMITIVE:
            return [f"{target} = {self._read_scalar(field)}"]
        if kind == FieldKind.ENUM:
            return [f"{target} = {self._read_scalar(field)}"]
        if kind == FieldKind.DATACLASS:
            gd_name = self._resolve_name(field.type_ref or "")
            return [f"{target} = {gd_name}.read(reader, context)"]
        if kind == FieldKind.BYTES:
            size_expr = self._render_size_hint(field.size_hint, receiver)
            return [f"{target} = reader.read_bytes({size_expr})"]
        if kind == FieldKind.LOCSTRING:
            return [f"{target} = reader.read_locstring(context)"]
        if kind == FieldKind.TUPLE:
            temp = self._new_temp("tuple")
            lines = [f"var {temp} = []"]
            assert field.elements is not None
            for elem in field.elements:
                lines.extend(self._emit_read_append(temp, elem, receiver))
            lines.append(f"{target} = {temp}")
            return lines
        if kind == FieldKind.LIST:
            return self._emit_read_list(target, field, receiver)
        if kind == FieldKind.BITMASK_LIST:
            return self._emit_read_bitmask_list(target, field, receiver)
        if kind == FieldKind.TAGGED:
            return self._emit_read_tagged(target, field, receiver)
        raise UnsupportedMessageError(f"unsupported read kind: {kind}")

    def _emit_write_assignment(
        self, source: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        kind = field.kind
        if kind == FieldKind.PRIMITIVE:
            return [self._write_scalar(field, source)]
        if kind == FieldKind.ENUM:
            return [self._write_scalar(field, f"int({source})")]
        if kind == FieldKind.DATACLASS:
            return [f"if {source} != null:", f"    {source}.write(writer, context)"]
        if kind == FieldKind.BYTES:
            return self._emit_write_bytes(source, field, receiver)
        if kind == FieldKind.LOCSTRING:
            return [f"writer.write_locstring({source})"]
        if kind == FieldKind.TUPLE:
            return self._emit_write_tuple(source, field, receiver)
        if kind == FieldKind.LIST:
            return self._emit_write_list(source, field, receiver)
        if kind == FieldKind.BITMASK_LIST:
            return self._emit_write_bitmask_list(source, field, receiver)
        if kind == FieldKind.TAGGED:
            return self._emit_write_tagged(source, field, receiver)
        raise UnsupportedMessageError(f"unsupported write kind: {kind}")

    # -- compound read dispatches -------------------------------------------

    def _emit_read_list(
        self, target: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        count_var = self._new_temp("count")
        temp = self._new_temp("items")
        lines = [
            f"var {count_var} = {self._render_size_hint(field.size_hint, receiver)}"
        ]
        lines.append(f"var {temp} = []")
        lines.append(f"for _{temp}_i in {count_var}:")
        assert field.element is not None
        for nested in self._emit_read_append(temp, field.element, receiver):
            lines.append(f"    {nested}")
        lines.append(f"{target} = {temp}")
        return lines

    def _emit_read_append(
        self, array_name: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        kind = field.kind
        if kind in {FieldKind.PRIMITIVE, FieldKind.ENUM}:
            if field.build_type is None:
                return [f"{array_name}.append({self._read_scalar(field)})"]
            # Build-type branch
            then_render = _replace(field, wire_type=field.build_type.then)
            default_render = _replace(field, wire_type=field.build_type.default)
            return self._emit_runtime_type_branch(
                field.build_type,
                [f"{array_name}.append({self._read_scalar(then_render)})"],
                [f"{array_name}.append({self._read_scalar(default_render)})"],
            )
        if kind == FieldKind.DATACLASS:
            gd_name = self._resolve_name(field.type_ref or "")
            return [f"{array_name}.append({gd_name}.read(reader, context))"]
        if kind == FieldKind.BYTES:
            size_expr = self._render_size_hint(field.size_hint, receiver)
            return [f"{array_name}.append(reader.read_bytes({size_expr}))"]
        if kind == FieldKind.LOCSTRING:
            return [f"{array_name}.append(reader.read_locstring(context))"]
        if kind == FieldKind.TUPLE:
            temp = self._new_temp("tuple")
            lines = [f"var {temp} = []"]
            assert field.elements is not None
            for elem in field.elements:
                lines.extend(self._emit_read_append(temp, elem, receiver))
            lines.append(f"{array_name}.append({temp})")
            return lines
        if kind in {FieldKind.LIST, FieldKind.BITMASK_LIST}:
            temp = self._new_temp("nested")
            lines = [f"var {temp} = []"]
            if kind == FieldKind.LIST:
                lines.extend(self._emit_read_list(temp, field, receiver))
            else:
                lines.extend(self._emit_read_bitmask_list(temp, field, receiver))
            lines.append(f"{array_name}.append({temp})")
            return lines
        if kind == FieldKind.TAGGED:
            temp = self._new_temp("tagged")
            lines = [f"var {temp} = null"]
            lines.extend(self._emit_read_tagged(temp, field, receiver))
            lines.append(f"{array_name}.append({temp})")
            return lines
        raise UnsupportedMessageError(f"unsupported read append kind: {kind}")

    def _emit_read_bitmask_list(
        self, target: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        assert field.bitmask_size_prefix is not None
        flags_var = self._new_temp("flags")
        temp = self._new_temp("items")
        bit_count = self._render_slot(
            field.bitmask_bit_count
            if field.bitmask_bit_count is not None
            else _default_bit_count(field.bitmask_size_prefix),
            receiver,
        )
        lines = [
            f"var {flags_var} = {self._read_bitsized(field.bitmask_size_prefix.value, bit_count)}"
        ]
        lines.append(f"var {temp} = []")
        lines.append(
            f"for _{temp}_i in {self._render_slot(field.bitmask_max_slots, receiver)}:"
        )
        lines.append(f"    if {flags_var} & (1 << _{temp}_i):")
        assert field.bitmask_element is not None
        for nested in self._emit_read_append(temp, field.bitmask_element, receiver):
            lines.append(f"        {nested}")
        lines.append("    else:")
        lines.append(f"        {temp}.append(null)")
        lines.append(f"{target} = {temp}")
        return lines

    def _emit_read_tagged(
        self, target: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        discriminator = self._new_temp("tag")
        lines = [
            f"var {discriminator} = {self._read_discriminator(field, receiver)}",
            "match %s:" % discriminator,
        ]
        assert field.tagged_variants is not None
        for variant in field.tagged_variants:
            lines.append(f"    {variant.key}:")
            for nested in self._emit_read_assignment(target, variant.field, receiver):
                lines.append(f"        {nested}")
        lines.append("    _:")
        # Extract message class name from context
        msg_name = self._msg_class_qualname
        lines.append(
            f'        reader._fail("Unsupported tagged discriminator while reading {msg_name}")'
        )
        return lines

    # -- compound write dispatches ------------------------------------------

    def _emit_write_list(
        self, source: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        lines = []
        if isinstance(field.size_hint, SizePrefix):
            lines.append(
                self._write_scalar(
                    AgnosticField(
                        name="",
                        kind=FieldKind.PRIMITIVE,
                        wire_type=field.size_hint.value,
                    ),
                    f"{source}.size()",
                )
            )
        loop_var = self._new_temp("item")
        lines.append(f"for {loop_var} in {source}:")
        assert field.element is not None
        for nested in self._emit_write_item(loop_var, field.element, receiver):
            lines.append(f"    {nested}")
        return lines

    def _emit_write_item(
        self, source: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        kind = field.kind
        if kind in {FieldKind.PRIMITIVE, FieldKind.ENUM}:
            payload = source if kind == FieldKind.PRIMITIVE else f"int({source})"
            if field.build_type is None:
                return [self._write_scalar(field, payload)]
            then_render = _replace(field, wire_type=field.build_type.then)
            default_render = _replace(field, wire_type=field.build_type.default)
            return self._emit_runtime_type_branch(
                field.build_type,
                [self._write_scalar(then_render, payload)],
                [self._write_scalar(default_render, payload)],
            )
        if kind == FieldKind.DATACLASS:
            return [f"if {source} != null:", f"    {source}.write(writer, context)"]
        if kind == FieldKind.BYTES:
            return self._emit_write_bytes(source, field, receiver)
        if kind == FieldKind.LOCSTRING:
            return [f"writer.write_locstring({source})"]
        if kind == FieldKind.TUPLE:
            return self._emit_write_tuple(source, field, receiver)
        if kind == FieldKind.LIST:
            return self._emit_write_list(source, field, receiver)
        if kind == FieldKind.BITMASK_LIST:
            return self._emit_write_bitmask_list(source, field, receiver)
        if kind == FieldKind.TAGGED:
            return self._emit_write_tagged(source, field, receiver)
        raise UnsupportedMessageError(f"unsupported write item kind: {kind}")

    def _emit_write_tuple(
        self, source: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        lines = []
        assert field.elements is not None
        for index, nested in enumerate(field.elements):
            lines.extend(self._emit_write_item(f"{source}[{index}]", nested, receiver))
        return lines

    def _emit_write_tagged(
        self, source: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        lines = []
        assert field.tagged_variants is not None
        for index, variant in enumerate(field.tagged_variants):
            keyword = "if" if index == 0 else "elif"
            lines.append(
                f"{keyword} {self._render_tagged_condition(source, variant.field)}:"
            )
            if field.tagged_discriminator_type is not None:
                lines.append(f"    {self._write_discriminator(field, variant.key)}")
            for nested in self._emit_write_assignment(source, variant.field, receiver):
                lines.append(f"    {nested}")
        lines.append("else:")
        msg_name = self._msg_class_qualname
        lines.append(
            f'    push_error("Unsupported tagged runtime type while writing {msg_name}")'
        )
        return lines

    def _emit_write_bitmask_list(
        self, source: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        assert field.bitmask_size_prefix is not None
        flags_var = self._new_temp("flags")
        item_var = self._new_temp("item")
        bit_count = self._render_slot(
            field.bitmask_bit_count
            if field.bitmask_bit_count is not None
            else _default_bit_count(field.bitmask_size_prefix),
            receiver,
        )
        max_slots = self._render_slot(field.bitmask_max_slots, receiver)
        lines = [f"var {flags_var} = 0"]
        lines.append(f"for _{item_var}_i in {max_slots}:")
        lines.append(
            f"    var {item_var} = {source}[_{item_var}_i] if _{item_var}_i < {source}.size() else null"
        )
        lines.append(f"    if {item_var} != null:")
        lines.append(f"        {flags_var} |= 1 << _{item_var}_i")
        lines.append(
            self._write_bitsized(field.bitmask_size_prefix.value, bit_count, flags_var)
        )
        lines.append(f"for _{item_var}_i in {max_slots}:")
        lines.append(
            f"    var {item_var} = {source}[_{item_var}_i] if _{item_var}_i < {source}.size() else null"
        )
        lines.append(f"    if {item_var} != null:")
        assert field.bitmask_element is not None
        for nested in self._emit_write_item(item_var, field.bitmask_element, receiver):
            lines.append(f"        {nested}")
        return lines

    def _emit_write_bytes(
        self, source: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        lines: list[str] = []
        if isinstance(field.size_hint, SizePrefix):
            lines.append(
                self._write_scalar(
                    AgnosticField(
                        name="",
                        kind=FieldKind.PRIMITIVE,
                        wire_type=field.size_hint.value,
                    ),
                    f"{source}.size()",
                )
            )
            lines.append(f"writer.write_bytes({source})")
            return lines

        if field.size_hint is None:
            lines.append(f"writer.write_bytes({source})")
            return lines

        lines.append(
            f"writer.write_bytes({source}, {self._render_size_hint(field.size_hint, receiver)})"
        )
        return lines

    # -- build-type runtime branching ---------------------------------------

    @staticmethod
    def _emit_runtime_type_branch(
        build_type: BuildType, then_lines: list[str], default_lines: list[str]
    ) -> list[str]:
        condition = f"context.satisfies({build_type.if_build[0]}, {build_type.if_build[1]}, {build_type.if_build[2]})"
        return (
            [f"if {condition}:"]
            + [f"    {line}" for line in then_lines]
            + ["else:"]
            + [f"    {line}" for line in default_lines]
        )

    # -- formatting helpers -------------------------------------------------

    def _read_scalar(self, field: AgnosticField) -> str:
        if field.float_bits is not None:
            if isinstance(field.float_bits, QuantFloat):
                return f"reader.read_float({field.float_bits.multiplier}, {field.float_bits.bits})"
            return f"reader.read_float_lim({field.float_bits.min}, {field.float_bits.max}, {field.float_bits.bits})"

        mt = field.wire_type
        bits = field.bits
        if mt == MessageType.BOOL:
            return "reader.read_bool()"
        if mt == MessageType.BYTE:
            return self._read_bitsized(mt, bits or 8)
        if mt == MessageType.CHAR:
            return f"reader.read_char({bits or 8})"
        if mt == MessageType.WORD:
            return self._read_bitsized(mt, bits or 16)
        if mt == MessageType.SHORT:
            return f"reader.read_short({bits or 16})"
        if mt == MessageType.DWORD:
            return self._read_bitsized(mt, bits or 32)
        if mt == MessageType.INT:
            return f"reader.read_int({bits or 32})"
        if mt == MessageType.DWORD64:
            return f"reader.read_dword64({bits or 64})"
        if mt == MessageType.INT64:
            return f"reader.read_int64({bits or 64})"
        if mt == MessageType.FLOAT:
            return f"reader.read_float(1.0, {bits or 32})"
        if mt == MessageType.DOUBLE:
            return "reader.read_double()"
        if mt == MessageType.STRING:
            return "reader.read_string()"
        if mt == MessageType.RESREF:
            return "reader.read_resref()"
        if mt == MessageType.JSON:
            return "reader.read_json()"
        if mt == MessageType.OBJECT_ID:
            return f"reader.read_object_id({bits or 32})"
        raise UnsupportedMessageError(f"unsupported reader for {mt}")

    def _read_bitsized(self, mt: MessageType, bits: int | str) -> str:
        bit_expr = str(bits)
        if mt == MessageType.BOOL:
            return "reader.read_bool()"
        if mt == MessageType.BYTE:
            return f"reader.read_byte({bit_expr})"
        if mt == MessageType.CHAR:
            return f"reader.read_char({bit_expr})"
        if mt == MessageType.WORD:
            return f"reader.read_word({bit_expr})"
        if mt == MessageType.SHORT:
            return f"reader.read_short({bit_expr})"
        if mt == MessageType.DWORD:
            return f"reader.read_dword({bit_expr})"
        if mt == MessageType.INT:
            return f"reader.read_int({bit_expr})"
        if mt == MessageType.DWORD64:
            return f"reader.read_dword64({bit_expr})"
        if mt == MessageType.INT64:
            return f"reader.read_int64({bit_expr})"
        if mt == MessageType.FLOAT:
            return f"reader.read_float(1.0, {bit_expr})"
        raise UnsupportedMessageError(f"unsupported bitsized reader for {mt}")

    def _read_discriminator(self, field: AgnosticField, receiver: str) -> str:
        if field.tagged_twoda_name is not None:
            assert field.tagged_twoda_field is not None
            assert field.tagged_twoda_column is not None
            ref = self._safe_field_ref(receiver, field.tagged_twoda_field)
            return (
                f"int(context.get_twoda_value({json.dumps(field.tagged_twoda_name)}, "
                f"{ref}, "
                f"{json.dumps(field.tagged_twoda_column)}))"
            )
        assert field.tagged_discriminator_type is not None
        return self._read_bitsized(
            field.tagged_discriminator_type,
            field.tagged_discriminator_bits
            or _PRIMITIVE_FULL_WIDTHS.get(field.tagged_discriminator_type, 8),
        )

    def _write_scalar(self, field: AgnosticField, value_expr: str) -> str:
        if field.float_bits is not None:
            if isinstance(field.float_bits, QuantFloat):
                return f"writer.write_float({value_expr}, {field.float_bits.multiplier}, {field.float_bits.bits})"
            return f"writer.write_float_lim({value_expr}, {field.float_bits.min}, {field.float_bits.max}, {field.float_bits.bits})"

        mt = field.wire_type
        bits = field.bits
        if mt == MessageType.BOOL:
            return f"writer.write_bool({value_expr})"
        if mt == MessageType.BYTE:
            return self._write_bitsized(mt, bits or 8, value_expr)
        if mt == MessageType.CHAR:
            return f"writer.write_char({value_expr}, {bits or 8})"
        if mt == MessageType.WORD:
            return self._write_bitsized(mt, bits or 16, value_expr)
        if mt == MessageType.SHORT:
            return f"writer.write_short({value_expr}, {bits or 16})"
        if mt == MessageType.DWORD:
            return self._write_bitsized(mt, bits or 32, value_expr)
        if mt == MessageType.INT:
            return f"writer.write_int({value_expr}, {bits or 32})"
        if mt == MessageType.DWORD64:
            return f"writer.write_dword64({value_expr}, {bits or 64})"
        if mt == MessageType.INT64:
            return f"writer.write_int64({value_expr}, {bits or 64})"
        if mt == MessageType.FLOAT:
            return f"writer.write_float({value_expr}, 1.0, {bits or 32})"
        if mt == MessageType.DOUBLE:
            return f"writer.write_double({value_expr})"
        if mt == MessageType.STRING:
            return f"writer.write_string({value_expr})"
        if mt == MessageType.RESREF:
            return f"writer.write_resref({value_expr})"
        if mt == MessageType.JSON:
            return f"writer.write_json({value_expr})"
        if mt == MessageType.OBJECT_ID:
            return f"writer.write_object_id({value_expr}, {bits or 32})"
        raise UnsupportedMessageError(f"unsupported writer for {mt}")

    def _write_bitsized(self, mt: MessageType, bits: int | str, value_expr: str) -> str:
        bit_expr = str(bits)
        if mt == MessageType.BOOL:
            return f"writer.write_bool({value_expr})"
        if mt == MessageType.BYTE:
            return f"writer.write_byte({value_expr}, {bit_expr})"
        if mt == MessageType.CHAR:
            return f"writer.write_char({value_expr}, {bit_expr})"
        if mt == MessageType.WORD:
            return f"writer.write_word({value_expr}, {bit_expr})"
        if mt == MessageType.SHORT:
            return f"writer.write_short({value_expr}, {bit_expr})"
        if mt == MessageType.DWORD:
            return f"writer.write_dword({value_expr}, {bit_expr})"
        if mt == MessageType.INT:
            return f"writer.write_int({value_expr}, {bit_expr})"
        if mt == MessageType.DWORD64:
            return f"writer.write_dword64({value_expr}, {bit_expr})"
        if mt == MessageType.INT64:
            return f"writer.write_int64({value_expr}, {bit_expr})"
        if mt == MessageType.FLOAT:
            return f"writer.write_float({value_expr}, 1.0, {bit_expr})"
        raise UnsupportedMessageError(f"unsupported bitsized writer for {mt}")

    def _write_discriminator(self, field: AgnosticField, value_expr: str) -> str:
        assert field.tagged_discriminator_type is not None
        return self._write_bitsized(
            field.tagged_discriminator_type,
            field.tagged_discriminator_bits
            or _PRIMITIVE_FULL_WIDTHS.get(field.tagged_discriminator_type, 8),
            value_expr,
        )

    def _render_condition(self, cond: ConditionInfo, receiver: str) -> str:
        field_ref = self._safe_field_ref(receiver, cond.field)
        if cond.op == "flag":
            return f"{field_ref} & {self._render_literal(cond.value)}"
        if cond.op == "eq":
            return f"{field_ref} == {self._render_literal(cond.value)}"
        if cond.op == "ne":
            return f"{field_ref} != {self._render_literal(cond.value)}"
        if cond.op == "gt":
            return f"{field_ref} > {self._render_literal(cond.value)}"
        if cond.op == "in":
            values = ", ".join(
                self._render_literal(v) for v in sorted(cond.value, key=repr)
            )
            return f"{field_ref} in [{values}]"
        if cond.op == "not_in":
            values = ", ".join(
                self._render_literal(v) for v in sorted(cond.value, key=repr)
            )
            return f"not ({field_ref} in [{values}])"
        if cond.op == "twoda":
            twoda, column, values = cond.value
            values_list = ", ".join(
                self._render_literal(v) for v in sorted(values, key=repr)
            )
            return (
                f"str(context.get_twoda_value({json.dumps(twoda)}, "
                f"{field_ref}, "
                f"{json.dumps(column)})) in [{values_list}]"
            )
        if cond.op == "build":
            build, patch, postfix = cond.value
            return f"context.satisfies({build}, {patch}, {postfix})"
        if cond.op == "not_build":
            build, patch, postfix = cond.value
            return f"not context.satisfies({build}, {patch}, {postfix})"
        raise UnsupportedMessageError(f"unsupported condition op: {cond.op}")

    def _render_literal(self, value: Any) -> str:
        if isinstance(value, str):
            return json.dumps(value)
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return "null"
        if isinstance(value, int):
            return str(value)
        return str(value)

    def _render_tagged_condition(self, source: str, field: AgnosticField) -> str:
        if field.kind == FieldKind.DATACLASS:
            gd_name = self._resolve_name(field.type_ref or "")
            return f"{source} is {gd_name}"
        if field.kind == FieldKind.LOCSTRING:
            return f"{source} is NetMessageUtil.LocString or typeof({source}) == TYPE_INT or {source} == null"
        if field.kind == FieldKind.BYTES:
            return f"typeof({source}) == TYPE_PACKED_BYTE_ARRAY"
        if field.kind in {FieldKind.LIST, FieldKind.TUPLE, FieldKind.BITMASK_LIST}:
            return f"typeof({source}) == TYPE_ARRAY"
        if field.kind == FieldKind.ENUM:
            return f"typeof({source}) == TYPE_INT"
        if field.kind == FieldKind.PRIMITIVE:
            mt = field.wire_type
            if mt == MessageType.BOOL:
                return f"typeof({source}) == TYPE_BOOL"
            if mt in {
                MessageType.BYTE,
                MessageType.CHAR,
                MessageType.WORD,
                MessageType.SHORT,
                MessageType.DWORD,
                MessageType.INT,
                MessageType.DWORD64,
                MessageType.INT64,
                MessageType.OBJECT_ID,
            }:
                return f"typeof({source}) == TYPE_INT"
            if mt in {MessageType.FLOAT, MessageType.DOUBLE}:
                return f"typeof({source}) == TYPE_FLOAT"
            if mt in {MessageType.STRING, MessageType.RESREF}:
                return f"typeof({source}) == TYPE_STRING"
        return "false"

    def _render_size_hint(self, size_hint: Any, receiver: str) -> str:
        if size_hint is None:
            raise UnsupportedMessageError(
                "missing size hint for generated list/bytes field"
            )
        if isinstance(size_hint, SizePrefix):
            return self._read_scalar(
                AgnosticField(
                    name="",
                    kind=FieldKind.PRIMITIVE,
                    wire_type=size_hint.value,
                )
            )
        if isinstance(size_hint, TwoDARowCountHint):
            return f"context.get_twoda_row_count({json.dumps(size_hint.twoda_name)})"
        if isinstance(size_hint, FixedSizeHint):
            return str(size_hint.size)
        if isinstance(size_hint, ComputedMultiplySizeHint):
            return f"{self._safe_field_ref(receiver, size_hint.field1)} * {self._safe_field_ref(receiver, size_hint.field2)}"
        if isinstance(size_hint, ComputedAddSizeHint):
            return f"{self._safe_field_ref(receiver, size_hint.field1)} + {self._safe_field_ref(receiver, size_hint.field2)}"
        if isinstance(size_hint, BuildSizeHint):
            return f"{size_hint.new} if context.satisfies({size_hint.build}, {size_hint.patch}, {size_hint.postfix}) else {size_hint.old}"
        raise UnsupportedMessageError(
            f"unsupported size hint {type(size_hint).__name__}"
        )

    def _render_slot(
        self, value: int | str | TwoDARowCountHint | None, receiver: str
    ) -> str:
        if value is None:
            raise UnsupportedMessageError("missing slot/count expression")
        if isinstance(value, int):
            return str(value)
        if isinstance(value, TwoDARowCountHint):
            return f"context.get_twoda_row_count({json.dumps(value.twoda_name)})"
        return self._safe_field_ref(receiver, value)

    def _safe_field_ref(self, receiver: str, field_name: str) -> str:
        safe = FIELD_NAME_OVERRIDES.get(field_name, field_name)
        return f"{receiver}.{safe}"

    @staticmethod
    def _wrap_conditions(lines: list[str], conditions: list[str]) -> list[str]:
        wrapped = list(lines)
        for condition in reversed(conditions):
            wrapped = [f"if {condition}:"] + [f"    {line}" for line in wrapped]
        return wrapped

    def _new_temp(self, stem: str) -> str:
        self._temp_counter += 1
        return f"_{stem}_{self._temp_counter}"

    @staticmethod
    def _indent(lines: list[str], *, prefix: str) -> list[str]:
        return [f"{prefix}{line}" if line else "" for line in lines]

    @staticmethod
    def _join(sections: list[list[str]]) -> str:
        return "\n\n".join("\n".join(section) for section in sections if section) + "\n"


# ---------------------------------------------------------------------------
# Flimsy hack: _field_name_map so custom-io stub naming can look up helpers
# that have custom IO.  Set before render_custom if needed.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Module-level export functions
# ---------------------------------------------------------------------------

_renderer_global: _GodotRenderer | None = None


def _get_renderer(
    global_registry: TypeRegistry | None = None,
    module_registry: TypeRegistry | None = None,
) -> _GodotRenderer:
    return _GodotRenderer(
        global_registry=global_registry,
        module_registry=module_registry,
    )


def render_message_source(
    resolved: ResolvedMessage,
    global_registry: TypeRegistry | None = None,
    module_registry: TypeRegistry | None = None,
) -> str:
    """Render a message file from its resolved representation."""
    renderer = _get_renderer(global_registry, module_registry)
    return renderer.render_message(resolved)


def render_shared_types_source(
    resolved: ResolvedMessage,
    module: str,
    global_registry: TypeRegistry | None = None,
) -> str:
    """Render a shared-types file from its resolved representation."""
    renderer = _get_renderer(global_registry=global_registry)
    return renderer.render_shared(resolved, module)


def render_custom_source(
    resolved: ResolvedMessage,
    global_registry: TypeRegistry | None = None,
    module_registry: TypeRegistry | None = None,
) -> str:
    """Render a custom-io companion stub file."""
    renderer = _get_renderer(global_registry, module_registry)
    return renderer.render_custom(resolved)


# ---------------------------------------------------------------------------
# Default value helper
# ---------------------------------------------------------------------------


def field_default(field: AgnosticField) -> str:
    """Language-agnostic default → GDScript literal."""
    if field.kind in {FieldKind.TUPLE, FieldKind.LIST, FieldKind.BITMASK_LIST}:
        return "[]"
    if field.kind == FieldKind.BYTES:
        return "PackedByteArray()"
    if field.kind == FieldKind.LOCSTRING:
        return "null"
    if field.kind in {FieldKind.DATACLASS, FieldKind.TAGGED}:
        return "null"

    mt = field.wire_type
    if mt is None:
        return "null"
    if mt == MessageType.BOOL:
        return "false"
    if mt in {
        MessageType.BYTE,
        MessageType.CHAR,
        MessageType.WORD,
        MessageType.SHORT,
        MessageType.DWORD,
        MessageType.INT,
        MessageType.DWORD64,
        MessageType.INT64,
        MessageType.OBJECT_ID,
        MessageType.BITS,
    }:
        return "0"
    if mt in {MessageType.FLOAT, MessageType.DOUBLE}:
        return "0.0"
    if mt in {MessageType.STRING, MessageType.RESREF}:
        return '""'
    return "null"


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def _default_bit_count(size_prefix: SizePrefix) -> int:
    if size_prefix == SizePrefix.BYTE:
        return 8
    if size_prefix == SizePrefix.WORD:
        return 16
    if size_prefix in {SizePrefix.INT, SizePrefix.DWORD}:
        return 32
    raise UnsupportedMessageError("unsupported bitmask size prefix")


def _replace(field: AgnosticField, **kwargs) -> AgnosticField:
    """Return a copy of *field* with selected attributes replaced."""
    d = {f.name: getattr(field, f.name) for f in dc_fields(field)}
    d.update(kwargs)
    return AgnosticField(**d)


HELPER_FILE_SOURCE = open(
    os.path.join(_HELPER_DIR, HELPER_FILE_NAME), encoding="utf-8"
).read()
