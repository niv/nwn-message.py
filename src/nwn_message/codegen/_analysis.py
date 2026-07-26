"""Language-agnostic message-discovery and type-dependency analysis.

All functions in this module work purely with Python types and do **not**
reference any target-language naming conventions.
"""

from __future__ import annotations

import re
from dataclasses import fields, is_dataclass
from enum import Enum
from types import UnionType
from typing import Annotated, Any, Union, get_args, get_origin

from nwn_message import messages as _messages  # noqa: F401 — populate REGISTRY
from nwn_message.message import (
    REGISTRY,
    Direction,
    Message,
    validate_annotation,
)

# -- message discovery -------------------------------------------------------


def discover_messages() -> list[type[Message]]:
    discovered = sorted(
        set(REGISTRY.values()),
        key=lambda cls: (cls.MAJOR, cls.MINOR, cls.DIRECTION.value, cls.__name__),
    )
    return [cls for cls in discovered if issubclass(cls, Message)]


def filter_messages(
    messages: list[type[Message]], selectors: list[str] | None
) -> list[type[Message]]:
    if not selectors:
        return messages

    selected = []
    wanted = [selector.strip() for selector in selectors if selector.strip()]
    for message_cls in messages:
        if any(_message_matches_selector(message_cls, selector) for selector in wanted):
            selected.append(message_cls)
    return selected


def _message_matches_selector(message_cls: type[Message], selector: str) -> bool:
    lowered = selector.lower()
    if lowered == message_cls.__name__.lower():
        return True

    numeric = selector.replace("0x", "").replace("0X", "")
    parts = [part for part in re.split(r"[.:/]+", numeric) if part]
    if len(parts) in {2, 3}:
        try:
            major = int(parts[0], 16 if selector.lower().startswith("0x") else 10)
            minor = int(parts[1], 16 if selector.lower().startswith("0x") else 10)
        except ValueError:
            major = minor = None
        if major is not None and minor is not None:
            if message_cls.MAJOR != major or message_cls.MINOR != minor:
                return False
            if len(parts) == 2:
                return True
            return parts[2].lower() in _direction_aliases(message_cls.DIRECTION)

    if lowered in {
        f"{message_cls.MAJOR}.{message_cls.MINOR}",
        f"{message_cls.MAJOR:02x}.{message_cls.MINOR:02x}",
    }:
        return True

    return False


def _direction_aliases(direction: Direction) -> set[str]:
    if direction == Direction.S2C:
        return {"s2c", "server_to_client", direction.value}
    if direction == Direction.C2S:
        return {"c2s", "client_to_server", direction.value}
    if direction == Direction.BOTH:
        return {"both", direction.value}
    return {direction.value}


# -- type walking ------------------------------------------------------------


def collect_type_dependencies(
    annotation: Any, visited: set[type] | None = None
) -> set[type]:
    """Walk a type annotation to discover all referenced dataclass and enum types."""
    if visited is None:
        visited = set()

    anno = validate_annotation(annotation)

    if anno.tagged is not None:
        for variant_annotation in anno.tagged.lut.values():
            collect_type_dependencies(variant_annotation, visited)
        # Discriminator keys (enum values) are also type references
        for raw_value in anno.tagged.lut.keys():
            if isinstance(raw_value, Enum):
                visited.add(type(raw_value))
        return visited

    real_type = anno.real_type
    if get_origin(real_type) is Annotated:
        return collect_type_dependencies(real_type, visited)

    origin = get_origin(real_type)

    if origin in {Union, UnionType}:
        for nested in get_args(real_type):
            collect_type_dependencies(nested, visited)
        return visited

    if origin is tuple:
        for nested in get_args(real_type):
            collect_type_dependencies(nested, visited)
        return visited

    if origin is list:
        return collect_type_dependencies(get_args(real_type)[0], visited)

    if is_dataclass(real_type):
        if real_type in visited:
            return visited
        visited.add(real_type)
        for dc_field in fields(real_type):
            collect_type_dependencies(dc_field.type, visited)
        return visited

    if isinstance(real_type, type) and issubclass(real_type, Enum):
        visited.add(real_type)

    return visited


def collect_message_type_dependencies(message_cls: type[Message]) -> set[type]:
    """Collect all dataclass and enum types referenced by a message's fields."""
    deps: set[type] = set()
    for dc_field in fields(message_cls):  # pyright: ignore[reportArgumentType]
        collect_type_dependencies(dc_field.type, deps)
    return deps


def transitive_closure(shared: set[type]) -> set[type]:
    """Expand a set of shared types to include all types reachable from them."""
    result = set(shared)
    changed = True
    while changed:
        changed = False
        for t in list(result):
            if is_dataclass(t):
                for dc_field in fields(t):
                    field_deps = collect_type_dependencies(dc_field.type, set())
                    for dep in field_deps:
                        if dep not in result:
                            result.add(dep)
                            changed = True
    return result


# -- utility -----------------------------------------------------------------


def snake_case(name: str) -> str:
    if name.endswith("C2S"):
        return f"{snake_case(name[:-3])}_c2s"
    if name.endswith("S2C"):
        return f"{snake_case(name[:-3])}_s2c"
    step1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    step2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", step1)
    return step2.lower()
