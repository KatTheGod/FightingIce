import itertools
from enum import StrEnum

from MotionClasses.MotionHeaders import MotionHeadersEnum
from MotionClasses.MotionNames import MotionNamesEnum

"""
    This will hold indices for the meta space subset any experiment uses.
    This will be something that is only appended on and not redacted in any sense
    This is such that we can track even OLDER experiments
"""


class MapperType(StrEnum):
    ATTACK_HIT_BOX_WIDTH: str = 'ATTACK_HIT_BOX_WIDTH'
    ATTACK_HIT_BOX_HEIGHT: str = 'ATTACK_HIT_BOX_HEIGHT'


MAPPER_TYPE_TO_HEADER: dict[str, MotionHeadersEnum] = {
    MapperType.ATTACK_HIT_BOX_WIDTH: MotionHeadersEnum.HIT_BOX_WIDTH,
    MapperType.ATTACK_HIT_BOX_HEIGHT: MotionHeadersEnum.HIT_BOX_HEIGHT,
}


MAPPER_TYPE_TRANSLATIONS: dict[str, list[MotionHeadersEnum]] = {
    MapperType.ATTACK_HIT_BOX_WIDTH: [
        MotionHeadersEnum.ATTACK_HIT_AREA_LEFT,
        MotionHeadersEnum.ATTACK_HIT_AREA_RIGHT,
    ],
    MapperType.ATTACK_HIT_BOX_HEIGHT: [
        MotionHeadersEnum.ATTACK_HIT_AREA_UP,
        MotionHeadersEnum.ATTACK_HIT_AREA_DOWN,
    ],
}

MAPPER_TYPE_TRANSLATED_HEADERS: list[MotionHeadersEnum] = list(itertools.chain(MAPPER_TYPE_TRANSLATIONS.values()))

MAPPER_TYPE_TRANSLATIONS_REVERSE: dict[MotionHeadersEnum, MotionHeadersEnum] = {}
MAPPER_TYPE_TRANSLATIONS_PAIRS: dict[MotionHeadersEnum, list[MotionHeadersEnum]] = {}
for mapped_header, translated_headers in MAPPER_TYPE_TRANSLATIONS.items():
    for translated_header in translated_headers:
        MAPPER_TYPE_TRANSLATIONS_REVERSE[translated_header] = MAPPER_TYPE_TO_HEADER[mapped_header]

        MAPPER_TYPE_TRANSLATIONS_PAIRS[translated_header] = translated_headers.copy()
        MAPPER_TYPE_TRANSLATIONS_PAIRS[translated_header].remove(translated_header)


class MetaMapper:
    def __init__(self, mapper_types: list[MapperType]) -> None:
        self.mapper_types = mapper_types


def to_meta_subspace(meta_subspace: list[tuple[MotionNamesEnum, MotionHeadersEnum]]) -> list[tuple[MotionNamesEnum, MotionHeadersEnum]]:
    new_meta_subspace: list[tuple[MotionNamesEnum, MotionHeadersEnum]] = []
    known_mapper_types: list[MapperType] = list(MapperType)
    for adjustment in meta_subspace:
        adjustment_motion: MotionNamesEnum = adjustment[0]
        adjustment_header: MotionNamesEnum = adjustment[1]

        if adjustment_header.value in known_mapper_types:
            new_meta_subspace.extend(
                [
                    (adjustment_motion, translated_header)  #
                    for translated_header in MAPPER_TYPE_TRANSLATIONS[adjustment_header.value]
                ]
            )
        else:
            new_meta_subspace.append(adjustment)

    # Validate solution
    unmapped_headers = set({mapper_type.value for mapper_type in MapperType})
    for adjustment in new_meta_subspace:
        if adjustment[1] in unmapped_headers:
            raise RuntimeError(f'Incomplete Code.\nMapper did not fully map all: {adjustment[1].value} should be mapped!')

    return new_meta_subspace


def from_meta_space(
    new_meta_subspace: list[tuple[MotionNamesEnum, MotionHeadersEnum]],
    mapper_types: list[MapperType],
) -> list[tuple[MotionNamesEnum, MotionHeadersEnum]]:
    """
    This is the one thats going to be a but more complicated with many more potential errors.
    We are going to find the pairs, then validate that all pairs are found
        otherwise we throw an error
    Then, we are going to replace those pairs with the
    """

    meta_subspace: list[tuple[MotionNamesEnum, MotionHeadersEnum]] = []
    seen_indices: list[int] = []
    for index, adjustment in enumerate(new_meta_subspace):
        if index in seen_indices:
            continue

        adjustment_value: MotionHeadersEnum = adjustment[0]
        adjustment_header: MotionHeadersEnum = adjustment[1]

        if adjustment_header in mapper_types:
            adjustment_header_pairs: list[MotionHeadersEnum] = MAPPER_TYPE_TRANSLATIONS_PAIRS[adjustment_header]
            seen_indices.append(index)
            meta_subspace.append(MAPPER_TYPE_TRANSLATIONS_REVERSE[adjustment_header])

            for adjustment_header_pair in adjustment_header_pairs:
                correlated_adjustment: tuple[MotionNamesEnum, MotionHeadersEnum] = (
                    adjustment_value,
                    adjustment_header_pair,
                )

                try:
                    seen_indices.append(new_meta_subspace.index(correlated_adjustment))
                except ValueError as error:
                    raise RuntimeError(f'correlated adjustment: {correlated_adjustment} is not in meta space: {new_meta_subspace}') from error

    return meta_subspace
