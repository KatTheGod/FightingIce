# TODO: We need to add a mapper. For some stuff, it just makes sense to have some mapper that can handle certain cases
'''
    Examples:
        Not all agents have projectiles mapped to the same motion...
            So it doesn't make sense to use it.

        Secondly, if an attack's speed is being adjusted, and we are trying to change a 0 to a positive number, dont do it

        Remember, all speed Ys are negative
'''
import asyncio
import pathlib
import re
import uuid
from datetime import datetime
from typing import Any
import os

import numpy as np
from distributed import Client
from pymoo.core.problem import Problem
from pymoo.core.variable import Integer

import constants as c
import functions as f
import GeneticAlgorithm.genetic_functions as gf
from MotionClasses.MotionHeaders import MotionHeaders as headers
from MotionClasses.MotionNames import MotionNames as motion_names

"""
    This will hold indices for the meta space subset any experiment uses.
    This will be something that is only appended on and not redacted in any sense
    This is such that we can track even OLDER experiments
"""


class MetaStateSubset:
    def __init__(
        self,
        index: int,
        name: str,
        description: str,
        meta_subspace: list[tuple[str, str]],
    ) -> None:
        self.index: int = index
        self.name: str = name
        self.description: str = description
        self.meta_subspace: list[tuple[str, str]] = meta_subspace

    def __eq__(self, other: None) -> bool:
        if not isinstance(other, MetaStateSubset):
            return NotImplemented

        return self.name == other.name


META_SUBSPACE_COLLECTION: dict[int, MetaStateSubset] = {}


def add_to_collection(metaSpaceSubset: MetaStateSubset) -> None:
    if metaSpaceSubset.index in META_SUBSPACE_COLLECTION.keys():
        raise KeyError(f'Index: {metaSpaceSubset.index} already existed in collection: {", ".join(META_SUBSPACE_COLLECTION.keys())}')


basicStandA_B = MetaStateSubset(
    index=0,
    name='basicStandA_B',
    description="""
        First experiment done just to test the waters.
        Stand A and Stand B, adjusting the attack hit damage
    """,
    meta_subspace=[
        (motion_names.STAND_A, headers.ATTACK_HIT_DAMAGE),
        (motion_names.STAND_B, headers.ATTACK_HIT_DAMAGE),
    ],
)
add_to_collection(basicStandA_B)


characterSpeed = MetaStateSubset(
    index=1,
    name='characterSpeed',
    description="""
        We are going to be adjusting the movement speed.
        Not really playing in dimensions that aren't specified.
        We are going to adjust the range to be between:
            Vertical: [-29, -10]
            Horizontal: [1,10]
    """,
    meta_subspace=[
        (motion_names.FORWARD_WALK, headers.SPEED_X), # pos
        (motion_names.DASH, headers.SPEED_X), # pos
        (motion_names.BACK_STEP, headers.SPEED_X), # neg
        (motion_names.JUMP, headers.SPEED_Y), # neg
        (motion_names.FOR_JUMP, headers.SPEED_Y), # neg
        (motion_names.FOR_JUMP, headers.SPEED_X), # pos
        (motion_names.BACK_JUMP, headers.SPEED_Y), # neg
        (motion_names.BACK_JUMP, headers.SPEED_X), # neg
        (motion_names.THROW_SUFFER, headers.SPEED_Y), # neg
        (motion_names.THROW_SUFFER, headers.SPEED_X), # pos
    ],
)
add_to_collection(characterSpeed)

