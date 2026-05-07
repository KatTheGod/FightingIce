# import os

# import constants as c
# import MotionClasses.MotionEditor as me
# from MotionClasses.MotionEditor import MotionEditor
# from MotionClasses.MotionHeaders import MotionHeaders as headers
# from MotionClasses.MotionNames import MotionNames as motion_names

# motion_editor = MotionEditor(
#     c.CHARACTERS.ZEN,
#     os.path.join(
#         'custom_motions',
#         'motion_editor_1.csv',
#     ),
# )

# print(motion_editor.motion_custom.columns)
# motion_editor.motion_custom.at[motion_names.NEUTRAL, headers.FRAME_NUMBER] += 50
# motion_editor.save_custom_motion(motion_editor.custom_motion_path)

# t = me.get_motion_difference(motion_editor.motion_default, motion_editor.motion_custom)
# print('t', t)

# Experiment to determine the point at which running more engines is bad for the system and should rather run more rounds
import pathlib
import time
import math
import dill
import numpy as np
from distributed import Client, LocalCluster
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.decomposition.pbi import PBI
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PolynomialMutation
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.util.ref_dirs import get_reference_directions
import sys

import constants as c
import functions as f
import GeneticAlgorithm.genetic_functions as gf
from GeneticAlgorithm.FightingIceProblem import FightingIceProblem

from pymoo.core.algorithm import Algorithm
from pymoo.core.problem import Problem
from pymoo.core.result import Result


# async def run_games(no_engines: int):
#     common_commands = [
#         'java',
#         '-cp',
#         os.pathsep.join(['dare.jar', '.']),
#         'Main',
#         '--limithp',
#         str(c.PLAYER_HP),
#         str(c.PLAYER_HP),
#         # '-df',
#         '-r',
#         '1',
#         '-f',
#         str(c.GAME_DURATION_SEC * 60),
#         '--time-stamp',
#         c.GAME_TIME,
#         # '--headless-mode',
#         '--input-sync',
#         # '--lightweight-mode',
#         '--pyftg-mode',
#         '--non-delay',
#         '2',
#     ]
#     await f.start_simulators(
#         no_engines=no_engines,
#         common_commands=common_commands,
#         characters=np.array(
#             [
#                 [c.CHARACTERS.ZEN.name, c.CHARACTERS.GARNET.name],
#                 [c.CHARACTERS.ZEN.name, c.CHARACTERS.LUD.name],
#                 [c.CHARACTERS.GARNET.name, c.CHARACTERS.LUD.name],
#             ]
#         ),
#         # Not really used anyways
#         motions=me.DEFAULT_MOTION_LIST,
#         agent_names=np.full(shape=(3, 2), dtype=object, fill_value=c.AgentNames.MCTS_AGENT),
#         experiment_name='low',
#         deterministic=True,
#     )


# if __name__ == '__main__':
#     c.start_time = time.perf_counter()
#     # c.PLAYER_HP = 10000
#     c.NO_GAMES = 2
#     c.POLL_INTERVAL_SEC = 0
#     asyncio.run(run_games(no_engines=1))
#     print(f'time: {c.end_time - c.start_time}')


# Clock time experiments
# MOEAD - pop = 3 - time = 222.09393120001187
# NSGA - pop = 3 - time = 236.92388630000642

# Uniqueness adjustments tests
# import GeneticAlgorithm.genetic_functions as gf

# from MotionClasses.MotionHeaders import MotionHeaders as headers
# from MotionClasses.MotionNames import MotionNames as motion_names

# if __name__ == '__main__' and False:
#     motion_adjustments: list[tuple[str, str]] = [
#         (motion_names.STAND_A, headers.ATTACK_HIT_ADD_ENERGY),
#         (motion_names.STAND_A, headers.ATTACK_GIVE_ENERGY),
#     ]

#     motion_coordinates = gf.get_motion_coordinates(motion_adjustments)
#     x = gf.generate_random_gene(motion_adjustments)
#     mutated_motions = gf.gene_to_motions(gene=x, motion_coordinates=motion_coordinates)
#     mapped_motion_coordinates = gf.map_numerical_motion_coordinates(motion_adjustments)

