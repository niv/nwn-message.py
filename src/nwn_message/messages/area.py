from typing import Annotated
from dataclasses import dataclass, field
from enum import IntEnum, IntFlag

from .. import message as m
from ..net_types import VisualTransformData


@dataclass(kw_only=True)
class AmbientSound:
    music_playing: m.Bool = False
    battle_playing: m.Bool = False
    sound_playing: m.Bool = False
    music_delay: m.Int = 0
    music_day_track: m.Int = 0
    music_night_track: m.Int = 0
    battle_track: m.Int = 0
    sound_day_track: m.Int = 0
    sound_night_track: m.Int = 0
    day_volume: m.Byte = 0
    night_volume: m.Byte = 0


@dataclass(kw_only=True)
class CustomWind:
    direction: m.Vec3
    magnitude: m.Float
    yaw: m.Float
    pitch: m.Float


@dataclass(kw_only=True)
class GrassInfo:
    default_grass_disabled: m.Bool = False

    @dataclass(kw_only=True)
    class Override:
        material_index: m.Byte
        texture: m.String
        density: m.Float
        height: m.Float
        ambient: m.Vec3
        diffuse: m.Vec3

    overrides: Annotated[list[Override], m.SizePrefix.INT] = field(default_factory=list)


class TileFlag(IntFlag):
    MAIN_LIGHT_1 = 0x0001
    MAIN_LIGHT_2 = 0x0002
    SOURCE_LIGHT_1 = 0x0004
    SOURCE_LIGHT_2 = 0x0008
    REPLACE_TEXTURE = 0x0010
    ANIM_LOOP_1 = 0x0020
    ANIM_LOOP_2 = 0x0040
    ANIM_LOOP_3 = 0x0080


@dataclass(kw_only=True)
class Tile:
    id: m.Int = 0
    orientation: m.Int = 0
    height: m.Int = 0
    flags: Annotated[TileFlag, m.MessageType.WORD] = TileFlag(0)
    main_light_1: Annotated[m.Byte, m.IfFlag("flags", TileFlag.MAIN_LIGHT_1)] = 0
    main_light_2: Annotated[m.Byte, m.IfFlag("flags", TileFlag.MAIN_LIGHT_2)] = 0
    source_light_1: Annotated[m.Byte, m.IfFlag("flags", TileFlag.SOURCE_LIGHT_1)] = 0
    source_light_2: Annotated[m.Byte, m.IfFlag("flags", TileFlag.SOURCE_LIGHT_2)] = 0
    replace_texture: Annotated[m.Byte, m.IfFlag("flags", TileFlag.REPLACE_TEXTURE)] = 0
    anim_loop_1: Annotated[m.Byte, m.IfFlag("flags", TileFlag.ANIM_LOOP_1)] = 0
    anim_loop_2: Annotated[m.Byte, m.IfFlag("flags", TileFlag.ANIM_LOOP_2)] = 0
    anim_loop_3: Annotated[m.Byte, m.IfFlag("flags", TileFlag.ANIM_LOOP_3)] = 0


@dataclass(kw_only=True)
class Sound:
    object_id: m.ObjectId
    is_active: m.Bool
    positional: m.Bool
    looping: m.Bool
    volume: m.Byte
    volume_variation: m.Byte
    time_of_day: m.Byte
    pitch_variation: m.Float
    hours: m.Dword
    priority: m.Byte
    interval: m.Dword
    interval_variance: m.Dword
    min_distance: m.Float
    max_distance: m.Float
    continuous: m.Bool
    random: m.Bool
    random_position: m.Bool
    random_x_range: m.Float
    random_y_range: m.Float
    position: m.Vec3
    sound_list: Annotated[list[m.ResRef], m.SizePrefix.WORD]


@dataclass(kw_only=True)
class MapNote:
    object_id: m.ObjectId
    position: m.Vec3
    enabled: m.Bool
    note: m.LocStr


@dataclass(kw_only=True)
class UserNote:
    index: m.Int
    note: m.String
    position: m.Vec3


@dataclass(kw_only=True)
class PlaceableLight:
    object_id: m.ObjectId
    appearance: m.Word
    position: m.Vec3


@dataclass(kw_only=True)
class Placeable:
    object_id: m.ObjectId
    appearance: m.Word
    position: m.Vec3
    orientation: m.Vec3


class AreaFlag(IntFlag):
    INTERIOR = 0x1
    UNDERGROUND = 0x2
    NATURAL = 0x4


class AreaWeatherType(IntEnum):
    NONE = -1
    CLEAR = 0
    RAIN = 1
    SNOW = 2


