from dataclasses import dataclass
from typing import Annotated
from enum import IntEnum

import nwn_message.message as m
from nwn_message.messages.gui_info_popup import INVALID_OBJECT_ID


class GuiPanel(IntEnum):
    PLAYER_DEATH = 0
    MINIMAP = 2
    COMPASS = 3
    INVENTORY = 4
    PLAYERLIST = 5
    JOURNAL = 6
    SPELLBOOK = 7
    CHARACTERSHEET = 8
    LEVELUP = 9
    GOLD_INVENTORY = 10
    GOLD_BARTER = 11
    EXAMINE_CREATURE = 12
    EXAMINE_ITEM = 13
    EXAMINE_PLACEABLE = 14
    EXAMINE_DOOR = 15
    RADIAL_TILE = 16
    RADIAL_TRIGGER = 17
    RADIAL_CREATURE = 18
    RADIAL_ITEM = 19
    RADIAL_PLACEABLE = 20
    RADIAL_DOOR = 21
    RADIAL_QUICKBAR = 22
    QUICKBAR = 23
    QUICKBAR_KEYS = 24
    CHAT_BAR = 25
    CHAT_HISTORY = 26
    PLAYER_AND_PARTY = 27


@dataclass(kw_only=True)
class GuiEventNotify(m.Message):
    MAJOR = 0x35
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    gui_event: m.Word
    gui_event_integer: m.Word
    gui_event_object: m.ObjectId
    gui_event_position: tuple[m.Float, m.Float, m.Float]


@dataclass(kw_only=True)
class GuiEventDisable(m.Message):
    MAJOR = 0x35
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    gui_element: Annotated[GuiPanel, m.MessageType.INT]
    disable: m.Bool
    gui_event_object: m.ObjectId = INVALID_OBJECT_ID