hitBoxes = MetaStateSubset(
    index=2,
    name='hitBoxes',
    description="""
        First iteration of adjusting the attack hitboxes
        We are going to think of a smarter method later.
        For now, I dont wanna change where the hitbox offset is, I just wanna adjust its range.
    """,
    meta_subspace=[
        (motion_names.STAND_D_DF_FC, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.STAND_D_DF_FC, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.STAND_F_D_DFB, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.STAND_F_D_DFB, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.AIR_D_DB_BB, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.AIR_D_DB_BB, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.AIR_D_DF_FB, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.AIR_D_DF_FB, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.STAND_D_DB_BB, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.STAND_D_DB_BB, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.THROW_B, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.THROW_B, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.AIR_UB, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.AIR_UB, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.STAND_D_DF_FB, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.STAND_D_DF_FB, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.AIR_F_D_DFB, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.AIR_F_D_DFB, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.AIR_D_DB_BA, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.AIR_D_DB_BA, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.STAND_FB, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.STAND_FB, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.CROUCH_FB, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.CROUCH_FB, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.AIR_FB, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.AIR_FB, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.THROW_A, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.THROW_A, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.STAND_B, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.STAND_B, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.CROUCH_B, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.CROUCH_B, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.AIR_B, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.AIR_B, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.AIR_DB, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.AIR_DB, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.AIR_FA, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.AIR_FA, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.AIR_UA, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.AIR_UA, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.STAND_F_D_DFA, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.STAND_F_D_DFA, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.STAND_D_DB_BA, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.STAND_D_DB_BA, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.AIR_D_DF_FA, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.AIR_D_DF_FA, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.AIR_F_D_DFA, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.AIR_F_D_DFA, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.AIR_A, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.AIR_A, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.AIR_DA, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.AIR_DA, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.STAND_FA, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.STAND_FA, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.CROUCH_FA, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.CROUCH_FA, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.STAND_A, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.STAND_A, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.CROUCH_A, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.CROUCH_A, headers.ATTACK_HIT_AREA_DOWN),
        (motion_names.STAND_D_DF_FA, headers.ATTACK_HIT_AREA_RIGHT),
        (motion_names.STAND_D_DF_FA, headers.ATTACK_HIT_AREA_DOWN),
    ],
)
add_to_collection(hitBoxes)