@dataclass(kw_only=True)
class AreaClientArea(m.Message):
    MAJOR = 0x04
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    transition: m.Int = 0
    location: m.Vec3 = (0.0, 0.0, 0.0)
    orientation: m.Float = 0.0
    player_new_to_module: m.Bool = True

    object_id: m.ObjectId
    resref: m.ResRef
    # This is re-wrapping locstr for some reason
    is_display_name: m.Bool = True
    name: Annotated[m.LocStr | None, m.IfEq("is_display_name", False)] = None
    display_name: Annotated[m.String, m.IfEq("is_display_name", True)] = ""

    _module_entry_info_start: m.Vec3i = (0, 0, 0)  # unused

    flags: Annotated[AreaFlag, m.MessageType.DWORD] = AreaFlag.INTERIOR

    moon_ambient_color: m.Dword = 0xCCCCCC
    moon_diffuse_color: m.Dword = 0xCCCCCC

    moon_direction: m.Vec3 = (0.0, 0.0, 0.0)

    moon_fog_color: m.Dword = 0
    moon_fog_amount: m.Byte = 0
    moon_shadows: m.Bool = False

    sun_ambient_color: m.Dword = 0xFFFFFF
    sun_diffuse_color: m.Dword = 0xFFFFFF

    sun_direction: m.Vec3 = (0.0, 0.0, 0.0)

    sun_fog_color: m.Dword = 0
    sun_fog_amount: m.Byte = 0
    sun_shadows: m.Bool = False

    use_daynight_cycle: m.Bool = True
    is_night: m.Bool = False

    pvp: m.Byte = 0
    resting_allowed: m.Bool = False
    shadow_opacity: m.Byte = 0
    fog_clip_distance: m.Float = 45.0
    environmental_audio: m.Int = 0

    ambient_sound: AmbientSound = field(default_factory=AmbientSound)

    time_of_day_state: m.Byte = 0
    time_into_transition: m.Dword = 0
    hour: m.Byte = 12
    day: m.Byte = 1
    month: m.Byte = 1
    year: m.Dword = 1376
    dawn: m.Byte = 6
    dusk: m.Byte = 18
    skybox: m.Byte = 0

    chance_of_lightning: m.Byte = 0
    wind_amount: m.Byte = 0
    custom_wind: Annotated[CustomWind | None, m.IfEq("wind_amount", 3)] = None

    weather_type: Annotated[AreaWeatherType, m.MessageType.BYTE] = AreaWeatherType.CLEAR
    weather_started: m.Bool = False
    width: m.Int
    height: m.Int
    tileset: m.ResRef

    grass: GrassInfo = field(default_factory=GrassInfo)
    tile_border_disabled: m.Bool = False

    tiles: Annotated[list[Tile], m.ComputedMultiplySizeHint("width", "height")]
    map_notes: Annotated[list[MapNote], m.SizePrefix.INT] = field(default_factory=list)
    user_notes: Annotated[list[UserNote], m.SizePrefix.INT] = field(
        default_factory=list
    )
    sounds: Annotated[list[Sound], m.SizePrefix.WORD] = field(default_factory=list)
    placeable_lights: Annotated[list[PlaceableLight], m.SizePrefix.WORD] = field(
        default_factory=list
    )
    static_placeables: Annotated[list[Placeable], m.SizePrefix.WORD] = field(
        default_factory=list
    )
    placeable_count: m.Word = 0
    creature_count: m.Word = 0


@dataclass(kw_only=True)
class AreaVisualEffect(m.Message):
    MAJOR = 0x04
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    anim_id: m.Word
    position: m.Vec3
    vt: VisualTransformData


@dataclass(kw_only=True)
class AreaAreaLoaded(m.Message):
    MAJOR = 0x04
    MINOR = 0x03
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class AreaWeather(m.Message):
    MAJOR = 0x04
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    weather_type: Annotated[AreaWeatherType, m.MessageType.BYTE]
    start: m.Bool


class TileChangeType(IntEnum):
    BOTH = ord("B")
    MAIN_ONLY = ord("M")
    SOURCE_ONLY = ord("S")


@dataclass(kw_only=True)
class AreaRecomputeStaticLighting(m.Message):
    MAJOR = 0x04
    MINOR = 0x05
    DIRECTION = m.Direction.S2C

    @dataclass(kw_only=True)
    class TileChange:
        type: Annotated[TileChangeType, m.Char]
        x: m.Byte
        y: m.Byte
        main1: Annotated[m.Byte, m.IfNotEq("type", 83)]
        main2: Annotated[m.Byte, m.IfNotEq("type", 83)]
        source1: Annotated[m.Byte, m.IfNotEq("type", 77)]
        source2: Annotated[m.Byte, m.IfNotEq("type", 77)]

    @dataclass(kw_only=True)
    class PlaceableChange:
        object_id: m.ObjectId
        light_is_on: m.Bool

    tile_changes: Annotated[list[TileChange], m.SizePrefix.WORD]
    placeable_changes: Annotated[list[PlaceableChange], m.SizePrefix.WORD]


@dataclass(kw_only=True)
class AreaChangeDayNight(m.Message):
    MAJOR = 0x04
    MINOR = 0x06
    DIRECTION = m.Direction.S2C

    is_day: m.Bool
    transition_time: m.Float


