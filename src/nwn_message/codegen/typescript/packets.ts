// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * NWN WebSocket handshake packets (TypeScript port).
 *
 * These packets use string headers (e.g. "GNHI", "BNES") as prefix instead of
 * type canaries.  The wire format is raw little-endian binary with the packet
 * header prepended by the transport layer.
 *
 * See `nwn_message/packets.py` in the Python project for reference.
 */

// -----------------------------------------------------------------------
// Low-level packet reader / writer
// -----------------------------------------------------------------------

export class PacketReader {
    private pos = 0;

    constructor(private data: Uint8Array) {}

    get atEnd(): boolean {
        return this.pos >= this.data.length;
    }

    readU8(): number {
        return this.data[this.pos++];
    }

    readU16(): number {
        const v = this.data[this.pos] | (this.data[this.pos + 1] << 8);
        this.pos += 2;
        return v;
    }

    readI16(): number {
        const raw = this.readU16();
        return raw >= 0x8000 ? raw - 0x10000 : raw;
    }

    readU32(): number {
        const v =
            (this.data[this.pos] |
                (this.data[this.pos + 1] << 8) |
                (this.data[this.pos + 2] << 16) |
                (this.data[this.pos + 3] << 24)) >>>
            0;
        this.pos += 4;
        return v;
    }

    readI32(): number {
        const raw = this.readU32();
        return raw >= 0x80000000 ? raw - 0x100000000 : raw;
    }

    readU64(): bigint {
        const lo =
            (this.data[this.pos] |
                (this.data[this.pos + 1] << 8) |
                (this.data[this.pos + 2] << 16) |
                (this.data[this.pos + 3] << 24)) >>>
            0;
        const hi =
            (this.data[this.pos + 4] |
                (this.data[this.pos + 5] << 8) |
                (this.data[this.pos + 6] << 16) |
                (this.data[this.pos + 7] << 24)) >>>
            0;
        this.pos += 8;
        return (BigInt(hi) << 32n) | BigInt(lo);
    }

    readBytes(n: number): Uint8Array {
        const chunk = this.data.subarray(this.pos, this.pos + n);
        this.pos += n;
        return chunk;
    }

    /** Read a length-prefixed string (1-byte length). */
    readLp8(): string {
        return decodeUtf8(this.readBytes(this.readU8()));
    }

    /** Read a length-prefixed string (2-byte length LE). */
    readLp16(): string {
        return decodeUtf8(this.readBytes(this.readU16()));
    }

    /** Read a length-prefixed string (4-byte length LE). */
    readLp32(): string {
        return decodeUtf8(this.readBytes(this.readU32()));
    }
}

export class PacketWriter {
    private buf: number[] = [];

    constructor(private head: string) {
        for (let i = 0; i < head.length; i++) this.buf.push(head.charCodeAt(i));
    }

    getBytes(): Uint8Array {
        return new Uint8Array(this.buf);
    }

    writeU8(v: number): void {
        this.buf.push(v & 0xff);
    }

    writeU16(v: number): void {
        this.buf.push(v & 0xff, (v >>> 8) & 0xff);
    }

    writeI16(v: number): void {
        this.writeU16(v & 0xffff);
    }

    writeU32(v: number): void {
        this.buf.push(
            v & 0xff,
            (v >>> 8) & 0xff,
            (v >>> 16) & 0xff,
            (v >>> 24) & 0xff,
        );
    }

    writeI32(v: number): void {
        this.writeU32(v & 0xffffffff);
    }

    writeU64(v: bigint): void {
        this.writeU32(Number(v & 0xffffffffn));
        this.writeU32(Number((v >> 32n) & 0xffffffffn));
    }

    writeI64(v: bigint): void {
        this.writeU64(v & 0xffffffffffffffffn);
    }

    writeBytes(data: Uint8Array): void {
        for (let i = 0; i < data.length; i++) this.buf.push(data[i]);
    }

    writeLp8(s: string): void {
        const enc = encodeUtf8(s);
        this.writeU8(enc.length);
        this.writeBytes(enc);
    }

    writeLp16(s: string): void {
        const enc = encodeUtf8(s);
        this.writeU16(enc.length);
        this.writeBytes(enc);
    }

    writeLp32(s: string): void {
        const enc = encodeUtf8(s);
        this.writeU32(enc.length);
        this.writeBytes(enc);
    }
}

// -----------------------------------------------------------------------
// Packet types
// -----------------------------------------------------------------------

/** GNHI — Server greeting on connect */
export interface GNHI {
    protocolVersion: number;
    caps: number;
}

