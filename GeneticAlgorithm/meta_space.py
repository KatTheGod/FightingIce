# TODO: We need to add a mapper. For some stuff, it just makes sense to have some mapper that can handle certain cases
"""
Examples:
    Not all agents have projectiles mapped to the same motion...
        So it doesn't make sense to use it.

    Secondly, if an attack's speed is being adjusted, and we are trying to change a 0 to a positive number, dont do it

    Remember, all speed Ys are negative
"""

from itertools import product
from typing import TypedDict
import numpy as np
import math

import constants as c
from MotionClasses.MotionEditor import MAX_FRAME_NUMBERS
from MotionClasses.MotionHeaders import MotionHeadersEnum
from MotionClasses.MotionNames import (
    ATTACK_ACTIONS_ALL,
    MOVEMENT_ACTIONS,
    PRIMARY_ACTIONS_ATTACK,
    SECONDARY_ACTIONS_ATTACK,
    TERTIARY_ACTIONS_ATTACK,
    ULTIMATE_ATTACK,
    MotionNamesEnum,
)
from GeneticAlgorithm.meta_mapper import MapperType

"""
    This will hold indices for the meta space subset any experiment uses.
    This will be something that is only appended on and not redacted in any sense
    This is such that we can track even OLDER experiments
"""


class RangeLimit(TypedDict):
    character_exclude_list: list[c.CHARACTERS]
    header_subset: list[MotionHeadersEnum]
    motions_names: list[MotionNamesEnum]
    min: int
    max: int
    nullify_character_exclude_list: bool


class MetaStateSubset:
    def __init__(
        self,
        index: int,
        name: str,
        description: str,
        motion_subset: list[MotionNamesEnum],
        header_subset: list[MotionHeadersEnum],
        limits: list[RangeLimit],
        exclude_list: list[tuple[MotionNamesEnum, MotionHeadersEnum]] | None = None,
        mapper_types: list[MapperType] | None = None,
    ) -> None:
        self.index: int = index
        self.name: str = name
        self.description: str = description
        self.limits = limits
        self.mapper_types = mapper_types

        self.motion_subset = motion_subset
        self.header_subset = header_subset
        self.meta_subspace: list[tuple[MotionNamesEnum, MotionHeadersEnum]] = list(
            product(
                self.motion_subset,
                self.header_subset,
            )
        )

        """
            NOTE
            Some configs, like character speed and forward walk, NEVER wanna adjust the other header.
            Imagine we are justing the y for a forward walk!??? We never want that to happen
        """
        if exclude_list is not None:
            self.meta_subspace = list(set(self.meta_subspace) - set(exclude_list))

        self.validate_limits()
        self.set_uniqueness_limit()

    def __eq__(self, other: None) -> bool:
        if not isinstance(other, MetaStateSubset):
            return NotImplemented

        return self.name == other.name

    def validate_limits(self) -> None:
        limits_motions = set()
        for limit in self.limits:
            limits_motions.update(limit['motions_names'])

        if set(self.motion_subset) != limits_motions:
            print(f'Invalid meta space definition for: {self.name}\nMotion Subset: {set(self.motion_subset)}\nLimit Motion Subset: {limits_motions}')
            raise RuntimeError('Invalid Meta Space Config')

    """
        NOTE
            Not going to be PERFECT
            There's an issue when you have a character exclude list.
            Say you exclude zen, when you are normalizing, you would need to consider that, which is just too much work for the small gain.
            So we are going to accept that it wont be exactly 1, but something close.
    """

    def set_uniqueness_limit(self) -> None:
        self.uniqueness_limit: float = 0
        for limit in self.limits:
            self.uniqueness_limit += pow(
                (
                    abs(limit['max'] - limit['min'])  #
                    * len(limit['header_subset'])
                    * len(limit['motions_names'])
                ),
                2,
            )

        self.uniqueness_limit: float = math.sqrt(self.set_uniqueness_limit)


META_SUBSPACE_COLLECTION: dict[int, MetaStateSubset] = {}


def add_to_collection(metaSpaceSubset: MetaStateSubset) -> None:
    if metaSpaceSubset.index in META_SUBSPACE_COLLECTION.keys():
        raise KeyError(f'Index: {metaSpaceSubset.index} already existed in collection: {", ".join(META_SUBSPACE_COLLECTION.keys())}')