energy = MetaStateSubset(
    index=3,
    name='energy',
    description="""
        This is going to be a bigger experiment to determine the effect of energy.
        With the full range of energy metrics
    """,
    meta_subspace=[
        (motion_names.STAND_D_DF_FC, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.STAND_D_DF_FC, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.STAND_D_DF_FC, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.STAND_D_DF_FC, headers.ATTACK_GIVE_ENERGY),
        (motion_names.STAND_F_D_DFB, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.STAND_F_D_DFB, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.STAND_F_D_DFB, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.STAND_F_D_DFB, headers.ATTACK_GIVE_ENERGY),
        (motion_names.AIR_D_DB_BB, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.AIR_D_DB_BB, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.AIR_D_DB_BB, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.AIR_D_DB_BB, headers.ATTACK_GIVE_ENERGY),
        (motion_names.AIR_D_DF_FB, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.AIR_D_DF_FB, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.AIR_D_DF_FB, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.AIR_D_DF_FB, headers.ATTACK_GIVE_ENERGY),
        (motion_names.STAND_D_DB_BB, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.STAND_D_DB_BB, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.STAND_D_DB_BB, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.STAND_D_DB_BB, headers.ATTACK_GIVE_ENERGY),
        (motion_names.THROW_B, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.THROW_B, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.THROW_B, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.THROW_B, headers.ATTACK_GIVE_ENERGY),
        (motion_names.AIR_UB, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.AIR_UB, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.AIR_UB, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.AIR_UB, headers.ATTACK_GIVE_ENERGY),
        (motion_names.STAND_D_DF_FB, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.STAND_D_DF_FB, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.STAND_D_DF_FB, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.STAND_D_DF_FB, headers.ATTACK_GIVE_ENERGY),
        (motion_names.AIR_F_D_DFB, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.AIR_F_D_DFB, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.AIR_F_D_DFB, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.AIR_F_D_DFB, headers.ATTACK_GIVE_ENERGY),
        (motion_names.AIR_D_DB_BA, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.AIR_D_DB_BA, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.AIR_D_DB_BA, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.AIR_D_DB_BA, headers.ATTACK_GIVE_ENERGY),
        (motion_names.STAND_FB, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.STAND_FB, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.STAND_FB, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.STAND_FB, headers.ATTACK_GIVE_ENERGY),
        (motion_names.CROUCH_FB, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.CROUCH_FB, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.CROUCH_FB, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.CROUCH_FB, headers.ATTACK_GIVE_ENERGY),
        (motion_names.AIR_FB, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.AIR_FB, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.AIR_FB, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.AIR_FB, headers.ATTACK_GIVE_ENERGY),
        (motion_names.THROW_A, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.THROW_A, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.THROW_A, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.THROW_A, headers.ATTACK_GIVE_ENERGY),
        (motion_names.STAND_B, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.STAND_B, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.STAND_B, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.STAND_B, headers.ATTACK_GIVE_ENERGY),
        (motion_names.CROUCH_B, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.CROUCH_B, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.CROUCH_B, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.CROUCH_B, headers.ATTACK_GIVE_ENERGY),
        (motion_names.AIR_B, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.AIR_B, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.AIR_B, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.AIR_B, headers.ATTACK_GIVE_ENERGY),
        (motion_names.AIR_DB, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.AIR_DB, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.AIR_DB, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.AIR_DB, headers.ATTACK_GIVE_ENERGY),
        (motion_names.AIR_FA, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.AIR_FA, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.AIR_FA, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.AIR_FA, headers.ATTACK_GIVE_ENERGY),
        (motion_names.AIR_UA, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.AIR_UA, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.AIR_UA, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.AIR_UA, headers.ATTACK_GIVE_ENERGY),
        (motion_names.STAND_F_D_DFA, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.STAND_F_D_DFA, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.STAND_F_D_DFA, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.STAND_F_D_DFA, headers.ATTACK_GIVE_ENERGY),
        (motion_names.STAND_D_DB_BA, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.STAND_D_DB_BA, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.STAND_D_DB_BA, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.STAND_D_DB_BA, headers.ATTACK_GIVE_ENERGY),
        (motion_names.AIR_D_DF_FA, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.AIR_D_DF_FA, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.AIR_D_DF_FA, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.AIR_D_DF_FA, headers.ATTACK_GIVE_ENERGY),
        (motion_names.AIR_F_D_DFA, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.AIR_F_D_DFA, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.AIR_F_D_DFA, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.AIR_F_D_DFA, headers.ATTACK_GIVE_ENERGY),
        (motion_names.AIR_A, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.AIR_A, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.AIR_A, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.AIR_A, headers.ATTACK_GIVE_ENERGY),
        (motion_names.AIR_DA, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.AIR_DA, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.AIR_DA, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.AIR_DA, headers.ATTACK_GIVE_ENERGY),
        (motion_names.STAND_FA, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.STAND_FA, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.STAND_FA, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.STAND_FA, headers.ATTACK_GIVE_ENERGY),
        (motion_names.CROUCH_FA, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.CROUCH_FA, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.CROUCH_FA, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.CROUCH_FA, headers.ATTACK_GIVE_ENERGY),
        (motion_names.STAND_A, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.STAND_A, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.STAND_A, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.STAND_A, headers.ATTACK_GIVE_ENERGY),
        (motion_names.CROUCH_A, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.CROUCH_A, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.CROUCH_A, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.CROUCH_A, headers.ATTACK_GIVE_ENERGY),
        (motion_names.STAND_D_DF_FA, headers.ATTACK_START_ADD_ENERGY),
        (motion_names.STAND_D_DF_FA, headers.ATTACK_HIT_ADD_ENERGY),
        (motion_names.STAND_D_DF_FA, headers.ATTACK_GUARD_ADD_ENERGY),
        (motion_names.STAND_D_DF_FA, headers.ATTACK_GIVE_ENERGY),

    ],
)
add_to_collection(energy)

