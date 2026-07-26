from dataclasses import dataclass
from typing import Annotated

from .. import message as m


@dataclass(kw_only=True)
class StoreRequestBuy(m.Message):
    MAJOR = 0x07
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    item: m.ObjectId
    desired_x: m.Byte
    desired_y: m.Byte
    desired_repository: m.ObjectId


@dataclass(kw_only=True)
class StoreRequestSell(m.Message):
    MAJOR = 0x07
    MINOR = 0x02
    DIRECTION = m.Direction.C2S

    item: m.ObjectId


@dataclass(kw_only=True)
class StoreConfirmTransaction(m.Message):
    MAJOR = 0x07
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    store_gold: m.Int


@dataclass(kw_only=True)
class StoreOpenPanelC2S(m.Message):
    MAJOR = 0x07
    MINOR = 0x04
    DIRECTION = m.Direction.C2S

    panel: m.Byte


@dataclass(kw_only=True)
class StoreOpenPanelS2C(m.Message):
    MAJOR = 0x07
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    panel: m.Byte
    sell_rate: m.Short
    buy_rate: m.Byte
    black_market_rate: m.Byte
    id_cost: m.Int
    max_buy: m.Int
    store_gold: m.Int
    black_market: m.Bool
    # if True, buy_list is items store will NOT buy; else items it will ONLY buy
    will_not_buy: m.Bool
    buy_list: Annotated[list[m.Int], m.SizePrefix.INT]


@dataclass(kw_only=True)
class StoreOpenPage(m.Message):
    MAJOR = 0x07
    MINOR = 0x05
    DIRECTION = m.Direction.C2S

    page: m.Byte


@dataclass(kw_only=True)
class StoreClose(m.Message):
    MAJOR = 0x07
    MINOR = 0x06


@dataclass(kw_only=True)
class StoreIdentify(m.Message):
    MAJOR = 0x07
    MINOR = 0x07
    DIRECTION = m.Direction.C2S

    item: m.ObjectId