def get_limit(
    meta_subspace: MetaStateSubset,
    adjustment: tuple[MotionNamesEnum, MotionHeadersEnum],
    character: c.CHARACTERS,
) -> RangeLimit:
    for limit in meta_subspace.limits:
        if adjustment[0] in limit['motions_names'] and adjustment[1] in limit['header_subset']:
            if character.value not in limit['character_exclude_list']:
                return limit
            elif limit['nullify_character_exclude_list']:
                return {
                    **limit,
                    'min': 0,
                    'max': 0,
                }

    raise RuntimeError(f'Requested limit for {adjustment}, but cannot find in meta subspace: {meta_subspace}')


basicStandA_B = MetaStateSubset(
    index=0,
    name='basicStandA_B',
    description="""
        First experiment done just to test the waters.
        Stand A and Stand B, adjusting the attack hit damage
    """,
    motion_subset=[
        MotionNamesEnum.STAND_A,
        MotionNamesEnum.STAND_B,
    ],
    header_subset=[MotionHeadersEnum.ATTACK_HIT_DAMAGE],
    limits=[
        {
            'header_subset': [MotionHeadersEnum.ATTACK_HIT_DAMAGE],
            'motions_names': [
                MotionNamesEnum.STAND_A,
                MotionNamesEnum.STAND_B,
            ],
            'max': 50,
            'min': 5,
        }
    ],
)
add_to_collection(basicStandA_B)

characterSpeed = MetaStateSubset(
    index=1,
    name='characterSpeed',
    description="""
        We are going to be adjusting the movement speed.
        Not really playing in dimensions that aren't specified.
    """,
    motion_subset=[
        *MOVEMENT_ACTIONS,
        MotionNamesEnum.THROW_SUFFER,
    ],
    header_subset=[
        MotionHeadersEnum.SPEED_X,
        MotionHeadersEnum.SPEED_Y,
    ],
    exclude_list=[
        (MotionNamesEnum.FORWARD_WALK, MotionHeadersEnum.SPEED_Y),
        (MotionNamesEnum.DASH, MotionHeadersEnum.SPEED_Y),
        (MotionNamesEnum.JUMP, MotionHeadersEnum.SPEED_Y),
        (MotionNamesEnum.BACK_STEP, MotionHeadersEnum.SPEED_Y),
    ],
    limits=[
        {
            'header_subset': [MotionHeadersEnum.SPEED_X],
            'motions_names': MOVEMENT_ACTIONS,
            'min': 1,
            'max': 10,
        },
        {
            'header_subset': [MotionHeadersEnum.SPEED_Y],
            'motions_names': MOVEMENT_ACTIONS,
            'min': -29,
            'max': -10,
        },
    ],
)
add_to_collection(characterSpeed)

hitBoxes = MetaStateSubset(
    index=2,
    name='hitBoxes',
    description="""
        First iteration of adjusting the attack hitboxes
        We are going to think of a smarter method later.
        For now, we are just going to be adjusting the reach of an action.
        Adjust the width and the height.
        I think in the next iteration, we can look into adjusting the ratio and the scale.
        Because rn, some attacks could lose the plot and become blocks.
        Additionally, ONLY ZEN has a long vertical attack: STAND_F_D_DFB, so we are going to limit that one to 400, and the others to 200
    """,
    header_subset=[
        MotionHeadersEnum.HIT_BOX_WIDTH,
        MotionHeadersEnum.HIT_BOX_HEIGHT,
    ],
    mapper_types=[
        MapperType.ATTACK_HIT_BOX_WIDTH,
        MapperType.ATTACK_HIT_BOX_HEIGHT,
    ],
    motion_subset=ATTACK_ACTIONS_ALL,
    limits=[
        # Special ZEN ATTACK
        {
            'character_exclude_list': [
                c.CHARACTERS.GARNET,
                c.CHARACTERS.LUD,
            ],
            'nullify_character_exclude_list': False,
            'header_subset': [MotionHeadersEnum.HIT_BOX_HEIGHT],
            'motions_names': [MotionNamesEnum.STAND_F_D_DFB],
            'max': 400,
            'min': 200,
        },
        # Special ZEN ATTACK for everyone else
        {
            'character_exclude_list': [c.CHARACTERS.ZEN],
            'nullify_character_exclude_list': False,
            'header_subset': [MotionHeadersEnum.HIT_BOX_HEIGHT],
            'motions_names': [MotionNamesEnum.STAND_F_D_DFB],
            'max': c.MAX_HIT_BOX_HEIGHT,
            'min': 10,
        },
        # WIDTH
        {
            'header_subset': [MotionHeadersEnum.HIT_BOX_WIDTH],
            'motions_names': [
                motion_name  #
                for motion_name in ATTACK_ACTIONS_ALL
                if motion_name != MotionNamesEnum.STAND_F_D_DFB
            ],
            'max': c.MAX_HIT_BOX_WIDTH,
            'min': 10,
        },
        # HEIGHT
        {
            'header_subset': [MotionHeadersEnum.HIT_BOX_HEIGHT],
            'motions_names': [
                motion_name  #
                for motion_name in ATTACK_ACTIONS_ALL
                if motion_name != MotionNamesEnum.STAND_F_D_DFB
            ],
            'max': c.MAX_HIT_BOX_HEIGHT,
            'min': 10,
        },
    ],
)
add_to_collection(hitBoxes)

