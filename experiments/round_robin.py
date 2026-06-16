import asyncio
import json
import math
import os
import pathlib
import time
from itertools import product

import numpy as np
from distributed import Client, LocalCluster

import constants as c
import functions as f
import genetic_algorithm.genetic_functions as gf
from motion_classes.motion_editor import DEFAULT_MOTION_LIST


class AgentConfigRanges:
    maxDepth: list[int] = np.arange(5, 30, 5).tolist()  # 5
    ucbConstant: list[float] = [math.sqrt(2) / 2.0, math.sqrt(2), 2, 3]  # 4
    rolloutDuration: list[int] = np.arange(30, 150, 30).tolist()  # 4
    childCreationSimulationLimit: list[int] = np.arange(20, 80, 20).tolist()  # 3
    maxTreeDepth: list[int] = np.arange(2, 12, 2).tolist()  # 5
    minVisitCountBeforeRollout: list[int] = np.arange(5, 25, 5).tolist()  # 4
    usedReversedActionList: list[bool] = [True, False]  # 2

    # Total = 9600


def run_matchup(configuration: list[int, float, int, int, int, int, bool]) -> tuple[np.ndarray, np.ndarray]:
    iteration_count = (
        AgentConfigRanges.maxDepth.index(configuration[0])
        * AgentConfigRanges.ucbConstant.index(configuration[1])
        * AgentConfigRanges.rolloutDuration.index(configuration[2])
        * AgentConfigRanges.childCreationSimulationLimit.index(configuration[3])
        * AgentConfigRanges.maxTreeDepth.index(configuration[4])
        * AgentConfigRanges.minVisitCountBeforeRollout.index(configuration[5])
        * AgentConfigRanges.usedReversedActionList.index(configuration[6])
    )

    no_matches: int = 12
    game_time: int = c.GAME_DURATION_SEC
    engine_multiplier: int = 1

    win_rates: list[np.ndarray] = []
    experiment_name: str = f"matchup_{iteration_count}_P1"
    amended_experiment_name: str = f.append_time_uuid_experiment(experiment_name)

    environment: str = json.dumps(
        {
            "maxDepth": configuration[0],
            "ucbConstant": configuration[1],
            "rolloutDuration": configuration[2],
            "childCreationSimulationLimit": configuration[3],
            "maxTreeDepth": configuration[4],
            "minVisitCountBeforeRollout": configuration[5],
            "usedReversedActionList": configuration[6],
        },
    )
    environment_name: str = "AGENT_CONFIG_P1"

    win_rates.append(
        asyncio.run(
            gf.orchestrate_matches(
                mutated_motions=DEFAULT_MOTION_LIST,
                no_matches=no_matches,
                experiment_name=amended_experiment_name,
                engine_multiplier=engine_multiplier,
                game_duration_sec=game_time,
                visual=False,
                agents=np.tile(
                    np.array(
                        [
                            c.AgentNames.KAY_MCTS_MX_AGENT,
                            c.AgentNames.CONSISTENT_MCTS_AGENT,
                        ],
                        dtype=object,
                    ),
                    reps=3,
                ).reshape(3, -1),
                environment=environment,
                environment_name=environment_name,
                force_frame_data_unlink=True,
            ),
        ),
    )

    f.consolidate_data(
        amended_experiment_name,
        exclude_list=[
            c.LOGS.FRAME_DATA,
            c.LOGS.POINT,
        ],
    )

    experiment_name: str = f"matchup_{iteration_count}_P2"
    amended_experiment_name: str = f.append_time_uuid_experiment(experiment_name)
    environment_name: str = "AGENT_CONFIG_P2"

    win_rates.append(
        asyncio.run(
            gf.orchestrate_matches(
                mutated_motions=DEFAULT_MOTION_LIST,
                no_matches=no_matches,
                experiment_name=amended_experiment_name,
                engine_multiplier=engine_multiplier,
                game_duration_sec=game_time,
                visual=False,
                agents=np.tile(
                    np.array(
                        [
                            c.AgentNames.CONSISTENT_MCTS_AGENT,
                            c.AgentNames.KAY_MCTS_MX_AGENT,
                        ],
                        dtype=object,
                    ),
                    reps=3,
                ).reshape(3, -1),
                environment=environment,
                environment_name=environment_name,
                force_frame_data_unlink=True,
            ),
        ),
    )

    f.consolidate_data(
        amended_experiment_name,
        exclude_list=[
            c.LOGS.FRAME_DATA,
            c.LOGS.POINT,
        ],
    )

    return tuple(win_rates)


if __name__ == "__main__":
    f.set_random_seeds(c.GLOBAL_SEED)
    f.arg_parser()

    pathlib.Path(os.path.join(c.LOGS.EXPERIMENTS_FOLDER, c.LOGS.ROUND_ROBIN)).mkdir(parents=True, exist_ok=True)

    if c.SCHEDULER_FILE is not None:
        if not pathlib.Path(c.SCHEDULER_FILE).exists():
            raise FileNotFoundError(f"Missing file: {c.SCHEDULER_FILE}.\nCannot start job at all")

        print("--- Running with Scheduler File ---")
        client = Client(scheduler_file=c.SCHEDULER_FILE)

        print("Waiting for workers to report for duty...")
        client.wait_for_workers(n_workers=c.NODES, timeout=30)
        print("Cluster is fully populated. Starting Evolution.")
    else:
        print("--- Running with LocalCluster ---")

        core_count: int = c.CORES // c.NODES
        cluster = LocalCluster(
            n_workers=c.NODES,
            threads_per_worker=core_count,
            resources={"cores": core_count},
        )

        client = Client(cluster)

    print(f"Dask Dashboard available at: {client.dashboard_link}")
    start_time = time.perf_counter()

    configurations: list[int, float, int, int, int, int, bool] = list(
        product(
            *[
                AgentConfigRanges.maxDepth,
                AgentConfigRanges.ucbConstant,
                AgentConfigRanges.rolloutDuration,
                AgentConfigRanges.childCreationSimulationLimit,
                AgentConfigRanges.maxTreeDepth,
                AgentConfigRanges.minVisitCountBeforeRollout,
                AgentConfigRanges.usedReversedActionList,
            ],
        ),
    )

    # NOTE: To make this work, I edited the orchestrate matches function. It will not pass through the win_rates as is

    win_rates = client.gather(
        client.map(
            run_matchup,
            configurations,
            resources={"cores": 3},
        ),
    )

    end_time = time.perf_counter()
    print(f"time: {end_time - start_time}")

    with open(
        os.path.join(
            c.LOGS.EXPERIMENTS_FOLDER,
            c.LOGS.ROUND_ROBIN,
            f"{(f.append_time_uuid_experiment('round_robin_results'))}.txt",
        ),
        "a",
    ) as f:
        f.write("Win rates:\n")
        f.write(f"{win_rates}\n\n")

    # TODO: Maybe look into consolidating the other entries.