export function readGNHI(reader: PacketReader): GNHI {
    return { protocolVersion: reader.readU8(), caps: Number(reader.readU64()) };
}

export function writeGNHI(): Uint8Array {
    const wr = new PacketWriter("GNHI");
    wr.writeU8(1);
    wr.writeU64(0n);
    return wr.getBytes();
}

/** BNES — Client enumerate servers request */
export interface BNES {
    portNumber: number;
    enumerateType: number;
}

export function writeBNES(port = 5121, enumType = 0): Uint8Array {
    const wr = new PacketWriter("BNES");
    wr.writeU16(port);
    wr.writeU8(enumType);
    return wr.getBytes();
}

/** BNER — Server enumerate response */
export interface BNER {
    enumerateType: number;
    sessionName: string;
}

export function readBNER(reader: PacketReader): BNER {
    const u = reader.readU8(); // should be 'U' (0x55)
    if (u !== 0x55) console.warn(`BNER: expected 'U', got 0x${u.toString(16)}`);
    reader.readU16(); // port (ignored)
    const enumType = reader.readU8();
    const sessionName = reader.readLp8();
    return { enumerateType: enumType, sessionName };
}

/** BNXI — Client info exchange */
export interface BNXI {
    playerName: string;
    publicKey: string;
    legacyPublicKey: string;
    language: number;
    connectionType: number;
    platform: number;
    buildNumber: string;
    buildRevision: string;
    buildPostfix: string;
    buildGitCommit: string;
}

export function writeBNXI(info: BNXI): Uint8Array {
    const wr = new PacketWriter("BNXI");
    wr.writeU16(5121);
    wr.writeLp8(info.playerName);
    wr.writeLp8(info.publicKey);
    wr.writeLp8(info.legacyPublicKey);
    wr.writeU8(info.language);
    wr.writeU8(info.connectionType);
    wr.writeU8(info.platform);
    wr.writeLp8(info.buildNumber);
    wr.writeLp8(info.buildRevision);
    wr.writeLp8(info.buildPostfix);
    wr.writeLp8(info.buildGitCommit);
    return wr.getBytes();
}

/** BNXR — Server info response */
export interface BNXR {
    passworded: boolean;
    minLevel: number;
    maxLevel: number;
    currentPlayers: number;
    maxPlayers: number;
    allowLocalVault: boolean;
    pvpSetting: number;
    pauseAndPlay: boolean;
    onePartyOnly: boolean;
    elc: boolean;
    ilr: boolean;
    expansionPack: number;
    moduleName: string;
    nwsyncUrl: string;
    nwsyncPrimaryManifest: string;
    nwsyncAdditionalManifests: Array<{
        flags: number;
        languageId: number;
        hash: string;
    }>;
    advancedVersion: string;
}

export function readBNXR(reader: PacketReader): BNXR {
    reader.readU16(); // port
    const version = reader.readU8();
    if (version !== 0xfd)
        console.warn(`BNXR: expected 0xFD, got 0x${version.toString(16)}`);

    const passworded = !!reader.readU8();
    const minLevel = reader.readU8();
    const maxLevel = reader.readU8();
    const currentPlayers = reader.readU8();
    const maxPlayers = reader.readU8();
    const allowLocalVault = !!reader.readU8();
    const pvpSetting = reader.readU8();
    const pauseAndPlay = !!reader.readU8();
    const onePartyOnly = !!reader.readU8();
    const elc = !!reader.readU8();
    const ilr = !!reader.readU8();
    const expansionPack = reader.readU8();
    const moduleName = reader.readLp8();

    let nwsyncUrl = "";
    let nwsyncPrimaryManifest = "";
    const nwsyncAdditionalManifests: Array<{
        flags: number;
        languageId: number;
        hash: string;
    }> = [];

    if (!reader.atEnd) {
        const nwsyncVersion = reader.readU8();
        if (nwsyncVersion === 2 && !reader.atEnd) {
            const nwsyncPresent = !!reader.readU8();
            if (nwsyncPresent) {
                nwsyncUrl = reader.readLp8();
                nwsyncPrimaryManifest = reader.readLp8();
                const count = reader.readU8();
                for (let i = 0; i < count; i++) {
                    nwsyncAdditionalManifests.push({
                        flags: reader.readU8(),
                        languageId: reader.readU8(),
                        hash: reader.readLp8(),
                    });
                }
            }
        }
    }

    let advancedVersion = "";
    if (!reader.atEnd) {
        advancedVersion = reader.readLp16();
    }

    return {
        passworded,
        minLevel,
        maxLevel,
        currentPlayers,
        maxPlayers,
        allowLocalVault,
        pvpSetting,
        pauseAndPlay,
        onePartyOnly,
        elc,
        ilr,
        expansionPack,
        moduleName,
        nwsyncUrl,
        nwsyncPrimaryManifest,
        nwsyncAdditionalManifests,
        advancedVersion,
    };
}