energy = MetaStateSubset(
    index=3,
    name='energy',
    description="""
        This is going to be a bigger experiment to determine the effect of energy.
        With the full range of energy metrics
        Note, we aren't adding any special restrictions, so we can and up in a state where you can't move naturally.
    """,
    header_subset=[
        MotionHeadersEnum.ATTACK_START_ADD_ENERGY,
        MotionHeadersEnum.ATTACK_HIT_ADD_ENERGY,
        MotionHeadersEnum.ATTACK_GUARD_ADD_ENERGY,
        MotionHeadersEnum.ATTACK_GIVE_ENERGY,
    ],
    motion_subset=ATTACK_ACTIONS_ALL,
    limits=[
        # Start Add Energy
        {
            'header_subset': [MotionHeadersEnum.ATTACK_START_ADD_ENERGY],
            'motions_names': MOVEMENT_ACTIONS,
            'min': -10,
            'max': 5,
        },
        {
            'header_subset': [MotionHeadersEnum.ATTACK_START_ADD_ENERGY],
            'motions_names': PRIMARY_ACTIONS_ATTACK,
            'min': -30,
            'max': 0,
        },
        {
            'header_subset': [MotionHeadersEnum.ATTACK_START_ADD_ENERGY],
            'motions_names': SECONDARY_ACTIONS_ATTACK,
            'min': -50,
            'max': -5,
        },
        {
            'header_subset': [MotionHeadersEnum.ATTACK_START_ADD_ENERGY],
            'motions_names': TERTIARY_ACTIONS_ATTACK,
            'min': -100,
            'max': -10,
        },
        {
            'header_subset': [MotionHeadersEnum.ATTACK_START_ADD_ENERGY],
            'motions_names': ULTIMATE_ATTACK,
            'min': -250,
            'max': -100,
        },
        # Hit Add Energy
        {
            'header_subset': [MotionHeadersEnum.ATTACK_HIT_ADD_ENERGY],
            'motions_names': ATTACK_ACTIONS_ALL,
            'min': 0,
            'max': 50,
        },
        # Guard Add Energy
        {
            'header_subset': [MotionHeadersEnum.ATTACK_GUARD_ADD_ENERGY],
            'motions_names': ATTACK_ACTIONS_ALL,
            'min': 0,
            'max': 50,
        },
        # ATTACK_GIVE_ENERGY
        {
            'header_subset': [MotionHeadersEnum.ATTACK_GIVE_ENERGY],
            'motions_names': ATTACK_ACTIONS_ALL,
            'min': 5,
            'max': 50,
        },
        {
            'header_subset': [MotionHeadersEnum.ATTACK_GIVE_ENERGY],
            'motions_names': ULTIMATE_ATTACK,
            'max': 100,
            'min': 30,
        },
    ],
)
add_to_collection(energy)

