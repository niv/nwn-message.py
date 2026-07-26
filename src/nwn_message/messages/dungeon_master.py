from dataclasses import dataclass, field
from enum import IntEnum
from typing import Annotated, Self

from .. import message as m
from ..context import Context
from ..types import ObjectType

# Omitted 0x1f handlers:
# MINOR 0x2A (Duplicate): server handler is a DM stub implementation.
# MINOR 0x81 (TakeItem): server handler is a DM stub implementation.
# MINOR 0x88 (SetDate): defined in message defs, but no active handler implementation.


class DungeonMasterVarType(IntEnum):
    INTEGER = 0
    FLOAT = 1
    STRING = 2
    OBJECT_ID = 3
    VECTOR = 4


@dataclass(kw_only=True)
class DungeonMasterObjectListEntry:
    object_id: m.ObjectId
    first_name: m.LocStr
    last_name: m.LocStr = field(default_factory=m.LocStr)
    current_hit_points: m.Short = 0
    max_hit_points: m.Short = 0
    invulnerable: m.Bool = False
    immortal: m.Bool = False
    is_pc: m.Bool = False
    is_dm: m.Bool = False
    is_controlled: m.Bool = False
    ai_on: m.Bool = False


@dataclass(kw_only=True)
class DungeonMasterRequestObjectList(m.Message):
    MAJOR = 0x1F
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    object_type: m.Int


@dataclass(kw_only=True)
class DungeonMasterObjectList(m.Message):
    MAJOR = 0x1F
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    area: m.ObjectId
    object_type: m.Int
    objects: list[DungeonMasterObjectListEntry] = field(default_factory=list)

    @classmethod
    def read(cls, rd: m.Reader, _context: Context) -> Self:
        area = rd.read_object_id()
        object_type = rd.read_int()
        count = rd.read_int()

        objects = []
        for _ in range(count):
            object_id = rd.read_object_id()
            first_name = rd.read_locstr()

            if object_type == ObjectType.CREATURE:
                objects.append(
                    DungeonMasterObjectListEntry(
                        object_id=object_id,
                        first_name=first_name,
                        last_name=rd.read_locstr(),
                        current_hit_points=rd.read_short(),
                        max_hit_points=rd.read_short(),
                        invulnerable=rd.read_bool(),
                        immortal=rd.read_bool(),
                        is_pc=rd.read_bool(),
                        is_dm=rd.read_bool(),
                        is_controlled=rd.read_bool(),
                        ai_on=rd.read_bool(),
                    )
                )
            else:
                objects.append(
                    DungeonMasterObjectListEntry(
                        object_id=object_id,
                        first_name=first_name,
                    )
                )

        return cls(area=area, object_type=object_type, objects=objects)

    def write(self, wr: m.Writer, _context: Context) -> None:
        wr.write_object_id(self.area)
        wr.write_int(self.object_type)
        wr.write_int(len(self.objects))

        for obj in self.objects:
            wr.write_object_id(obj.object_id)
            wr.write_locstr(obj.first_name)
            if self.object_type == ObjectType.CREATURE:
                wr.write_locstr(obj.last_name)
                wr.write_short(obj.current_hit_points)
                wr.write_short(obj.max_hit_points)
                wr.write_bool(obj.invulnerable)
                wr.write_bool(obj.immortal)
                wr.write_bool(obj.is_pc)
                wr.write_bool(obj.is_dm)
                wr.write_bool(obj.is_controlled)
                wr.write_bool(obj.ai_on)


@dataclass(kw_only=True)
class DungeonMasterSearchByTag(m.Message):
    MAJOR = 0x1F
    MINOR = 0x03
    DIRECTION = m.Direction.C2S

    tag: m.String
    object_type: m.Int


@dataclass(kw_only=True)
class DungeonMasterSearchByTagResult(m.Message):
    MAJOR = 0x1F
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    area: m.ObjectId
    object_id: m.ObjectId
    object_type: m.Int


@dataclass(kw_only=True)
class DungeonMasterSearchByTagResultNone(m.Message):
    MAJOR = 0x1F
    MINOR = 0x05
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class DungeonMasterCreatorList(m.Message):
    MAJOR = 0x1F
    MINOR = 0x06
    DIRECTION = m.Direction.S2C

    expansion_packs: m.Byte = 0x1 | 0x2
    creature_palette: m.Void
    item_palette: m.Void
    encounter_palette: m.Void
    waypoint_palette: m.Void
    trigger_palette: m.Void
    portal_palette: m.Void
    placeable_palette: m.Void


@dataclass(kw_only=True)
class DungeonMasterAreaListEntry:
    area: m.ObjectId
    is_display_name: m.Bool
    name: Annotated[m.LocStr, m.IfEq("is_display_name", False)]
    display_name: Annotated[m.String, m.IfEq("is_display_name", True)]
    tag: m.String


@dataclass(kw_only=True)
class DungeonMasterAreaList(m.Message):
    MAJOR = 0x1F
    MINOR = 0x07
    DIRECTION = m.Direction.S2C

    areas: Annotated[list[DungeonMasterAreaListEntry], m.SizePrefix.INT]


