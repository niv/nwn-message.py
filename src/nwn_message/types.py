from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from nwn.types import Gender


class ConnectionType(IntEnum):
    PLAYER = 0x10
    DM = 0x20


class ObjectType(IntEnum):
    GUI = 1
    TILE = 2
    MODULE = 3
    AREA = 4
    CREATURE = 5
    ITEM = 6
    TRIGGER = 7
    PROJECTILE = 8
    PLACEABLE = 9
    DOOR = 10
    AREAOFEFFECTOBJECT = 11
    WAYPOINT = 12
    ENCOUNTER = 13
    STORE = 14
    PORTAL = 15
    SOUND = 16


class PVPSetting(IntEnum):
    NONE = 0
    PARTY = 1
    FULL = 2


STRREF_NONE = 0xFFFFFFFF


class LocStr(str):
    """
    A string value read from the TLK.

    You likely don't want to use this yourself: Instead, use the Tlk reader,
    the Context, or if you don't care about the str_ref, just pass plain strings.

    When receiving a LocStr, unless you care about the attached tlk data; just
    treat it like a regular string.

    The string value is the resolved/translated value according to your
    environment/Context and just for plain use. If you need to SEND a strref,
    you need to pass a StrRef object with only the tlk entry set.
    """

    __slots__ = ("gender", "str_ref", "sound_resref", "sound_length", "_locked")

    def __new__(
        cls,
        value: str = "",
        str_ref: int = STRREF_NONE,
        gender: Gender = Gender.MALE,
        sound_resref: str = "",
        sound_length: float = 0.0,
    ):
        obj = str.__new__(cls, value)
        obj.gender = gender
        if str_ref < 0 or str_ref > STRREF_NONE:
            raise ValueError(
                f"StrRef must be between 0 and {STRREF_NONE}, got {str_ref}"
            )
        obj.str_ref = str_ref
        obj.sound_resref = sound_resref
        obj.sound_length = sound_length
        obj._locked = True
        return obj

    def __setattr__(self, name, value):
        if getattr(self, "_locked", False):
            raise AttributeError(f"{self.__class__.__name__} is immutable")
        super().__setattr__(name, value)


@dataclass(frozen=True)
class Version:
    build: int  # 8193
    patch: int  # 36
    postfix: int  # 12
    git_commit: str = ""

    def satisfies(self, other: Version) -> bool:
        """
        Check if this version is compatible with the "other" version.
        That is, if this version is >= other version.

        Returns True if compatible, False otherwise.
        """
        if self.build != other.build:
            return False
        if self.patch < other.patch:
            return False
        if self.patch > other.patch:
            return True
        return self.postfix >= other.postfix

    def __str__(self) -> str:
        s = f"{self.build}.{self.patch}.{self.postfix}"
        if self.git_commit:
            s += f"-{self.git_commit}"
        return s


@dataclass(kw_only=True)
class ServerSettings:
    """
    Server settings that the server self-advertises as.

    This data structure is also used clientside to store information about the
    currently-connected server.
    """

    # BNER
    session_name: str = "PyNWN"

    # BNDR
    game_details: str = "Game Details"
    module_description: str = "Module Description"

    # BNXR
    passworded: bool = False
    min_level: int = 0
    max_level: int = 40
    max_players: int = 8
    allow_localvault: bool = True
    pvp_setting: PVPSetting = PVPSetting.NONE
    pause_and_play: bool = False
    one_party_only: bool = True
    elc: bool = True
    ilr: bool = False
    module_name: str = "Module"
    nwsync_url: str = ""
    nwsync_primary_manifest: str = ""