# TODO: Incomplete, because we need a validator for the frame duration
projectile = MetaStateSubset(
    index=4,
    name='projectile',
    description="""
        First iteration for adjust the power of projectiles.
        In next iteration, could consider also adjusting the startup.
        This is a bit complicated... because different characters have different things that should be controled for.
        Pain in the but!
        In the next experiment, we could think of adjusting the startup, because that determines the delay before a projectile showing
    """,
    header_subset=[
        MotionHeadersEnum.ATTACK_SPEED_X,
        MotionHeadersEnum.ATTACK_SPEED_Y,
        MotionHeadersEnum.FRAME_NUMBER,
    ],
    motion_subset=[
        MotionNamesEnum.AIR_DA,
        MotionNamesEnum.STAND_D_DF_FA,
        MotionNamesEnum.STAND_D_DF_FB,
        MotionNamesEnum.STAND_F_D_DFA,
        MotionNamesEnum.AIR_D_DF_FA,
        MotionNamesEnum.AIR_D_DF_FB,
        MotionNamesEnum.STAND_D_DF_FC,
    ],
    exclude_list=[
        (MotionNamesEnum.STAND_D_DF_FA, MotionHeadersEnum.ATTACK_SPEED_Y),
        (MotionNamesEnum.AIR_D_DF_FA, MotionHeadersEnum.ATTACK_SPEED_Y),
        (MotionNamesEnum.STAND_D_DF_FC, MotionHeadersEnum.ATTACK_SPEED_Y),
    ],
    limits=[
        # Attack speed x
        {
            'motions_names': [
                MotionNamesEnum.STAND_D_DF_FA,
                MotionNamesEnum.STAND_D_DF_FB,
            ],
            'header_subset': [MotionHeadersEnum.ATTACK_SPEED_X],
            'max': c.MAX_ATTACK_SPEED_X,
            'min': 1,
        },
        {
            'motions_names': [
                MotionNamesEnum.AIR_DA,
                MotionNamesEnum.STAND_F_D_DFA,
            ],
            'header_subset': [MotionHeadersEnum.ATTACK_SPEED_X],
            'character_exclude_list': [
                c.CHARACTERS.ZEN,
                c.CHARACTERS.GARNET,
            ],
            'nullify_character_exclude_list': True,
            'max': c.MAX_ATTACK_SPEED_X,
            'min': 1,
        },
        {
            'motions_names': [
                MotionNamesEnum.AIR_D_DF_FA,
                MotionNamesEnum.STAND_D_DF_FC,
            ],
            'character_exclude_list': [
                c.CHARACTERS.GARNET,
                c.CHARACTERS.LUD,
            ],
            'nullify_character_exclude_list': True,
            'header_subset': [MotionHeadersEnum.ATTACK_SPEED_X],
            'max': c.MAX_ATTACK_SPEED_X,
            'min': 1,
        },
        {
            'motions_names': [MotionNamesEnum.AIR_D_DF_FB],
            'character_exclude_list': [c.CHARACTERS.LUD],
            'nullify_character_exclude_list': True,
            'header_subset': [MotionHeadersEnum.ATTACK_SPEED_X],
            'max': c.MAX_ATTACK_SPEED_X,
            'min': 1,
        },
        # Attack speed y
        {
            'motions_names': [
                MotionNamesEnum.AIR_DA,
                MotionNamesEnum.STAND_F_D_DFA,
            ],
            'character_exclude_list': [
                c.CHARACTERS.ZEN,
                c.CHARACTERS.GARNET,
            ],
            'nullify_character_exclude_list': True,
            'header_subset': [MotionHeadersEnum.ATTACK_SPEED_Y],
            'max': c.MAX_ATTACK_SPEED_Y,
            'min': 1,
        },
        {
            'motions_names': [MotionNamesEnum.STAND_D_DF_FB],
            'character_exclude_list': [c.CHARACTERS.ZEN],
            'nullify_character_exclude_list': True,
            'header_subset': [MotionHeadersEnum.ATTACK_SPEED_Y],
            'max': -1,
            'min': -c.MAX_ATTACK_SPEED_Y,
        },
        {
            'motions_names': [MotionNamesEnum.AIR_D_DF_FB],
            'character_exclude_list': [c.CHARACTERS.LUD],
            'nullify_character_exclude_list': True,
            'header_subset': [MotionHeadersEnum.ATTACK_SPEED_Y],
            'max': c.MAX_ATTACK_SPEED_Y,
            'min': 1,
        },
        # Frame Limit
        {
            'header_subset': [MotionHeadersEnum.FRAME_NUMBER],
            'motions_names': [
                MotionNamesEnum.AIR_DA,
                MotionNamesEnum.STAND_D_DF_FA,
                MotionNamesEnum.STAND_D_DF_FB,
                MotionNamesEnum.STAND_F_D_DFA,
                MotionNamesEnum.AIR_D_DF_FA,
                MotionNamesEnum.AIR_D_DF_FB,
                MotionNamesEnum.STAND_D_DF_FC,
            ],
            'max': c.MAX_PROJECTILE_FRAME_COUNT,
            'min': 1,
        },
    ],
)
add_to_collection(projectile)

