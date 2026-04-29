import asyncio
import math
import os
import pathlib
import time
from datetime import datetime
from itertools import combinations
import json

import numpy as np
import pandas

import constants as c
import functions as f
import MotionClasses.MotionEditor as me
import MotionClasses.MotionHeaders as mh
import MotionClasses.MotionNames as mn
from GeneticAlgorithm.FrameData import parse_frame_data


# According to research, its just euclid distance between objects
def constraint_novelty_search(
    numerical_motions: np.ndarray,
    motion_coordinates: np.ndarray,
    mapped_numerical_motion_coordinates: np.ndarray,
    string_motions: np.ndarray | None,
    boolean_motions: np.ndarray | None,
) -> float:
    numerical_motions_slice = numerical_motions.copy()

    # We are going to make it such that we only care about the indices in question
    # The code is indexing the second column of the `motion_coordinates` array and storing it in the
    numerical_rows = mapped_numerical_motion_coordinates[:, 0]
    numerical_cols = mapped_numerical_motion_coordinates[:, 1]
    picked_numerical_differences = np.zeros_like(numerical_motions_slice, dtype=numerical_motions_slice.dtype)
    picked_numerical_differences[:, numerical_rows, numerical_cols] = numerical_motions_slice[:, numerical_rows, numerical_cols]

    num_zen_garnet_distance = np.linalg.norm(picked_numerical_differences[0] - picked_numerical_differences[1])
    num_zen_lud_distance = np.linalg.norm(picked_numerical_differences[0] - picked_numerical_differences[2])
    num_garnet_lud_distance = np.linalg.norm(picked_numerical_differences[1] - picked_numerical_differences[2])

    if string_motions is None:
        str_zen_garnet_distance = 0
        str_zen_lud_distance = 0
        str_garnet_lud_distance = 0
    else:
        str_zen_garnet_distance = np.linalg.norm((string_motions[0] != string_motions[1]).astype(int))
        str_zen_lud_distance = np.linalg.norm((string_motions[0] != string_motions[2]).astype(int))
        str_garnet_lud_distance = np.linalg.norm((string_motions[1] != string_motions[2]).astype(int))

    if boolean_motions is None:
        bool_zen_garnet_distance = 0
        bool_zen_lud_distance = 0
        bool_garnet_lud_distance = 0
    else:
        bool_zen_garnet_distance = np.linalg.norm((boolean_motions[0] != boolean_motions[1]).astype(int))
        bool_zen_lud_distance = np.linalg.norm((boolean_motions[0] != boolean_motions[2]).astype(int))
        bool_garnet_lud_distance = np.linalg.norm((boolean_motions[1] != boolean_motions[2]).astype(int))

    numerical_normalization: float = me.calculate_theoretical_max_uniqueness(f.numpy_2d_to_tuple(motion_coordinates))

    str_normalization: float = (
        1  #
        if string_motions is None
        else string_motions.shape[1] * string_motions.shape[2]
    )

    bool_normalization: float = (
        1  #
        if boolean_motions is None
        else boolean_motions.shape[1] * boolean_motions.shape[2]
    )

    return (
        f.calculate_harmonic_mean(
            np.array(
                [
                    num_zen_garnet_distance,
                    num_zen_lud_distance,
                    num_garnet_lud_distance,
                ]
            ),
            numerical_normalization,
        )
        + f.calculate_harmonic_mean(
            np.array(
                [
                    str_zen_garnet_distance,
                    str_zen_lud_distance,
                    str_garnet_lud_distance,
                ]
            ),
            str_normalization,
        )
        + f.calculate_harmonic_mean(
            np.array(
                [
                    bool_zen_garnet_distance,
                    bool_zen_lud_distance,
                    bool_garnet_lud_distance,
                ]
            ),
            bool_normalization,
        )
    ) / 3


async def wait_for_point_file(experiment_name: str, timeout: int = 10) -> pathlib.Path | None:
    if c.BASE_PATH is not None:
        point_path: pathlib.Path = pathlib.Path(os.path.join(c.BASE_PATH, 'log', 'point'))
    else:
        point_path: pathlib.Path = pathlib.Path(os.path.join('log', 'point'))

    start_poll = time.time()
    time_str = datetime.now().strftime('%H:%M:%S')

    print(f'looking for {experiment_name} at {time_str}')
    while time.time() - start_poll < timeout:
        point_csv: pathlib.Path | None = next(point_path.glob(f'{experiment_name}*.csv'), None)
        if point_csv is not None:
            return point_csv

        await asyncio.sleep(1)

    time_str = datetime.now().strftime('%H:%M:%S')
    print(f'Failed at {time_str}')
    return None