@dataclass(kw_only=True)
class DungeonMasterAreaListSorted(m.Message):
    MAJOR = 0x1F
    MINOR = 0x08
    DIRECTION = m.Direction.C2S

    areas: Annotated[list[m.ObjectId], m.SizePrefix.INT]


@dataclass(kw_only=True)
class DungeonMasterPartyList(m.Message):
    MAJOR = 0x1F
    MINOR = 0x09
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class DungeonMasterSpawnCreature(m.Message):
    MAJOR = 0x1F
    MINOR = 0x0A
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    position: m.Vec3
    template: m.ResRef


@dataclass(kw_only=True)
class DungeonMasterSpawnItem(m.Message):
    MAJOR = 0x1F
    MINOR = 0x0B
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    position: m.Vec3
    template: m.ResRef


@dataclass(kw_only=True)
class DungeonMasterSpawnTrigger(m.Message):
    MAJOR = 0x1F
    MINOR = 0x0C
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    position: m.Vec3
    template: m.ResRef


@dataclass(kw_only=True)
class DungeonMasterSpawnWaypoint(m.Message):
    MAJOR = 0x1F
    MINOR = 0x0D
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    position: m.Vec3
    name: m.String


@dataclass(kw_only=True)
class DungeonMasterSpawnEncounter(m.Message):
    MAJOR = 0x1F
    MINOR = 0x0E
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    position: m.Vec3
    template: m.ResRef


@dataclass(kw_only=True)
class DungeonMasterSpawnPortal(m.Message):
    MAJOR = 0x1F
    MINOR = 0x0F
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    position: m.Vec3
    portal_info: m.String


@dataclass(kw_only=True)
class DungeonMasterSpawnPlaceable(m.Message):
    MAJOR = 0x1F
    MINOR = 0x10
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    position: m.Vec3
    orientation: m.Vec3
    template: m.ResRef


@dataclass(kw_only=True)
class DungeonMasterDifficultyC2S(m.Message):
    MAJOR = 0x1F
    MINOR = 0x11
    DIRECTION = m.Direction.C2S

    difficulty: m.Int


@dataclass(kw_only=True)
class DungeonMasterDifficultyS2C(m.Message):
    MAJOR = 0x1F
    MINOR = 0x11
    DIRECTION = m.Direction.S2C

    difficulty: m.Int


@dataclass(kw_only=True)
class DungeonMasterViewInventory(m.Message):
    MAJOR = 0x1F
    MINOR = 0x12
    DIRECTION = m.Direction.C2S

    open_inventory: m.Int
    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterSpawnTrapOnObject(m.Message):
    MAJOR = 0x1F
    MINOR = 0x13
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    target: m.ObjectId
    trap: m.ResRef


@dataclass(kw_only=True)
class DungeonMasterLogin(m.Message):
    MAJOR = 0x1F
    MINOR = 0x14
    DIRECTION = m.Direction.C2S

    password: m.String


@dataclass(kw_only=True)
class DungeonMasterLogout(m.Message):
    MAJOR = 0x1F
    MINOR = 0x15
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class DungeonMasterLoginState(m.Message):
    MAJOR = 0x1F
    MINOR = 0x16
    DIRECTION = m.Direction.S2C

    is_dm: m.Bool
    is_dm_manifested: m.Bool
    difficulty_level: m.Int


@dataclass(kw_only=True)
class DungeonMasterHeal(m.Message):
    MAJOR = 0x1F
    MINOR = 0x20
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterKill(m.Message):
    MAJOR = 0x1F
    MINOR = 0x21
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterGoto(m.Message):
    MAJOR = 0x1F
    MINOR = 0x22
    DIRECTION = m.Direction.C2S

    area_or_object: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterPossess(m.Message):
    MAJOR = 0x1F
    MINOR = 0x23
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterInvulnerable(m.Message):
    MAJOR = 0x1F
    MINOR = 0x24
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterRest(m.Message):
    MAJOR = 0x1F
    MINOR = 0x25
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterLimbo(m.Message):
    MAJOR = 0x1F
    MINOR = 0x26
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterSearchNext(m.Message):
    MAJOR = 0x1F
    MINOR = 0x27
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterSearchById(m.Message):
    MAJOR = 0x1F
    MINOR = 0x28
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterImpersonate(m.Message):
    MAJOR = 0x1F
    MINOR = 0x29
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterToggleAI(m.Message):
    MAJOR = 0x1F
    MINOR = 0x2B
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterToggleLock(m.Message):
    MAJOR = 0x1F
    MINOR = 0x2C
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterDisableTrap(m.Message):
    MAJOR = 0x1F
    MINOR = 0x2D
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterTriggerEntered(m.Message):
    MAJOR = 0x1F
    MINOR = 0x2E
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterTriggerExit(m.Message):
    MAJOR = 0x1F
    MINOR = 0x2F
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterManifest(m.Message):
    MAJOR = 0x1F
    MINOR = 0x30
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterUnmanifest(m.Message):
    MAJOR = 0x1F
    MINOR = 0x31
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterImmortal(m.Message):
    MAJOR = 0x1F
    MINOR = 0x32
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterGotoPoint(m.Message):
    MAJOR = 0x1F
    MINOR = 0x50
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    position: m.Vec3


