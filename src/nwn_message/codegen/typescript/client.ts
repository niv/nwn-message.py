// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * NWN WebSocket client — completes the login handshake and dispatches
 * game messages.
 *
 * Usage:
 *   const client = new NwnClient("localhost", 5121, {
 *     playerName: "bot",
 *     cdKey: "ABCDABCD-ABCDABCD",
 *   });
 *   await client.run();
 *
 * After connection, received messages are dispatched to handlers registered
 * via `client.on(...)`.
 */

import { md5Hex } from "./md5";
import { Reader, Writer } from "./net_message_util";
import {
    PacketReader,
    PacketWriter,
    readGNHI,
    writeGNHI,
    writeBNES,
    readBNER,
    writeBNXI,
    readBNXR,
    writeBNDS,
    readBNDR,
    writeBNCS,
    readBNCR,
    writeBNVS,
    readBNVR,
} from "./packets";

// -----------------------------------------------------------------------
// CD Key helpers
// -----------------------------------------------------------------------

const BASE26 = "UANPXTFWCQ9DVLE3GYJHK74R6M";

/**
 * Extract the 8-character public key from a full NWN CD key string.
 *
 * The full key has the format "ABCDABCD-ABCDABCD-ABCDABCD-ABCDABCD-ABCDABCD-ABCDA"
 * (41 characters with dashes).  The public key is 8 base-26 characters embedded
 * within it via an interleaving scheme.
 */
export function publicKey(fullKey: string): string {
    const clean = fullKey.replace(/-/g, "");
    if (clean.length !== 35)
        throw new Error(
            `Invalid CD key length: ${clean.length} (expected 35 chars without dashes)`,
        );

    let part = 0;
    const privateChars: string[] = [];
    const crcChars: string[] = [];
    const publicChars: string[] = [];
    const crcStart = 20 - 7 - 1; // PRIVATE_SIZE - CRC_SIZE - 1 = 12

    for (const ch of clean) {
        while (true) {
            if (part === 0) {
                part = 1;
                if (privateChars.length < 20) {
                    // PRIVATE_SIZE
                    privateChars.push(ch);
                    break;
                }
            }
            if (part === 1) {
                part = 2;
                if (privateChars.length > crcStart && crcChars.length < 7) {
                    // CRC_SIZE
                    crcChars.push(ch);
                    break;
                }
            }
            if (part === 2) {
                part = 0;
                if (publicChars.length < 8) {
                    // PUBLIC_SIZE
                    publicChars.push(ch);
                    break;
                }
                if (privateChars.length < 20 || crcChars.length < 7) continue;
                break;
            }
        }
    }

    return publicChars.join("");
}

// -----------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------

export interface NwnClientOptions {
    playerName: string;
    cdKey: string;
    connectionType?: number;
    language?: number;
    platform?: number;
    password?: string;
}

type MessageHandler = (reader: Reader) => void;

// -----------------------------------------------------------------------
// Message registry
// -----------------------------------------------------------------------

/**
 * Global message registry mapping (major, minor, direction) → handler.
 * Generated code registers into this.
 */
export const MESSAGE_REGISTRY: Record<
    number,
    Record<number, MessageHandler>
> = {};

/**
 * Register a message handler for a given (major, minor).
 */
export function registerMessage(
    major: number,
    minor: number,
    handler: MessageHandler,
): void {
    if (!MESSAGE_REGISTRY[major]) MESSAGE_REGISTRY[major] = {};
    MESSAGE_REGISTRY[major][minor] = handler;
}

// -----------------------------------------------------------------------
// Client
// -----------------------------------------------------------------------

const LOG_PACKETS = true;

export class NwnClient {
    private ws: WebSocket | null = null;
    private handlers: Map<number, Map<number, MessageHandler>> = new Map();
    private connected = false;
    private authenticated = false;

    constructor(
        private host: string,
        private port: number,
        private options: NwnClientOptions,
    ) {}

