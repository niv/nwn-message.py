from dataclasses import dataclass, field
from typing import Annotated, Self

from ..context import Context
from .. import message as m

CNWSPELL_NUM_LEVELS = 10


def _class_has_domains(context: Context, class_id: int) -> bool:
    return context.twoda("classes", class_id, "PickDomains") == "1"


def _class_has_specialization(context: Context, class_id: int) -> bool:
    return context.twoda("classes", class_id, "PickSchool") == "1"


@dataclass(kw_only=True)
class LevelUpSkillChanges:
    ranks: Annotated[
        list[m.Char],
        m.BitmaskConditionedList(
            m.MessageType.CHAR,
            m.SizePrefix.DWORD,
            m.TwoDARowCountHint("skills"),
            m.TwoDARowCountHint("skills"),
        ),
    ]


@dataclass(kw_only=True)
class LevelUpSpellLevelChanges:
    added: Annotated[list[m.Dword], m.SizePrefix.BYTE]
    removed: Annotated[list[m.Dword], m.SizePrefix.BYTE]


@dataclass(kw_only=True)
class LevelUpNull(m.Message):
    MAJOR = 0x1D
    MINOR = 0x00
    DIRECTION = m.Direction.C2S

    class_leveled_up_in: m.Byte
    has_ability_gain: bool
    ability_gain: m.Byte = 0
    hit_die: m.Byte = 0
    skill_changes: LevelUpSkillChanges = field(
        default_factory=lambda: LevelUpSkillChanges(ranks=[])
    )
    skill_points_remaining: m.Word = 0
    feats: list[int] = field(default_factory=list)
    spell_changes: list[LevelUpSpellLevelChanges] = field(default_factory=list)
    familiar_creature_type: m.Int = 0
    familiar_name: m.String = ""
    animal_companion_creature_type: m.Int = 0
    animal_companion_name: m.String = ""
    domain1: m.Byte = 0
    domain2: m.Byte = 0
    school: m.Byte = 0

    @classmethod
    def _read_variant(
        cls, rd: m.Reader, context: Context, has_ability_gain: bool
    ) -> Self:
        class_leveled_up_in = rd.read_byte()
        ability_gain = rd.read_byte() if has_ability_gain else 0
        hit_die = rd.read_byte()
        skill_changes = m.read_dataclass(LevelUpSkillChanges, rd, context)
        skill_points_remaining = rd.read_word()

        feats_to_add = rd.read_byte()
        feats = [rd.read_word() for _ in range(feats_to_add)]
        spell_changes = [
            LevelUpSpellLevelChanges(
                added=[rd.read_dword() for _ in range(rd.read_byte())],
                removed=[rd.read_dword() for _ in range(rd.read_byte())],
            )
            for _ in range(CNWSPELL_NUM_LEVELS)
        ]

        familiar_creature_type = rd.read_int()
        familiar_name = rd.read_str()
        animal_companion_creature_type = rd.read_int()
        animal_companion_name = rd.read_str()

        domain1 = 0
        domain2 = 0
        if _class_has_domains(context, class_leveled_up_in):
            domain1 = rd.read_byte()
            domain2 = rd.read_byte()

        school = 0
        if _class_has_specialization(context, class_leveled_up_in):
            school = rd.read_byte()

        return cls(
            class_leveled_up_in=class_leveled_up_in,
            has_ability_gain=has_ability_gain,
            ability_gain=ability_gain,
            hit_die=hit_die,
            skill_changes=skill_changes,
            skill_points_remaining=skill_points_remaining,
            feats=feats,
            spell_changes=spell_changes,
            familiar_creature_type=familiar_creature_type,
            familiar_name=familiar_name,
            animal_companion_creature_type=animal_companion_creature_type,
            animal_companion_name=animal_companion_name,
            domain1=domain1,
            domain2=domain2,
            school=school,
        )

    @classmethod
    def read(cls, rd: m.Reader, context: Context) -> Self:
        hint = context.fields.get("levelup_has_ability_gain")
        attempts = [bool(hint)] if hint is not None else [False, True]
        errors = []

        start_pos = rd.tell()
        original_fields = dict(context.fields)

        for has_ability_gain in attempts:
            rd.seek(start_pos)
            context.fields = dict(original_fields)
            try:
                message = cls._read_variant(rd, context, has_ability_gain)
                if rd.at_end:
                    return message
                errors.append(
                    f"ability={has_ability_gain}: stopped at {rd.tell()}, expected {rd.len()}"
                )
            except (IndexError, KeyError, ValueError) as exc:
                errors.append(f"ability={has_ability_gain}: {exc}")

        rd.seek(start_pos)
        context.fields = original_fields
        raise ValueError("Failed to parse LevelUpNull: " + "; ".join(errors))

    def write(self, wr: m.Writer, context: Context) -> None:
        wr.write_byte(self.class_leveled_up_in)
        if self.has_ability_gain:
            wr.write_byte(self.ability_gain)
        wr.write_byte(self.hit_die)
        m.write_dataclass(self.skill_changes, wr, context)
        wr.write_word(self.skill_points_remaining)

        wr.write_byte(len(self.feats))
        for feat in self.feats:
            wr.write_word(feat)

        assert len(self.spell_changes) == CNWSPELL_NUM_LEVELS
        for spell_level in self.spell_changes:
            wr.write_byte(len(spell_level.added))
            for spell_id in spell_level.added:
                wr.write_dword(spell_id)

            wr.write_byte(len(spell_level.removed))
            for spell_id in spell_level.removed:
                wr.write_dword(spell_id)

        wr.write_int(self.familiar_creature_type)
        wr.write_str(self.familiar_name)
        wr.write_int(self.animal_companion_creature_type)
        wr.write_str(self.animal_companion_name)

        if _class_has_domains(context, self.class_leveled_up_in):
            wr.write_byte(self.domain1)
            wr.write_byte(self.domain2)

        if _class_has_specialization(context, self.class_leveled_up_in):
            wr.write_byte(self.school)


@dataclass(kw_only=True)
class LevelUpConfirm(m.Message):
    MAJOR = 0x1D
    MINOR = 0x01
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class LevelUpDeny(m.Message):
    MAJOR = 0x1D
    MINOR = 0x02
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class LevelUpButtonOn(m.Message):
    MAJOR = 0x1D
    MINOR = 0x03


@dataclass(kw_only=True)
class LevelUpBegin(m.Message):
    MAJOR = 0x1D
    MINOR = 0x04
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class LevelUpBeginS2C(m.Message):
    MAJOR = 0x1D
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    valid_classes: Annotated[list[m.Bool], m.SizePrefix.BYTE]
