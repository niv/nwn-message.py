from dataclasses import dataclass
from typing import Annotated

from .. import message as m


@dataclass(kw_only=True)
class Speaker:
    speaker_id: m.ObjectId
    message: m.String
    position: m.Vec3
    original_name: m.Bool
    first_name: Annotated[m.LocStr, m.IfEq("original_name", True)]
    last_name: Annotated[m.LocStr, m.IfEq("original_name", True)]
    display_name: Annotated[m.String, m.IfEq("original_name", False)]


@dataclass(kw_only=True)
class ChatTalk(m.Message):
    MAJOR = 0x09
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    speaker_id: m.ObjectId
    message: m.String


@dataclass(kw_only=True)
class ChatShout(m.Message):
    MAJOR = 0x09
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    speaker: Speaker


@dataclass(kw_only=True)
class ChatWhisper(m.Message):
    MAJOR = 0x09
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    speaker_id: m.ObjectId
    message: m.String


@dataclass(kw_only=True)
class ChatTell(m.Message):
    MAJOR = 0x09
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    speaker: Speaker


@dataclass(kw_only=True)
class ChatServerTell(m.Message):
    MAJOR = 0x09
    MINOR = 0x05
    DIRECTION = m.Direction.S2C

    message: m.String


@dataclass(kw_only=True)
class ChatParty(m.Message):
    MAJOR = 0x09
    MINOR = 0x06
    DIRECTION = m.Direction.S2C

    speaker: Speaker


@dataclass(kw_only=True)
class ChatTalkRef(m.Message):
    MAJOR = 0x09
    MINOR = 0x08
    DIRECTION = m.Direction.S2C

    speaker_id: m.ObjectId
    strref: m.Dword


@dataclass(kw_only=True)
class ChatShoutRef(m.Message):
    MAJOR = 0x09
    MINOR = 0x09
    DIRECTION = m.Direction.S2C

    speaker_id: m.ObjectId
    strref: m.Dword


@dataclass(kw_only=True)
class ChatWhisperRef(m.Message):
    MAJOR = 0x09
    MINOR = 0x0A
    DIRECTION = m.Direction.S2C

    speaker_id: m.ObjectId
    strref: m.Dword


@dataclass(kw_only=True)
class ChatTokenTalk(m.Message):
    MAJOR = 0x09
    MINOR = 0x0B
    DIRECTION = m.Direction.S2C

    speaker_id: m.ObjectId
    target_id: m.ObjectId
    message: m.LocStr
    sound: m.ResRef
    play_hello_sound: m.Bool
    last_speaker_id: m.ObjectId


@dataclass(kw_only=True)
class ChatTokenTalkNoBubble(m.Message):
    MAJOR = 0x09
    MINOR = 0x0C
    DIRECTION = m.Direction.S2C

    speaker_id: m.ObjectId
    target_id: m.ObjectId
    message: m.LocStr
    sound: m.ResRef
    play_hello_sound: m.Bool
    last_speaker_id: m.ObjectId


@dataclass(kw_only=True)
class ChatSilentShout(m.Message):
    MAJOR = 0x09
    MINOR = 0x0E
    DIRECTION = m.Direction.S2C

    speaker: Speaker


@dataclass(kw_only=True)
class ChatServerTellRef(m.Message):
    MAJOR = 0x09
    MINOR = 0x0F
    DIRECTION = m.Direction.S2C

    speaker_id: m.ObjectId
    strref: m.Dword


@dataclass(kw_only=True)
class ChatDMTalk(m.Message):
    MAJOR = 0x09
    MINOR = 0x11
    DIRECTION = m.Direction.S2C

    speaker: Speaker


@dataclass(kw_only=True)
class ChatDMWhisper(m.Message):
    MAJOR = 0x09
    MINOR = 0x13
    DIRECTION = m.Direction.S2C

    speaker: Speaker


@dataclass(kw_only=True)
class ChatDMSilentShout(m.Message):
    MAJOR = 0x09
    MINOR = 0x1E
    DIRECTION = m.Direction.S2C

    speaker: Speaker


@dataclass(kw_only=True)
class ChatTalkC2S(m.Message):
    MAJOR = 0x09
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    message: m.String


@dataclass(kw_only=True)
class ChatShoutC2S(m.Message):
    MAJOR = 0x09
    MINOR = 0x02
    DIRECTION = m.Direction.C2S

    message: m.String


@dataclass(kw_only=True)
class ChatWhisperC2S(m.Message):
    MAJOR = 0x09
    MINOR = 0x03
    DIRECTION = m.Direction.C2S

    message: m.String


@dataclass(kw_only=True)
class ChatTellC2S(m.Message):
    MAJOR = 0x09
    MINOR = 0x04
    DIRECTION = m.Direction.C2S

    use_name: m.Bool
    target_player_id: Annotated[m.Dword, m.IfEq("use_name", False)]
    target_name: Annotated[m.String, m.IfEq("use_name", True)]
    message: m.String


@dataclass(kw_only=True)
class ChatPartyC2S(m.Message):
    MAJOR = 0x09
    MINOR = 0x06
    DIRECTION = m.Direction.C2S

    message: m.String


@dataclass(kw_only=True)
class ChatSilentShoutC2S(m.Message):
    MAJOR = 0x09
    MINOR = 0x0E
    DIRECTION = m.Direction.C2S

    message: m.String
