# This file will be used to replay one solution
# Or it can be used to find the optimal number of runs for a solution to be stable.
# Will write to file, and we can interpret that result in jupyter (just easier)
# This could be done on the cluster with mure more compute, but its not that deep, its something that is ran once.
# If we see ourselves doing this often, we can look into that

import asyncio
import os
import uuid
import pathlib
from datetime import datetime
import time

import numpy as np
from sympy import divisors

import constants as c
import functions as f
from GeneticAlgorithm.genetic_functions import constraint_novelty_search, gene_to_motions, generate_random_gene, orchestrate_matches, get_motion_coordinates
from GeneticAlgorithm.genetic_functions import map_numerical_motion_coordinates
from MotionClasses.MotionHeaders import MotionHeaders as headers
from MotionClasses.MotionNames import MotionNames as motion_names


def replay_single_mutation(gene: np.ndarray, match_per_agent: int, motion_adjustments: list[tuple[str, str]]) -> tuple[float, float]:
    max_capacity = c.CORES // 3

    # Subject to change with other experiments
    motion_adjustments: list[tuple[str, str]] = [
        (motion_names.STAND_A, headers.ATTACK_HIT_DAMAGE),
        (motion_names.STAND_B, headers.ATTACK_HIT_ADD_ENERGY),
    ]

    motion_coordinates = get_motion_coordinates(motion_adjustments)
    mutated_motions = gene_to_motions(gene, motion_coordinates)

    if match_per_agent <= max_capacity:
        engine_multiplier = match_per_agent
    else:
        factors = divisors(match_per_agent)
        engine_multiplier = factors[np.searchsorted(factors, max_capacity, side='left') - 1]

    time_for_match: str = datetime.now().strftime('%H.%M.%S')
    average_win_rate = asyncio.run(
        orchestrate_matches(
            mutated_motions=mutated_motions,
            no_matches=match_per_agent // engine_multiplier,
            experiment_name='visual',
            experiment_suffix=time_for_match,
            engine_multiplier=engine_multiplier,
            game_duration_sec=60,
            visual=False,
        )
    )

    numerical_differences = np.stack([motion.select_dtypes('number') for motion in mutated_motions])
    uniqueness_reward: float = constraint_novelty_search(
        numerical_differences,
        get_motion_coordinates(motion_adjustments),
        map_numerical_motion_coordinates(motion_adjustments),
        None,
        None,
    )

    competitive_balance: float = f.transform_win_rate(average_win_rate)

    return (float(uniqueness_reward), float(competitive_balance))


# We designed this function such that we can maybe expand it to work on the cluster if we need it to.
def generate_data(match_counts: np.ndarray, repeat_count: int = 10) -> None:
    raise NotImplementedError("Generating a new gene needs to be adjusted")
    motion_adjustments: list[tuple[str, str]] = [
        (motion_names.STAND_A, headers.ATTACK_HIT_DAMAGE),
        (motion_names.STAND_B, headers.ATTACK_HIT_ADD_ENERGY),
    ]
    job_id: str = f.parse_argument_str(
        shorthand='jid',
        full_name='jon_id',
    )

    # Could parse nodes and cores as well

    if job_id is None:
        job_id = uuid.uuid4().hex

    pathlib.Path(os.path.join(c.LOGS.SOLUTION_EXPLORER, 'logs', job_id)).mkdir(parents=True, exist_ok=True)

    print(f'generating data for job {job_id}')
    for match_count in match_counts:
        print(f'About to start simulations for match count: {match_count}')
        results = np.zeros(shape=repeat_count, dtype=np.float64)
        times = np.zeros(shape=repeat_count, dtype=np.float64)
        for repeat in range(repeat_count):
            print(f'repeat: {repeat}')
            start_time = time.perf_counter()
            results[repeat] = replay_single_mutation(
                gene=generate_random_gene(motion_adjustments),
                match_per_agent=match_count,
            )[1]
            times[repeat] = time.perf_counter() - start_time

        np.savetxt(
            fname=os.path.join(
                c.LOGS.SOLUTION_EXPLORER,
                'logs',
                job_id,
                f'match_count_{match_count}.csv',
            ),
            X=results,
            delimiter=',',
            fmt='%.10f',
        )

        np.savetxt(
            fname=os.path.join(
                c.LOGS.SOLUTION_EXPLORER,
                'logs',
                job_id,
                f'match_time_{match_count}.csv',
            ),
            X=times,
            delimiter=',',
            fmt='%.10f',
        )


if __name__ == '__main__':
    generate_data(match_counts=np.array([1, 2, 3, 5, 7, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]), repeat_count=10)
    # print(replay_single_mutation(gene=np.array([140, 107, 144, 224, 174, 14]), match_per_agent=8))