"""
* TODO: Think about scaling at a later stage
* For now, we will have 3 engines to handle the different matches against the MCTS agents
"""


async def orchestrate_matches(
    mutated_motions: list[pandas.DataFrame],
    no_matches: int,
    experiment_name: str,
    experiment_suffix: str,
    engine_multiplier: int,
    game_duration_sec: int = 60,
    visual: bool = False,
) -> float:
    c.NO_GAMES = no_matches
    c.POLL_INTERVAL_SEC = 0
    c.GAME_DURATION_SEC = game_duration_sec

    experiment_name = f'{experiment_name}_iter_{experiment_suffix}'

    custom_motion_paths: list[str] = [
        os.path.join(
            c.CUSTOM_MOTION_PATH,
            experiment_name,
            f'{character_name.lower()}.csv',
        )  #
        for character_name in c.CHARACTER_ORDER.keys()
    ]

    for path, mutated_motion in zip(custom_motion_paths, mutated_motions, strict=True):
        me.save_custom_motion(
            motion=mutated_motion,
            path=path,
        )

    argument_for_custom_motions: np.ndarray = np.full(shape=(3, 6), dtype=object, fill_value='')
    character_order_combinations: list[tuple[int, int]] = list(combinations([0, 1, 2], 2))
    for index, combination in enumerate(character_order_combinations):
        argument_for_custom_motions[index, :] = np.array(
            [
                '--config-path',
                '2',
                c.CHARACTER_ORDER_REVERSE[combination[0]],
                custom_motion_paths[combination[0]],
                c.CHARACTER_ORDER_REVERSE[combination[1]],
                custom_motion_paths[combination[1]],
            ]
        )

    common_commands = [
        'java',
        '-cp',
        os.pathsep.join(['dare.jar', '.']),
        'Main',
        '--limithp',
        str(c.PLAYER_HP),
        str(c.PLAYER_HP),
        '-df',
        '-r',
        '1',
        '-f',
        str(c.GAME_DURATION_SEC * 60),
        '--time-stamp',
        c.GAME_TIME,
        *(['--headless-mode'] if not visual else []),
        '--input-sync',
        *(['--lightweight-mode'] if not visual else []),
        '--pyftg-mode',
        '--non-delay',
        '2',
    ]

    os.makedirs(os.path.join('log', 'engines'), exist_ok=True)

    characters = [
        character_name  #
        for combination in character_order_combinations
        for character_name in [c.CHARACTER_ORDER_REVERSE[combination[0]], c.CHARACTER_ORDER_REVERSE[combination[1]]]  #
    ]
    characters = np.array(characters).reshape(3, -1)

    agents = np.full(shape=(3, 2), fill_value=c.AgentNames.MCTS_AGENT)

    await f.start_simulators(
        engine_multiplier * 3,
        common_commands,
        characters,
        mutated_motions,
        agents,
        experiment_name,
        # deterministic=deterministic, really dont care
        extra_commands=argument_for_custom_motions,
    )

    f.consolidate_data(experiment_name, log_list=[c.LOGS.POINT, c.LOGS.FRAME_DATA])

    # To get the game results, we are going to get the HP differences in each game.
    # The first implementation of this is going to be rather crude.
    # We will assume that:
    #   x % 3 == 0 -> zen vd garnet
    #   x % 3 == 1 -> zen vd lud
    #   x % 3 == 2 -> garnet vd lud

    point_csv: pathlib.Path | None = await wait_for_point_file(experiment_name)
    if point_csv is None:
        raise FileExistsError(f'Glob failed to fined experiment | {point_csv} | in folder')
    if not point_csv.exists():
        raise FileExistsError(f"Point file | {point_csv} | doesn't exist folder")

    point_df: pandas.DataFrame = f.read_match_results(point_csv)
    pairing_index = point_df[[c.PointHeaderNames.INSTANCE]].to_numpy()

    hp_diff_zen_garnet = point_df[pairing_index % 3 == 0][[c.PointHeaderNames.HP_ONE, c.PointHeaderNames.HP_TWO]].to_numpy().astype(np.int16)
    hp_diff_zen_lud = point_df[pairing_index % 3 == 1][[c.PointHeaderNames.HP_ONE, c.PointHeaderNames.HP_TWO]].to_numpy().astype(np.int16)
    hp_diff_garnet_lud = point_df[pairing_index % 3 == 2][[c.PointHeaderNames.HP_ONE, c.PointHeaderNames.HP_TWO]].to_numpy().astype(np.int16)

    # Think about this more, if we have z-g and z-l, do we need to add g-z again?
    zen_win_rate = (
        (hp_diff_zen_garnet[:, 0] > hp_diff_zen_garnet[:, 1]).sum()  #
        + (hp_diff_zen_lud[:, 0] > hp_diff_zen_lud[:, 1]).sum()
    ) / (no_matches * engine_multiplier * 2)
    garnet_win_rate = (
        (hp_diff_zen_garnet[:, 0] < hp_diff_zen_garnet[:, 1]).sum()  #
        + (hp_diff_garnet_lud[:, 0] > hp_diff_garnet_lud[:, 1]).sum()
    ) / (no_matches * engine_multiplier * 2)
    lud_win_rate = (
        (hp_diff_zen_lud[:, 0] < hp_diff_zen_lud[:, 1]).sum()  #
        + (hp_diff_garnet_lud[:, 0] < hp_diff_garnet_lud[:, 1]).sum()
    ) / (no_matches * engine_multiplier * 2)

    win_rates: np.ndarray = np.array(
        [
            zen_win_rate,
            garnet_win_rate,
            lud_win_rate,
        ]
    )

    win_rates: np.ndarray = f.transform_win_rate_array(win_rates)

    return min(
        f.calculate_harmonic_mean(values=win_rates),
        1,
    )


