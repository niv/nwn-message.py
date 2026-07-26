"""
CLI runner for the codegen pipeline.

Discovers NWN message definitions, resolves them into language-agnostic
``ResolvedMessage`` trees, and dispatches to a per-language backend for
source-code emission.
"""

import argparse
import json
import logging
import os
from collections import defaultdict
from pathlib import Path

from nwn_message.codegen import (
    HELPER_FILE_NAME,
    HELPER_FILE_SOURCE,
    TypeResolver,
    UnsupportedMessageError,
    build_global_shared_types,
    build_module_shared_types,
    discover_messages,
    filter_messages,
)

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Run code gen for one or more messages.")
parser.add_argument(
    "paths",
    nargs="*",
    help="Optional output directory. For backward compatibility, you may also pass the old 'template output' positional pair; the template path will be ignored.",
)
parser.add_argument(
    "--message",
    action="append",
    dest="messages",
    default=[],
    help="Optional message selector. Accepts Python class names or major.minor.",
)
parser.add_argument(
    "--skip-helper",
    action="store_true",
    help="Do not emit the shared Godot utility file.",
)
parser.add_argument(
    "--manifest",
    action="store_true",
    help="Write a manifest.json summary next to the generated files.",
)
parser.add_argument(
    "--lang",
    default="godot4",
    choices=["godot4", "typescript"],
    help="Target language backend (default: godot4).",
)
args = parser.parse_args()


def _looks_like_template_path(path: str) -> bool:
    return path.endswith((".j2", ".jinja2"))


def _resolve_output_dir(raw_paths: list[str]) -> Path:
    default_dir = (
        Path("generated/typescript/messages").resolve()
        if args.lang == "typescript"
        else Path("generated/godot4/messages").resolve()
    )
    if not raw_paths:
        return default_dir
    if len(raw_paths) == 1:
        if _looks_like_template_path(raw_paths[0]):
            logger.warning("Ignoring legacy template argument: %s", raw_paths[0])
            return default_dir
        return Path(raw_paths[0]).resolve()
    if len(raw_paths) == 2 and _looks_like_template_path(raw_paths[0]):
        logger.warning("Ignoring legacy template argument: %s", raw_paths[0])
        return Path(raw_paths[1]).resolve()
    parser.error("expected [output] or legacy [template output]")


def _with_spdx_header(source: str) -> str:
    comment = "//" if args.lang == "typescript" else "#"
    return f"{comment} SPDX-License-Identifier: GPL-3.0-or-later\n\n{source.rstrip()}\n"


def _shared_types_file_name(module: str) -> str:
    from nwn_message.codegen._analysis import snake_case

    base = module.rsplit(".", 1)[-1]
    ext = ".ts" if args.lang == "typescript" else ".gd"
    return f"{snake_case(base)}_types{ext}"


