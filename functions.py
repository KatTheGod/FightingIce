import argparse
import asyncio
import datetime
import math
import os
import pathlib
import random
import re
import shutil
import subprocess
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from itertools import islice

import aiofiles
import dill
import numpy as np
import pandas
from pyftg.socket.aio.gateway import Gateway
from pymoo.core.algorithm import Algorithm
from pymoo.core.result import Result

import constants as c
import functions as f
from agents.KatKickAi import KatKickAi
from MotionClasses.MotionEditor import MotionEditor


def parse_argument_str(shorthand: str, full_name: str, default: str | None = None, help: str = '') -> str:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='FightingICE Research Runner', add_help=False)

    parser.add_argument(
        f'-{shorthand}',
        f'--{full_name}',
        type=str,
        default=default,
        help=help,
    )

    args, _ = parser.parse_known_args()
    return getattr(args, full_name)


def arg_parser() -> str:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='FightingICE Research Runner')

    parser.add_argument(
        '-hp',
        '--player_hit_points',
        type=int,
        default=-1,
        help='Hit-points for both agents',
    )
    parser.add_argument(
        '-i',
        '--poll_interval_sec',
        type=int,
        default=-1,
        help='Time lag for updating console log',
    )
    parser.add_argument(
        '-e',
        '--engine_count',
        type=int,
        default=-1,
        help='Number of engines that will run at once',
    )
    parser.add_argument(
        '-g',
        '--no_games',
        type=int,
        default=-1,
        help='Number of games each engine will simulate',
    )
    parser.add_argument(
        '-d',
        '--game_duration',
        type=int,
        default=-1,
        help='Max drain of each match between agents',
    )
    parser.add_argument(
        '-exp',
        '--game_name',
        type=str,
        default='adhoc',
        help='Name of the experiment',
    )
    parser.add_argument(
        '-zip',
        '--zip_files',
        type=str,
        default='True',
        help='Flag to ascertain if log files should be zipped or not',
    )
    parser.add_argument(
        '-c',
        '--cores',
        type=int,
        default=-1,
        help='Multiprocessing: Flag for core count per node',
    )
    parser.add_argument(
        '-n',
        '--nodes',
        type=int,
        default=-1,
        help='Multiprocessing: Flag for node count',
    )
    parser.add_argument(
        '-p',
        '--partition',
        type=str,
        default='regular',
        help='Multiprocessing: Name of partition',
    )
    parser.add_argument(
        '-sf',
        '--scheduler_file',
        type=str,
        default=None,
        help='Multiprocessing: Config file for scheduler',
    )
    parser.add_argument(
        '-bp',
        '--base_path',
        type=str,
        default=None,
        help='Multiprocessing: Base path for absolute routing',
    )

    # Booleans (Flags)
    # action="store_true" means if the flag is present, it's True. If not, it's False.
    # parser.add_argument("--headless", action="store_true", help="Run in headless mode")

    args = parser.parse_args()

    c.NO_ENGINES = (
        c.NO_ENGINES  #
        if args.engine_count == -1
        else args.engine_count
    )
    c.NO_GAMES = (
        c.NO_GAMES  #
        if args.no_games == -1
        else args.no_games
    )
    c.PLAYER_HP = (
        c.PLAYER_HP  #
        if args.player_hit_points == -1
        else args.player_hit_points
    )
    c.POLL_INTERVAL_SEC = (
        c.POLL_INTERVAL_SEC  #
        if args.poll_interval_sec == -1
        else args.poll_interval_sec
    )
    c.GAME_DURATION_SEC = (
        c.GAME_DURATION_SEC  #
        if args.game_duration == -1
        else args.game_duration
    )
    c.EXPERIMENT_NAME = (
        c.EXPERIMENT_NAME  #
        if args.game_name == 'adhoc'
        else args.game_name
    )
    c.ZIP_FILES = (
        c.ZIP_FILES  #
        if args.zip_files == 'True'
        else False
    )
    c.NODES = (
        c.NODES  #
        if args.nodes == -1
        else args.nodes
    )
    c.CORES = (
        c.CORES  #
        if args.cores == -1
        else args.cores
    )
    c.PARTITION = (
        c.PARTITION  #
        if args.partition == 'regular'
        else args.partition
    )
    c.SCHEDULER_FILE = (
        c.SCHEDULER_FILE  #
        if args.scheduler_file == 'None' or args.scheduler_file is None
        else args.scheduler_file
    )
    c.BASE_PATH = (
        c.BASE_PATH  #
        if args.base_path == 'None' or args.base_path is None
        else args.base_path
    )

    return args.game_name


