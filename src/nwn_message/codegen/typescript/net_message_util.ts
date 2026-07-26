// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Runtime library for NWN binary message parsing (TypeScript port).
 *
 * Provides Reader/Writer classes that handle NWN's type-canary wire format:
 *   each value is preceded by a 1-byte MessageType canary, followed by
 *   the value's little-endian binary encoding.
 *
 * BigInt is used for 64-bit integer types (DWORD64, INT64) to avoid
 * precision loss.
 */

/* eslint-disable @typescript-eslint/no-unused-vars */

// -----------------------------------------------------------------------
// MessageType enum
// -----------------------------------------------------------------------

export const enum MessageType {
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

// -----------------------------------------------------------------------
// LocString
// -----------------------------------------------------------------------

export const STRREF_NONE = 0xffffffff;

export interface LocString {
  text: string;
  strRef: number;
  gender: number;
  hasStrRef: boolean;
}

export function makeLocString(
  text = "",
  strRef = STRREF_NONE,
  gender = 0,
  hasStrRef = false,
): LocString {
  return { text, strRef, gender, hasStrRef };
}

// -----------------------------------------------------------------------
// Reader
// -----------------------------------------------------------------------

export class Reader {
  private buf: Uint8Array;
  private pos = 0;
  failed = false;
  errorMessage = "";

  constructor(source: ArrayBuffer | Uint8Array) {
    this.buf = source instanceof Uint8Array ? source : new Uint8Array(source);
  }

  get atEnd(): boolean {
    return !this.failed && this.pos >= this.buf.length;
  }

  get remaining(): number {
    return this.buf.length - this.pos;
  }

  /** Read position (for debugging). */
  tell(): number {
    return this.pos;
  }

  // -- internal helpers --------------------------------------------------

  private need(count: number): void {
    if (this.failed) return;
    if (this.pos + count > this.buf.length) {
      this.fail(
        `Message truncated at pos ${this.pos}: need ${count} bytes, have ${this.buf.length - this.pos}`,
        this.pos,
      );
    }
  }

  private bytes(count: number): Uint8Array {
    if (this.failed) return new Uint8Array(0);
    this.need(count);
    if (this.failed) return new Uint8Array(0);
    const chunk = this.buf.subarray(this.pos, this.pos + count);
    this.pos += chunk.length;
    return chunk;
  }

  private u8(): number {
    const chunk = this.bytes(1);
    return chunk.length === 0 ? 0 : chunk[0];
  }

  private u16(): number {
    const chunk = this.bytes(2);
    if (chunk.length < 2) return 0;
    return chunk[0] | (chunk[1] << 8);
  }

  private u32(): number {
    const chunk = this.bytes(4);
    if (chunk.length < 4) return 0;
    return (chunk[0] | (chunk[1] << 8) | (chunk[2] << 16) | (chunk[3] << 24)) >>> 0;
  }

  private u64AsBigInt(): bigint {
    const chunk = this.bytes(8);
    if (chunk.length < 8) return 0n;
    const lo = (chunk[0] | (chunk[1] << 8) | (chunk[2] << 16) | (chunk[3] << 24)) >>> 0;
    const hi = (chunk[4] | (chunk[5] << 8) | (chunk[6] << 16) | (chunk[7] << 24)) >>> 0;
    return (BigInt(hi) << 32n) | BigInt(lo);
  }

  private i16(): number {
    const raw = this.u16();
    return raw >= 0x8000 ? raw - 0x10000 : raw;
  }

  private i32(): number {
    const raw = this.u32();
    return raw >= 0x80000000 ? raw - 0x100000000 : raw;
  }

  private i64AsBigInt(): bigint {
    const raw = this.u64AsBigInt();
    if (raw >= 0x8000000000000000n) return raw - 0x10000000000000000n;
    return raw;
  }

  fail(message: string, pos = -1): void {
    if (this.failed) return;
    this.failed = true;
    this.errorMessage = message;
    this.pos = this.buf.length;
  }

  private readCanary(expected: number): boolean {
    if (this.failed) return false;
    if (this.pos >= this.buf.length) {
      this.fail(`Message truncated at pos ${this.pos}: need 1 byte, have 0`, this.pos);
      return false;
    }
    const canaryPos = this.pos;
    const ty = this.buf[this.pos];
    this.pos += 1;
    if (ty !== expected) {
      this.fail(`Type mismatch at pos ${canaryPos}: expected ${expected}, got ${ty}`, canaryPos);
      return false;
    }
    return true;
  }

  // -- typed readers --------------------------------------------------------

  readBool(): boolean {
    if (!this.readCanary(MessageType.BOOL)) return false;
    return this.u8() !== 0;
  }

  readByte(_bits = 8): number {
    if (!this.readCanary(MessageType.BYTE)) return 0;
    return this.u8();
  }

  readChar(_bits = 8): number {
    if (!this.readCanary(MessageType.CHAR)) return 0;
    const v = this.u8();
    return v < 128 ? v : v - 256;
  }

  readWord(_bits = 16): number {
    if (!this.readCanary(MessageType.WORD)) return 0;
    return this.u16();
  }

  readShort(_bits = 16): number {
    if (!this.readCanary(MessageType.SHORT)) return 0;
    return this.i16();
  }

  readDword(_bits = 32): number {
    if (!this.readCanary(MessageType.DWORD)) return 0;
    return this.u32();
  }

  readInt(_bits = 32): number {
    if (!this.readCanary(MessageType.INT)) return 0;
    return this.i32();
  }

  readDword64(_bits = 64): bigint {
    if (!this.readCanary(MessageType.DWORD64)) return 0n;
    return this.u64AsBigInt();
  }

  readInt64(_bits = 64): bigint {
    if (!this.readCanary(MessageType.INT64)) return 0n;
    return this.i64AsBigInt();
  }

  readFloat(_multiplier = 1.0, _bits = 32): number {
    if (!this.readCanary(MessageType.FLOAT)) return 0.0;
    const chunk = this.bytes(4);
    if (chunk.length < 4) return 0.0;
    return decodeFloat32(chunk);
  }

  readFloatLim(_min: number, _max: number, _bits: number): number {
    return this.readFloat();
  }

  readDouble(): number {
    if (!this.readCanary(MessageType.DOUBLE)) return 0.0;
    const chunk = this.bytes(8);
    if (chunk.length < 8) return 0.0;
    return decodeFloat64(chunk);
  }

  readDoubleLim(_min: number, _max: number, _bits = 64): number {
    return this.readDouble();
  }

  readResref(_count = 16): string {
    if (!this.readCanary(MessageType.RESREF)) return "";
    const length = this.u8();
    return decodeUtf8(this.bytes(length));
  }

  readString(): string {
    if (!this.readCanary(MessageType.STRING)) return "";
    const length = this.u32();
    return decodeUtf8(this.bytes(length));
  }

  readBytes(expectedCount = -1): Uint8Array {
    if (!this.readCanary(MessageType.VOIDPTR)) return new Uint8Array(0);
    const length = this.u32();
    const value = this.bytes(length);
    if (expectedCount >= 0 && length !== expectedCount) {
      console.warn(`VOIDPTR payload length ${length} differs from expected ${expectedCount}`);
    }
    return value;
  }

  readJson(): unknown {
    if (!this.readCanary(MessageType.JSON)) return null;
    const length = this.u32();
    const text = decodeUtf8(this.bytes(length));
    return JSON.parse(text);
  }

  readObjectId(_bits = 32): number {
    if (!this.readCanary(MessageType.OBJECT_ID)) return 0;
    return this.u32();
  }

  readLocString(_context?: unknown): LocString {
    if (!this.readCanary(MessageType.LOCSTRING)) return makeLocString();
    const value = makeLocString();
    if (this.u8() !== 0) {
      value.hasStrRef = true;
      value.gender = this.u8();
      value.strRef = this.u32();
      value.text = `<strref:${value.strRef}>`;
    } else {
      const length = this.u32();
      value.text = decodeUtf8(this.bytes(length));
    }
    return value;
  }
}

// -----------------------------------------------------------------------
// Writer
// -----------------------------------------------------------------------

export class Writer {
  private buf: number[] = [];

  getBytes(): Uint8Array {
    return new Uint8Array(this.buf);
  }

  // -- internal helpers --------------------------------------------------

  private u8(value: number): void {
    this.buf.push(value & 0xff);
  }

  private u16(value: number): void {
    this.buf.push(value & 0xff);
    this.buf.push((value >>> 8) & 0xff);
  }

  private u32(value: number): void {
    this.buf.push(value & 0xff);
    this.buf.push((value >>> 8) & 0xff);
    this.buf.push((value >>> 16) & 0xff);
    this.buf.push((value >>> 24) & 0xff);
  }

  private u64(value: bigint): void {
    this.u32(Number(value & 0xffffffffn));
    this.u32(Number((value >> 32n) & 0xffffffffn));
  }

  private i16(value: number): void {
    this.u16(value & 0xffff);
  }

  private i32(value: number): void {
    this.u32(value & 0xffffffff);
  }

  private i64(value: bigint): void {
    this.u64(value & 0xffffffffffffffffn);
  }

  private appendBytes(data: Uint8Array): void {
    for (let i = 0; i < data.length; i++) this.buf.push(data[i]);
  }

  private writeCanary(ty: number): void {
    this.u8(ty);
  }

  // -- typed writers -----------------------------------------------------

  writeBool(value: boolean): void {
    this.writeCanary(MessageType.BOOL);
    this.u8(value ? 1 : 0);
  }

  writeByte(value: number, bits = 8): void {
    if (bits !== 8) warnNumericRange("BYTE", value, bits, false);
    this.writeCanary(MessageType.BYTE);
    this.u8(value);
  }

  writeChar(value: number, bits = 8): void {
    if (bits !== 8) warnNumericRange("CHAR", value, bits, true);
    this.writeCanary(MessageType.CHAR);
    this.u8(value);
  }

  writeWord(value: number, bits = 16): void {
    if (bits !== 16) warnNumericRange("WORD", value, bits, false);
    this.writeCanary(MessageType.WORD);
    this.u16(value);
  }

  writeShort(value: number, bits = 16): void {
    if (bits !== 16) warnNumericRange("SHORT", value, bits, true);
    this.writeCanary(MessageType.SHORT);
    this.i16(value);
  }

  writeDword(value: number, bits = 32): void {
    if (bits !== 32) warnNumericRange("DWORD", value, bits, false);
    this.writeCanary(MessageType.DWORD);
    this.u32(value);
  }

  writeInt(value: number, bits = 32): void {
    if (bits !== 32) warnNumericRange("INT", value, bits, true);
    this.writeCanary(MessageType.INT);
    this.i32(value);
  }

  writeDword64(value: bigint, bits = 64): void {
    if (bits !== 64) warnNumericRange("DWORD64", Number(value), bits, false);
    this.writeCanary(MessageType.DWORD64);
    this.u64(value);
  }

  writeInt64(value: bigint, bits = 64): void {
    if (bits !== 64) warnNumericRange("INT64", Number(value), bits, true);
    this.writeCanary(MessageType.INT64);
    this.i64(value);
  }

  writeFloat(value: number, _multiplier = 1.0, _bits = 32): void {
    this.writeCanary(MessageType.FLOAT);
    this.appendBytes(encodeFloat32(value));
  }

  writeFloatLim(value: number, _min: number, _max: number, _bits = 32): void {
    this.writeCanary(MessageType.FLOAT);
    this.appendBytes(encodeFloat32(value));
  }

  writeDouble(value: number): void {
    this.writeCanary(MessageType.DOUBLE);
    this.appendBytes(encodeFloat64(value));
  }

  writeDoubleLim(value: number, _min: number, _max: number, _bits = 64): void {
    this.writeCanary(MessageType.DOUBLE);
    this.appendBytes(encodeFloat64(value));
  }

  writeResref(value: string, count = 16): void {
    this.writeCanary(MessageType.RESREF);
    const encoded = encodeUtf8(value);
    if (encoded.length > count) {
      console.warn(`ResRef ${value} exceeds ${count} bytes`);
    }
    this.u8(Math.min(encoded.length, count));
    this.appendBytes(encoded.subarray(0, count));
  }

  writeString(value: string): void {
    this.writeCanary(MessageType.STRING);
    const encoded = encodeUtf8(value);
    this.u32(encoded.length);
    this.appendBytes(encoded);
  }

  writeBytes(value: Uint8Array, expectedCount = -1): void {
    this.writeCanary(MessageType.VOIDPTR);
    if (expectedCount >= 0 && value.length !== expectedCount) {
      console.warn(`VOIDPTR payload length ${value.length} differs from expected ${expectedCount}`);
    }
    this.u32(value.length);
    this.appendBytes(value);
  }

  writeJson(value: unknown): void {
    this.writeCanary(MessageType.JSON);
    const encoded = encodeUtf8(JSON.stringify(value));
    this.u32(encoded.length);
    this.appendBytes(encoded);
  }

  writeObjectId(value: number, bits = 32): void {
    if (bits !== 32) warnNumericRange("OBJECT_ID", value, bits, false);
    this.writeCanary(MessageType.OBJECT_ID);
    this.u32(value);
  }

  writeLocString(value: LocString): void {
    this.writeCanary(MessageType.LOCSTRING);
    if (value.hasStrRef) {
      this.u8(1);
    } else {
      this.u8(0);
      const encoded = encodeUtf8(value.text);
      this.u32(encoded.length);
      this.appendBytes(encoded);
    }
  }
}

// -----------------------------------------------------------------------
// Utility
// -----------------------------------------------------------------------

export function isTruthy(value: unknown): boolean {
  if (value === null || value === undefined) return false;
  if (typeof value === "boolean") return value;
  if (typeof value === "number") return value !== 0;
  if (typeof value === "bigint") return value !== 0n;
  if (typeof value === "string") return value !== "";
  if (value instanceof Uint8Array) return value.length > 0;
  if (Array.isArray(value)) return value.length > 0;
  return true;
}

function warnNumericRange(name: string, value: number, bits: number, signed: boolean): void {
  const max = signed ? 1 << (bits - 1) : (1 << bits) - 1;
  const min = signed ? -(1 << (bits - 1)) : 0;
  if (value < min || value > max) {
    console.warn(`${name} value ${value} out of range for ${bits} bits`);
  }
}

// -----------------------------------------------------------------------
// Binary encoding helpers
// -----------------------------------------------------------------------

function decodeFloat32(bytes: Uint8Array): number {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  return view.getFloat32(0, true);
}

function decodeFloat64(bytes: Uint8Array): number {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  return view.getFloat64(0, true);
}

function encodeFloat32(value: number): Uint8Array {
  const buf = new ArrayBuffer(4);
  const view = new DataView(buf);
  view.setFloat32(0, value, true);
  return new Uint8Array(buf);
}

function encodeFloat64(value: number): Uint8Array {
  const buf = new ArrayBuffer(8);
  const view = new DataView(buf);
  view.setFloat64(0, value, true);
  return new Uint8Array(buf);
}

function decodeUtf8(bytes: Uint8Array): string {
  return new TextDecoder().decode(bytes);
}

function encodeUtf8(str: string): Uint8Array {
  return new TextEncoder().encode(str);
}
