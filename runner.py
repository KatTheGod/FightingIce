import asyncio
import numpy as np
import os

from pyftg.socket.aio.gateway import Gateway
import MotionClasses.MotionEditor as me
from MotionClasses.MotionNames import MotionNames as motion_names
from MotionClasses.MotionHeaders import MotionHeaders as headers
import MotionClasses.MotionEditor as me
import GeneticAlgorithm.genetic_functions as gf
import pathlib
import pandas

import constants as c
import functions as f
from itertools import combinations

"""
	Objective of this file
		We are trying to simulate x games, ran over multiple simulators.
		Maybe we can pass in who's playing who, and where the motions are.
"""

"""
    TODO:
        * Get the overwriting thing working well.
        * Linter
        * create script / python to kill all active instances?????
			* Don't remember what this is
"""
experiment_name: str = f.append_time_uuid_experiment('delete')
asyncio.run(
    gf.orchestrate_matches(
        me.DEFAULT_MOTION_LIST,
        1,
        experiment_name,
        1,
        60,
        False,
    )
)

f.consolidate_data(
    experiment_name,
    exclude_list=[
        c.LOGS.POINT,
        c.LOGS.FRAME_DATA,
    ],
)