"""
	We currently have so many logs in the root folders.
	We need to consolidate everything into a single file, and maybe format it as well
"""


def get_number_from_file_name(file_name: str, string_to_find: str) -> int:
    match = re.search(rf'{string_to_find}-(\d+)', file_name)

    if match:
        return int(match.group(1))
    return -1


def consolidate_data(
    experiment_name: str,
    log_list: list[str] | None = None,
    exclude_list: list[str] | None = None,
) -> None:
    if exclude_list is None:
        exclude_list = []

    # We will first throw an error if you add a folder to the logs that we are not aware of
    directory: pathlib.Path = pathlib.Path('log')
    unknown_directories: list[str] = []

    use_default_log_list: bool = log_list is None
    if use_default_log_list:
        log_list = c.LOGS.KNOWN_LOGS

        for folder in directory.iterdir():
            if folder.is_dir() and folder.name not in log_list:
                unknown_directories.append(folder.name)

        if len(unknown_directories) != 0:
            raise FileNotFoundError(
                'Known log directories are:',  #
                ','.join(log_list),
                '\nFound these unknown directories:',
                ','.join(unknown_directories),
            )

    for log_group_name in log_list:
        if log_group_name in exclude_list:
            continue

        log_group: pathlib.Path = directory.joinpath(log_group_name)
        # We will first check if it is already in a folder

        time_stamps: set = set()
        file_names: list[str] = []
        for file in log_group.iterdir():
            if file.is_file():
                file_names.append(file.name)
                time_stamps.add(file.name.split('-').pop().rsplit('.', 1)[0])

        for time_stamp in time_stamps:
            experiment_regex: re.Pattern = re.compile(rf'{re.escape(experiment_name)}.*?{re.escape(time_stamp)}')

            experiment_files: list[pathlib.Path] = []
            for experiment in file_names:
                if experiment_regex.match(experiment):
                    experiment_files.append(directory.joinpath(log_group_name, experiment))

            file_extension = file_names[0].split('.')[-1]
            consolidated_file_name: pathlib.Path = directory.joinpath(log_group_name, f'{experiment_name}-{time_stamp}.{file_extension}')

            if len(experiment_files) == 0:
                continue

            if log_group_name == c.LOGS.REPLAY:
                experiment_folder_name: str = f'{experiment_name}-{c.GAME_TIME}'
                log_group_path: str = os.path.join('log', log_group_name)
                experiment_folder_path: str = os.path.join(log_group_path, experiment_folder_name)
                os.makedirs(experiment_folder_path, exist_ok=True)
                for experiment_file in experiment_files:
                    experiment_file.rename(
                        os.path.join(
                            'log',
                            log_group_name,
                            experiment_folder_name,
                            experiment_file.name,
                        )
                    )

                if c.ZIP_FILES:
                    experiment_folder = os.path.join(log_group_path, experiment_folder_name)
                    shutil.make_archive(
                        experiment_folder,
                        'zip',
                        experiment_folder_path,
                    )

                    purge_directory(experiment_folder, True)
            else:
                """
					we will handle the points and the frame data differently.
				"""
                with consolidated_file_name.open(mode='w') as consolidated_file:
                    if log_group_name == c.LOGS.FRAME_DATA:
                        consolidated_file.write('[')

                    for experiment_file_index, experiment_file in enumerate(experiment_files):
                        if experiment_file.name == consolidated_file_name.name:
                            continue

                        if log_group_name == c.LOGS.FRAME_DATA:
                            consolidated_file.write(f'{{"{experiment_file.name}":')
                        elif log_group_name != c.LOGS.POINT:
                            consolidated_file.write(f'{experiment_file}\n')

                        with experiment_file.open(mode='r') as src_file:
                            if log_group_name == c.LOGS.POINT:
                                instance_number: int = get_number_from_file_name(experiment_file.name, 'instance')
                                round_number: int = get_number_from_file_name(experiment_file.name, 'round')
                                match_result: list[str] = src_file.readline().split(',')
                                # Remove the round count from the engine
                                match_result.pop(0)
                                match_result[-1] = match_result[-1].replace('\n', '')
                                winner: int = (match_result[0] > match_result[1]) - (match_result[1] > match_result[0])
                                consolidated_file.write(f'{instance_number},{round_number},{",".join(match_result)},{winner}')
                            else:
                                shutil.copyfileobj(src_file, consolidated_file)

                        if log_group_name == c.LOGS.FRAME_DATA:
                            if experiment_file_index == len(experiment_files) - 1:
                                consolidated_file.write('}\n')
                            else:
                                consolidated_file.write('},\n')
                        else:
                            consolidated_file.write('\n')

                        experiment_file.unlink(missing_ok=True)

                    if log_group_name == c.LOGS.FRAME_DATA:
                        consolidated_file.write(']')


