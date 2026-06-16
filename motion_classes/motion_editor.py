import os
import pathlib

import numpy as np
import pandas as pd

import constants as c
from motion_classes.motion_headers import MotionHeaders
from motion_classes.motion_headers import MotionHeadersEnum as headers
from motion_classes.motion_names import MotionNamesEnum


def read_motion_file(motion_path: str) -> pd.DataFrame:
    return pd.read_csv(
        filepath_or_buffer=motion_path,
        index_col=headers.MOTION_NAME,
        true_values=["TRUE"],
        false_values=["FALSE"],
        dtype=MotionHeaders.D_TYPE,
    )


def get_motion_difference(motion_original: pd.DataFrame, motion_custom: pd.DataFrame) -> pd.DataFrame:
    return motion_original.compare(
        motion_custom,
        keep_equal=True,
        keep_shape=True,
    )


def get_motion_difference_path(motion_original_path: str, motion_custom_path: str) -> pd.DataFrame:
    motion_original = read_motion_file(motion_original_path)
    motion_custom = read_motion_file(motion_custom_path)

    return get_motion_difference(motion_original, motion_custom)


def get_character_default_motion_path(character_name: str) -> str:
    return os.path.join(
        c.DEFAULT_MOTIONS_PATH,
        character_name,
        "Motion.csv",
    )


def get_motion_diffs(character_name: str, motions: list[pd.DataFrame]) -> pd.DataFrame | None:
    if len(motions) == 0:
        return None

    default_motion = read_motion_file(get_character_default_motion_path(character_name))
    motion_diffs = pd.concat(
        [get_motion_difference(default_motion, motion) for motion in motions],
        keys=range(len(motions)),
        names=[c.PointHeaderNames.SIMULATION_NUMBER, headers.MOTION_NAME],
    )

    other = motion_diffs.xs("other", level=1, axis=1)
    selves = motion_diffs.xs("self", level=1, axis=1)

    numerical_diffs = other.select_dtypes(include="number") - selves.select_dtypes(include="number")
    # print(numerical_diffs)
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    # print(numerical_diffs)
    clean_numerical_diffs = numerical_diffs.loc[:, (numerical_diffs != 0).any()]

    # We will think of these later to be honest.
    # string_diffs = other.select_dtypes(include='str') + ' | ' + selves.select_dtypes(include='str')
    # clean_string_diffs =
    # bool_diffs = other.select_dtypes(include='bool').astype(int) - selves.select_dtypes(include='bool').astype(int)

    return clean_numerical_diffs


def get_non_0_motion_name_in_diff(motion_diff: pd.DataFrame, header: str) -> str:
    mask = motion_diff[header] != 0
    return motion_diff[mask].index.get_level_values(1).unique().tolist().pop()


def modify_motion(
    original_motion: pd.DataFrame,
    motion: pd.DataFrame,
    percentage: float,
    headers_subset: list[str],
    motion_names_subset: list[str] | None = None,
) -> None:
    selected_motions_list = (
        list(MotionNamesEnum)  #
        if motion_names_subset is None
        else motion_names_subset
    )

    percentage = max(percentage, 0)

    motion.loc[selected_motions_list, headers_subset] = (
        (
            original_motion.loc[  #
                selected_motions_list,
                headers_subset,
            ]
            * percentage
        )
        .round()
        .astype("int16")
    )


def save_custom_motion(
    motion: pd.DataFrame,
    path: str,
) -> None:
    motion_custom_copy = motion.copy()

    motion_custom_copy[headers.ATTACK_DOWN_PROP] = motion_custom_copy[headers.ATTACK_DOWN_PROP].map({True: "TRUE", False: "FALSE"})
    motion_custom_copy[headers.CONTROL] = motion_custom_copy[headers.CONTROL].map({True: "TRUE", False: "FALSE"})
    motion_custom_copy[headers.LANDING_FLAG] = motion_custom_copy[headers.LANDING_FLAG].map({True: "TRUE", False: "FALSE"})

    pathlib.Path(path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    motion_custom_copy.to_csv(path)


DEFAULT_ZEN_MOTION: pd.DataFrame = read_motion_file(
    os.path.join(
        c.DEFAULT_MOTIONS_PATH,
        c.CHARACTERS.ZEN,
        c.MOTIONS_FILE_NAME,
    ),
)

DEFAULT_GARNET_MOTION: pd.DataFrame = read_motion_file(
    os.path.join(
        c.DEFAULT_MOTIONS_PATH,
        c.CHARACTERS.GARNET,
        c.MOTIONS_FILE_NAME,
    ),
)

DEFAULT_LUD_MOTION: pd.DataFrame = read_motion_file(
    os.path.join(
        c.DEFAULT_MOTIONS_PATH,
        c.CHARACTERS.LUD,
        c.MOTIONS_FILE_NAME,
    ),
)

# If you ever change the order here, you might be killing other code...
DEFAULT_MOTION_LIST: list[pd.DataFrame] = [
    DEFAULT_ZEN_MOTION,
    DEFAULT_GARNET_MOTION,
    DEFAULT_LUD_MOTION,
]

NUMERICAL_SHAPE = DEFAULT_ZEN_MOTION.select_dtypes("number").shape

MAX_FRAME_NUMBERS: pd.Series = pd.Series(
    np.vstack([motion.loc[:, headers.FRAME_NUMBER].to_numpy() for motion in DEFAULT_MOTION_LIST]).max(axis=0),
    index=DEFAULT_ZEN_MOTION.index,
)


class MotionEditor:
    def __init__(
        self,
        character_name: str,
        custom_motion_path: str | None = None,
    ) -> None:
        self.character_name: str = character_name
        self.custom_motion_path = custom_motion_path

        default_motion_file_path: str = get_character_default_motion_path(character_name)
        self.motion_default: pd.DataFrame = read_motion_file(default_motion_file_path)

        self.motion_custom: pd.DataFrame = (
            read_motion_file(custom_motion_path)  #
            if custom_motion_path is not None and os.path.exists(custom_motion_path)
            else read_motion_file(default_motion_file_path)
        )

    def save_custom_motion(self, path: str | None = None) -> None:
        determined_path = (
            path  #
            if path is not None
            else self.custom_motion_path
        )

        save_custom_motion(motion=self.motion_custom, path=determined_path)
