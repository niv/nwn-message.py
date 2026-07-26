// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Minimal MD5 implementation for NWN authentication.
 *
 * The MD5 hex digests are used for CD-key and password responses
 * during the BNCS/BNVS handshake.  This is a standalone implementation
 * so no crypto library is needed in the browser.
 */

function md5Core(input: Uint8Array): string {
  // Initial state
  let a = 0x67452301;
  let b = 0xefcdab89;
  let c = 0x98badcfe;
  let d = 0x10325476;

  // Pre-processing: append 0x80, pad with zeros, append length in bits
  const bitLen = input.length * 8;
  const paddedLen = (((input.length + 8) >>> 6) + 1) << 6;
  const padded = new Uint8Array(paddedLen);
  padded.set(input);
  padded[input.length] = 0x80;
  const dv = new DataView(padded.buffer);
  dv.setUint32(paddedLen - 8, bitLen >>> 0, true);  // low 32 bits of length
  dv.setUint32(paddedLen - 4, Math.floor(bitLen / 0x100000000), true); // high 32 bits

  // Process 64-byte blocks
  for (let offset = 0; offset < paddedLen; offset += 64) {
    const w = new Uint32Array(16);
    for (let i = 0; i < 16; i++) {
      w[i] = dv.getUint32(offset + i * 4, true);
    }

    let aa = a, bb = b, cc = c, dd = d;

    for (let i = 0; i < 64; i++) {
      let f, g;
      if (i < 16) {
        f = (b & c) | (~b & d);
        g = i;
      } else if (i < 32) {
        f = (d & b) | (~d & c);
        g = (5 * i + 1) % 16;
      } else if (i < 48) {
        f = b ^ c ^ d;
        g = (3 * i + 5) % 16;
      } else {
        f = c ^ (b | ~d);
        g = (7 * i) % 16;
      }

      const temp = d;
      d = c;
      c = b;
      b = (b + leftRotate((a + f + K[i] + w[g]) >>> 0, S[i])) >>> 0;
      a = temp;
    }

    a = (a + aa) >>> 0;
    b = (b + bb) >>> 0;
    c = (c + cc) >>> 0;
    d = (d + dd) >>> 0;
  }

  // Hex encode result
  const buf = new Uint8Array(16);
  const dv2 = new DataView(buf.buffer);
  dv2.setUint32(0, a, true);
  dv2.setUint32(4, b, true);
  dv2.setUint32(8, c, true);
  dv2.setUint32(12, d, true);
  return hex(buf);
}

const S = [
  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,
  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,
  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,
  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,
];

const K = new Uint32Array(64);
for (let i = 0; i < 64; i++) {
  K[i] = Math.floor(Math.abs(Math.sin(i + 1)) * 0x100000000) >>> 0;
}

function leftRotate(x: number, n: number): number {
  return ((x << n) | (x >>> (32 - n))) >>> 0;
}

function hex(buf: Uint8Array): string {
  return Array.from(buf).map((b) => b.toString(16).padStart(2, "0")).join("");
}

export function md5(data: Uint8Array): Uint8Array {
  const hexStr = md5Core(data);
  const out = new Uint8Array(16);
  for (let i = 0; i < 16; i++) {
    out[i] = parseInt(hexStr.substring(i * 2, i * 2 + 2), 16);
  }
  return out;
}

export function md5Hex(data: Uint8Array): string {
  return md5Core(data);
}