def kill_process(process: asyncio.subprocess.Process) -> None:
    if process.returncode is None:
        print(f'Forcefully killing process tree for PID {process.pid}...')

        # Windows
        if os.name == 'nt':
            subprocess.run(
                ['taskkill', '/F', '/T', '/PID', str(process.pid)],
                capture_output=True,
                # check=True,
                check=False,
            )
        # Linux/Mac
        else:
            process.kill()


async def close_files(log_files: list[aiofiles.threadpool.text.AsyncTextIOWrapper]) -> None:
    for file in log_files:
        await file.close()


def kill_processes(
    simulators: list[asyncio.subprocess.Process],
    experiment_name: str,
    consolidate_input: bool = False,
) -> None:
    for simulator in simulators:
        kill_process(simulator)

    if consolidate_input:
        consolidate_data(experiment_name)


async def process_simulator_logs(
    subprocess: list[asyncio.subprocess.Process],
    log_file: aiofiles.threadpool.text.AsyncTextIOWrapper,
    process_id: int,
    ready_event: asyncio.Event,
) -> None:
    while True:
        line_bytes = await subprocess.stdout.readline()
        if not line_bytes:
            break

        line: str = line_bytes.decode().strip()
        await log_file.write(line + '\n')

        if 'Waiting to launch a game' in line:
            await log_file.flush()
            ready_event.set()

        if any(err in line for err in ['Exception', 'Error', 'SEVERE']):
            print(f'!!! CRITICAL ERROR ON PROCESS {process_id} !!!\n{line}')
            await log_file.flush()
            kill_process(subprocess)
            break


async def monitor_matches(
    simulators: list[asyncio.subprocess.Process],
    matches: list[asyncio.Task],
) -> None:
    last_heartbeat: float = time.time() + c.POLL_INTERVAL_SEC
    while True:
        active_simulators: np.ndarray = np.full(
            shape=len(simulators),
            fill_value=False,
            dtype=bool,
        )

        for index, (simulator, match) in enumerate(zip(simulators, matches, strict=True)):
            active_simulators[index] = simulator.returncode is None and not match.done()

        if not np.any(active_simulators):
            print('Simulation Completed Successfully (Maybe)')
            break

        if c.POLL_INTERVAL_SEC != 0 and time.time() - last_heartbeat >= c.POLL_INTERVAL_SEC:
            last_heartbeat: float = time.time()
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            line: str = ''
            for index, is_active in enumerate(active_simulators):
                line += f'PID: {simulators[index].pid} - {"ACTIVE" if is_active else "DEAD  "}'
            print(line)
            for match in matches:
                print(f'Match {"playing" if not match.done() else "finished"}')
                print(match._state)
            # print(f"\033[{len(active_simulators) + 2}F", end="", flush=True)
            # print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "\n")
            # line = ""
            # for index, is_active in enumerate(active_simulators):
            #     line += f"Port: {gateways[index].port} - {"ACTIVE" if is_active else "DEAD  "}\n"
            # print(line, end="")
            # print(f"\033[{len(active_simulators) + 2}F", end="", flush=True)

        await asyncio.sleep(c.POLL_INTERVAL_SEC)

    print('All executions are closed')
    for simulator in simulators:
        print(f'PID: {simulator.pid} - {simulator.returncode}')


