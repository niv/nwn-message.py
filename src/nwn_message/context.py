from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from nwn.types import Gender

from .types import LocStr

logger = logging.getLogger(__name__)


class Context(ABC):
    """
    Context is ephemeral data used during message parsing and handling; it also
    serves as glue between the message parser and the stateful data on the
    client/server (message reader/writers need to access to certain game data, for example).

    You must NOT re-use contexts between connection attempts.
    """

    # Inflight punchthrough for version checking.
    # This is a prime candidate for a cleaner solution.
    peer: Any

    # Inflight parse data only needed for the dataclass parser; this is
    # managed in read/write_dataclass.
    # This is a prime candidate for a cleaner solution.
    fields: dict

    def __init__(self, peer):
        self.peer = peer
        self._hack_is_trap = {}

    # TODO: revisit to see if REALLY needed or just in a handful of places
    @abstractmethod
    def twoda_row_count(self, twoda: str) -> int:
        """
        Return the number of rows in a 2DA file.
        """
        ...

    @abstractmethod
    def twoda(self, twoda: str, row: int, column: str) -> str:
        """
        Look up a 2da value for purposes of reading from the network.
        """
        ...

    @abstractmethod
    def tlk(self, row: int, gender: Gender = Gender.MALE) -> LocStr:
        """
        Look up the talk table for purposes of reading from the network.
        """
        ...

    # Trigger->is_trap is the only punch through where the network code genuinely
    # needs object state. This is so ugly I feel it deserved a special call out
    # via this pair of functions.
    #
    # About the only saving grace is that NWN, at least, always sends the _Add
    # and _Update for the trigger in the same GOU payload list.
    def hack_get_is_trap(self, object_id: int) -> bool:
        try:
            return self._hack_is_trap[object_id]
        except KeyError as e:
            raise KeyError(
                "Protocol desync or mistake: tried to parse a trigger "
                "update before parsing the add trigger"
            ) from e

    def hack_set_is_trap(self, object_id: int, is_trap: bool):
        self._hack_is_trap[object_id] = is_trap