projectile_speed = MetaStateSubset(
    index=4,
    name='projectile_speed',
    description="""
        First iteration for adjust the power of projectiles.
        We are only adjusting the speed in this iterations
    """,
    meta_subspace=[
        (motion_names.STAND_D_DF_FC, headers.ATTACK_SPEED_X),
        (motion_names.STAND_D_DF_FC, headers.ATTACK_SPEED_Y),
        (motion_names.STAND_D_DF_FB, headers.ATTACK_SPEED_X),
        (motion_names.STAND_D_DF_FB, headers.ATTACK_SPEED_Y),
        (motion_names.AIR_D_DF_FB, headers.ATTACK_SPEED_X),
        (motion_names.AIR_D_DF_FB, headers.ATTACK_SPEED_Y),
        (motion_names.STAND_D_DF_FA, headers.ATTACK_SPEED_X),
        (motion_names.STAND_D_DF_FA, headers.ATTACK_SPEED_Y),
        (motion_names.AIR_D_DF_FA, headers.ATTACK_SPEED_X),
        (motion_names.AIR_D_DF_FA, headers.ATTACK_SPEED_Y),
    ],
)
add_to_collection(projectile_speed)

combo = MetaStateSubset(
    index=5,
    name='combo',
    description="""
        First iteration for adjust the combo system
        We are really just going to affect the cancellable frame and stuff
        This will need a mapper, because its either -1 or >0
    """,
    meta_subspace=[
        (motion_names.STAND_D_DF_FC, headers.CANCEL_ABLE_FRAME),
        (motion_names.STAND_D_DF_FC, headers.MOTION_LEVEL),
        (motion_names.STAND_D_DF_FC, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.AIR_D_DB_BB, headers.CANCEL_ABLE_FRAME),
        (motion_names.AIR_D_DB_BB, headers.MOTION_LEVEL),
        (motion_names.AIR_D_DB_BB, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.STAND_F_D_DFB, headers.CANCEL_ABLE_FRAME),
        (motion_names.STAND_F_D_DFB, headers.MOTION_LEVEL),
        (motion_names.STAND_F_D_DFB, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.AIR_D_DF_FB, headers.CANCEL_ABLE_FRAME),
        (motion_names.AIR_D_DF_FB, headers.MOTION_LEVEL),
        (motion_names.AIR_D_DF_FB, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.STAND_D_DB_BB, headers.CANCEL_ABLE_FRAME),
        (motion_names.STAND_D_DB_BB, headers.MOTION_LEVEL),
        (motion_names.STAND_D_DB_BB, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.STAND_D_DF_FB, headers.CANCEL_ABLE_FRAME),
        (motion_names.STAND_D_DF_FB, headers.MOTION_LEVEL),
        (motion_names.STAND_D_DF_FB, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.AIR_F_D_DFB, headers.CANCEL_ABLE_FRAME),
        (motion_names.AIR_F_D_DFB, headers.MOTION_LEVEL),
        (motion_names.AIR_F_D_DFB, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.THROW_B, headers.CANCEL_ABLE_FRAME),
        (motion_names.THROW_B, headers.MOTION_LEVEL),
        (motion_names.THROW_B, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.AIR_UB, headers.CANCEL_ABLE_FRAME),
        (motion_names.AIR_UB, headers.MOTION_LEVEL),
        (motion_names.AIR_UB, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.AIR_D_DB_BA, headers.CANCEL_ABLE_FRAME),
        (motion_names.AIR_D_DB_BA, headers.MOTION_LEVEL),
        (motion_names.AIR_D_DB_BA, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.CROUCH_FB, headers.CANCEL_ABLE_FRAME),
        (motion_names.CROUCH_FB, headers.MOTION_LEVEL),
        (motion_names.CROUCH_FB, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.STAND_FB, headers.CANCEL_ABLE_FRAME),
        (motion_names.STAND_FB, headers.MOTION_LEVEL),
        (motion_names.STAND_FB, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.AIR_FB, headers.CANCEL_ABLE_FRAME),
        (motion_names.AIR_FB, headers.MOTION_LEVEL),
        (motion_names.AIR_FB, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.STAND_F_D_DFA, headers.CANCEL_ABLE_FRAME),
        (motion_names.STAND_F_D_DFA, headers.MOTION_LEVEL),
        (motion_names.STAND_F_D_DFA, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.AIR_D_DF_FA, headers.CANCEL_ABLE_FRAME),
        (motion_names.AIR_D_DF_FA, headers.MOTION_LEVEL),
        (motion_names.AIR_D_DF_FA, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.STAND_D_DB_BA, headers.CANCEL_ABLE_FRAME),
        (motion_names.STAND_D_DB_BA, headers.MOTION_LEVEL),
        (motion_names.STAND_D_DB_BA, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.AIR_DB, headers.CANCEL_ABLE_FRAME),
        (motion_names.AIR_DB, headers.MOTION_LEVEL),
        (motion_names.AIR_DB, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.CROUCH_B, headers.CANCEL_ABLE_FRAME),
        (motion_names.CROUCH_B, headers.MOTION_LEVEL),
        (motion_names.CROUCH_B, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.STAND_B, headers.CANCEL_ABLE_FRAME),
        (motion_names.STAND_B, headers.MOTION_LEVEL),
        (motion_names.STAND_B, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.AIR_B, headers.CANCEL_ABLE_FRAME),
        (motion_names.AIR_B, headers.MOTION_LEVEL),
        (motion_names.AIR_B, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.AIR_FA, headers.CANCEL_ABLE_FRAME),
        (motion_names.AIR_FA, headers.MOTION_LEVEL),
        (motion_names.AIR_FA, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.THROW_A, headers.CANCEL_ABLE_FRAME),
        (motion_names.THROW_A, headers.MOTION_LEVEL),
        (motion_names.THROW_A, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.AIR_UA, headers.CANCEL_ABLE_FRAME),
        (motion_names.AIR_UA, headers.MOTION_LEVEL),
        (motion_names.AIR_UA, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.AIR_F_D_DFA, headers.CANCEL_ABLE_FRAME),
        (motion_names.AIR_F_D_DFA, headers.MOTION_LEVEL),
        (motion_names.AIR_F_D_DFA, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.AIR_DA, headers.CANCEL_ABLE_FRAME),
        (motion_names.AIR_DA, headers.MOTION_LEVEL),
        (motion_names.AIR_DA, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.AIR_A, headers.CANCEL_ABLE_FRAME),
        (motion_names.AIR_A, headers.MOTION_LEVEL),
        (motion_names.AIR_A, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.STAND_FA, headers.CANCEL_ABLE_FRAME),
        (motion_names.STAND_FA, headers.MOTION_LEVEL),
        (motion_names.STAND_FA, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.CROUCH_FA, headers.CANCEL_ABLE_FRAME),
        (motion_names.CROUCH_FA, headers.MOTION_LEVEL),
        (motion_names.CROUCH_FA, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.STAND_D_DF_FA, headers.CANCEL_ABLE_FRAME),
        (motion_names.STAND_D_DF_FA, headers.MOTION_LEVEL),
        (motion_names.STAND_D_DF_FA, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.CROUCH_A, headers.CANCEL_ABLE_FRAME),
        (motion_names.CROUCH_A, headers.MOTION_LEVEL),
        (motion_names.CROUCH_A, headers.CANCEL_ABLE_MOTION_LEVEL),
        (motion_names.STAND_A, headers.CANCEL_ABLE_FRAME),
        (motion_names.STAND_A, headers.MOTION_LEVEL),
        (motion_names.STAND_A, headers.CANCEL_ABLE_MOTION_LEVEL),
    ],
)
add_to_collection(combo)