async def stop_orchestration(
    simulators: list[asyncio.subprocess.Process],
    experiment_name: str,
    task_containers: list[asyncio.Task],
    log_files: list[aiofiles.threadpool.text.AsyncTextIOWrapper],
) -> None:
    kill_processes(simulators, experiment_name)
    await asyncio.gather(*task_containers, return_exceptions=True)
    await close_files(log_files)


# TODO: Will no longer support single usage. Can look into getting the capability back in future
async def orchestrate_matches(
    no_engines: int,
    task_containers: list[asyncio.Task],
    simulators: list[asyncio.subprocess.Process],
    simulator_ready_events: list[asyncio.Event],
    log_files: list[aiofiles.threadpool.text.AsyncTextIOWrapper],
    character_names: np.ndarray,
    motions: list[MotionEditor],
    agent_names: np.ndarray,
    experiment_name: str,
    deterministic: bool = False,
) -> None:
    matches: list[asyncio.Task] = []

    try:
        print('Waiting for all engines to be ready')
        await asyncio.wait_for(
            asyncio.gather(*(event.wait() for event in simulator_ready_events)),
            timeout=30.0,
        )
        print('All engines are ready')
    except asyncio.TimeoutError:
        print('One or more engines failed to start in time!')
        await stop_orchestration(
            simulators,
            experiment_name,
            task_containers,
            log_files,
        )

    for index in range(no_engines):
        port: int | None = f.get_port_number_from_engine_logs(experiment_name, simulators[index].pid)
        print(f'PID: {simulators[index].pid}, PORT: {port}')

        if port is None:
            raise RuntimeError('FAILED TO GET PORT NUMBER FROM FILE, ABORT ALL')

        gateway = Gateway(port=port)

        agent1 = None
        agent2 = None

        character_duo = character_names[index % 3, :]
        agent_duo = agent_names[index % 3, :]

        agent_1_name = agent_duo[0]
        agent_2_name = agent_duo[1]

        agent_1_motion = motions[c.CHARACTER_ORDER[character_duo[0]]]
        agent_2_motion = motions[c.CHARACTER_ORDER[character_duo[1]]]

        match agent_duo[0]:
            case c.AgentNames.KAT_KICK_AI:
                agent1 = KatKickAi(
                    use_kick=True,
                    interval=(0.5 if not deterministic else 0),
                    character_name=character_duo[0],
                    motion=agent_1_motion,
                    deterministic=deterministic,
                )
                gateway.register_ai(agent1.name(), agent1)
                agent_1_name = agent1.name()

        match agent_duo[1]:
            case c.AgentNames.KAT_KICK_AI:
                agent2 = KatKickAi(
                    use_kick=True,
                    interval=(0.5 if not deterministic else 0),
                    character_name=character_duo[1],
                    motion=agent_2_motion,
                    deterministic=deterministic,
                )
                gateway.register_ai(agent2.name(), agent2)
                agent_2_name = agent2.name()

        game_name = f'{experiment_name}-instance-{index}-{agent_1_name}-vs-{agent_2_name}'

        matches.append(
            asyncio.create_task(
                gateway.run_game(
                    [f'{game_name}<name>{character_duo[0]}', character_duo[1]],
                    [agent_1_name, agent_2_name],
                    c.NO_GAMES,
                )
            )
        )

    # Kill matches if games take too long to finish
    duration: float = c.GAME_DURATION_SEC * c.NO_GAMES * 1.5
    try:
        await asyncio.wait_for(
            monitor_matches(simulators, matches),
            timeout=duration,
        )
    except asyncio.TimeoutError:
        print(f'[CRITICAL] Experiment exceeded time limit: {duration} sec. Shutting down.')
        await stop_orchestration(
            simulators,
            experiment_name,
            task_containers,
            log_files,
        )

    c.end_time = time.perf_counter()
    await stop_orchestration(
        simulators,
        experiment_name,
        task_containers,
        log_files,
    )


