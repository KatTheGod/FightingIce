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
    * We need to think about if we are going to use Problem or ElementWiseProblem.
    * Right now, I am leaning more towards element wise, and will use something to parallelized the process.

    * Now talking about the data structures.
    * Its going to be a meta state set for all 3 characters...
"""

"""
    We are going to handle the meta variable changes manually in this class...
    Not something that can really be passed you know...

    Right now, we are going to work with:
        * Damage - stand a
        * Hit Add Energy - stand b
"""


class IndividualSettings:
    def __init__(
        self,
        motion_coordinates: np.ndarray,
        mapped_numerical_motion_coordinates: np.ndarray,
        no_matches: int,
        experiment_name: str,
        engine_multiplier: int,
        game_duration_sec: int,
        visual: bool,
    ):
        self.motion_coordinates = motion_coordinates
        self.mapped_numerical_motion_coordinates = mapped_numerical_motion_coordinates
        self.no_matches = no_matches
        self.experiment_name = experiment_name
        self.engine_multiplier = engine_multiplier
        self.game_duration_sec = game_duration_sec
        self.visual = visual


def evaluate_individual(x: np.ndarray, settings: IndividualSettings) -> np.ndarray:
    mutated_motions = gf.gene_to_motions(gene=x, motion_coordinates=settings.motion_coordinates)

    numerical_differences = np.stack([motion.select_dtypes('number') for motion in mutated_motions])
    uniqueness_reward = gf.constraint_novelty_search(
        numerical_motions=numerical_differences,
        motion_coordinates=settings.motion_coordinates,
        mapped_numerical_motion_coordinates=settings.mapped_numerical_motion_coordinates,
        string_motions=None,
        boolean_motions=None,
    )

    amended_experiment_name: str = f.append_time_uuid_experiment(settings.experiment_name)

    average_win_rate = asyncio.run(
        gf.orchestrate_matches(
            mutated_motions=mutated_motions,
            no_matches=settings.no_matches,
            experiment_name=amended_experiment_name,
            engine_multiplier=settings.engine_multiplier,
            game_duration_sec=settings.game_duration_sec,
            visual=settings.visual,
        )
    )

    competitive_balance: float = f.transform_win_rate(average_win_rate)

    excitement = asyncio.run(gf.calculate_excitement(amended_experiment_name, frame_window=10))

    return np.array(
        [
            -competitive_balance,
            -excitement,
            -uniqueness_reward,
        ],
        dtype=np.float64,
    )


class FightingIceProblem(Problem):
    def __init__(
        self,
        experiment_name: str,
        dask_client: Client,
        no_matches: int = 1,
        engine_multiplier: int = 1,
        game_duration_sec: int = 60,
        visual: bool = False,
        **kwargs: Any,
    ) -> None:

        self.visual = visual
        self.experiment_name = experiment_name
        self.no_matches = no_matches
        self.engine_multiplier = engine_multiplier
        self.game_duration_sec = game_duration_sec
        self.client = dask_client

        # Going to adjust the experiment name if its already in use
        pathlib.Path(c.CUSTOM_MOTION_PATH).mkdir(parents=True, exist_ok=True)
        experiment_name_regex = re.compile(rf'{experiment_name}_(\d+).*')
        experiment_name_number: int = -1
        for directory in pathlib.Path(c.CUSTOM_MOTION_PATH).iterdir():
            match = experiment_name_regex.match(directory.name)
            if match:
                experiment_name_number = max(-1, int(match.group(1)))

        self.experiment_name = f'{experiment_name}_{experiment_name_number + 1}'
        print(f'Derived experiment name: {self.experiment_name}')

        # For the first iteration, we are only going to increase the hit damage for stand a, and energy add for stand b
        # Remember this is for every character
        self.motion_adjustments: list[tuple[str, str]] = [
            (motion_names.STAND_A, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.STAND_A, headers.ATTACK_GIVE_ENERGY),
            (motion_names.STAND_B, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.STAND_B, headers.ATTACK_GIVE_ENERGY),
            (motion_names.CROUCH_A, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.CROUCH_A, headers.ATTACK_GIVE_ENERGY),
            (motion_names.CROUCH_B, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.CROUCH_B, headers.ATTACK_GIVE_ENERGY),
            (motion_names.AIR_A, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.AIR_A, headers.ATTACK_GIVE_ENERGY),
            (motion_names.AIR_B, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.AIR_B, headers.ATTACK_GIVE_ENERGY),
            (motion_names.AIR_DA, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.AIR_DA, headers.ATTACK_GIVE_ENERGY),
            (motion_names.AIR_DB, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.AIR_DB, headers.ATTACK_GIVE_ENERGY),
            (motion_names.STAND_FA, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.STAND_FA, headers.ATTACK_GIVE_ENERGY),
            (motion_names.STAND_FB, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.STAND_FB, headers.ATTACK_GIVE_ENERGY),
            (motion_names.CROUCH_FA, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.CROUCH_FA, headers.ATTACK_GIVE_ENERGY),
            (motion_names.CROUCH_FB, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.CROUCH_FB, headers.ATTACK_GIVE_ENERGY),
            (motion_names.AIR_FA, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.AIR_FA, headers.ATTACK_GIVE_ENERGY),
            (motion_names.AIR_FB, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.AIR_FB, headers.ATTACK_GIVE_ENERGY),
            (motion_names.AIR_UA, headers.ATTACK_HIT_ADD_ENERGY),
            (motion_names.AIR_UA, headers.ATTACK_GIVE_ENERGY),
        ]

        self.motion_coordinates: np.ndarray = gf.get_motion_coordinates(self.motion_adjustments)
        self.numerical_mapped_motion_coordinates = gf.map_numerical_motion_coordinates(self.motion_adjustments)

        # might not be needed
        self.motion_mapper = f.motion_cord_to_index_bulk(self.motion_coordinates)

        gene_count: int = len(self.motion_adjustments) * 3
        xl = np.zeros(shape=gene_count, dtype=np.int64)
        xu = np.zeros(shape=gene_count, dtype=np.int64)

        for character_index in range(3):
            for index, (_, header) in enumerate(self.motion_adjustments):
                xl[character_index * (gene_count // 3) + index] = headers.HEADER_LIMITS[header]['min']
                xu[character_index * (gene_count // 3) + index] = headers.HEADER_LIMITS[header]['max']

        prob_vars: dict[str, int] = {f'x{i}': Integer(bounds=(xl[i], xu[i])) for i in range(gene_count)}
        super().__init__(
            elementwise=False,
            **kwargs,
            n_obj=3,
            n_ieq_constr=0,
            xl=xl,
            xu=xu,
            vtype=int,
            vars=prob_vars,
        )

    def _evaluate(
        self,
        X: np.ndarray,
        out: dict[str, np.ndarray],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        eval_settings = IndividualSettings(
            motion_coordinates=self.motion_coordinates,
            mapped_numerical_motion_coordinates=self.numerical_mapped_motion_coordinates,
            no_matches=self.no_matches,
            experiment_name=self.experiment_name,
            engine_multiplier=self.engine_multiplier,
            game_duration_sec=self.game_duration_sec,
            visual=self.visual,
        )

        futures = self.client.map(
            evaluate_individual,
            X,
            settings=eval_settings,
            resources={'cores': self.engine_multiplier * 3},
        )

        results = self.client.gather(futures)

        out['F'] = np.array(results, dtype=np.float64)

    # These 2 are for when pymoo makes a copy of this object.
    # It will try to copy the client, but thats an object that can't be copied.
    def __getstate__(self) -> dict:
        state = self.__dict__.copy()
        if 'client' in state:
            del state['client']
        return state

    def __setstate__(self, state: dict) -> None:
        self.__dict__.update(state)
        self.client = None