combo = MetaStateSubset(
    index=5,
    name='combo',
    description="""
        First iteration for adjust the combo system
        We are really just going to affect the cancellable frame and stuff
        This will need a mapper, because its either -1 or >0
        Again, for the cacnelable frame, I am going to use that frame number as max
        Also... we arent really adjusting the motion level of other motions, so rn, the combo thing is only adjusting transitioning from an attack to another attack.
    """,
    header_subset=[
        MotionHeadersEnum.CANCEL_ABLE_FRAME,
        MotionHeadersEnum.CANCEL_ABLE_MOTION_LEVEL,
        MotionHeadersEnum.MOTION_LEVEL,
    ],
    motion_subset=ATTACK_ACTIONS_ALL,
    limits=[
        # Cancelable frame
        *[
            {
                'header_subset': [MotionHeadersEnum.CANCEL_ABLE_FRAME],
                'motions_names': [motion_name],
                'min': 0,
                'max': MAX_FRAME_NUMBERS.loc[motion_name.value],
            }
            for motion_name in ATTACK_ACTIONS_ALL
        ],
        # Cancelable motion level
        {
            'header_subset': [MotionHeadersEnum.CANCEL_ABLE_MOTION_LEVEL],
            'motions_names': ATTACK_ACTIONS_ALL,
            'min': 0,
            'max': len(ATTACK_ACTIONS_ALL),
        },
        # Motion Level
        {
            'header_subset': [MotionHeadersEnum.MOTION_LEVEL],
            'motions_names': ATTACK_ACTIONS_ALL,
            'min': 0,
            'max': len(ATTACK_ACTIONS_ALL),
        },
        # Motion Levle
    ],
)
add_to_collection(combo)

attackUpTime = MetaStateSubset(
    index=6,
    name='attackUpTime',
    description="""
        We are going to adjust the start up and active time for attacks.
        This will affect their duration and stuff.
        Could maybe look into combining this will the combo.
        For this one... im going to be a but more hands on.. I wanna have very specific limits for each motion
        I dont wanna waste time making solutions that are invalid, so I am going to cap the limits to the max of all characters and their frame numbers
        Note, might look a bit weird becuase it wont match the animation...
    """,
    header_subset=[
        MotionHeadersEnum.ATTACK_START_UP,
        MotionHeadersEnum.ATTACK_ACTIVE,
    ],
    motion_subset=ATTACK_ACTIONS_ALL,
    limits=[
        # Start Up
        *[
            {
                'header_subset': MotionHeadersEnum.ATTACK_START_UP,
                'motions_names': [motion_name],
                'min': 0,
                'max': MAX_FRAME_NUMBERS.loc[motion_name.value],
            }
            for motion_name in ATTACK_ACTIONS_ALL
        ],
        # Active
        *[
            {
                'header_subset': MotionHeadersEnum.ATTACK_ACTIVE,
                'motions_names': [motion_name],
                'min': 0,
                'max': MAX_FRAME_NUMBERS.loc[motion_name.value],
            }
            for motion_name in ATTACK_ACTIONS_ALL
        ],
    ],
)
add_to_collection(attackUpTime)