attackUpTime = MetaStateSubset(
    index=6,
    name='attackUpTime',
    description="""
        We are going to adjust the staup and active time for attacks.
        This will affect their duration and stuff.
        Could maybe look into combining this will the combo.
    """,
    meta_subspace=[
        (motion_names.STAND_D_DF_FC, headers.ATTACK_START_UP),
        (motion_names.STAND_D_DF_FC, headers.ATTACK_ACTIVE),
        (motion_names.AIR_D_DB_BB, headers.ATTACK_START_UP),
        (motion_names.AIR_D_DB_BB, headers.ATTACK_ACTIVE),
        (motion_names.STAND_F_D_DFB, headers.ATTACK_START_UP),
        (motion_names.STAND_F_D_DFB, headers.ATTACK_ACTIVE),
        (motion_names.AIR_D_DF_FB, headers.ATTACK_START_UP),
        (motion_names.AIR_D_DF_FB, headers.ATTACK_ACTIVE),
        (motion_names.STAND_D_DB_BB, headers.ATTACK_START_UP),
        (motion_names.STAND_D_DB_BB, headers.ATTACK_ACTIVE),
        (motion_names.STAND_D_DF_FB, headers.ATTACK_START_UP),
        (motion_names.STAND_D_DF_FB, headers.ATTACK_ACTIVE),
        (motion_names.AIR_F_D_DFB, headers.ATTACK_START_UP),
        (motion_names.AIR_F_D_DFB, headers.ATTACK_ACTIVE),
        (motion_names.THROW_B, headers.ATTACK_START_UP),
        (motion_names.THROW_B, headers.ATTACK_ACTIVE),
        (motion_names.AIR_UB, headers.ATTACK_START_UP),
        (motion_names.AIR_UB, headers.ATTACK_ACTIVE),
        (motion_names.AIR_D_DB_BA, headers.ATTACK_START_UP),
        (motion_names.AIR_D_DB_BA, headers.ATTACK_ACTIVE),
        (motion_names.CROUCH_FB, headers.ATTACK_START_UP),
        (motion_names.CROUCH_FB, headers.ATTACK_ACTIVE),
        (motion_names.STAND_FB, headers.ATTACK_START_UP),
        (motion_names.STAND_FB, headers.ATTACK_ACTIVE),
        (motion_names.AIR_FB, headers.ATTACK_START_UP),
        (motion_names.AIR_FB, headers.ATTACK_ACTIVE),
        (motion_names.STAND_F_D_DFA, headers.ATTACK_START_UP),
        (motion_names.STAND_F_D_DFA, headers.ATTACK_ACTIVE),
        (motion_names.AIR_D_DF_FA, headers.ATTACK_START_UP),
        (motion_names.AIR_D_DF_FA, headers.ATTACK_ACTIVE),
        (motion_names.STAND_D_DB_BA, headers.ATTACK_START_UP),
        (motion_names.STAND_D_DB_BA, headers.ATTACK_ACTIVE),
        (motion_names.AIR_DB, headers.ATTACK_START_UP),
        (motion_names.AIR_DB, headers.ATTACK_ACTIVE),
        (motion_names.CROUCH_B, headers.ATTACK_START_UP),
        (motion_names.CROUCH_B, headers.ATTACK_ACTIVE),
        (motion_names.STAND_B, headers.ATTACK_START_UP),
        (motion_names.STAND_B, headers.ATTACK_ACTIVE),
        (motion_names.AIR_B, headers.ATTACK_START_UP),
        (motion_names.AIR_B, headers.ATTACK_ACTIVE),
        (motion_names.AIR_FA, headers.ATTACK_START_UP),
        (motion_names.AIR_FA, headers.ATTACK_ACTIVE),
        (motion_names.THROW_A, headers.ATTACK_START_UP),
        (motion_names.THROW_A, headers.ATTACK_ACTIVE),
        (motion_names.AIR_UA, headers.ATTACK_START_UP),
        (motion_names.AIR_UA, headers.ATTACK_ACTIVE),
        (motion_names.AIR_F_D_DFA, headers.ATTACK_START_UP),
        (motion_names.AIR_F_D_DFA, headers.ATTACK_ACTIVE),
        (motion_names.AIR_DA, headers.ATTACK_START_UP),
        (motion_names.AIR_DA, headers.ATTACK_ACTIVE),
        (motion_names.AIR_A, headers.ATTACK_START_UP),
        (motion_names.AIR_A, headers.ATTACK_ACTIVE),
        (motion_names.STAND_FA, headers.ATTACK_START_UP),
        (motion_names.STAND_FA, headers.ATTACK_ACTIVE),
        (motion_names.CROUCH_FA, headers.ATTACK_START_UP),
        (motion_names.CROUCH_FA, headers.ATTACK_ACTIVE),
        (motion_names.STAND_D_DF_FA, headers.ATTACK_START_UP),
        (motion_names.STAND_D_DF_FA, headers.ATTACK_ACTIVE),
        (motion_names.CROUCH_A, headers.ATTACK_START_UP),
        (motion_names.CROUCH_A, headers.ATTACK_ACTIVE),
        (motion_names.STAND_A, headers.ATTACK_START_UP),
        (motion_names.STAND_A, headers.ATTACK_ACTIVE),
    ],
)
add_to_collection(attackUpTime)

