"""TypeScript codegen backend.

Consumes the language-agnostic ``ResolvedMessage`` / ``AgnosticField`` trees
and emits TypeScript source code for browser-based NWN message parsing.
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import fields as dc_fields
from typing import Any

from nwn_message.message import (
    BuildSizeHint,
    BuildType,
    ComputedAddSizeHint,
    ComputedMultiplySizeHint,
    FixedSizeHint,
    MessageType,
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

# -----------------------------------------------------------------------
# TypeScript naming configuration
# -----------------------------------------------------------------------

_CLASS_TO_FILE_OVERRIDES: dict[str, str] = {
    "Resource": "resource",
}


def _ts_name(name: str) -> str:
    """PascalCase → camelCase field name."""
    if not name:
        return name
    return name[0].lower() + name[1:]


def _ts_type(
    wire_type: MessageType | None, kind: FieldKind, enum_name: str | None = None
) -> str:
    if kind == FieldKind.ENUM:
        return "number"
    if kind == FieldKind.DATACLASS:
        return enum_name or "unknown"
    if kind == FieldKind.BYTES:
        return "Uint8Array"
    if kind == FieldKind.LOCSTRING:
        return "LocString"
    if kind in {FieldKind.LIST, FieldKind.TUPLE, FieldKind.BITMASK_LIST}:
        return "Array"
    if kind == FieldKind.TAGGED:
        return "unknown"
    # Primitive
    if wire_type is None:
        return "unknown"
    if wire_type == MessageType.BOOL:
        return "boolean"
    if wire_type in {MessageType.DWORD64, MessageType.INT64}:
        return "bigint"
    if wire_type == MessageType.FLOAT or wire_type == MessageType.DOUBLE:
        return "number"
    if wire_type == MessageType.STRING or wire_type == MessageType.RESREF:
        return "string"
    return "number"  # all other int types


def _ts_default(kind: FieldKind, wire_type: MessageType | None) -> str:
    if kind in {FieldKind.TUPLE, FieldKind.LIST, FieldKind.BITMASK_LIST}:
        return "[]"
    if kind == FieldKind.BYTES:
        return "new Uint8Array(0)"
    if kind == FieldKind.LOCSTRING:
        return "makeLocString()"
    if kind in {FieldKind.DATACLASS, FieldKind.TAGGED}:
        return "null"
    if wire_type is None:
        return "null"
    if wire_type == MessageType.BOOL:
        return "false"
    if wire_type in {MessageType.DWORD64, MessageType.INT64}:
        return "0n"
    if wire_type in {MessageType.FLOAT, MessageType.DOUBLE}:
        return "0.0"
    if wire_type in {MessageType.STRING, MessageType.RESREF}:
        return '""'
    return "0"


def _reader_method(wire_type: MessageType | None, bits: int | None = None) -> str:
    if wire_type is None:
        raise UnsupportedMessageError("cannot read field with no wire type")
    return _reader_method_impl(wire_type, bits)


def _reader_method_impl(wire_type: MessageType, bits: int | None = None) -> str:
    b = bits or _full_width(wire_type)
    mt = wire_type
    if mt == MessageType.BOOL:
        return "reader.readBool()"
    if mt == MessageType.BYTE:
        return f"reader.readByte({b})"
    if mt == MessageType.CHAR:
        return f"reader.readChar({b})"
    if mt == MessageType.WORD:
        return f"reader.readWord({b})"
    if mt == MessageType.SHORT:
        return f"reader.readShort({b})"
    if mt == MessageType.DWORD:
        return f"reader.readDword({b})"
    if mt == MessageType.INT:
        return f"reader.readInt({b})"
    if mt == MessageType.DWORD64:
        return f"reader.readDword64({b})"
    if mt == MessageType.INT64:
        return f"reader.readInt64({b})"
    if mt == MessageType.FLOAT:
        return f"reader.readFloat(1.0, {b})"
    if mt == MessageType.DOUBLE:
        return "reader.readDouble()"
    if mt == MessageType.STRING:
        return "reader.readString()"
    if mt == MessageType.RESREF:
        return "reader.readResref()"
    if mt == MessageType.JSON:
        return "reader.readJson()"
    if mt == MessageType.OBJECT_ID:
        return f"reader.readObjectId({b})"
    raise UnsupportedMessageError(f"unsupported reader for {mt}")


def _writer_method(
    wire_type: MessageType | None, source: str, bits: int | None = None
) -> str:
    if wire_type is None:
        raise UnsupportedMessageError("cannot write field with no wire type")
    return _writer_method_impl(wire_type, source, bits)


def _writer_method_impl(
    wire_type: MessageType, source: str, bits: int | None = None
) -> str:
    b = bits or _full_width(wire_type)
    mt = wire_type
    if mt == MessageType.BOOL:
        return f"writer.writeBool({source})"
    if mt == MessageType.BYTE:
        return f"writer.writeByte({source}, {b})"
    if mt == MessageType.CHAR:
        return f"writer.writeChar({source}, {b})"
    if mt == MessageType.WORD:
        return f"writer.writeWord({source}, {b})"
    if mt == MessageType.SHORT:
        return f"writer.writeShort({source}, {b})"
    if mt == MessageType.DWORD:
        return f"writer.writeDword({source}, {b})"
    if mt == MessageType.INT:
        return f"writer.writeInt({source}, {b})"
    if mt == MessageType.DWORD64:
        return f"writer.writeDword64({source}, {b})"
    if mt == MessageType.INT64:
        return f"writer.writeInt64({source}, {b})"
    if mt == MessageType.FLOAT:
        return f"writer.writeFloat({source}, 1.0, {b})"
    if mt == MessageType.DOUBLE:
        return f"writer.writeDouble({source})"
    if mt == MessageType.STRING:
        return f"writer.writeString({source})"
    if mt == MessageType.RESREF:
        return f"writer.writeResref({source})"
    if mt == MessageType.JSON:
        return f"writer.writeJson({source})"
    if mt == MessageType.OBJECT_ID:
        return f"writer.writeObjectId({source}, {b})"
    raise UnsupportedMessageError(f"unsupported writer for {mt}")


def _full_width(mt: MessageType) -> int:
    return {
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
    }.get(mt, 32)


# -----------------------------------------------------------------------
# TypeScript renderer
# -----------------------------------------------------------------------


class _TSRenderer:
    """Produces TypeScript source from resolved message / shared-type trees."""

    def __init__(
        self,
        global_registry: TypeRegistry | None = None,
        module_registry: TypeRegistry | None = None,
    ):
        self._global_registry = global_registry
        self._module_registry = module_registry
        self._name_map: dict[str, str] = {}
        self._temp_counter = 0
        self._msg_class_name = ""

    # -- public render entry points ----------------------------------------

    def render_message(self, resolved: ResolvedMessage) -> str:
        """Render a single message type as TypeScript."""
        self._reset(resolved)
        iface_name = resolved.source_class

        imports = ['import { Reader, Writer, MessageType } from "../net_message_util";']
        imports.extend(self._collect_imports(resolved))

        lines: list[str] = []
        lines.extend(imports)
        lines.append("")

        # Enums
        for e in resolved.enums:
            lines.extend(self._render_enum(e))

        # Helper interfaces
        for h in resolved.helpers:
            lines.extend(self._render_helper_interface(h))

        # Message metadata
        direction_str = resolved.direction.value
        lines.append(
            f'export const MSG_{resolved.source_class.upper()} = {{ major: 0x{resolved.major:02X}, minor: 0x{resolved.minor:02X}, direction: "{direction_str}" }};'
        )
        lines.append("")

        # Main interface
        lines.append(f"export interface {iface_name} {{")
        for f in resolved.fields:
            lines.append(
                f"  {_ts_name(f.name)}: {_ts_type(f.wire_type, f.kind, self._resolve_name(f.type_ref or ''))};"
            )
        lines.append("}")
        lines.append("")

        # Read function (skip for custom-io messages)
        if not resolved.custom_io:
            # Recursive read helpers for inner classes
            for h in resolved.helpers:
                lines.extend(self._indent(self._render_helper_read(h), 2))

            lines.append(
                f"export function read{iface_name}(reader: Reader): {iface_name} {{"
            )
            body = self._emit_read_body(resolved.fields, "obj")
            lines.append(f"  const obj: {iface_name} = {{}} as {iface_name};")
            for line in body:
                lines.append(f"  {line}")
            lines.append("  return obj;")
            lines.append("}")
            lines.append("")

            # Write function
            lines.append(
                f"export function write{iface_name}(writer: Writer, msg: {iface_name}): void {{"
            )
            body = self._emit_write_body(resolved.fields, "msg")
            for line in body:
                lines.append(f"  {line}")
            lines.append("}")
            lines.append("")

        return "\n".join(lines)

    def render_shared(self, resolved: ResolvedMessage, module: str) -> str:
        """Render a shared-types module."""
        self._reset(resolved)

        imports = [
            'import { Reader, Writer, LocString, makeLocString, MessageType } from "../net_message_util";'
        ]
        lines: list[str] = []
        lines.extend(imports)
        lines.append("")

        for e in resolved.enums:
            lines.extend(self._render_enum(e))
        for h in resolved.helpers:
            lines.extend(self._render_helper_interface(h))
            lines.extend(self._render_helper_read(h))
            lines.extend(self._render_helper_write(h))

        return "\n".join(lines)

    def render_custom(self, resolved: ResolvedMessage) -> str:
        """Not applicable for TS (no companion stub concept)."""
        return ""

    def _render_enum(self, enum_def: EnumDef) -> list[str]:
        gd_name = self._resolve_name(enum_def.name)
        lines = [f"export const enum {gd_name} {{"]
        for name, value in enum_def.values:
            lines.append(f"  {name} = {value},")
        lines.append("}")
        lines.append("")
        return lines

    def _render_helper_interface(self, helper: HelperClass) -> list[str]:
        iface_name = self._resolve_name(helper.name)
        lines = [f"export interface {iface_name} {{"]
        for f in helper.fields:
            lines.append(
                f"  {_ts_name(f.name)}: {_ts_type(f.wire_type, f.kind, self._resolve_name(f.type_ref or ''))};"
            )
        lines.append("}")
        lines.append("")
        return lines

    def _render_helper_read(self, helper: HelperClass) -> list[str]:
        iface_name = self._resolve_name(helper.name)
        lines: list[str] = []
        if helper.custom_io:
            return lines  # skip — custom IO is not generated
        lines.append(f"function _read{iface_name}(reader: Reader): {iface_name} {{")
        body = self._emit_read_body(helper.fields, "obj")
        lines.append(f"  const obj = {{}} as {iface_name};")
        for line in body:
            lines.append(f"  {line}")
        lines.append("  return obj;")
        lines.append("}")
        lines.append("")
        return lines

    def _render_helper_write(self, helper: HelperClass) -> list[str]:
        iface_name = self._resolve_name(helper.name)
        lines: list[str] = []
        if helper.custom_io:
            return lines
        lines.append(
            f"function _write{iface_name}(writer: Writer, msg: {iface_name}): void {{"
        )
        body = self._emit_write_body(helper.fields, "msg")
        for line in body:
            lines.append(f"  {line}")
        lines.append("}")
        lines.append("")
        return lines

    # -- internal ----------------------------------------------------------

    def _reset(self, resolved: ResolvedMessage) -> None:
        self._name_map.clear()
        self._temp_counter = 0
        self._msg_class_name = resolved.source_class

        # Simple naming: just use the qualname last part
        for h in resolved.helpers:
            short = h.py_type.__qualname__.rsplit(".", 1)[-1]
            self._name_map[h.name] = short
        for e in resolved.enums:
            short = e.py_type.__qualname__.rsplit(".", 1)[-1]
            self._name_map[e.name] = short

    def _resolve_name(self, qualname: str) -> str:
        return self._name_map.get(qualname, qualname.rsplit(".", 1)[-1])

    def _collect_imports(self, resolved: ResolvedMessage) -> list[str]:
        """Collect imports for referenced shared types."""
        imports: set[str] = set()
        for f in resolved.fields:
            if f.type_ref and f.type_ref not in self._name_map:
                # External type — need to import
                short = f.type_ref.rsplit(".", 1)[-1]
                if short not in imports:
                    imports.add(short)
        return [f'import {{ {name} }} from "./{name}";' for name in sorted(imports)]

    def _emit_read_body(self, fields: list[AgnosticField], receiver: str) -> list[str]:
        lines: list[str] = []
        for f in fields:
            lines.extend(self._emit_read_field(f, receiver))
        return lines

    def _emit_write_body(self, fields: list[AgnosticField], receiver: str) -> list[str]:
        lines: list[str] = []
        for f in fields:
            lines.extend(self._emit_write_field(f, receiver))
        return lines

    def _emit_read_field(self, field: AgnosticField, receiver: str) -> list[str]:
        conditions = [self._render_condition(c, receiver) for c in field.conditionals]
        body = self._emit_field_read_body(field, receiver)
        return self._wrap_conditions(body, conditions)

    def _emit_write_field(self, field: AgnosticField, receiver: str) -> list[str]:
        conditions = [self._render_condition(c, receiver) for c in field.conditionals]
        body = self._emit_field_write_body(field, receiver)
        return self._wrap_conditions(body, conditions)

    def _emit_field_read_body(self, field: AgnosticField, receiver: str) -> list[str]:
        target = f"{receiver}.{_ts_name(field.name)}"
        body = self._emit_read_assignment(target, field, receiver)
        if field.bool_prefix:
            body = ["if (reader.readBool()) {"] + [f"  {line}" for line in body] + ["}"]
        return body

    def _emit_field_write_body(self, field: AgnosticField, receiver: str) -> list[str]:
        source = f"{receiver}.{_ts_name(field.name)}"
        body = self._emit_write_assignment(source, field, receiver)
        if field.bool_prefix:
            has_var = self._new_temp("has")
            body = (
                [
                    f"const {has_var} = isTruthy({source});",
                    f"writer.writeBool({has_var});",
                    f"if ({has_var}) {{",
                ]
                + [f"  {line}" for line in body]
                + ["}"]
            )
        return body

    def _emit_read_assignment(
        self, target: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        kind = field.kind
        if kind == FieldKind.PRIMITIVE:
            return [f"{target} = {_reader_method(field.wire_type, field.bits)};"]
        if kind == FieldKind.ENUM:
            return [f"{target} = {_reader_method(field.wire_type, field.bits)};"]
        if kind == FieldKind.DATACLASS:
            name = self._resolve_name(field.type_ref or "")
            return [f"{target} = _read{name}(reader);"]
        if kind == FieldKind.BYTES:
            size_expr = self._render_size_hint(field.size_hint, receiver)
            return [f"{target} = reader.readBytes({size_expr});"]
        if kind == FieldKind.LOCSTRING:
            return [f"{target} = reader.readLocString();"]
        if kind == FieldKind.TUPLE:
            temp = self._new_temp("tuple")
            lines: list[str] = [f"const {temp}: unknown[] = [];"]
            assert field.elements is not None
            for elem in field.elements:
                lines.extend(self._emit_read_append(temp, elem, receiver))
            lines.append(f"{target} = {temp};")
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
            return [f"{_writer_method(field.wire_type, source, field.bits)};"]
        if kind == FieldKind.ENUM:
            return [f"{_writer_method(field.wire_type, source, field.bits)};"]
        if kind == FieldKind.DATACLASS:
            name = self._resolve_name(field.type_ref or "")
            return [
                f"if ({source} != null) {{",
                f"  _write{name}(writer, {source});",
                "}",
            ]
        if kind == FieldKind.BYTES:
            return self._emit_write_bytes(source, field, receiver)
        if kind == FieldKind.LOCSTRING:
            return [f"writer.writeLocString({source});"]
        if kind == FieldKind.TUPLE:
            return self._emit_write_tuple(source, field, receiver)
        if kind == FieldKind.LIST:
            return self._emit_write_list(source, field, receiver)
        if kind == FieldKind.BITMASK_LIST:
            return self._emit_write_bitmask_list(source, field, receiver)
        if kind == FieldKind.TAGGED:
            return self._emit_write_tagged(source, field, receiver)
        raise UnsupportedMessageError(f"unsupported write kind: {kind}")

    # -- compound read dispatches ------------------------------------------

    def _emit_read_list(
        self, target: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        count_var = self._new_temp("count")
        temp = self._new_temp("items")
        lines = [
            f"const {count_var} = {self._render_size_hint(field.size_hint, receiver)};"
        ]
        lines.append(f"const {temp}: unknown[] = [];")
        lines.append(
            f"for (let _{temp}_i = 0; _{temp}_i < {count_var}; _{temp}_i++) {{"
        )
        assert field.element is not None
        for nested in self._emit_read_append(temp, field.element, receiver):
            lines.append(f"  {nested}")
        lines.append("}")
        lines.append(f"{target} = {temp};")
        return lines

    def _emit_read_append(
        self, array_name: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        kind = field.kind
        if kind in {FieldKind.PRIMITIVE, FieldKind.ENUM}:
            if field.build_type is None:
                return [
                    f"{array_name}.push({_reader_method(field.wire_type, field.bits)});"
                ]
            then_render = _replace(field, wire_type=field.build_type.then)
            default_render = _replace(field, wire_type=field.build_type.default)
            return self._emit_build_branch(
                field.build_type,
                [
                    f"{array_name}.push({_reader_method(then_render.wire_type, then_render.bits)});"
                ],
                [
                    f"{array_name}.push({_reader_method(default_render.wire_type, default_render.bits)});"
                ],
            )
        if kind == FieldKind.DATACLASS:
            name = self._resolve_name(field.type_ref or "")
            return [f"{array_name}.push(_read{name}(reader));"]
        if kind == FieldKind.BYTES:
            size_expr = self._render_size_hint(field.size_hint, receiver)
            return [f"{array_name}.push(reader.readBytes({size_expr}));"]
        if kind == FieldKind.LOCSTRING:
            return [f"{array_name}.push(reader.readLocString());"]
        if kind == FieldKind.TUPLE:
            temp = self._new_temp("tuple")
            lines = [f"const {temp}: unknown[] = [];"]
            assert field.elements is not None
            for elem in field.elements:
                lines.extend(self._emit_read_append(temp, elem, receiver))
            lines.append(f"{array_name}.push({temp});")
            return lines
        if kind in {FieldKind.LIST, FieldKind.BITMASK_LIST}:
            temp = self._new_temp("nested")
            lines = [f"let {temp}: unknown[] = [];"]
            if kind == FieldKind.LIST:
                lines.extend(self._emit_read_list(temp, field, receiver))
            else:
                lines.extend(self._emit_read_bitmask_list(temp, field, receiver))
            lines.append(f"{array_name}.push({temp});")
            return lines
        if kind == FieldKind.TAGGED:
            temp = self._new_temp("tagged")
            lines = [f"let {temp}: unknown = null;"]
            lines.extend(self._emit_read_tagged(temp, field, receiver))
            lines.append(f"{array_name}.push({temp});")
            return lines
        raise UnsupportedMessageError(f"unsupported read append kind: {kind}")

    def _emit_read_bitmask_list(
        self, target: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        assert field.bitmask_size_prefix is not None
        flags_var = self._new_temp("flags")
        temp = self._new_temp("items")
        lines = [
            f"const {flags_var} = {_reader_method(field.bitmask_size_prefix.value, 0)};"
        ]
        lines.append(f"const {temp}: unknown[] = [];")
        lines.append(
            f"for (let _{temp}_i = 0; _{temp}_i < {self._render_slot(field.bitmask_max_slots, receiver)}; _{temp}_i++) {{"
        )
        lines.append(f"  if (({flags_var} & (1 << _{temp}_i)) !== 0) {{")
        assert field.bitmask_element is not None
        for nested in self._emit_read_append(
            "  " + temp, field.bitmask_element, receiver
        ):
            lines.append(f"    {nested}")
        lines.append("  } else {")
        lines.append(f"    {temp}.push(null);")
        lines.append("  }")
        lines.append("}")
        lines.append(f"{target} = {temp};")
        return lines

    def _emit_read_tagged(
        self, target: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        discriminator = self._new_temp("tag")
        lines = [
            f"const {discriminator} = {self._read_discriminator(field, receiver)};",
            f"switch ({discriminator}) {{",
        ]
        assert field.tagged_variants is not None
        for variant in field.tagged_variants:
            lines.append(f"  case {variant.key}: {{")
            for nested in self._emit_read_assignment(target, variant.field, receiver):
                lines.append(f"    {nested}")
            lines.append("    break;")
            lines.append("  }")
        lines.append("  default:")
        lines.append('    reader.fail("Unsupported tagged discriminator");')
        lines.append("}")
        return lines

    # -- compound write dispatches -----------------------------------------

    def _emit_write_list(
        self, source: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        lines: list[str] = []
        if isinstance(field.size_hint, SizePrefix):
            lines.append(
                f"{_writer_method(field.size_hint.value, f'{source}.length', 0)};"
            )
        loop_var = self._new_temp("item")
        lines.append(f"for (const {loop_var} of {source}) {{")
        assert field.element is not None
        for nested in self._emit_write_item(loop_var, field.element, receiver):
            lines.append(f"  {nested}")
        lines.append("}")
        return lines

    def _emit_write_item(
        self, source: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        kind = field.kind
        if kind in {FieldKind.PRIMITIVE, FieldKind.ENUM}:
            payload = source if kind == FieldKind.PRIMITIVE else source
            if field.build_type is None:
                return [f"{_writer_method(field.wire_type, payload, field.bits)};"]
            then_render = _replace(field, wire_type=field.build_type.then)
            default_render = _replace(field, wire_type=field.build_type.default)
            return self._emit_build_branch(
                field.build_type,
                [
                    f"{_writer_method(then_render.wire_type, payload, then_render.bits)};"
                ],
                [
                    f"{_writer_method(default_render.wire_type, payload, default_render.bits)};"
                ],
            )
        if kind == FieldKind.DATACLASS:
            name = self._resolve_name(field.type_ref or "")
            return [
                f"if ({source} != null) {{",
                f"  _write{name}(writer, {source});",
                "}",
            ]
        if kind == FieldKind.BYTES:
            return self._emit_write_bytes(source, field, receiver)
        if kind == FieldKind.LOCSTRING:
            return [f"writer.writeLocString({source});"]
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
        lines: list[str] = []
        assert field.elements is not None
        for index, nested in enumerate(field.elements):
            lines.extend(self._emit_write_item(f"{source}[{index}]", nested, receiver))
        return lines

    def _emit_write_tagged(
        self, source: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        lines: list[str] = []
        assert field.tagged_variants is not None
        for index, variant in enumerate(field.tagged_variants):
            keyword = "if" if index == 0 else "} else if"
            lines.append(
                f"{keyword} ({self._render_tagged_condition(source, variant.field)}) {{"
            )
            if field.tagged_discriminator_type is not None:
                lines.append(f"  {self._write_discriminator(field, variant.key)};")
            for nested in self._emit_write_assignment(source, variant.field, receiver):
                lines.append(f"  {nested}")
        lines.append("} else {")
        lines.append('  console.error("Unsupported tagged runtime type");')
        lines.append("}")
        return lines

    def _emit_write_bitmask_list(
        self, source: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        assert field.bitmask_size_prefix is not None
        flags_var = self._new_temp("flags")
        item_var = self._new_temp("item")
        max_slots = self._render_slot(field.bitmask_max_slots, receiver)
        lines = [f"let {flags_var} = 0;"]
        lines.append(
            f"for (let _{item_var}_i = 0; _{item_var}_i < {max_slots}; _{item_var}_i++) {{"
        )
        lines.append(
            f"  const {item_var} = _{item_var}_i < {source}.length ? {source}[_{item_var}_i] : null;"
        )
        lines.append(f"  if ({item_var} != null) {{")
        lines.append(f"    {flags_var} |= 1 << _{item_var}_i;")
        lines.append("  }")
        lines.append("}")
        lines.append(
            f"{_writer_method(field.bitmask_size_prefix.value, flags_var, 0)};"
        )
        lines.append(
            f"for (let _{item_var}_i = 0; _{item_var}_i < {max_slots}; _{item_var}_i++) {{"
        )
        lines.append(
            f"  const {item_var} = _{item_var}_i < {source}.length ? {source}[_{item_var}_i] : null;"
        )
        lines.append(f"  if ({item_var} != null) {{")
        assert field.bitmask_element is not None
        for nested in self._emit_write_item(item_var, field.bitmask_element, receiver):
            lines.append(f"    {nested}")
        lines.append("  }")
        lines.append("}")
        return lines

    def _emit_write_bytes(
        self, source: str, field: AgnosticField, receiver: str
    ) -> list[str]:
        lines: list[str] = []
        if isinstance(field.size_hint, SizePrefix):
            lines.append(
                f"{_writer_method(field.size_hint.value, f'{source}.length', 0)};"
            )
            lines.append(f"writer.writeBytes({source});")
            return lines
        if field.size_hint is None:
            lines.append(f"writer.writeBytes({source});")
            return lines
        lines.append(
            f"writer.writeBytes({source}, {self._render_size_hint(field.size_hint, receiver)});"
        )
        return lines

    # -- build-type runtime branching --------------------------------------

    @staticmethod
    def _emit_build_branch(
        build_type: BuildType, then_lines: list[str], default_lines: list[str]
    ) -> list[str]:
        condition = f"context.satisfies({build_type.if_build[0]}, {build_type.if_build[1]}, {build_type.if_build[2]})"
        return (
            [f"if ({condition}) {{"]
            + [f"  {line}" for line in then_lines]
            + ["} else {"]
            + [f"  {line}" for line in default_lines]
            + ["}"]
        )

    # -- formatting helpers -------------------------------------------------

    def _render_condition(self, cond: ConditionInfo, receiver: str) -> str:
        field_ref = f"{receiver}.{_ts_name(cond.field)}"
        if cond.op == "flag":
            return f"({field_ref} & {self._render_literal(cond.value)})"
        if cond.op == "eq":
            return f"{field_ref} === {self._render_literal(cond.value)}"
        if cond.op == "ne":
            return f"{field_ref} !== {self._render_literal(cond.value)}"
        if cond.op == "gt":
            return f"{field_ref} > {self._render_literal(cond.value)}"
        if cond.op == "in":
            values = ", ".join(
                self._render_literal(v) for v in sorted(cond.value, key=repr)
            )
            return f"[{values}].includes({field_ref})"
        if cond.op == "not_in":
            values = ", ".join(
                self._render_literal(v) for v in sorted(cond.value, key=repr)
            )
            return f"![{values}].includes({field_ref})"
        if cond.op == "twoda":
            twoda, column, values = cond.value
            values_list = ", ".join(
                self._render_literal(v) for v in sorted(values, key=repr)
            )
            return f"[{values_list}].includes(String(context.getTwodaValue({json.dumps(twoda)}, {field_ref}, {json.dumps(column)})))"
        if cond.op == "build":
            build, patch, postfix = cond.value
            return f"context.satisfies({build}, {patch}, {postfix})"
        if cond.op == "not_build":
            build, patch, postfix = cond.value
            return f"!context.satisfies({build}, {patch}, {postfix})"
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
            name = self._resolve_name(field.type_ref or "")
            return f"{source} instanceof {name}Type"
        if field.kind == FieldKind.LOCSTRING:
            return f"typeof {source} === 'object' && {source} !== null && 'text' in {source}"
        if field.kind in {FieldKind.BYTES}:
            return f"{source} instanceof Uint8Array"
        if field.kind in {FieldKind.LIST, FieldKind.TUPLE, FieldKind.BITMASK_LIST}:
            return f"Array.isArray({source})"
        if field.kind == FieldKind.ENUM:
            return f"typeof {source} === 'number'"
        if field.kind == FieldKind.PRIMITIVE:
            mt = field.wire_type
            if mt == MessageType.BOOL:
                return f"typeof {source} === 'boolean'"
            if mt in {MessageType.DWORD64, MessageType.INT64}:
                return f"typeof {source} === 'bigint'"
            if mt in {MessageType.FLOAT, MessageType.DOUBLE}:
                return f"typeof {source} === 'number'"
            if mt in {MessageType.STRING, MessageType.RESREF}:
                return f"typeof {source} === 'string'"
            return f"typeof {source} === 'number'"
        return "false"

    def _render_size_hint(self, size_hint: Any, receiver: str) -> str:
        if size_hint is None:
            raise UnsupportedMessageError("missing size hint for list/bytes field")
        if isinstance(size_hint, SizePrefix):
            return _reader_method(size_hint.value, 0)
        if isinstance(size_hint, TwoDARowCountHint):
            return f"context.getTwodaRowCount({json.dumps(size_hint.twoda_name)})"
        if isinstance(size_hint, FixedSizeHint):
            return str(size_hint.size)
        if isinstance(size_hint, ComputedMultiplySizeHint):
            return f"{receiver}.{_ts_name(size_hint.field1)} * {receiver}.{_ts_name(size_hint.field2)}"
        if isinstance(size_hint, ComputedAddSizeHint):
            return f"{receiver}.{_ts_name(size_hint.field1)} + {receiver}.{_ts_name(size_hint.field2)}"
        if isinstance(size_hint, BuildSizeHint):
            return f"context.satisfies({size_hint.build}, {size_hint.patch}, {size_hint.postfix}) ? {size_hint.new} : {size_hint.old}"
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
            return f"context.getTwodaRowCount({json.dumps(value.twoda_name)})"
        return f"{receiver}.{_ts_name(value)}"

    def _read_discriminator(self, field: AgnosticField, receiver: str) -> str:
        if field.tagged_twoda_name is not None:
            assert field.tagged_twoda_field is not None
            assert field.tagged_twoda_column is not None
            ref = f"{receiver}.{_ts_name(field.tagged_twoda_field)}"
            return f"Number(context.getTwodaValue({json.dumps(field.tagged_twoda_name)}, {ref}, {json.dumps(field.tagged_twoda_column)}))"
        assert field.tagged_discriminator_type is not None
        return _reader_method(
            field.tagged_discriminator_type,
            field.tagged_discriminator_bits
            or _full_width(field.tagged_discriminator_type),
        )

    def _write_discriminator(self, field: AgnosticField, value_expr: str) -> str:
        assert field.tagged_discriminator_type is not None
        return _writer_method(
            field.tagged_discriminator_type,
            value_expr,
            field.tagged_discriminator_bits
            or _full_width(field.tagged_discriminator_type),
        )

    @staticmethod
    def _wrap_conditions(lines: list[str], conditions: list[str]) -> list[str]:
        for condition in reversed(conditions):
            lines = [f"if ({condition}) {{"] + [f"  {line}" for line in lines] + ["}"]
        return lines

    def _new_temp(self, stem: str) -> str:
        self._temp_counter += 1
        return f"_{stem}_{self._temp_counter}"

    @staticmethod
    def _indent(lines: list[str], level: int) -> list[str]:
        prefix = "  " * level
        return [f"{prefix}{line}" if line else "" for line in lines]


# -----------------------------------------------------------------------
# Module-level export functions
# -----------------------------------------------------------------------


def render_message_source(
    resolved: ResolvedMessage,
    global_registry: TypeRegistry | None = None,
    module_registry: TypeRegistry | None = None,
) -> str:
    renderer = _TSRenderer(global_registry, module_registry)
    return renderer.render_message(resolved)


def render_shared_types_source(
    resolved: ResolvedMessage,
    module: str,
    global_registry: TypeRegistry | None = None,
) -> str:
    renderer = _TSRenderer(global_registry=global_registry)
    return renderer.render_shared(resolved, module)


def render_custom_source(
    resolved: ResolvedMessage,
    global_registry: TypeRegistry | None = None,
    module_registry: TypeRegistry | None = None,
) -> str:
    return ""


def copy_static_files(output_dir: str) -> None:
    """Copy hand-written runtime .ts files into the generated output directory."""
    src = os.path.join(os.path.dirname(__file__), "typescript")
    for fn in ("net_message_util.ts", "md5.ts"):
        shutil.copy2(os.path.join(src, fn), os.path.join(output_dir, fn))


def render_registry(resolved_messages: list[ResolvedMessage]) -> str:
    """Generate a `registry.ts` that maps (major, minor) → lazy reader imports.

    The client can use this to dynamically import and call the correct reader
    function when a message is received.
    """
    from ._analysis import snake_case

    lines = [
        'import { Reader, Writer } from "../net_message_util";',
        "",
        "export interface RegistryEntry {",
        "  module: string;          // import path (without .js)",
        "  reader?: string;         // exported reader function name (S2C)",
        "  writer?: string;         // exported writer function name (C2S)",
        "  major: number;",
        "  minor: number;",
        "}",
        "",
        "// (major, minor) → entry with optional reader/writer",
        "export const MESSAGE_REGISTRY: Record<number, Record<number, RegistryEntry>> = {",
    ]

    by_major: dict[int, list[tuple[int, str, str | None, str | None]]] = {}
    for msg in resolved_messages:
        if msg.custom_io:
            continue
        file_base = snake_case(msg.source_class)
        reader_fn = None
        writer_fn = None
        dir_val = msg.direction.value
        if dir_val in ("s2c", "both"):
            reader_fn = f"read{msg.source_class}"
        if dir_val in ("c2s", "both"):
            writer_fn = f"write{msg.source_class}"
        if reader_fn is None and writer_fn is None:
            continue
        by_major.setdefault(msg.major, []).append(
            (msg.minor, file_base, reader_fn, writer_fn)
        )

    for major in sorted(by_major):
        lines.append(f"  0x{major:02X}: {{")
        for minor, file_base, reader_fn, writer_fn in sorted(
            by_major[major], key=lambda x: x[0]
        ):
            parts = [
                f'module: "{file_base}"',
                f"major: 0x{major:02X}",
                f"minor: 0x{minor:02X}",
            ]
            if reader_fn:
                parts.append(f'reader: "{reader_fn}"')
            if writer_fn:
                parts.append(f'writer: "{writer_fn}"')
            line = "    " + ", ".join(parts)
            lines.append(f"  0x{minor:02X}: {{ {line} }},")
        lines.append("  },")
    lines.append(
        "};",
    )
    lines.append("")
    return "\n".join(lines) + "\n"


# -----------------------------------------------------------------------
# Utility
# -----------------------------------------------------------------------


def _default_bit_count(size_prefix: SizePrefix) -> int:
    if size_prefix == SizePrefix.BYTE:
        return 8
    if size_prefix == SizePrefix.WORD:
        return 16
    if size_prefix in {SizePrefix.INT, SizePrefix.DWORD}:
        return 32
    raise UnsupportedMessageError("unsupported bitmask size prefix")


def _replace(field: AgnosticField, **kwargs) -> AgnosticField:
    d = {f.name: getattr(field, f.name) for f in dc_fields(field)}
    d.update(kwargs)
    return AgnosticField(**d)
