import time
from pathlib import Path

import dill
from distributed import Client, LocalCluster
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.core.algorithm import Algorithm
from pymoo.decomposition.pbi import PBI
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PolynomialMutation
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.util.ref_dirs import get_reference_directions

import constants as c
import functions as f
from genetic_algorithm import meta_space
from genetic_algorithm.fighting_ice_problem import FightingIceProblem

if __name__ == "__main__":
    f.set_random_seeds(c.GLOBAL_SEED)
    f.arg_parser()

    if c.SCHEDULER_FILE is not None:
        if not Path(c.SCHEDULER_FILE).exists():
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
    c.OBJECTIVE_SET = [
        c.Objectives.competitive_balance,
        c.Objectives.uniqueness,
    ]
    meta_subspace = meta_space.BASIC_STAND_A_B
    experiment_name: str = meta_subspace.derive_experiment_name("testing_nfs_fix")

    # TODO: COMPLETE ME
    # We are going to continue / start an experiment
    # TODO: Keep engines running
    # TODO: Run experiments to see how many cores we can cram into simulations, check win-rate stability

    try:
        previous_result = f.resume_algorithm(None)
        termination: any = get_termination(
            c.pymoo.TERMINATION.DEFAULT_MOO_TERMINATION,
            n_max_gen=2,
            ftol=1e-6,
            period=1,
        )

        start_time = time.perf_counter()
        if previous_result is None:
            print("New experiment")
            current_gen_count: int = 0
            problem = FightingIceProblem(
                experiment_name=experiment_name,
                dask_client=client,
                # bigbatch -> 32
                # engine_multiplier=4,
                # no_matches=8,
                # stampede -> 30
                engine_multiplier=5,
                no_matches=3,
                # local run
                # engine_multiplier=1,
                # no_matches=1,
                game_duration_sec=c.GAME_DURATION_SEC,
                visual=False,
                save_fitness=True,
                meta_subspace=meta_subspace,
            )

            """
                Stampede

                Time Estimation:
                    36 * 10 -> 360 Simulations
                    6 -> 30 Games per simulation
                    6 * 360 -> 2160 Games

                Cluster Capabilities:
                    Nodes == 5
                    Cores == 16

                    -> each node handles 1 individual
                    2160 / 5 -> 432 Games in sequence

                Time Estimations
                    Minutes:
                        1.0: 7,2 hours
                        1.5: 10,8 hours
                        2.0: 14,4 hours (Hanging on limit)

                BigBatch

                Time Estimation:
                    # Incorrect, because we have one taking longer than that...
                    Weird!
                    36 * 10 -> 360 Simulations
                    8 -> 32 Games per simulation
                    8 * 360 -> 2880 Games

                Cluster Capabilities:
                    Nodes == 6
                    Cores == 14

                    -> each node handles 1 individual
                    2880 / 6 -> 480 Games in sequence

                Time Estimations
                    Minutes:
                        1.0: 8 hours
                        1.5: 12 hours
                        2.0: 16 hours (further out though)
            """
            res = minimize(
                problem=problem,
                algorithm=MOEAD(
                    # N = n_partitions + 1 (for n_obj == 2)
                    # Must be greater than n_neighbors
                    ref_dirs=get_reference_directions(
                        c.pymoo.MOEAD.SpreadType.DAS_DENNIS,
                        # n_partitions=10 == 66
                        # n_partitions=7, # == 36
                        n_partitions=9, # small local tests
                        n_dim=len(c.OBJECTIVE_SET),
                        # n_partitions=29,
                    ),
                    # Magic number is 20
                    # n_neighbors=7,
                    # n_neighbors=15, Used for 66 individuals
                    # n_neighbors=8, # Used for 30-32 individuals
                    n_neighbors=2,
                    decomposition=PBI(theta=10),
                    sampling=IntegerRandomSampling(),
                    crossover=SBX(prob=1.0, eta=20, vtype=int),
                    mutation=PolynomialMutation(prob=1.0, eta=20, vtype=int),
                ),
                termination=termination,
                copy_algorithm=previous_result is None,
                seed=c.GLOBAL_SEED,
                save_history=True,
                verbose=True,
            )
        else:
            # This only works for COMPLETED terminations, can't stop midway
            print("Continuing experiment")
            problem: FightingIceProblem = previous_result.problem
            algorithm: Algorithm = previous_result.algorithm

            # Re-attach dask client
            problem.client = client

            current_gen_count: int = algorithm.n_gen
            # This might not work, worth checking
            termination.n_max_gen += current_gen_count
            algorithm.termination = termination

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
        print(f"time: {end_time - start_time}")

        Path(c.Directories.DUMP_FILES).mkdir(exist_ok=True, parents=True)
        with Path.open(
            str(
                Path(c.Directories.DUMP_FILES)  #
                / f"{experiment_name}.pkl"
            ),
            "wb",
        ) as res_file:
            dill.dump(res, res_file)
    finally:
        client.shutdown()
        client.close()