#     numerical_differences = np.stack([motion.select_dtypes('number') for motion in mutated_motions])
#     uniqueness_reward = gf.constraint_novelty_search(
#         numerical_motions=numerical_differences,
#         motion_coordinates=motion_coordinates,
#         mapped_numerical_motion_coordinates=mapped_motion_coordinates,
#         string_motions=None,
#         boolean_motions=None,
#     )

# if __name__ == '__main__':
#     # frame_window: int = 360
#     # exp_name: str = 'runner_03.07.03-2026.04.29_03.07.02.json'
#     win_probabilities = gf.calculate_win_probabilities(exp_name, frame_window=frame_window)
#     best_diff = 1-math.sqrt(1./6.)
#     # best_diff = 0.6
#     # print(best_diff)
#     win_probabilities = np.array([1, best_diff, 1, best_diff, 1, best_diff])
#     # entropy = gf.calculate_entropy_score(win_probabilities[::3], frame_window=frame_window)
#     entropy = gf.calculate_entropy_score([win_probabilities], frame_window=1)
#     print(entropy)

if __name__ == '__main__':
    f.arg_parser()

    if c.SCHEDULER_FILE is not None:
        if not pathlib.Path(c.SCHEDULER_FILE).exists():
            raise FileNotFoundError(f'Missing file: {c.SCHEDULER_FILE}.\nCannot start job at all')

        print('--- Running with Scheduler File ---')
        client = Client(scheduler_file=c.SCHEDULER_FILE)

        print('Waiting for workers to report for duty...')
        client.wait_for_workers(n_workers=c.NODES, timeout=30)
        print('Cluster is fully populated. Starting Evolution.')
    else:
        print('--- Running with LocalCluster ---')

        core_count: int = c.CORES // c.NODES
        cluster = LocalCluster(
            n_workers=c.NODES,
            threads_per_worker=core_count,
            resources={'cores': core_count},
        )

        client = Client(cluster)

    print(f'Dask Dashboard available at: {client.dashboard_link}')
    experiment_name: str = 'comp_p32_n10_energy'

    try:
        previous_result = f.resume_algorithm(None)

        start_time = time.perf_counter()
        if previous_result is None:
            print('New experiment')
            current_gen_count: int = 0
            problem = FightingIceProblem(
                experiment_name=experiment_name,
                dask_client=client,
                engine_multiplier=4,
                no_matches=3,
                game_duration_sec=60,
                visual=False,
            )

            res = minimize(
                problem=problem,
                algorithm=MOEAD(
                    # N = n_partitions + 1 (for n_obj == 2)
                    # Must be greater than n_neighbors
                    ref_dirs=get_reference_directions(
                        c.pymoo.MOEAD.SpreadType.DAS_DENNIS,
                        n_dim=2,
                        n_partitions=29,
                    ),
                    # Magic number is 20
                    n_neighbors=10,
                    decomposition=PBI(theta=10),
                    sampling=IntegerRandomSampling(),
                    crossover=SBX(prob=1.0, eta=20, vtype=int),
                    mutation=PolynomialMutation(prob=1.0, eta=20, vtype=int),
                ),
                termination=get_termination(
                    c.pymoo.TERMINATION.DEFAULT_MOO_TERMINATION,
                    n_max_gen=20,
                    ftol=1e-6,
                    period=6,
                ),
                copy_algorithm=previous_result is None,
                seed=1,
                save_history=True,
                verbose=True,
            )
        else:
            print('Continuing experiment')
            problem: FightingIceProblem = previous_result.problem
            algorithm: Algorithm = previous_result.algorithm

            # Re-attach dask client
            problem.client = client

            current_gen_count: int = algorithm.n_gen
            algorithm.termination = get_termination(
                c.pymoo.TERMINATION.DEFAULT_MOO_TERMINATION,
                n_max_gen=20 + current_gen_count,
                ftol=1e-6,
                period=6,
            )

            # Manually run the minimize loop
            while algorithm.has_next():
                algorithm.next()

            res = algorithm.result()

        f.consolidate_data(
            problem.experiment_name,
            exclude_list=[
                c.LOGS.POINT,
                c.LOGS.FRAME_DATA,
            ],
        )

        end_time = time.perf_counter()
        print(f'time: {end_time - start_time}')

        with open(f'{experiment_name}.pkl', 'wb') as res_file:
            dill.dump(res, res_file)
    finally:
        client.shutdown()
        client.close()
