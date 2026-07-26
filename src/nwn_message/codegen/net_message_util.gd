# SPDX-License-Identifier: GPL-3.0-or-later

class_name NetMessageUtil

const STRREF_NONE: int = 0xFFFFFFFF

enum MessageType {
    BITS = 1,
    BOOL = 2,
    BYTE = 3,
    CHAR = 4,
    WORD = 5,
    SHORT = 6,
    DWORD = 7,
    INT = 8,
    DWORD64 = 9,
    INT64 = 10,
    FLOAT = 11,
    DOUBLE = 12,
    RESREF = 13,
    STRING = 14,
    VOIDPTR = 15,
    JSON = 16,
    OBJECT_ID = 17,
    LOCSTRING = 18,
}


class LocString:
    var text: String = ""
    var str_ref: int = STRREF_NONE
    var gender: int = 0
    var has_str_ref: bool = false

    func _to_string() -> String:
        if text != "":
            return text
        if has_str_ref:
            return "<strref:%d>" % str_ref
        return ""


class Reader:
    var _buf: PackedByteArray = PackedByteArray()
    var _pos: int = 0
    var _failed: bool = false
    var _error_message: String = ""
    var _error_pos: int = -1
    var context = null

    func _init(source, initial_context = null):
        context = initial_context
        if source is StreamPeerBuffer:
            _buf = NetMessageUtil.read_bytes(source, source.get_available_bytes())
        elif typeof(source) == TYPE_PACKED_BYTE_ARRAY:
            _buf = source
        else:
            push_error("Unsupported NetMessageUtil.Reader source: %s" % [source])
            _buf = PackedByteArray()

    func more() -> bool:
        return not _failed and _pos < _buf.size()

    func tell() -> int:
        return _pos

    func seek(pos: int) -> void:
        _pos = clampi(pos, 0, _buf.size())
        _failed = false
        _error_message = ""
        _error_pos = -1

    func at_end() -> bool:
        return not _failed and _pos >= _buf.size()

    func len() -> int:
        return _buf.size()

    func failed() -> bool:
        return _failed

    func error_message() -> String:
        return _error_message

    func error_pos() -> int:
        return _error_pos if _error_pos >= 0 else _pos

    func _fail(message: String, pos: int = -1) -> void:
        if _failed:
            return

        _failed = true
        _error_message = message
        _error_pos = pos if pos >= 0 else _pos
        push_error(message)
        _pos = _buf.size()

    func _need(count: int) -> void:
        if _failed:
            return
        if _pos + count > _buf.size():
            _fail(
                (
                    "Message truncated at pos %d: need %d bytes, have %d"
                    % [_pos, count, _buf.size() - _pos]
                ),
                _pos
            )

    func _bytes(count: int) -> PackedByteArray:
        if _failed:
            return PackedByteArray()
        _need(count)
        if _failed or _pos >= _buf.size():
            return PackedByteArray()
        var chunk = NetMessageUtil._slice_bytes(_buf, _pos, count)
        _pos += chunk.size()
        return chunk

    func _u8() -> int:
        var chunk = _bytes(1)
        if chunk.size() == 0:
            return 0
        return chunk[0]

    func _u16() -> int:
        var chunk = _bytes(2)
        if chunk.size() < 2:
            return 0
        return NetMessageUtil._decode_u16(chunk)

    func _u32() -> int:
        var chunk = _bytes(4)
        if chunk.size() < 4:
            return 0
        return NetMessageUtil._decode_u32(chunk)

    func _u64() -> int:
        var chunk = _bytes(8)
        if chunk.size() < 8:
            return 0
        return NetMessageUtil._decode_u64(chunk)

    func _i16() -> int:
        var raw = _u16()
        if raw >= 0x8000:
            raw -= 0x10000
        return raw

    func _i32() -> int:
        var raw = _u32()
        if raw >= 0x80000000:
            raw -= 0x100000000
        return raw

    func _i64() -> int:
        var chunk = _bytes(8)
        if chunk.size() < 8:
            return 0
        return NetMessageUtil._decode_i64(chunk)

    func _read_canary(expected: int) -> bool:
        if _failed:
            return false
        if _pos >= _buf.size():
            _fail("Message truncated at pos %d: need 1 bytes, have 0" % [_pos], _pos)
            return false

        var canary_pos = _pos
        var ty = _buf[_pos]
        _pos += 1
        if ty != expected:
            _fail(
                (
                    "Type mismatch at pos %d: expected %s, got %s"
                    % [
                        canary_pos,
                        NetMessageUtil._message_type_name(expected),
                        NetMessageUtil._message_type_name(ty),
                    ]
                ),
                canary_pos
            )
            return false
        return true

    func read_typed(ty: int):
        match ty:
            MessageType.BOOL:
                return read_bool()
            MessageType.BYTE:
                return read_byte()
            MessageType.CHAR:
                return read_char()
            MessageType.WORD:
                return read_word()
            MessageType.SHORT:
                return read_short()
            MessageType.DWORD:
                return read_dword()
            MessageType.INT:
                return read_int()
            MessageType.DWORD64:
                return read_dword64()
            MessageType.INT64:
                return read_int64()
            MessageType.FLOAT:
                return read_float()
            MessageType.DOUBLE:
                return read_double()
            MessageType.RESREF:
                return read_resref()
            MessageType.STRING:
                return read_string()
            MessageType.VOIDPTR:
                return read_bytes()
            MessageType.JSON:
                return read_json()
            MessageType.OBJECT_ID:
                return read_object_id()
            MessageType.LOCSTRING:
                return read_locstring()
            _:
                _fail("Unsupported typed read: %s" % [ty])
                return null

    func read_bool() -> bool:
        if not _read_canary(MessageType.BOOL):
            return false
        return _u8() != 0

    func read_byte(bits: int = 8) -> int:
        if not _read_canary(MessageType.BYTE):
            return 0
        return _u8()

    func read_char(bits: int = 8) -> int:
        if not _read_canary(MessageType.CHAR):
            return 0
        var value = _u8()
        return value if value < 128 else value - 256

    func read_word(bits: int = 16) -> int:
        if not _read_canary(MessageType.WORD):
            return 0
        return _u16()

    func read_short(bits: int = 16) -> int:
        if not _read_canary(MessageType.SHORT):
            return 0
        return _i16()

    func read_dword(bits: int = 32) -> int:
        if not _read_canary(MessageType.DWORD):
            return 0
        return _u32()

    func read_int(bits: int = 32) -> int:
        if not _read_canary(MessageType.INT):
            return 0
        return _i32()

    func read_dword64(bits: int = 64) -> int:
        if not _read_canary(MessageType.DWORD64):
            return 0
        return _u64()

    func read_int64(bits: int = 64) -> int:
        if not _read_canary(MessageType.INT64):
            return 0
        return _i64()

    func read_float(multiplier: float = 1.0, bits: int = 32) -> float:
        if not _read_canary(MessageType.FLOAT):
            return 0.0
        var chunk = _bytes(4)
        if chunk.size() < 4:
            return 0.0
        return NetMessageUtil._decode_float32(chunk)

    func read_float_lim(mn: float, mx: float, bits: int) -> float:
        return read_float()

    func read_double() -> float:
        if not _read_canary(MessageType.DOUBLE):
            return 0.0
        var chunk = _bytes(8)
        if chunk.size() < 8:
            return 0.0
        return NetMessageUtil._decode_double(chunk)

    func read_double_lim(mn: float, mx: float, bits: int = 64) -> float:
        return read_double()

    func read_resref(count: int = 16) -> String:
        if not _read_canary(MessageType.RESREF):
            return ""
        var length = _u8()
        return _bytes(length).get_string_from_utf8()

    func read_string() -> String:
        if not _read_canary(MessageType.STRING):
            return ""
        var length = _u32()
        return _bytes(length).get_string_from_utf8()

    func read_bytes(expected_count: int = -1) -> PackedByteArray:
        if not _read_canary(MessageType.VOIDPTR):
            return PackedByteArray()
        var length = _u32()
        var value = _bytes(length)
        if expected_count >= 0 and length != expected_count:
            push_warning(
                "VOIDPTR payload length %d differs from expected %d" % [length, expected_count]
            )
        return value

    func read_json():
        if not _read_canary(MessageType.JSON):
            return null
        var length = _u32()
        var text = _bytes(length).get_string_from_utf8()
        return JSON.parse_string(text)

    func read_object_id(bits: int = 32) -> int:
        if not _read_canary(MessageType.OBJECT_ID):
            return 0
        return _u32()

    func read_locstring(context_override = null) -> LocString:
        if not _read_canary(MessageType.LOCSTRING):
            return LocString.new()
        var resolved_context = context_override if context_override != null else context
        var value = LocString.new()
        if _u8() != 0:
            value.has_str_ref = true
            value.gender = _u8()
            value.str_ref = _u32()
            if resolved_context != null and resolved_context.has_method("resolve_locstring"):
                value.text = str(resolved_context.resolve_locstring(value.str_ref, value.gender))
            elif resolved_context != null and resolved_context.has_method("resolve_strref"):
                value.text = str(resolved_context.resolve_strref(value.str_ref, value.gender))
            else:
                value.text = "<strref:%d>" % value.str_ref
        else:
            var length = _u32()
            value.text = _bytes(length).get_string_from_utf8()
        return value


