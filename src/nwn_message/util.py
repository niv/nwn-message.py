import platform
from dataclasses import fields

from nwn.types import Platform


def collect_fields_from(target, source):
    """
    Collects values from source (dict or object) for fields in target dataclass.

    Skips any fields not present in source; does not error on missing fields.
    """
    is_dict = isinstance(source, dict)
    result = {}

    for field in fields(target):
        if is_dict:
            if field.name in source:
                result[field.name] = source[field.name]
        else:
            if hasattr(source, field.name):
                result[field.name] = getattr(source, field.name)

    return result


def apply_fields_from(target, source):
    """
    Updates target dataclass with values from source (dict or object).

    Skips any fields not present in source; does not error on missing fields.
    """
    values = collect_fields_from(target, source)
    for k, v in values.items():
        setattr(target, k, v)


# [TODO] move to nwn.py?
def detect_platform() -> Platform:
    system = platform.system()
    machine = platform.machine().lower()

    if system == "Windows":
        if machine in ("amd64", "x86_64"):
            return Platform.WINDOWS_X64
        if machine in ("x86", "i386", "i686"):
            return Platform.WINDOWS_X86
    elif system == "Linux":
        if machine in ("x86_64", "amd64"):
            return Platform.LINUX_X64
        if machine in ("x86", "i386", "i686"):
            return Platform.LINUX_X86
        if "arm" in machine or "aarch64" in machine:
            if "64" in machine or machine == "aarch64":
                return Platform.LINUX_ARM64
            return Platform.LINUX_ARM32
    elif system == "Darwin":
        if machine in ("x86_64", "amd64"):
            return Platform.MAC_X64
        if machine in ("arm64", "aarch64"):
            return Platform.MAC_ARM64
        if machine in ("i386", "x86"):
            return Platform.MAC_X86
    return Platform.INVALID
