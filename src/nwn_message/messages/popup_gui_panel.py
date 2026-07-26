from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class PopUpGUIPanelPopUpPlayerDeathPanel(m.Message):
    MAJOR = 0x24
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    respawn_button: m.Bool
    wait_for_help_button: m.Bool
    string_reference: m.Dword
    string_override: m.String


@dataclass(kw_only=True)
class PopUpGUIPanelDestroyPlayerDeathPanel(m.Message):
    MAJOR = 0x24
    MINOR = 0x02
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class PopUpGUIPanelPopUpPartyInvitationReceivedPanel(m.Message):
    MAJOR = 0x24
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    inviter: m.String


@dataclass(kw_only=True)
class PopUpGUIPanelPopUpOtherPlayerPanel(m.Message):
    MAJOR = 0x24
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    gui_panel: m.Int