/** BNLM — Server listing message */
export interface BNLM {
    port: number;
    messageNo: number;
    sessionId: number;
}

export function readBNLM(reader: PacketReader): BNLM {
    return {
        port: reader.readU16(),
        messageNo: reader.readU8(),
        sessionId: reader.readU32(),
    };
}

export function writeBNLM(msg: BNLM): Uint8Array {
    const wr = new PacketWriter("BNLM");
    wr.writeU16(msg.port);
    wr.writeU8(msg.messageNo);
    wr.writeU32(msg.sessionId);
    return wr.getBytes();
}

/** BNLR — Server listing response */
export interface BNLR {
    port: number;
    messageNo: number;
    sessionId: number;
}

export function readBNLR(reader: PacketReader): BNLR {
    reader.readU16(); // port (unused)
    return {
        port: 5121,
        messageNo: reader.readU8(),
        sessionId: reader.readU32(),
    };
}

export function writeBNLR(msg: BNLR): Uint8Array {
    const wr = new PacketWriter("BNLR");
    wr.writeU16(msg.port);
    wr.writeU8(msg.messageNo);
    wr.writeU32(msg.sessionId);
    return wr.getBytes();
}

/** BNDS — Client details request */
export function writeBNDS(port = 5121): Uint8Array {
    const wr = new PacketWriter("BNDS");
    wr.writeU16(port);
    return wr.getBytes();
}

/** BNDR — Server details response */
export interface BNDR {
    portNumber: number;
    gameDetails: string;
    moduleDescription: string;
    build: string;
    gameType: number;
}

export function readBNDR(reader: PacketReader): BNDR {
    const portNumber = reader.readU16();
    const gameDetails = reader.readLp32();
    const moduleDescription = reader.readLp32();
    const build = reader.readLp32();
    const gameType = reader.readI16();
    return { portNumber, gameDetails, moduleDescription, build, gameType };
}

/** BNCS — Client authentication */
export interface BNCS {
    connectionType: number;
    playerLanguage: number;
    playerName: string;
    cdKey: string;
    appId: number;
    versionNumber: number;
    patchRevision: number;
    patchPostfix: number;
    gitCommit: string;
    legacyCdKey: string;
    platform: number;
}

export function writeBNCS(info: BNCS): Uint8Array {
    const wr = new PacketWriter("BNCS");
    wr.writeU16(5121);
    wr.writeU8(info.connectionType);
    wr.writeU32(info.versionNumber);
    wr.writeU16(0xffff);
    wr.writeU8(info.playerLanguage);
    wr.writeU32(info.appId);
    wr.writeLp8(info.playerName);
    wr.writeLp8(info.cdKey);
    wr.writeLp8(info.legacyCdKey);
    wr.writeU8(info.platform);
    wr.writeLp8(""); // psid
    wr.writeI32(info.patchRevision);
    wr.writeI32(info.patchPostfix);
    wr.writeLp8(info.gitCommit);
    return wr.getBytes();
}

/** BNCR — Server authentication response */
export const BNCRStatus = {
    ACCEPTED: 0,
    REJECTED: 1,
    PASSWORD_REQUIRED: 2,
} as const;

export interface BNCR {
    status: number;
    cdKeyChallenge: Uint8Array;
    gamePasswordChallenge: Uint8Array;
    masterPasswordChallenge: Uint8Array;
    rejectionReason: string;
}

