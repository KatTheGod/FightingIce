import os
import pathlib
from enum import StrEnum

import dill
import numpy as np
from pymoo.core.result import Result

import constants as c
import functions as f
import genetic_algorithm.genetic_functions as gf
from genetic_algorithm.fighting_ice_problem import IndividualSettings, evaluate_individual
from motion_classes.motion_headers import MotionHeadersEnum as headers
from motion_classes.motion_names import MotionNamesEnum as motion_names


class Objectives(StrEnum):
    COMPETITIVE_BALANCE: str = "competitive_balance"
    UNIQUENESS: str = "uniqueness"
    EXCITEMENT: str = "excitement"


class SolutionHolder:
    def __init__(
        self,
        gene: np.ndarray,
        fitness: np.ndarray,
        objectives: list[Objectives],
    ) -> None:
        self.gene: np.ndarray = gene
        self.fitness: dict[Objectives, float] = {}
        if len(objectives) == 1:
            fitness = fitness[:1]

        for objective, fitness_value in zip(objectives, fitness, strict=True):
            self.fitness[objective] = fitness_value

        self.global_fitness: dict[Objectives, float] = {}

    def set_global_fitness(self, setting: IndividualSettings) -> None:
        """
        NOTE: The order or the objectives from the problem must be manually extracted
        We could maybe think of a way to better handle this, but I would like something simple for now
        """
        objective_order: list[Objectives] = [
            Objectives.COMPETITIVE_BALANCE,
            Objectives.EXCITEMENT,
            Objectives.UNIQUENESS,
        ]

        fitness: np.ndarray = evaluate_individual(self.gene, setting)

        for objective, fitness_value in zip(objective_order, fitness, strict=True):
            self.global_fitness[objective] = fitness_value


class ResultHolder:
    def __init__(
        self,
        pkl_name: str,
        objectives: list[Objectives],
    ) -> None:
        self.n_objectives: int = len(objectives)
        self.experiment_name: str = f.append_time_uuid_experiment(f"{pkl_name.split('/', -1)[-1].split('.', 1)[0]}_result_replay")
        self.result: Result = f.resume_algorithm(plk_name=pkl_name, throw_error=True)
        self.solutions: list[SolutionHolder] = []
        for gene, fitness in zip(self.result.X, self.result.F, strict=True):
            self.solutions.append(
                SolutionHolder(
                    gene,
                    fitness,
                    objectives,
                ),
            )


def replay_results_and_save(results: list[ResultHolder], save: bool = True, rerun_three: bool = False) -> None:
    raise NotImplementedError("Need to accomodate for new meta_subspace")
    motion_adjustments: list[tuple[str, str]] = [
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

    motion_coordinates: np.ndarray = gf.get_motion_coordinates(motion_adjustments)
    numerical_mapped_motion_coordinates = gf.map_numerical_motion_coordinates(motion_adjustments)

    for result_index, result in enumerate(results):
        print(f"Expanding experiment: {result.experiment_name} ({result_index}/{len(results)})")

        if result.n_objectives == 3 and not rerun_three:
            print("Skipping, since already done all objectives")
            print("Will save if flag is enabled")
        else:
            for solution_index, solution in enumerate(result.solutions):
                print(f"Evaluating solution {solution_index}/{len(result.solutions)}")

                setting: IndividualSettings = IndividualSettings(
                    meta_subspace=motion_coordinates,
                    mapped_numerical_motion_coordinates=numerical_mapped_motion_coordinates,
                    no_matches=8,
                    engine_multiplier=4,
                    game_duration_sec=c.GAME_DURATION_SEC,
                    visual=False,
                    experiment_name=f"{result.experiment_name}{solution_index}",
                )
                solution.set_global_fitness(setting)

            print(f"Done expanding experiment: {result.experiment_name}\n")

        if save:
            save_path = pathlib.Path(
                os.path.join(
                    "GeneticAlgorithm",
                    "result_replay_container",
                ),
            )

            save_path.mkdir(parents=True, exist_ok=True)

            with open(f"{os.path.join(str(save_path), result.experiment_name)}.pkl", "wb") as result_file:
                dill.dump(result, result_file)