stunning = MetaStateSubset(
    index=7,
    name='stunning',
    description="""
        Will write some logic to affect the stunning effects.
    """,
    meta_subspace=[
        (motion_names.STAND_D_DF_FC, headers.ATTACK_IMPACT_X),
        (motion_names.STAND_D_DF_FC, headers.ATTACK_IMPACT_Y),
        (motion_names.STAND_D_DF_FC, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.AIR_D_DB_BB, headers.ATTACK_IMPACT_X),
        (motion_names.AIR_D_DB_BB, headers.ATTACK_IMPACT_Y),
        (motion_names.AIR_D_DB_BB, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.STAND_F_D_DFB, headers.ATTACK_IMPACT_X),
        (motion_names.STAND_F_D_DFB, headers.ATTACK_IMPACT_Y),
        (motion_names.STAND_F_D_DFB, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.AIR_D_DF_FB, headers.ATTACK_IMPACT_X),
        (motion_names.AIR_D_DF_FB, headers.ATTACK_IMPACT_Y),
        (motion_names.AIR_D_DF_FB, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.STAND_D_DB_BB, headers.ATTACK_IMPACT_X),
        (motion_names.STAND_D_DB_BB, headers.ATTACK_IMPACT_Y),
        (motion_names.STAND_D_DB_BB, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.STAND_D_DF_FB, headers.ATTACK_IMPACT_X),
        (motion_names.STAND_D_DF_FB, headers.ATTACK_IMPACT_Y),
        (motion_names.STAND_D_DF_FB, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.AIR_F_D_DFB, headers.ATTACK_IMPACT_X),
        (motion_names.AIR_F_D_DFB, headers.ATTACK_IMPACT_Y),
        (motion_names.AIR_F_D_DFB, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.THROW_B, headers.ATTACK_IMPACT_X),
        (motion_names.THROW_B, headers.ATTACK_IMPACT_Y),
        (motion_names.THROW_B, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.AIR_UB, headers.ATTACK_IMPACT_X),
        (motion_names.AIR_UB, headers.ATTACK_IMPACT_Y),
        (motion_names.AIR_UB, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.AIR_D_DB_BA, headers.ATTACK_IMPACT_X),
        (motion_names.AIR_D_DB_BA, headers.ATTACK_IMPACT_Y),
        (motion_names.AIR_D_DB_BA, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.CROUCH_FB, headers.ATTACK_IMPACT_X),
        (motion_names.CROUCH_FB, headers.ATTACK_IMPACT_Y),
        (motion_names.CROUCH_FB, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.STAND_FB, headers.ATTACK_IMPACT_X),
        (motion_names.STAND_FB, headers.ATTACK_IMPACT_Y),
        (motion_names.STAND_FB, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.AIR_FB, headers.ATTACK_IMPACT_X),
        (motion_names.AIR_FB, headers.ATTACK_IMPACT_Y),
        (motion_names.AIR_FB, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.STAND_F_D_DFA, headers.ATTACK_IMPACT_X),
        (motion_names.STAND_F_D_DFA, headers.ATTACK_IMPACT_Y),
        (motion_names.STAND_F_D_DFA, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.AIR_D_DF_FA, headers.ATTACK_IMPACT_X),
        (motion_names.AIR_D_DF_FA, headers.ATTACK_IMPACT_Y),
        (motion_names.AIR_D_DF_FA, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.STAND_D_DB_BA, headers.ATTACK_IMPACT_X),
        (motion_names.STAND_D_DB_BA, headers.ATTACK_IMPACT_Y),
        (motion_names.STAND_D_DB_BA, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.AIR_DB, headers.ATTACK_IMPACT_X),
        (motion_names.AIR_DB, headers.ATTACK_IMPACT_Y),
        (motion_names.AIR_DB, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.CROUCH_B, headers.ATTACK_IMPACT_X),
        (motion_names.CROUCH_B, headers.ATTACK_IMPACT_Y),
        (motion_names.CROUCH_B, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.STAND_B, headers.ATTACK_IMPACT_X),
        (motion_names.STAND_B, headers.ATTACK_IMPACT_Y),
        (motion_names.STAND_B, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.AIR_B, headers.ATTACK_IMPACT_X),
        (motion_names.AIR_B, headers.ATTACK_IMPACT_Y),
        (motion_names.AIR_B, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.AIR_FA, headers.ATTACK_IMPACT_X),
        (motion_names.AIR_FA, headers.ATTACK_IMPACT_Y),
        (motion_names.AIR_FA, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.THROW_A, headers.ATTACK_IMPACT_X),
        (motion_names.THROW_A, headers.ATTACK_IMPACT_Y),
        (motion_names.THROW_A, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.AIR_UA, headers.ATTACK_IMPACT_X),
        (motion_names.AIR_UA, headers.ATTACK_IMPACT_Y),
        (motion_names.AIR_UA, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.AIR_F_D_DFA, headers.ATTACK_IMPACT_X),
        (motion_names.AIR_F_D_DFA, headers.ATTACK_IMPACT_Y),
        (motion_names.AIR_F_D_DFA, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.AIR_DA, headers.ATTACK_IMPACT_X),
        (motion_names.AIR_DA, headers.ATTACK_IMPACT_Y),
        (motion_names.AIR_DA, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.AIR_A, headers.ATTACK_IMPACT_X),
        (motion_names.AIR_A, headers.ATTACK_IMPACT_Y),
        (motion_names.AIR_A, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.STAND_FA, headers.ATTACK_IMPACT_X),
        (motion_names.STAND_FA, headers.ATTACK_IMPACT_Y),
        (motion_names.STAND_FA, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.CROUCH_FA, headers.ATTACK_IMPACT_X),
        (motion_names.CROUCH_FA, headers.ATTACK_IMPACT_Y),
        (motion_names.CROUCH_FA, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.STAND_D_DF_FA, headers.ATTACK_IMPACT_X),
        (motion_names.STAND_D_DF_FA, headers.ATTACK_IMPACT_Y),
        (motion_names.STAND_D_DF_FA, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.CROUCH_A, headers.ATTACK_IMPACT_X),
        (motion_names.CROUCH_A, headers.ATTACK_IMPACT_Y),
        (motion_names.CROUCH_A, headers.ATTACK_GIVE_GUARD_RECOV),
        (motion_names.STAND_A, headers.ATTACK_IMPACT_X),
        (motion_names.STAND_A, headers.ATTACK_IMPACT_Y),
        (motion_names.STAND_A, headers.ATTACK_GIVE_GUARD_RECOV),
    ],
)
add_to_collection(stunning)