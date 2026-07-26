from dataclasses import dataclass
from typing import Annotated

from .. import message as m


@dataclass(kw_only=True)
class DialogReplyLine:
    text: m.LocStr
    reply_index: m.Dword


@dataclass(kw_only=True)
class DialogEntry(m.Message):
    MAJOR = 0x14
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    owner: m.ObjectId
    speaker: m.ObjectId
    token_target: m.ObjectId
    entry: m.LocStr


@dataclass(kw_only=True)
class DialogReplies(m.Message):
    MAJOR = 0x14
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    current_entry_index: m.Dword
    end_of_dialog: m.Bool
    disable_camera_zoom: m.Bool
    token_target: m.ObjectId
    replies_count: m.Dword
    inactive_replies_count: m.Dword
    replies: Annotated[
        list[DialogReplyLine],
        m.ComputedAddSizeHint("replies_count", "inactive_replies_count"),
    ]


@dataclass(kw_only=True)
class DialogReply(m.Message):
    MAJOR = 0x14
    MINOR = 0x03
    DIRECTION = m.Direction.C2S

    owner: m.ObjectId
    reply_index: m.Dword
    escape_dialog: m.Byte
    current_entry_index: m.Dword


@dataclass(kw_only=True)
class DialogReplyChosen(m.Message):
    MAJOR = 0x14
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    end_of_dialog: m.Byte
    reply_index: m.Dword
    current_entry_index: m.Dword
    token_target: m.ObjectId
    reply: m.LocStr


@dataclass(kw_only=True)
class DialogClose(m.Message):
    MAJOR = 0x14
    MINOR = 0x05
    DIRECTION = m.Direction.S2C