def gene_to_motions(gene: np.ndarray, motion_coordinates: np.ndarray) -> list[pandas.DataFrame]:
    mutated_motions = [motion.copy() for motion in me.DEFAULT_MOTION_LIST]

    adjustments = gene.reshape(3, -1).copy()

    # TODO: Right now, we are going to use a slow loop version, if you want this to work, we need to ensure that the dtypes we are adjusting are all the same.
    # I.E., numbers, strings, and booleans must be treated differently.

    for index, character_adjustment in enumerate(adjustments):
        rows = motion_coordinates[:, 0]
        cols = motion_coordinates[:, 1]
        for row, col, value in zip(rows, cols, character_adjustment, strict=True):
            mutated_motions[index].iloc[row, col] = value

    return mutated_motions


def get_motion_coordinates(motion_adjustments: list[tuple[str, str]]) -> np.ndarray:
    return np.array(
        [
            [
                mn.MotionNames.MOTION_NAMES.index(motion),
                mh.MotionHeaders.HEADERS.index(header),
            ]
            for motion, header in motion_adjustments
        ]
    )


def map_numerical_motion_coordinates(motion_adjustments: list[tuple[str, str]]) -> np.ndarray:
    # Add a +1 to accommodate for the motion_name being in the header...
    # Solution is kinda wacky, would like to rethink in the future
    return np.array(
        [
            [
                mn.MotionNames.MAPPER[motion],
                mh.MotionHeaders.MAPPER[mh.MotionHeaders.HEADERS.index(header)] + 1,
            ]
            for motion, header in motion_adjustments
        ]
    )


def generate_random_gene(motion_adjustments: list[tuple[str, str]]) -> np.ndarray:
    random_generator: np.random.Generator = np.random.default_rng(seed=1)

    header_limits_container = []
    for _, control_header in motion_adjustments:
        header_limits = mh.MotionHeaders.HEADER_LIMITS[control_header]
        header_limits_container.append(
            random_generator.integers(
                low=header_limits['min'],
                high=header_limits['max'] + 1,
                size=3,
            )
        )

    return np.stack(header_limits_container).T.flatten()


