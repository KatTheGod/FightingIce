import numpy as np

import constants as const
from genetic_algorithm import genetic_functions as gf
from genetic_algorithm import meta_mapper, meta_space
from genetic_algorithm.fighting_ice_problem import IndividualSettings, evaluate_individual

meta_subspace = meta_space.BASIC_STAND_A_B

motion_adjustments: list[tuple[str, str]] = meta_mapper.to_meta_subspace(meta_subspace.meta_subspace)
motion_coordinates: np.ndarray = gf.get_motion_coordinates(motion_adjustments)
numerical_mapped_motion_coordinates = gf.map_numerical_motion_coordinates(motion_adjustments)

evaluate_individual(
    x=gf.create_random_gene(meta_space_subset=meta_subspace),
    settings=IndividualSettings(
        meta_subspace=meta_subspace,
        motion_coordinates=motion_coordinates,
        mapped_numerical_motion_coordinates=numerical_mapped_motion_coordinates,
        no_matches=1,
        experiment_name="testing",
        engine_multiplier=1,
        game_duration_sec=const.GAME_DURATION_SEC,
        visual=False,
    ),
)