export function readBNCR(reader: PacketReader): BNCR {
    const port = reader.readU16();
    const status = reader.readU8();

    // Some server versions send ASCII status codes ('A'/'R'/'P')
    // instead of numeric (0/1/2). Normalise here.
    let normalised = status;
    if (status === 0x41)
        normalised = 0; // 'A' → ACCEPTED
    else if (status === 0x52)
        normalised = 1; // 'R' → REJECTED
    else if (status === 0x50)
        normalised = 2; // 'P' → PASSWORD_REQUIRED
    else if (status === 0x56) normalised = 0; // 'V' → Verified/Challenge → ACCEPTED

    // For REJECTED, the server may omit the challenge data.
    // Read challenges only if there's enough remaining bytes.
    let cdKeyChallenge: Uint8Array<ArrayBuffer> = new Uint8Array(0);
    let gamePasswordChallenge: Uint8Array<ArrayBuffer> = new Uint8Array(0);
    let masterPasswordChallenge: Uint8Array<ArrayBuffer> = new Uint8Array(0);
    let rejectionReason = "";

    if (!reader.atEnd) {
        const cdKeyChallengeLen = reader.readU16();
        cdKeyChallenge = reader.readBytes(
            cdKeyChallengeLen,
        ) as Uint8Array<ArrayBuffer>;
    }
    if (!reader.atEnd) {
        const gamePasswordChallengeLen = reader.readU16();
        gamePasswordChallenge = reader.readBytes(
            gamePasswordChallengeLen,
        ) as Uint8Array<ArrayBuffer>;
    }
    if (!reader.atEnd) {
        const masterPasswordChallengeLen = reader.readU16();
        masterPasswordChallenge = reader.readBytes(
            masterPasswordChallengeLen,
        ) as Uint8Array<ArrayBuffer>;
    }
    if (!reader.atEnd) {
        rejectionReason = reader.readLp16();
    }

    console.log(
        `[BNCR] port=${port} status=0x${status.toString(16)} (normalised=${normalised}) challenges=${cdKeyChallenge.length}/${gamePasswordChallenge.length}/${masterPasswordChallenge.length} reason="${rejectionReason}"`,
    );

    return {
        status: normalised,
        cdKeyChallenge,
        gamePasswordChallenge,
        masterPasswordChallenge,
        rejectionReason,
    };
}

/** BNVS — Client version/response */
export interface BNVS {
    cdKeyResponse: Uint8Array;
    masterPasswordResponse: Uint8Array;
    gamePasswordResponse: Uint8Array;
}

/**
 * Wire format:
 *   1 byte: status ('V'=0x56 no password, 'P'=0x50 password required)
 *   1 byte: num_cd_keys (0 or 1)
 *   if num_cd_keys == 1: lp8(cd_key_response)
 *   lp8(master_password_response)
 *   if status == 'P': lp8(game_password_response)
 */
export function writeBNVS(info: BNVS): Uint8Array {
    const hasGamePassword = info.gamePasswordResponse.length > 0;
    const wr = new PacketWriter("BNVS");
    wr.writeU8(hasGamePassword ? 0x50 : 0x56); // 'P' or 'V'
    wr.writeU8(info.cdKeyResponse.length > 0 ? 1 : 0);
    if (info.cdKeyResponse.length > 0) {
        wr.writeLp8(decodeUtf8(info.cdKeyResponse));
    }
    wr.writeLp8(decodeUtf8(info.masterPasswordResponse));
    if (hasGamePassword) {
        wr.writeLp8(decodeUtf8(info.gamePasswordResponse));
    }
    return wr.getBytes();
}

/** BNVR — Server version response */
export const BNVRConnectionStatus = {
    REJECTED: 0x52, // 'R'
    ACCEPTED: 0x41, // 'A'
} as const;

export interface BNVR {
    connectionStatus: number;
    rejectionReason: string;
    appId: number;
    serverBuild: number;
    serverPatch: number;
    serverPostfix: number;
}

/**
 * Wire format:
 *   1 byte: 'A' (0x41) = accepted, 'R' (0x52) = rejected
 *   If rejected: 1 byte rejection_reason
 *   If accepted: u32 app_id, then optional u32 build, u32 patch, u32 postfix
 */
export function readBNVR(reader: PacketReader): BNVR {
    const statusByte = reader.readU8();
    console.log(`[BNVR] status=0x${statusByte.toString(16)}`);

    if (statusByte === 0x52 /* 'R' */) {
        const reason = reader.readU8();
        return {
            connectionStatus: 0x52,
            rejectionReason: String(reason),
            appId: 0,
            serverBuild: 0,
            serverPatch: 0,
            serverPostfix: 0,
        };
    }

    // Accepted
    const appId = reader.readU32();
    let serverBuild = 0;
    let serverPatch = 0;
    let serverPostfix = 0;
    if (!reader.atEnd) serverBuild = reader.readU32();
    if (!reader.atEnd) serverPatch = reader.readU32();
    if (!reader.atEnd) serverPostfix = reader.readU32();

    console.log(
        `[BNVR] accepted appId=${appId} build=${serverBuild} patch=${serverPatch} postfix=${serverPostfix}`,
    );

    return {
        connectionStatus: 0x41,
        rejectionReason: "",
        appId,
        serverBuild,
        serverPatch,
        serverPostfix,
    };
}

// -----------------------------------------------------------------------
// Encoding helpers
// -----------------------------------------------------------------------

function decodeUtf8(bytes: Uint8Array): string {
    return new TextDecoder().decode(bytes);
}

function encodeUtf8(str: string): Uint8Array {
    return new TextEncoder().encode(str);
}