# TODO: This will no longer support single usage... Could look into giving it back that functionality
async def start_simulators(
    no_engines: int,
    common_commands: np.ndarray,
    characters: np.ndarray,
    motions: list[MotionEditor],
    agent_names: np.ndarray,
    experiment_name: str,
    deterministic: bool = True,  # We aren't really going to use this in future... should think of redacting
    extra_commands: list[str] | np.ndarray | None = None,
    environment: str | None = None,
    environment_name: str | None = None,
) -> None:
    if '-' in experiment_name:
        raise ValueError('Please avoid using experiment names with -, it will mess up the data consolidator')

    is_extra_commands_empty = False
    if extra_commands is None:
        extra_commands = []
        is_extra_commands_empty = True

    simulators: list[asyncio.subprocess.Process] = []
    log_files: list[aiofiles.threadpool.text.AsyncTextIOWrapper] = []
    simulator_ready_events: list[asyncio.Event] = [asyncio.Event() for _ in range(no_engines)]

    task_containers: list[asyncio.Task] = []

    process_env = os.environ.copy()
    if environment is not None:
        process_env[environment_name] = environment

    for index in range(no_engines):
        proc = await asyncio.create_subprocess_exec(
            *common_commands,
            *(
                []  #
                if is_extra_commands_empty
                else extra_commands[index % 3, :].tolist()
            ),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=process_env,
        )
        simulators.append(proc)

        log_files.append(
            await aiofiles.open(
                # f'log/engines/{experiment_name}-instance-{gateway.port}-{c.GAME_TIME}.log',
                f'log/engines/{experiment_name}-pid-{proc.pid}-{c.GAME_TIME}.log',
                'w',
            )
        )

        task_containers.append(
            asyncio.create_task(
                process_simulator_logs(
                    proc,
                    log_files[index],
                    proc.pid,
                    simulator_ready_events[index],
                )
            )
        )

        print(f'Engine started (PID: {simulators[index].pid}.')

    await orchestrate_matches(
        no_engines,
        task_containers,
        simulators,
        simulator_ready_events,
        log_files,
        characters,
        motions,
        agent_names,
        experiment_name,
        deterministic=deterministic,
    )


# GPT Function, not important to know how to delete files in folder
def purge_directory(target_dir: str | pathlib.Path, remove_root: bool = False) -> None:
    root = pathlib.Path(target_dir)

    if not root.exists():
        print(f'Path {root} does not exist.')
        print(os.getcwd())
        return

    # rglob("*") finds everything recursively
    # We sort them by length descending to ensure we process
    # the deepest files/folders first (children before parents)
    for path in sorted(root.rglob('*'), key=lambda p: len(p.parts), reverse=True):
        if path.is_file() or path.is_symlink():
            path.unlink()
        elif path.is_dir():
            path.rmdir()

    if remove_root:
        root.rmdir()


def motion_cord_to_index(motion_coordinate: tuple[int, int]) -> int:
    return motion_coordinate[0] * c.MotionData.rows + motion_coordinate[1]


def motion_cord_to_index_bulk(motion_coordinates: np.ndarray) -> list[int]:
    return (motion_coordinates @ np.array([c.MotionData.rows, 1])).tolist()


def motion_index_to_cord(motion_index: int) -> tuple[int, int]:
    return divmod(motion_index, c.MotionData.rows)


def motion_indices_to_cords(motion_indices: np.ndarray) -> np.ndarray:
    return np.stack(np.divmod(motion_indices, c.MotionData.rows)).T


@contextmanager
def full_view() -> Iterator[None]:
    with pandas.option_context(
        'display.max_rows',
        None,
        'display.max_columns',
        None,
    ):
        yield


def read_match_results(file_name: str) -> pandas.DataFrame:
    return pandas.read_csv(
        file_name,
        names=[
            c.PointHeaderNames.INSTANCE,
            c.PointHeaderNames.ROUND,
            c.PointHeaderNames.HP_ONE,
            c.PointHeaderNames.HP_TWO,
            c.PointHeaderNames.DRAIN,
            c.PointHeaderNames.WINNER,
        ],
        dtype=c.PointHeaderNames.D_TYPE,
    )