# TODO, can be vectorized and sped up, but really, not the slow point in your code
# Calculated at the POV of player 1
def calculate_win_probabilities(
    data_frame_file_name: str,
    energy_weight: float = 0.5,
    frame_window: int = 60,
    projected_hp_weight: float = 0.5,
) -> list[np.ndarray]:
    full_file_path: pathlib.Path = pathlib.Path(
        os.path.join(
            'log',
            c.LOGS.FRAME_DATA,
            data_frame_file_name,
        )
    )

    if not full_file_path.exists():
        raise FileNotFoundError(f"File: {str(full_file_path)} doesn't exist")

    frame_data_json: list[dict[str, any]]
    with open(str(full_file_path)) as file:
        frame_data_json = json.load(file)

    row_count: int = 1
    if isinstance(frame_data_json, list):
        row_count = len(frame_data_json)

    collected_win_probabilities: list[np.ndarray] = []

    for row in range(row_count):
        if row_count == 1:
            frame_data, max_frame = parse_frame_data(frame_data_json)
            win_probabilities = np.zeros(dtype=np.float64, shape=(max_frame))
        else:
            key_name: str = list(frame_data_json[row].keys())[0]
            frame_data, max_frame = parse_frame_data(frame_data_json[row][key_name])
            win_probabilities = np.zeros(dtype=np.float64, shape=(max_frame))

        for index, frame in enumerate(frame_data):
            p1_hp, p2_hp = frame.hitPoints
            p1_energy, p2_energy = frame.energy

            if p1_hp <= 0 and p2_hp <= 0 or index == 0:
                win_probabilities[index] = 0.5
                continue
            elif p1_hp <= 0:
                win_probabilities[index] = 0
                continue
            elif p2_hp <= 0:
                win_probabilities[index] = 1
                continue

            p1_effective_hp = p1_hp + (p1_energy * energy_weight)
            p2_effective_hp = p2_hp + (p2_energy * energy_weight)

            past_frame = frame_data[max(0, index - frame_window)]

            p1_hp_lost = past_frame.hitPoints[0] - p1_hp
            p2_hp_lost = past_frame.hitPoints[1] - p2_hp

            p1_projected_hp = p1_effective_hp - (p1_hp_lost * projected_hp_weight)
            p2_projected_hp = p2_effective_hp - (p2_hp_lost * projected_hp_weight)

            p1_projected_hp = p1_projected_hp / c.PLAYER_HP
            p2_projected_hp = p2_projected_hp / c.PLAYER_HP

            total_projected = p1_projected_hp + p2_projected_hp
            win_probabilities[index] = p1_projected_hp / total_projected

        collected_win_probabilities.append(win_probabilities)

    return collected_win_probabilities


# We are going to function under the assumption that the data has already been split
def calculate_entropy_score(
    win_probabilities_list: list[np.ndarray],
    frame_window: int = 60,
    epsilon: float = 1e-9,
    gamma_scale: float = 0.25,
) -> float:
    total_costs = np.zeros(shape=len(win_probabilities_list), dtype=np.float64)

    for match_index, win_probabilities in enumerate(win_probabilities_list):
        if win_probabilities.shape[0] <= frame_window:
            total_costs[match_index] = 1
            continue

        # TODO: We can speed this up very easily
        total_frames = win_probabilities.shape[0]
        time_step_size = 1.0 / total_frames

        total_cost = 0.0

        for frame_index in range(frame_window, total_frames):
            current_win_probability = win_probabilities[frame_index]
            previous_win_probability = win_probabilities[frame_index - 1]

            # Done just to enure we never pass o to log for errors
            sigma_t = (((current_win_probability - previous_win_probability) ** 2) / time_step_size) + epsilon

            # 4. Integrate (multiply by dt and add to the running total)
            total_cost += (sigma_t - math.log(sigma_t) - 1) * time_step_size

        normalization: float = (epsilon - math.log(epsilon) - 1) * (total_frames - frame_window) * time_step_size
        total_costs[match_index] = max(0, min(total_cost / normalization, 1))

    # TODO: Can look into using harmonic mean here or sum
    entropy_score = np.average(total_costs)

    return pow(entropy_score, gamma_scale)


def calculate_excitement(experiment_name: str, frame_window: int = 300) -> float:
    frame_data_path: pathlib.Path = pathlib.Path(os.path.join('log', c.LOGS.FRAME_DATA))
    frame_data_file: pathlib.Path | None = next(frame_data_path.glob(f'*{experiment_name}*.json'), None)

    if frame_data_file is None or not frame_data_file.exists():
        raise FileNotFoundError(f'cant find the consolidated point file: *{experiment_name}*.json')

    win_probabilities = calculate_win_probabilities(frame_data_file.name, frame_window=frame_window)
    overall_excitement: float = calculate_entropy_score(win_probabilities, frame_window=frame_window)

    return 1 - overall_excitement