def main() -> int:
    # -- select backend -------------------------------------------------------
    _FILE_EXT = ".ts" if args.lang == "typescript" else ".gd"

    if args.lang == "typescript":
        from nwn_message.codegen.typescript import (
            copy_static_files as ts_copy_static_files,
        )
        from nwn_message.codegen.typescript import (
            render_custom_source as ts_render_custom_source,
        )
        from nwn_message.codegen.typescript import (
            render_message_source as ts_render_message_source,
        )
        from nwn_message.codegen.typescript import (
            render_registry as ts_render_registry,
        )
        from nwn_message.codegen.typescript import (
            render_shared_types_source as ts_render_shared_types_source,
        )

        _render_msg = ts_render_message_source
        _render_shared = ts_render_shared_types_source
        _render_custom = ts_render_custom_source
        _render_registry = ts_render_registry
        _static_copied = False
    else:
        from nwn_message.codegen.godot4 import (
            render_custom_source as gd_render_custom_source,
        )
        from nwn_message.codegen.godot4 import (
            render_message_source as gd_render_message_source,
        )
        from nwn_message.codegen.godot4 import (
            render_shared_types_source as gd_render_shared_types_source,
        )

        _render_msg = gd_render_message_source
        _render_shared = gd_render_shared_types_source
        _render_custom = gd_render_custom_source

        def _noop_registry(_: list) -> str:
            return ""

        _render_registry = _noop_registry

        def _noop_copy(_: str) -> None:
            return None

        ts_copy_static_files = _noop_copy

    output_dir = _resolve_output_dir(args.paths)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.lang == "typescript":
        ts_copy_static_files(str(output_dir.parent))

    all_messages = discover_messages()
    selected_messages = filter_messages(all_messages, args.messages)

    generated: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []

    if not args.skip_helper and args.lang != "typescript":
        helper_path = output_dir / HELPER_FILE_NAME
        helper_path.write_text(_with_spdx_header(HELPER_FILE_SOURCE), encoding="utf-8")
        generated.append(
            {
                "source": "helper",
                "output": str(helper_path),
                "reason": "shared utility file",
            }
        )

    # -- global shared types ------------------------------------------------
    global_registry = build_global_shared_types(selected_messages)

    if global_registry is not None:
        try:
            resolver = TypeResolver(global_types=None)
            resolved = resolver.resolve_registry(global_registry, "nwn_net.net_types")
        except UnsupportedMessageError as exc:
            skipped.append({"source": "global shared types", "reason": str(exc)})
            resolved = None

        if resolved is not None:
            file_name = f"net_global_types{_FILE_EXT}"
            target_path = output_dir / file_name
            rendered = _with_spdx_header(_render_shared(resolved, "nwn_net.net_types"))
            target_path.write_text(rendered.rstrip() + "\n", encoding="utf-8")
            generated.append(
                {
                    "source": "global shared types",
                    "output": str(target_path),
                    "reason": "global shared types",
                }
            )

            has_custom = any(h.custom_io for h in resolved.helpers)
            if has_custom:
                os.makedirs(output_dir / "custom", exist_ok=True)
                custom_path = (
                    output_dir / "custom" / f"net_global_types_custom{_FILE_EXT}"
                )
                if not custom_path.exists():
                    custom_source = _with_spdx_header(_render_custom(resolved))
                    custom_path.write_text(custom_source, encoding="utf-8")
                    generated.append(
                        {
                            "source": "global shared types",
                            "output": str(custom_path),
                            "reason": "global shared types custom companion stub",
                        }
                    )

    _all_resolved: list = []  # collect for registry emission

    # -- module-level messages and shared types -----------------------------
    by_module: dict[str, list] = defaultdict(list)
    for msg_cls in selected_messages:
        by_module[msg_cls.__module__].append(msg_cls)

    for module, module_messages in by_module.items():
        module_registry = build_module_shared_types(
            module_messages, global_registry=global_registry
        )

        # Emit module shared types file
        if module_registry is not None:
            try:
                resolver = TypeResolver(global_types=global_registry)
                resolved = resolver.resolve_registry(module_registry, module)
            except UnsupportedMessageError as exc:
                skipped.append(
                    {"source": f"{module} (shared types)", "reason": str(exc)}
                )
                resolved = None

            if resolved is not None:
                file_name = _shared_types_file_name(module)
                target_path = output_dir / file_name
                rendered = _with_spdx_header(
                    _render_shared(resolved, module, global_registry=global_registry)
                )
                target_path.write_text(rendered.rstrip() + "\n", encoding="utf-8")
                generated.append(
                    {
                        "source": resolved.source_module,
                        "output": str(target_path),
                        "reason": "shared types",
                    }
                )

                has_custom = any(h.custom_io for h in resolved.helpers)
                if has_custom:
                    os.makedirs(output_dir / "custom", exist_ok=True)
                    custom_path = (
                        output_dir
                        / "custom"
                        / f"{file_name.replace(_FILE_EXT, '')}_custom{_FILE_EXT}"
                    )
                    if not custom_path.exists():
                        custom_source = _with_spdx_header(_render_custom(resolved))
                        custom_path.write_text(custom_source, encoding="utf-8")
                        generated.append(
                            {
                                "source": resolved.source_module,
                                "output": str(custom_path),
                                "reason": "shared types custom companion stub",
                            }
                        )

        # Per-message files
        for msg_cls in module_messages:
            try:
                resolver = TypeResolver(
                    shared_types=module_registry,
                    global_types=global_registry,
                )
                resolved = resolver.resolve_message(msg_cls)
                _all_resolved.append(resolved)
            except UnsupportedMessageError as exc:
                skipped.append(
                    {
                        "source": f"{msg_cls.__module__}.{msg_cls.__name__}",
                        "reason": str(exc),
                    }
                )
                continue

            from nwn_message.codegen._analysis import snake_case

            file_name = f"{snake_case(msg_cls.__name__)}{_FILE_EXT}"
            target_path = output_dir / file_name
            rendered = _with_spdx_header(
                _render_msg(
                    resolved,
                    global_registry=global_registry,
                    module_registry=module_registry,
                )
            )
            target_path.write_text(rendered.rstrip() + "\n", encoding="utf-8")
            generated.append(
                {
                    "source": f"{resolved.source_module}.{resolved.source_class}",
                    "output": str(target_path),
                    "reason": "message",
                }
            )

            has_custom = resolved.custom_io or any(
                h.custom_io for h in resolved.helpers
            )
            if has_custom:
                os.makedirs(output_dir / "custom", exist_ok=True)
                custom_path = (
                    output_dir
                    / "custom"
                    / f"{file_name.replace(_FILE_EXT, '')}_custom{_FILE_EXT}"
                )
                if not custom_path.exists():
                    custom_source = _with_spdx_header(
                        _render_custom(
                            resolved,
                            global_registry=global_registry,
                            module_registry=module_registry,
                        )
                    )
                    custom_path.write_text(custom_source, encoding="utf-8")
                    generated.append(
                        {
                            "source": f"{resolved.source_module}.{resolved.source_class}",
                            "output": str(custom_path),
                            "reason": "custom companion stub",
                        }
                    )

    # Emit message registry for TypeScript (lazy-import map)
    if args.lang == "typescript":
        registry_source = _with_spdx_header(_render_registry(_all_resolved))
        (output_dir / f"registry{_FILE_EXT}").write_text(
            registry_source, encoding="utf-8"
        )
        generated.append(
            {
                "source": "registry",
                "output": str(output_dir / f"registry{_FILE_EXT}"),
                "reason": "message registry",
            }
        )

    if args.manifest:
        manifest_path = output_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps({"generated": generated, "skipped": skipped}, indent=2) + "\n",
            encoding="utf-8",
        )

    logger.info("Selected %d message classes", len(selected_messages))
    logger.info("Generated %d files", len(generated))
    logger.info("Skipped %d messages", len(skipped))
    for item in skipped:
        logger.warning("SKIP %s: %s", item["source"], item["reason"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
