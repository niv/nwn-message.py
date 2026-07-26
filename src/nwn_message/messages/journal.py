from dataclasses import dataclass, field
from enum import IntFlag

from ..context import Context
from .. import message as m


@dataclass(kw_only=True)
class JournalAddWorld(m.Message):
    MAJOR = 0x1C
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    index: m.Int
    entry: m.String
    title: m.String
    calendar_day: m.Dword
    time_of_day: m.Dword


@dataclass(kw_only=True)
class JournalAddWorldStrref(m.Message):
    MAJOR = 0x1C
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    entry_strref: m.Dword
    title_strref: m.Dword
    calendar_day: m.Dword
    time_of_day: m.Dword


@dataclass(kw_only=True)
class JournalDeleteWorld(m.Message):
    MAJOR = 0x1C
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    index: m.Int


@dataclass(kw_only=True)
class JournalDeleteWorldStrref(m.Message):
    MAJOR = 0x1C
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    entry_strref: m.Dword


@dataclass(kw_only=True)
class JournalDeleteWorldAll(m.Message):
    MAJOR = 0x1C
    MINOR = 0x05
    DIRECTION = m.Direction.S2C

    marker: m.Byte


@dataclass(kw_only=True)
class JournalAddQuest(m.Message):
    MAJOR = 0x1C
    MINOR = 0x06
    DIRECTION = m.Direction.S2C

    name: m.LocStr
    text: m.LocStr
    calendar_day: m.Dword
    time_of_day: m.Dword
    plot_id: m.String
    state: m.Int
    priority: m.Dword
    picture_index: m.Word
    quest_completed: m.Bool


@dataclass(kw_only=True)
class JournalRemoveQuest(m.Message):
    MAJOR = 0x1C
    MINOR = 0x07
    DIRECTION = m.Direction.S2C

    plot_id: m.String


@dataclass(kw_only=True)
class JournalSetQuestPicture(m.Message):
    MAJOR = 0x1C
    MINOR = 0x08
    DIRECTION = m.Direction.S2C

    plot_id: m.String
    index: m.Int


class JournalUpdateFlag(IntFlag):
    SZNAME = 0x0001
    SZTEXT = 0x0002
    NCALENDARDAY = 0x0004
    NTIMEOFDAY = 0x0008
    NSTATE = 0x0010
    NPRIORITY = 0x0020
    NPICTUREINDEX = 0x0040
    BQUESTCOMPLETED = 0x0080
    LOADING = 0x0100
    REMOVE = 0x4000
    FULLUPDATE = 0x8000


@dataclass(kw_only=True)
class JournalFullUpdateEntry:
    flags: JournalUpdateFlag
    plot_id: m.String
    name: m.LocStr = m.LocStr("")
    text: m.LocStr = m.LocStr("")
    calendar_day: m.Dword = 0
    time_of_day: m.Dword = 0
    state: m.Int = 0
    priority: m.Dword = 0
    picture_index: m.Word = 0
    quest_completed: m.Bool = False

    @classmethod
    def read(cls, rd: m.Reader, context: Context):
        flags = JournalUpdateFlag(rd.read_word())
        plot_id = rd.read_str()

        if flags & JournalUpdateFlag.REMOVE:
            return cls(flags=flags, plot_id=plot_id)

        full_update = bool(context.fields.get("full_update", False))
        kwargs = {"flags": flags, "plot_id": plot_id}

        if full_update or flags & JournalUpdateFlag.SZNAME:
            kwargs["name"] = rd.read_locstr()
        if full_update or flags & JournalUpdateFlag.SZTEXT:
            kwargs["text"] = rd.read_locstr()
        if full_update or flags & JournalUpdateFlag.NCALENDARDAY:
            kwargs["calendar_day"] = rd.read_dword()
        if full_update or flags & JournalUpdateFlag.NTIMEOFDAY:
            kwargs["time_of_day"] = rd.read_dword()
        if full_update or flags & JournalUpdateFlag.NSTATE:
            kwargs["state"] = rd.read_int()
        if full_update or flags & JournalUpdateFlag.NPRIORITY:
            kwargs["priority"] = rd.read_dword()
        if full_update or flags & JournalUpdateFlag.NPICTUREINDEX:
            kwargs["picture_index"] = rd.read_word()
        if full_update or flags & JournalUpdateFlag.BQUESTCOMPLETED:
            kwargs["quest_completed"] = rd.read_bool()

        return cls(**kwargs)

    def write(self, wr: m.Writer, context: Context) -> None:
        wr.write_word(int(self.flags))
        wr.write_str(self.plot_id)

        if self.flags & JournalUpdateFlag.REMOVE:
            return

        full_update = bool(context.fields.get("full_update", False))

        if full_update or self.flags & JournalUpdateFlag.SZNAME:
            wr.write_locstr(self.name)
        if full_update or self.flags & JournalUpdateFlag.SZTEXT:
            wr.write_locstr(self.text)
        if full_update or self.flags & JournalUpdateFlag.NCALENDARDAY:
            wr.write_dword(self.calendar_day)
        if full_update or self.flags & JournalUpdateFlag.NTIMEOFDAY:
            wr.write_dword(self.time_of_day)
        if full_update or self.flags & JournalUpdateFlag.NSTATE:
            wr.write_int(self.state)
        if full_update or self.flags & JournalUpdateFlag.NPRIORITY:
            wr.write_dword(self.priority)
        if full_update or self.flags & JournalUpdateFlag.NPICTUREINDEX:
            wr.write_word(self.picture_index)
        if full_update or self.flags & JournalUpdateFlag.BQUESTCOMPLETED:
            wr.write_bool(self.quest_completed)