@dataclass(kw_only=True)
class AreaUpdateSkyBox(m.Message):
    MAJOR = 0x04
    MINOR = 0x07
    DIRECTION = m.Direction.S2C

    skybox: m.Int
    object_id: m.ObjectId


@dataclass(kw_only=True)
class AreaUpdateFogColor(m.Message):
    MAJOR = 0x04
    MINOR = 0x08
    DIRECTION = m.Direction.S2C

    sun_fog_color: m.Dword
    moon_fog_color: m.Dword
    object_id: m.ObjectId
    fade_time: m.Float


@dataclass(kw_only=True)
class AreaUpdateFogAmount(m.Message):
    MAJOR = 0x04
    MINOR = 0x09
    DIRECTION = m.Direction.S2C

    sun_fog_amount: m.Byte
    moon_fog_amount: m.Byte
    object_id: m.ObjectId


@dataclass(kw_only=True)
class AreaUpdateBlackoutEffect(m.Message):
    MAJOR = 0x04
    MINOR = 0x0A
    DIRECTION = m.Direction.S2C

    enable: m.Bool


@dataclass(kw_only=True)
class AreaSetName(m.Message):
    MAJOR = 0x04
    MINOR = 0x0B
    DIRECTION = m.Direction.S2C

    object_id: m.ObjectId
    is_display_name: m.Bool
    display_name: Annotated[m.String, m.IfEq("is_display_name", True)]
    area_name: Annotated[m.LocStr, m.IfEq("is_display_name", False)]


@dataclass(kw_only=True)
class AreaDestroyed(m.Message):
    MAJOR = 0x04
    MINOR = 0x0C
    DIRECTION = m.Direction.S2C

    object_id: m.ObjectId


@dataclass(kw_only=True)
class AreaUpdateWind(m.Message):
    MAJOR = 0x04
    MINOR = 0x0D
    DIRECTION = m.Direction.S2C

    direction: m.Vec3
    magnitude: m.Float
    yaw: m.Float
    pitch: m.Float


@dataclass(kw_only=True)
class AreaUpdateMoonAmbientColor(m.Message):
    MAJOR = 0x04
    MINOR = 0x0E
    DIRECTION = m.Direction.S2C

    color: m.Dword
    object_id: m.ObjectId
    fade_time: m.Float


@dataclass(kw_only=True)
class AreaUpdateMoonDiffuseColor(m.Message):
    MAJOR = 0x04
    MINOR = 0x0F
    DIRECTION = m.Direction.S2C

    color: m.Dword
    object_id: m.ObjectId
    fade_time: m.Float


@dataclass(kw_only=True)
class AreaUpdateMoonDirection(m.Message):
    MAJOR = 0x04
    MINOR = 0x10
    DIRECTION = m.Direction.S2C

    direction: m.Vec3
    object_id: m.ObjectId
    fade_time: m.Float


@dataclass(kw_only=True)
class AreaUpdateSunAmbientColor(m.Message):
    MAJOR = 0x04
    MINOR = 0x11
    DIRECTION = m.Direction.S2C

    color: m.Dword
    object_id: m.ObjectId
    fade_time: m.Float


@dataclass(kw_only=True)
class AreaUpdateSunDiffuseColor(m.Message):
    MAJOR = 0x04
    MINOR = 0x12
    DIRECTION = m.Direction.S2C

    color: m.Dword
    object_id: m.ObjectId
    fade_time: m.Float


@dataclass(kw_only=True)
class AreaUpdateSunDirection(m.Message):
    MAJOR = 0x04
    MINOR = 0x13
    DIRECTION = m.Direction.S2C

    direction: m.Vec3
    object_id: m.ObjectId
    fade_time: m.Float


@dataclass(kw_only=True)
class AreaSetTile(m.Message):
    MAJOR = 0x04
    MINOR = 0x14
    DIRECTION = m.Direction.S2C

    @dataclass(kw_only=True)
    class TileData:
        index: m.Word
        tile_id: m.Int
        orientation: m.Byte
        height: m.Byte
        anim_loop_1: m.Bool
        anim_loop_2: m.Bool
        anim_loop_3: m.Bool

    flags: m.Dword
    tileset: m.ResRef
    tiles: Annotated[list[TileData], m.SizePrefix.WORD]


@dataclass(kw_only=True)
class AreaAddGrassOverride(m.Message):
    MAJOR = 0x04
    MINOR = 0x15
    DIRECTION = m.Direction.S2C

    material_id: m.Byte
    texture: m.String
    density: m.Float
    height: m.Float
    ambient: m.Vec3
    diffuse: m.Vec3


@dataclass(kw_only=True)
class AreaRemoveGrassOverride(m.Message):
    MAJOR = 0x04
    MINOR = 0x16
    DIRECTION = m.Direction.S2C

    material_id: m.Byte


@dataclass(kw_only=True)
class AreaUpdateNoRestFlag(m.Message):
    MAJOR = 0x04
    MINOR = 0x17
    DIRECTION = m.Direction.S2C

    no_rest: m.Bool
    object_id: m.ObjectId