    /** Register a message handler. */
    on(major: number, minor: number, handler: MessageHandler): void {
        if (!this.handlers.has(major)) this.handlers.set(major, new Map());
        this.handlers.get(major)!.set(minor, handler);
    }

    /**
     * Send a typed message.  Looks up the writer function from the registry.
     *
     * Usage:
     *   await client.send(0x01, 0x00, {});  // ServerStatusRequest (no fields)
     *   await client.send(0x11, 0x01, {});  // CharListRequest (no fields)
     *
     * For complex messages, pass the data object matching the interface:
     *   await client.send(0x28, 0x01, { play: true });
     */
    async send(
        major: number,
        minor: number,
        data: Record<string, unknown>,
    ): Promise<void> {
        const { MESSAGE_REGISTRY } = await lazyImport(
            "./messages_js/registry.js",
        );
        const entry = MESSAGE_REGISTRY[major]?.[minor];
        if (!entry)
            throw new Error(
                `No writer for 0x${major.toString(16)}/0x${minor.toString(16)}`,
            );
        const mod = await lazyImport("./messages_js/" + entry.module + ".js");
        const writer = new Writer();
        mod[entry.writer!](writer, data);
        this.sendMessage(major, minor, writer);
    }

    private log(...args: unknown[]): void {
        console.log(`[NWN]`, ...args);
    }

    private logSend(prefix: string, data: Uint8Array): void {
        if (!LOG_PACKETS) return;
        const hex =
            data.length > 64
                ? `${data.length} bytes`
                : Array.from(data)
                      .map((b) => b.toString(16).padStart(2, "0"))
                      .join(" ");
        this.log(`→ ${prefix} (${hex})`);
    }

    private logRecv(prefix: string, data: Uint8Array): void {
        if (!LOG_PACKETS) return;
        const hex =
            data.length > 64
                ? `${data.length} bytes`
                : Array.from(data)
                      .map((b) => b.toString(16).padStart(2, "0"))
                      .join(" ");
        this.log(`← ${prefix} (${hex})`);
    }

    /** Connect and run the login flow. */
    async run(): Promise<void> {
        const uri = `ws://${this.host}:${this.port}?proto_flags=0x100`;

        return new Promise<void>((resolve, reject) => {
            this.ws = new WebSocket(uri);
            this.ws.binaryType = "arraybuffer";

            this.ws.onopen = async () => {
                try {
                    this.connected = true;
                    this.log(`Connected to ${uri}`);
                    await this.login();
                    this.authenticated = true;
                    this.log("Authenticated — game messages ready");

                    // Send initial messages (same as Python run_client.py)
                    this.sendMessage(0x01, 0x00, new Writer()); // ServerStatusRequest
                    this.log("→ ServerStatusRequest (0x01/0x00)");
                    this.sendMessage(0x11, 0x01, new Writer()); // CharListRequest
                    this.log("→ CharListRequest (0x11/0x01)");

                    resolve();
                } catch (err) {
                    reject(err);
                }
            };

            this.ws.onmessage = (event) => {
                const data = new Uint8Array(event.data as ArrayBuffer);
                this.handleIncoming(data);
            };

            this.ws.onerror = (err) => {
                this.log("WebSocket error:", err);
                reject(err);
            };

            this.ws.onclose = () => {
                this.connected = false;
                this.authenticated = false;
            };
        });
    }