@dataclass(kw_only=True)
class JournalFullUpdate(m.Message):
    MAJOR = 0x1C
    MINOR = 0x09
    DIRECTION = m.Direction.S2C

    changes_to_follow: m.Bool
    full_update: m.Bool = False
    entries: list[JournalFullUpdateEntry] = field(default_factory=list)
    clear_old_entries: m.Bool = False

    @classmethod
    def read(cls, rd: m.Reader, context: Context):
        changes_to_follow = rd.read_bool()
        if not changes_to_follow:
            if rd.more():
                full_update = rd.read_bool()
                entry_count = rd.read_int()
                for _ in range(entry_count):
                    JournalFullUpdateEntry.read(rd, context)
                return cls(
                    changes_to_follow=False,
                    full_update=full_update,
                    entries=[],
                    clear_old_entries=full_update,
                )
            return cls(changes_to_follow=False)

        full_update = rd.read_bool()
        entry_count = rd.read_int()
        context.fields = {"full_update": full_update}
        entries = [JournalFullUpdateEntry.read(rd, context) for _ in range(entry_count)]
        return cls(changes_to_follow=True, full_update=full_update, entries=entries)

    def write(self, wr: m.Writer, context: Context) -> None:
        wr.write_bool(self.changes_to_follow)
        if not self.changes_to_follow:
            if self.clear_old_entries:
                wr.write_bool(True)
                wr.write_int(0)
            return

        wr.write_bool(self.full_update)
        wr.write_int(len(self.entries))
        context.fields = {"full_update": self.full_update}
        for entry in self.entries:
            entry.write(wr, context)


@dataclass(kw_only=True)
class JournalQuestScreenOpen(m.Message):
    MAJOR = 0x1C
    MINOR = 0x0A
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class JournalQuestScreenClosed(m.Message):
    MAJOR = 0x1C
    MINOR = 0x0B
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class JournalUpdated(m.Message):
    MAJOR = 0x1C
    MINOR = 0x0C
    DIRECTION = m.Direction.S2C

    name: m.LocStr
    type_quest: m.Bool
    quest_completed: m.Bool


@dataclass(kw_only=True)
class JournalRequestAdd(m.Message):
    MAJOR = 0x1C
    MINOR = 0x0D
    DIRECTION = m.Direction.C2S

    title: m.String
    entry: m.String


@dataclass(kw_only=True)
class JournalRequestDelete(m.Message):
    MAJOR = 0x1C
    MINOR = 0x0E
    DIRECTION = m.Direction.C2S

    index: m.Int
    is_strref: m.Bool
