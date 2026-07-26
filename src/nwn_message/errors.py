class UnknownHeaderError(ValueError, KeyError):
    """
    Raised when an unknown header is encountered during parsing;
    likely meaning the packet is not registered or known to the system.
    """


class ReadOverrunError(ValueError):
    """
    Raised when too much data was attempted to be read during parsing;
    e.g. a buffer overrun beyond the end of the available data.
    """


class ReadUnderrunError(ValueError):
    """
    Raised when data was left over after parsing a message (successfully);
    this usually indicates a bug in the parsing code or outdated reading code;
    e.g. a newer game version might send more data than the application expects.
    """


class DisconnectedError(Exception):
    """Raised when the peer is disconnected by the remote."""


class AuthenticationError(DisconnectedError):
    """Login/authentication rejected by the server."""


class VersionMismatchError(DisconnectedError):
    """Client and server versions are incompatible."""