    /** Send raw bytes over the WebSocket. */
    sendBytes(data: Uint8Array): void {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(data);
        }
    }

    /** Send a game message (wraps with P prefix + major/minor + body). */
    sendMessage(major: number, minor: number, writer: Writer): void {
        const body = writer.getBytes();
        const header = new Uint8Array(3);
        header[0] = 0x70; // 'p' — client-to-server
        header[1] = major;
        header[2] = minor;
        const buf = new Uint8Array(header.length + body.length);
        buf.set(header);
        buf.set(body, header.length);
        this.logSend(`p ${major.toString(16)}/${minor.toString(16)}`, body);
        this.sendBytes(buf);
    }

    /** Send a login/transport packet. */
    sendPacket(data: Uint8Array): void {
        const prefix = String.fromCharCode(data[0], data[1], data[2], data[3]);
        this.logSend(prefix, data.subarray(4));
        this.sendBytes(data);
    }

    // -- internal ----------------------------------------------------------

    private async recvPacket(expectedPrefix: string): Promise<Uint8Array> {
        return new Promise<Uint8Array>((resolve) => {
            const originalHandler = this.ws!.onmessage;
            this.ws!.onmessage = (event) => {
                const data = new Uint8Array(event.data as ArrayBuffer);
                const prefix = String.fromCharCode(
                    data[0],
                    data[1],
                    data[2],
                    data[3],
                );
                this.logRecv(prefix, data.subarray(4));
                if (prefix.startsWith(expectedPrefix)) {
                    this.ws!.onmessage = originalHandler;
                    resolve(data);
                } else {
                    console.warn(
                        "Unexpected packet during login:",
                        prefix,
                        data,
                    );
                }
            };
        });
    }

    /** Complete the NWN login handshake. */
    private async login(): Promise<void> {
        const pubKey = publicKey(this.options.cdKey);
        this.log(`Public key: ${pubKey}`);

        // GNHI
        this.sendPacket(writeGNHI());
        const gnhiData = await this.recvPacket("G");
        const gnhi = readGNHI(new PacketReader(gnhiData.subarray(4)));
        this.log("GNHI:", gnhi);
        if (gnhi.protocolVersion !== 1)
            throw new Error(`Unsupported protocol: ${gnhi.protocolVersion}`);

        // BNES → BNER
        this.sendPacket(writeBNES());
        const bner = readBNER(
            new PacketReader((await this.recvPacket("B")).subarray(4)),
        );
        this.log("BNER:", bner);

        // BNXI → BNXR
        this.sendPacket(
            writeBNXI({
                playerName: this.options.playerName,
                publicKey: pubKey,
                legacyPublicKey: "",
                language: this.options.language ?? 0,
                connectionType: this.options.connectionType ?? 0,
                platform: this.options.platform ?? 2,
                buildNumber: "8193",
                buildRevision: "37",
                buildPostfix: "17",
                buildGitCommit: "",
            }),
        );
        const bnxr = readBNXR(
            new PacketReader((await this.recvPacket("B")).subarray(4)),
        );
        this.log("BNXR:", bnxr);

        // BNDS → BNDR
        this.sendPacket(writeBNDS());
        const bndr = readBNDR(
            new PacketReader((await this.recvPacket("B")).subarray(4)),
        );
        this.log("BNDR:", bndr);

        // BNCS → BNCR (authentication)
        const bncsData = writeBNCS({
            connectionType: this.options.connectionType ?? 0x10,
            playerLanguage: this.options.language ?? 0,
            playerName: this.options.playerName,
            cdKey: pubKey,
            appId: 0,
            versionNumber: 8193,
            patchRevision: 37,
            patchPostfix: 17,
            gitCommit: "",
            legacyCdKey: "",
            platform: this.options.platform ?? 2,
        });
        this.log(
            `BNCS fields: connectionType=0 playerLanguage=0 playerName="${this.options.playerName}" cdKey="${pubKey}" appId=0 versionNumber=8193 platform=2`,
        );
        this.sendPacket(bncsData);
        const bncr = readBNCR(
            new PacketReader((await this.recvPacket("B")).subarray(4)),
        );
        this.log("BNCR:", bncr);

        if (bncr.status === 1 /* REJECTED */) {
            throw new Error(`Authentication rejected: ${bncr.rejectionReason}`);
        }

        // Compute MD5 responses for BNVS
        // Format: "<raw_key>" + "<md5_hex(...)>"
        // md5 is over: key_bytes + challenge_raw_bytes
        const te = new TextEncoder();
        const challenge = bncr.cdKeyChallenge;

        // cd_key_response = pubKey + MD5(fullKeyWithDashes + challenge).hex
        const fullKeyWithDashes = this.options.cdKey; // 41 chars, with dashes
        const fullKeyBytes = concat(te.encode(fullKeyWithDashes), challenge);
        const cdKeyResponse = concat(
            te.encode(pubKey),
            te.encode(md5Hex(fullKeyBytes)),
        );

        // master_password_response = MD5("" + master_challenge).hex
        const masterBytes = concat(new Uint8Array(0), challenge);
        const masterPwResponse = te.encode(md5Hex(masterBytes));

        // game_password_response = MD5(password + game_challenge).hex (if password required)
        let gamePwResponse = new Uint8Array(0);
        if (
            bncr.status === 2 /* PASSWORD_REQUIRED */ &&
            bncr.gamePasswordChallenge.length > 0
        ) {
            const pwBytes = concat(
                te.encode(this.options.password || ""),
                bncr.gamePasswordChallenge,
            );
            gamePwResponse = te.encode(md5Hex(pwBytes));
        }

        // BNVS → BNVR
        this.sendPacket(
            writeBNVS({
                cdKeyResponse,
                masterPasswordResponse: masterPwResponse,
                gamePasswordResponse: gamePwResponse,
            }),
        );
        const bnvrData = await this.recvPacket("B");
        const bnvr = readBNVR(new PacketReader(bnvrData.subarray(4)));
        this.log("BNVR:", bnvr);

        if (bnvr.connectionStatus === 0x52 /* REJECTED */) {
            throw new Error(`Connection rejected: ${bnvr.rejectionReason}`);
        }
    }

    /** Dispatch incoming data to the right handler. */
    private async handleIncoming(data: Uint8Array): Promise<void> {
        if (data.length === 0) return;

        const prefix = data[0];

        if (prefix === 0x50 || prefix === 0x70) {
            // Game message
            if (data.length < 3) return;
            const major = data[1];
            const minor = data[2];
            const body = data.subarray(3);
            this.logRecv(
                `msg 0x${major.toString(16)}/0x${minor.toString(16)}`,
                body,
            );

            // Try to parse via the registry
            const reader = new Reader(body);
            if (reader.failed) {
                this.log(`  Failed to read (${reader.errorMessage})`);
                return;
            }

            try {
                const { MESSAGE_REGISTRY } = await lazyImport(
                    "./messages_js/registry.js",
                );
                const entry = MESSAGE_REGISTRY[major]?.[minor];
                if (entry && entry.reader) {
                    const mod = await lazyImport(
                        "./messages_js/" + entry.module + ".js",
                    );
                    const parsed = mod[entry.reader](reader);
                    this.log(`  →`, JSON.stringify(parsed, null, 2));
                } else {
                    this.log(
                        `  No reader for 0x${major.toString(16)}/0x${minor.toString(16)}`,
                    );
                }
            } catch {
                this.log(
                    `  Could not load reader for 0x${major.toString(16)}/0x${minor.toString(16)}`,
                );
            }
        } else if (prefix === 0x42 || prefix === 0x47) {
            // 'B' or 'G' packet
            this.logRecv(
                `packet ${String.fromCharCode(data[0], data[1], data[2], data[3])}`,
                data.subarray(4),
            );
        } else {
            this.log(`Unknown prefix 0x${prefix.toString(16)}`);
        }
    }
}

// -----------------------------------------------------------------------
// Utility
// -----------------------------------------------------------------------

function hexString(buf: Uint8Array): string {
    return Array.from(buf)
        .map((b) => b.toString(16).padStart(2, "0"))
        .join("");
}

/** Helper for runtime dynamic import (esbuild ignores this pattern). */
function lazyImport(url: string): Promise<any> {
    return new Function("u", "return import(u)")(url);
}

function concat(a: Uint8Array, b: Uint8Array): Uint8Array {
    const out = new Uint8Array(a.length + b.length);
    out.set(a);
    out.set(b, a.length);
    return out;
}