class Writer:
    var _buf: PackedByteArray = PackedByteArray()
    var context = null

    func _init(initial_context = null):
        context = initial_context

    func getvalue() -> PackedByteArray:
        return _buf

    func get_data() -> PackedByteArray:
        return _buf

    func finish(stream: StreamPeerBuffer) -> void:
        stream.put_data(_buf)

    func _append_bytes(bytes: PackedByteArray) -> void:
        for byte in bytes:
            _buf.append(byte)

    func _u8(value: int) -> void:
        _buf.append(value & 0xFF)

    func _u16(value: int) -> void:
        _append_bytes(NetMessageUtil._encode_u16(value))

    func _u32(value: int) -> void:
        _append_bytes(NetMessageUtil._encode_u32(value))

    func _u64(value: int) -> void:
        _append_bytes(NetMessageUtil._encode_u64(value))

    func _i16(value: int) -> void:
        _append_bytes(NetMessageUtil._encode_i16(value))

    func _i32(value: int) -> void:
        _append_bytes(NetMessageUtil._encode_i32(value))

    func _i64(value: int) -> void:
        _append_bytes(NetMessageUtil._encode_i64(value))

    func _write_canary(ty: int) -> void:
        _u8(ty)

    func write_typed(value, ty: int) -> void:
        match ty:
            MessageType.BOOL:
                write_bool(value)
            MessageType.BYTE:
                write_byte(value)
            MessageType.CHAR:
                write_char(value)
            MessageType.WORD:
                write_word(value)
            MessageType.SHORT:
                write_short(value)
            MessageType.DWORD:
                write_dword(value)
            MessageType.INT:
                write_int(value)
            MessageType.DWORD64:
                write_dword64(value)
            MessageType.INT64:
                write_int64(value)
            MessageType.FLOAT:
                write_float(value)
            MessageType.DOUBLE:
                write_double(value)
            MessageType.RESREF:
                write_resref(value)
            MessageType.STRING:
                write_string(value)
            MessageType.VOIDPTR:
                write_bytes(value)
            MessageType.JSON:
                write_json(value)
            MessageType.OBJECT_ID:
                write_object_id(value)
            MessageType.LOCSTRING:
                write_locstring(value)
            _:
                push_error("Unsupported typed write: %s" % [ty])

    func write_bool(value: bool) -> void:
        _write_canary(MessageType.BOOL)
        _u8(1 if value else 0)

    func write_byte(value: int, bits: int = 8) -> void:
        if bits != 8:
            NetMessageUtil._warn_numeric_range("BYTE", value, bits, false)
        _write_canary(MessageType.BYTE)
        _u8(value)

    func write_char(value: int, bits: int = 8) -> void:
        if bits != 8:
            NetMessageUtil._warn_numeric_range("CHAR", value, bits, true)
        _write_canary(MessageType.CHAR)
        _u8(value)

    func write_word(value: int, bits: int = 16) -> void:
        if bits != 16:
            NetMessageUtil._warn_numeric_range("WORD", value, bits, false)
        _write_canary(MessageType.WORD)
        _u16(value)

    func write_short(value: int, bits: int = 16) -> void:
        if bits != 16:
            NetMessageUtil._warn_numeric_range("SHORT", value, bits, true)
        _write_canary(MessageType.SHORT)
        _i16(value)

    func write_dword(value: int, bits: int = 32) -> void:
        if bits != 32:
            NetMessageUtil._warn_numeric_range("DWORD", value, bits, false)
        _write_canary(MessageType.DWORD)
        _u32(value)

    func write_int(value: int, bits: int = 32) -> void:
        if bits != 32:
            NetMessageUtil._warn_numeric_range("INT", value, bits, true)
        _write_canary(MessageType.INT)
        _i32(value)

    func write_dword64(value: int, bits: int = 64) -> void:
        if bits != 64:
            NetMessageUtil._warn_numeric_range("DWORD64", value, bits, false)
        _write_canary(MessageType.DWORD64)
        _u64(value)

    func write_int64(value: int, bits: int = 64) -> void:
        if bits != 64:
            NetMessageUtil._warn_numeric_range("INT64", value, bits, true)
        _write_canary(MessageType.INT64)
        _i64(value)

    func write_float(value: float, multiplier: float = 1.0, bits: int = 32) -> void:
        NetMessageUtil._warn_quant_float(value, multiplier, bits)
        _write_canary(MessageType.FLOAT)
        _append_bytes(NetMessageUtil._encode_float32(value))

    func write_float_lim(value: float, mn: float, mx: float, bits: int) -> void:
        NetMessageUtil._warn_float_range("FLOAT", value, mn, mx)
        _write_canary(MessageType.FLOAT)
        _append_bytes(NetMessageUtil._encode_float32(value))

    func write_double(value: float) -> void:
        _write_canary(MessageType.DOUBLE)
        _append_bytes(NetMessageUtil._encode_double(value))

    func write_double_lim(value: float, mn: float, mx: float, bits: int = 64) -> void:
        NetMessageUtil._warn_float_range("DOUBLE", value, mn, mx)
        _write_canary(MessageType.DOUBLE)
        _append_bytes(NetMessageUtil._encode_double(value))

    func write_resref(value: String, count: int = 16) -> void:
        _write_canary(MessageType.RESREF)
        var encoded = value.to_utf8_buffer()
        if encoded.size() > count:
            push_warning("ResRef %s exceeds %d bytes and will be truncated" % [value, count])
            encoded = NetMessageUtil._slice_bytes(encoded, 0, count)
        _u8(encoded.size())
        _append_bytes(encoded)

    func write_string(value: String) -> void:
        _write_canary(MessageType.STRING)
        var encoded = value.to_utf8_buffer()
        _u32(encoded.size())
        _append_bytes(encoded)

    func write_bytes(value: PackedByteArray, expected_count: int = -1) -> void:
        _write_canary(MessageType.VOIDPTR)
        if expected_count >= 0 and value.size() != expected_count:
            push_warning(
                (
                    "VOIDPTR payload length %d differs from expected %d"
                    % [value.size(), expected_count]
                )
            )
        _u32(value.size())
        _append_bytes(value)

    func write_json(value) -> void:
        _write_canary(MessageType.JSON)
        var encoded = JSON.stringify(value).to_utf8_buffer()
        _u32(encoded.size())
        _append_bytes(encoded)

    func write_object_id(value: int, bits: int = 32) -> void:
        if bits != 32:
            NetMessageUtil._warn_numeric_range("OBJECT_ID", value, bits, false)
        _write_canary(MessageType.OBJECT_ID)
        _u32(value)

    func write_locstring(value: LocString) -> void:
        _write_canary(MessageType.LOCSTRING)
        if value.has_str_ref:
            _u8(1)
        else:
            _u8(0)
            var encoded = value.text.to_utf8_buffer()
            _u32(encoded.size())
            _append_bytes(encoded)
