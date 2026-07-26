// SPDX-License-Identifier: GPL-3.0-or-later

/**
 * Build script: compiles & bundles the TypeScript message runtime for the
 * browser.
 *
 * Source lives in src/nwn_message/codegen/typescript/ (hand-written runtimes).
 * Generated message .ts files are in generated/typescript/messages/.
 * Output (bundle.js + compiled .js files) goes to generated/typescript/.
 *
 * Usage:
 *   cd src/nwn_message/codegen/typescript
 *   npm install     (one-time)
 *   node build.mjs
 */

import * as esbuild from "esbuild";
import { readdirSync, existsSync, mkdirSync, copyFileSync } from "fs";
import { join, dirname, resolve } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));

// Paths
const SRC = resolve(__dirname);
const ROOT = resolve(SRC, "../../../..");
const GENERATED = resolve(ROOT, "generated/typescript");
const MSG_SRC = join(GENERATED, "messages");
const MSG_OUT = join(GENERATED, "messages_js");

// Plugin: mark ./messages_js/* imports as external for runtime dynamic import
const externalMessagesPlugin = {
    name: "external-messages",
    setup(build) {
        build.onResolve({ filter: /^\.\/messages_js\// }, ({ path }) => {
            return { path, external: true };
        });
    },
};

// 1. Bundle the runtime (message JS files are loaded dynamically at runtime)
await esbuild.build({
    entryPoints: [join(SRC, "index.ts")],
    bundle: true,
    outfile: join(GENERATED, "bundle.js"),
    format: "esm",
    platform: "browser",
    target: "es2022",
    sourcemap: true,
    logLevel: "info",
    plugins: [externalMessagesPlugin],
});

// 2. Compile message .ts files individually
let msgCount = 0;
if (existsSync(MSG_SRC)) {
    const msgFiles = readdirSync(MSG_SRC)
        .filter((f) => f.endsWith(".ts"))
        .map((f) => join(MSG_SRC, f));
    msgCount = msgFiles.length;
    if (msgCount > 0) {
        mkdirSync(MSG_OUT, { recursive: true });
        await esbuild.build({
            entryPoints: msgFiles,
            outdir: MSG_OUT,
            format: "esm",
            platform: "browser",
            target: "es2022",
            sourcemap: false,
            logLevel: "info",
        });
    }
}

// 3. Copy test page
const htmlSrc = join(SRC, "index.html");
const htmlDst = join(GENERATED, "index.html");
try {
    copyFileSync(htmlSrc, htmlDst);
    console.log(`✓ index.html → ${htmlDst}`);
} catch {
    /* page may not exist */
}

console.log(`✓ bundle.js → ${join(GENERATED, "bundle.js")}`);
console.log(`✓ ${msgCount} message .js files → ${MSG_OUT}`);