@dataclass(kw_only=True)
class DungeonMasterGiveXP(m.Message):
    MAJOR = 0x1F
    MINOR = 0x60
    DIRECTION = m.Direction.C2S

    amount: m.Int
    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterGiveLevel(m.Message):
    MAJOR = 0x1F
    MINOR = 0x61
    DIRECTION = m.Direction.C2S

    amount: m.Int
    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterGiveGold(m.Message):
    MAJOR = 0x1F
    MINOR = 0x62
    DIRECTION = m.Direction.C2S

    amount: m.Int
    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterSetFaction(m.Message):
    MAJOR = 0x1F
    MINOR = 0x63
    DIRECTION = m.Direction.C2S

    faction: m.Int
    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterSetFactionByName(m.Message):
    MAJOR = 0x1F
    MINOR = 0x64
    DIRECTION = m.Direction.C2S

    target: m.ObjectId
    faction_name: m.String


@dataclass(kw_only=True)
class DungeonMasterGiveItem(m.Message):
    MAJOR = 0x1F
    MINOR = 0x80
    DIRECTION = m.Direction.C2S

    target: m.ObjectId
    item: m.ResRef


@dataclass(kw_only=True)
class DungeonMasterGotoPointTarget(m.Message):
    MAJOR = 0x1F
    MINOR = 0x82
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    position: m.Vec3
    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterGotoPointAllPlayers(m.Message):
    MAJOR = 0x1F
    MINOR = 0x83
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    position: m.Vec3


@dataclass(kw_only=True)
class DungeonMasterSetStat(m.Message):
    MAJOR = 0x1F
    MINOR = 0x84
    DIRECTION = m.Direction.C2S

    stat_id: m.Int
    stat_value: m.Float
    set_mode: m.Bool
    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterGetVar(m.Message):
    MAJOR = 0x1F
    MINOR = 0x85
    DIRECTION = m.Direction.C2S

    var_type: Annotated[DungeonMasterVarType, m.MessageType.BYTE]
    target: m.ObjectId
    name: m.String


@dataclass(kw_only=True)
class DungeonMasterSetVar(m.Message):
    MAJOR = 0x1F
    MINOR = 0x86
    DIRECTION = m.Direction.C2S

    var_type: Annotated[DungeonMasterVarType, m.MessageType.BYTE]
    target: m.ObjectId
    name: m.String
    int_value: Annotated[m.Int, m.IfEq("var_type", DungeonMasterVarType.INTEGER)]
    float_value: Annotated[m.Float, m.IfEq("var_type", DungeonMasterVarType.FLOAT)]
    string_value: Annotated[m.String, m.IfEq("var_type", DungeonMasterVarType.STRING)]
    object_id_value: Annotated[
        m.ObjectId,
        m.IfEq("var_type", DungeonMasterVarType.OBJECT_ID),
    ]
    vector_value: Annotated[m.Vec3, m.IfEq("var_type", DungeonMasterVarType.VECTOR)]


@dataclass(kw_only=True)
class DungeonMasterSetTime(m.Message):
    MAJOR = 0x1F
    MINOR = 0x87
    DIRECTION = m.Direction.C2S

    hour: m.Int
    minute: m.Int
    second: m.Int
    millisecond: m.Int


@dataclass(kw_only=True)
class DungeonMasterSetFactionReputation(m.Message):
    MAJOR = 0x1F
    MINOR = 0x89
    DIRECTION = m.Direction.C2S

    faction_1: m.String
    faction_2: m.String
    reputation: m.Int


@dataclass(kw_only=True)
class DungeonMasterGetFactionReputation(m.Message):
    MAJOR = 0x1F
    MINOR = 0x8A
    DIRECTION = m.Direction.C2S

    faction_1: m.String
    faction_2: m.String


@dataclass(kw_only=True)
class DungeonMasterDumpLocals(m.Message):
    MAJOR = 0x1F
    MINOR = 0x8B
    DIRECTION = m.Direction.C2S

    scope_type: m.Int
    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterGiveGoodAlignment(m.Message):
    MAJOR = 0x1F
    MINOR = 0x8C
    DIRECTION = m.Direction.C2S

    amount: m.Int
    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterGiveEvilAlignment(m.Message):
    MAJOR = 0x1F
    MINOR = 0x8D
    DIRECTION = m.Direction.C2S

    amount: m.Int
    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterGiveLawfulAlignment(m.Message):
    MAJOR = 0x1F
    MINOR = 0x8E
    DIRECTION = m.Direction.C2S

    amount: m.Int
    target: m.ObjectId


@dataclass(kw_only=True)
class DungeonMasterGiveChaoticAlignment(m.Message):
    MAJOR = 0x1F
    MINOR = 0x8F
    DIRECTION = m.Direction.C2S

    amount: m.Int
    target: m.ObjectId