def calculate_harmonic_mean(
    values: np.ndarray,
    normalization_value: float = 1,
    div_zero_slack: float = 1e-6,
) -> float:
    return values.shape[0] / (1 / ((values + div_zero_slack) / normalization_value)).sum()


def transform_win_rate_array(win_rates: np.ndarray, sigma: float = 0.20) -> np.ndarray:
    return np.exp(-(np.pow(0.5 - win_rates, 2)) / (2 * pow(sigma, 2)))


def transform_win_rate(win_rate: float, sigma: float = 0.20) -> np.ndarray:
    return math.exp(-(pow(0.5 - win_rate, 2)) / (2 * pow(sigma, 2)))


def get_port_number_from_engine_logs(experiment_name: str, pid: int) -> int | None:
    try:
        engine_logs_path = pathlib.Path(os.path.join('log', 'engines', f'{experiment_name}-pid-{pid}-{c.GAME_TIME}.log'))
        with open(engine_logs_path) as file:
            content: str = ''.join(list(islice(file, 10)))
            pattern: re.Pattern = re.compile(r'<PORT>:(\d+)')

            match = pattern.search(content)

            if match:
                return int(match.group(1))
    except FileNotFoundError:
        print(f'FILE NOT FOUND: {engine_logs_path}')
    except Exception as e:
        print(f'An error occured when trying to get port from {engine_logs_path}\n{e}')

    return None


def numpy_2d_to_tuple(numpy_array: np.ndarray) -> tuple:
    return tuple(map(tuple, numpy_array))


def get_current_time_str(delimiter: str = ':') -> str:
    return datetime.datetime.now().strftime(f'%H{delimiter}%M{delimiter}%S')


def read_results(res_name: str) -> None:
    with open(res_name, 'rb') as f:
        res: Result = dill.load(f)

    print(f'{"gen":>5} | {"n_eval":>7} | {"n_nds":>5} | {"eps":>12}')
    print('-' * 45)
    # Taken from output file
    print('time sec: 1366')

    for i, generation in enumerate(res.history):
        n_gen = i + 1
        n_eval = generation.evaluator.n_eval
        n_nds = len(generation.opt)
        print(f'{n_gen:>5} | {n_eval:>7} | {n_nds:>5} | {generation.opt.get("F").min():>12.6f}')

    print('non dominated solutions')
    population = res.opt

    genes: np.ndarray = population.get('X')
    fitnesses: np.ndarray = population.get('F')

    for gene, fitness in zip(genes, fitnesses, strict=True):
        print(f'Gene: [{", ".join(np.round(gene, 4).astype(str))}]')
        print(f'Fitness: {fitness}\n')

    print()

    for index, generation in enumerate(res.history):
        generation: Algorithm

        print(f'Generation: {index}\n')
        population = generation.pop

        genes: np.ndarray = population.get('X')
        fitnesses: np.ndarray = population.get('F')

        for gene, fitness in zip(genes, fitnesses, strict=True):
            print(f'Gene: [{", ".join(np.round(gene, 4).astype(str))}]')
            print(f'Fitness: {fitness}\n')

        print()


def append_time_uuid_experiment(experiment_name: str) -> str:
    experiment_suffix_uuid: str = uuid.uuid4().hex[:6]
    experiment_suffix_time: str = datetime.datetime.now().strftime('%H%M%S')

    return f'{experiment_name}_iter_{experiment_suffix_time}_{experiment_suffix_uuid}'


def resume_algorithm(plk_name: str | None, throw_error: bool = False) -> Result | None:
    if plk_name is None:
        return None

    plk_path: pathlib.Path = pathlib.Path(plk_name)

    if not plk_path.exists():
        if throw_error:
            raise FileNotFoundError(f'Failed to find file: {plk_path}')
        return None

    with open(plk_path, 'rb') as res_file:
        return dill.load(res_file)


def set_random_seeds(seed: int) -> None:
    np.random.seed(seed)
    random.seed(seed)