stunning = MetaStateSubset(
    index=7,
    name='stunning',
    description="""
        Will write some logic to affect the stunning effects.
        For some reason, by default, the throw_A and throw_B dont have an impact X and a recov thing, I think its related to that suffer stuff
        This one is a bit harder to judge, because not a lot of motions have attack act y... 
    """,
    header_subset=[
        MotionHeadersEnum.ATTACK_IMPACT_X,
        MotionHeadersEnum.ATTACK_IMPACT_Y,
        MotionHeadersEnum.ATTACK_GIVE_GUARD_RECOV,
    ],
    motion_subset=ATTACK_ACTIONS_ALL,
    exclude_list=[
        (MotionNamesEnum.THROW_A, MotionHeadersEnum.ATTACK_IMPACT_X),
        (MotionNamesEnum.THROW_B, MotionHeadersEnum.ATTACK_IMPACT_X),
        (MotionNamesEnum.THROW_A, MotionHeadersEnum.ATTACK_GIVE_GUARD_RECOV),
        (MotionNamesEnum.THROW_B, MotionHeadersEnum.ATTACK_GIVE_GUARD_RECOV),
    ],
    limits=[
        # By default, the throws don't have an impact x. Weird
        {
            'header_subset': [MotionHeadersEnum.ATTACK_IMPACT_X],
            'motions_names': ATTACK_ACTIONS_ALL,
            'min': 1,
            'max': 40,
        },
        # Knock DOWN
        {
            'header_subset': [MotionHeadersEnum.ATTACK_IMPACT_Y],
            'motions_names': [
                MotionNamesEnum.AIR_UA,
                MotionNamesEnum.AIR_UB,
                MotionNamesEnum.AIR_D_DF_FB,
            ],
            'min': 1,
            'max': 20,
        },
        # Knock up
        {
            'header_subset': [MotionHeadersEnum.ATTACK_IMPACT_Y],
            'motions_names': [
                MotionNamesEnum.STAND_B,
                MotionNamesEnum.AIR_A,
                MotionNamesEnum.AIR_B,
                MotionNamesEnum.AIR_DB,
                MotionNamesEnum.STAND_D_DF_FA,
                MotionNamesEnum.STAND_D_DF_FB,
                MotionNamesEnum.STAND_F_D_DFA,
                MotionNamesEnum.STAND_F_D_DFB,
                MotionNamesEnum.STAND_D_DB_BA,
                MotionNamesEnum.STAND_D_DB_BB,
                MotionNamesEnum.AIR_D_DB_BA,
                MotionNamesEnum.AIR_D_DB_BB,
                MotionNamesEnum.STAND_D_DF_FC,
            ],
            'min': -30,
            'max': -5,
        },
        {
            'header_subset': [MotionHeadersEnum.ATTACK_GIVE_GUARD_RECOV],
            'motions_names': ATTACK_ACTIONS_ALL,
            'min': 1,
            'max': 30,
        },
    ],
)
add_to_collection(stunning)

damage = MetaStateSubset(
    index=8,
    name='damage',
    description="""
        Will write some logic to affect the damage and guard damage effects.
        TODO: we are going to exclude changing AIR_UB, because that's Garnet's broken technique.
        NOTE: Not all attacks do guard damage by default, so we are going to add a bit of that ourselves.
    """,
    header_subset=[
        MotionHeadersEnum.ATTACK_HIT_DAMAGE,
        MotionHeadersEnum.ATTACK_GUARD_DAMAGE,
    ],
    motion_subset=ATTACK_ACTIONS_ALL,
    exclude_list=[
        (MotionNamesEnum.AIR_UB, MotionHeadersEnum.ATTACK_HIT_DAMAGE),
        (MotionNamesEnum.AIR_UB, MotionHeadersEnum.ATTACK_GUARD_DAMAGE),
    ],
    limits=[
        # Hit damage
        {
            'header_subset': [MotionHeadersEnum.ATTACK_HIT_DAMAGE],
            'motions_names': PRIMARY_ACTIONS_ATTACK,
            'min': 2,
            'max': 25,
        },
        {
            'header_subset': [MotionHeadersEnum.ATTACK_HIT_DAMAGE],
            'motions_names': SECONDARY_ACTIONS_ATTACK,
            'min': 5,
            'max': 40,
        },
        {
            'header_subset': [MotionHeadersEnum.ATTACK_HIT_DAMAGE],
            'motions_names': TERTIARY_ACTIONS_ATTACK,
            'min': 10,
            'max': 70,
        },
        {
            'header_subset': [MotionHeadersEnum.ATTACK_HIT_DAMAGE],
            'motions_names': [ULTIMATE_ATTACK],
            'min': 100,
            'max': 200,
        },
        # Guard Damage
        {
            'header_subset': [MotionHeadersEnum.ATTACK_HIT_DAMAGE],
            'motions_names': PRIMARY_ACTIONS_ATTACK,
            'min': 0,
            'max': 5,
        },
        {
            'header_subset': [MotionHeadersEnum.ATTACK_HIT_DAMAGE],
            'motions_names': SECONDARY_ACTIONS_ATTACK,
            'min': 0,
            'max': 10,
        },
        {
            'header_subset': [MotionHeadersEnum.ATTACK_HIT_DAMAGE],
            'motions_names': TERTIARY_ACTIONS_ATTACK,
            'min': 2,
            'max': 15,
        },
        {
            'header_subset': [MotionHeadersEnum.ATTACK_HIT_DAMAGE],
            'motions_names': [ULTIMATE_ATTACK],
            'min': 15,
            'max': 50,
        },
    ],
)
add_to_collection(damage)
