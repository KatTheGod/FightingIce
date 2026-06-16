from enum import Enum
from typing import TypedDict

import numpy as np

import constants as c


class MotionHeadersEnum(Enum):
    MOTION_NAME: str = 'motionName'
    FRAME_NUMBER: str = 'frameNumber'
    SPEED_X: str = 'speedX'
    SPEED_Y: str = 'speedY'
    HIT_AREA_LEFT: str = 'hitAreaLeft'
    HIT_AREA_RIGHT: str = 'hitAreaRight'
    HIT_AREA_UP: str = 'hitAreaUp'
    HIT_AREA_DOWN: str = 'hitAreaDown'
    STATE: str = 'state'
    ATTACK_HIT_AREA_LEFT: str = 'attack.hitAreaLeft'
    ATTACK_HIT_AREA_RIGHT: str = 'attack.hitAreaRight'
    ATTACK_HIT_AREA_UP: str = 'attack.hitAreaUp'
    ATTACK_HIT_AREA_DOWN: str = 'attack.hitAreaDown'
    ATTACK_SPEED_X: str = 'attack.speedX'
    ATTACK_SPEED_Y: str = 'attack.speedY'
    ATTACK_START_UP: str = 'attack.StartUp'
    ATTACK_ACTIVE: str = 'attack.Active'
    ATTACK_HIT_DAMAGE: str = 'attack.HitDamage'
    ATTACK_GUARD_DAMAGE: str = 'attack.GuardDamage'
    ATTACK_START_ADD_ENERGY: str = 'attack.StartAddEnergy'
    ATTACK_HIT_ADD_ENERGY: str = 'attack.HitAddEnergy'
    ATTACK_GUARD_ADD_ENERGY: str = 'attack.GuardAddEnergy'
    ATTACK_GIVE_ENERGY: str = 'attack.GiveEnergy'
    ATTACK_IMPACT_X: str = 'attack.ImpactX'
    ATTACK_IMPACT_Y: str = 'attack.ImpactY'
    ATTACK_GIVE_GUARD_RECOV: str = 'attack.GiveGuardRecov'
    ATTACK_ATTACK_TYPE: str = 'attack.AttackType'
    ATTACK_DOWN_PROP: str = 'attack.DownProp'
    CANCEL_ABLE_FRAME: str = 'cancelAbleFrame'
    CANCEL_ABLE_MOTION_LEVEL: str = 'cancelAbleMotionLevel'
    MOTION_LEVEL: str = 'motionLevel'
    CONTROL: str = 'control'
    LANDING_FLAG: str = 'landingFlag'
    IMAGE: str = 'Image'

    # NOTE: From here, these are going to be motion names that need to be mapped
    HIT_BOX_WIDTH: str = 'hitBoxWidth'
    HIT_BOX_HEIGHT: str = 'hitBoxHeight'


from MotionClasses.MotionNames import (
    MotionNamesEnum,
)


class RangeLimit(TypedDict):
    motions_names: list[MotionNamesEnum]
    min: int
    max: int


class MotionHeaders:
    MOTION_NAME: str = MotionHeadersEnum.MOTION_NAME.value
    FRAME_NUMBER: str = MotionHeadersEnum.FRAME_NUMBER.value
    SPEED_X: str = MotionHeadersEnum.SPEED_X.value
    SPEED_Y: str = MotionHeadersEnum.SPEED_Y.value
    HIT_AREA_LEFT: str = MotionHeadersEnum.HIT_AREA_LEFT.value
    HIT_AREA_RIGHT: str = MotionHeadersEnum.HIT_AREA_RIGHT.value
    HIT_AREA_UP: str = MotionHeadersEnum.HIT_AREA_UP.value
    HIT_AREA_DOWN: str = MotionHeadersEnum.HIT_AREA_DOWN.value
    STATE: str = MotionHeadersEnum.STATE.value
    ATTACK_HIT_AREA_LEFT: str = MotionHeadersEnum.ATTACK_HIT_AREA_LEFT.value
    ATTACK_HIT_AREA_RIGHT: str = MotionHeadersEnum.ATTACK_HIT_AREA_RIGHT.value
    ATTACK_HIT_AREA_UP: str = MotionHeadersEnum.ATTACK_HIT_AREA_UP.value
    ATTACK_HIT_AREA_DOWN: str = MotionHeadersEnum.ATTACK_HIT_AREA_DOWN.value
    ATTACK_SPEED_X: str = MotionHeadersEnum.ATTACK_SPEED_X.value
    ATTACK_SPEED_Y: str = MotionHeadersEnum.ATTACK_SPEED_Y.value
    ATTACK_START_UP: str = MotionHeadersEnum.ATTACK_START_UP.value
    ATTACK_ACTIVE: str = MotionHeadersEnum.ATTACK_ACTIVE.value
    ATTACK_HIT_DAMAGE: str = MotionHeadersEnum.ATTACK_HIT_DAMAGE.value
    ATTACK_GUARD_DAMAGE: str = MotionHeadersEnum.ATTACK_GUARD_DAMAGE.value
    ATTACK_START_ADD_ENERGY: str = MotionHeadersEnum.ATTACK_START_ADD_ENERGY.value
    ATTACK_HIT_ADD_ENERGY: str = MotionHeadersEnum.ATTACK_HIT_ADD_ENERGY.value
    ATTACK_GUARD_ADD_ENERGY: str = MotionHeadersEnum.ATTACK_GUARD_ADD_ENERGY.value
    ATTACK_GIVE_ENERGY: str = MotionHeadersEnum.ATTACK_GIVE_ENERGY.value
    ATTACK_IMPACT_X: str = MotionHeadersEnum.ATTACK_IMPACT_X.value
    ATTACK_IMPACT_Y: str = MotionHeadersEnum.ATTACK_IMPACT_Y.value
    ATTACK_GIVE_GUARD_RECOV: str = MotionHeadersEnum.ATTACK_GIVE_GUARD_RECOV.value
    ATTACK_ATTACK_TYPE: str = MotionHeadersEnum.ATTACK_ATTACK_TYPE.value
    ATTACK_DOWN_PROP: str = MotionHeadersEnum.ATTACK_DOWN_PROP.value
    CANCEL_ABLE_FRAME: str = MotionHeadersEnum.CANCEL_ABLE_FRAME.value
    CANCEL_ABLE_MOTION_LEVEL: str = MotionHeadersEnum.CANCEL_ABLE_MOTION_LEVEL.value
    MOTION_LEVEL: str = MotionHeadersEnum.MOTION_LEVEL.value
    CONTROL: str = MotionHeadersEnum.CONTROL.value
    LANDING_FLAG: str = MotionHeadersEnum.LANDING_FLAG.value
    IMAGE: str = MotionHeadersEnum.IMAGE.value

    HEADERS: list[str] = [
        # We are doing this because motion_name is the index, might adjust in the future
        # MOTION_NAME,
        FRAME_NUMBER,
        SPEED_X,
        SPEED_Y,
        HIT_AREA_LEFT,
        HIT_AREA_RIGHT,
        HIT_AREA_UP,
        HIT_AREA_DOWN,
        STATE,
        ATTACK_HIT_AREA_LEFT,
        ATTACK_HIT_AREA_RIGHT,
        ATTACK_HIT_AREA_UP,
        ATTACK_HIT_AREA_DOWN,
        ATTACK_SPEED_X,
        ATTACK_SPEED_Y,
        ATTACK_START_UP,
        ATTACK_ACTIVE,
        ATTACK_HIT_DAMAGE,
        ATTACK_GUARD_DAMAGE,
        ATTACK_START_ADD_ENERGY,
        ATTACK_HIT_ADD_ENERGY,
        ATTACK_GUARD_ADD_ENERGY,
        ATTACK_GIVE_ENERGY,
        ATTACK_IMPACT_X,
        ATTACK_IMPACT_Y,
        ATTACK_GIVE_GUARD_RECOV,
        ATTACK_ATTACK_TYPE,
        ATTACK_DOWN_PROP,
        CANCEL_ABLE_FRAME,
        CANCEL_ABLE_MOTION_LEVEL,
        MOTION_LEVEL,
        CONTROL,
        LANDING_FLAG,
        IMAGE,
    ]

    D_TYPE = {
        MOTION_NAME: 'string',
        FRAME_NUMBER: 'int16',
        SPEED_X: 'int16',
        SPEED_Y: 'int16',
        HIT_AREA_LEFT: 'int16',
        HIT_AREA_RIGHT: 'int16',
        HIT_AREA_UP: 'int16',
        HIT_AREA_DOWN: 'int16',
        STATE: 'string',
        ATTACK_HIT_AREA_LEFT: 'int16',
        ATTACK_HIT_AREA_RIGHT: 'int16',
        ATTACK_HIT_AREA_UP: 'int16',
        ATTACK_HIT_AREA_DOWN: 'int16',
        ATTACK_SPEED_X: 'int16',
        ATTACK_SPEED_Y: 'int16',
        ATTACK_START_UP: 'int16',
        ATTACK_ACTIVE: 'int16',
        ATTACK_HIT_DAMAGE: 'int16',
        ATTACK_GUARD_DAMAGE: 'int16',
        ATTACK_START_ADD_ENERGY: 'int16',
        ATTACK_HIT_ADD_ENERGY: 'int16',
        ATTACK_GUARD_ADD_ENERGY: 'int16',
        ATTACK_GIVE_ENERGY: 'int16',
        ATTACK_IMPACT_X: 'int16',
        ATTACK_IMPACT_Y: 'int16',
        ATTACK_GIVE_GUARD_RECOV: 'int16',
        ATTACK_ATTACK_TYPE: 'int16',
        ATTACK_DOWN_PROP: 'boolean',
        CANCEL_ABLE_FRAME: 'int16',
        CANCEL_ABLE_MOTION_LEVEL: 'int16',
        MOTION_LEVEL: 'int16',
        CONTROL: 'boolean',
        LANDING_FLAG: 'boolean',
        IMAGE: 'string',
    }

    NUMERICAL_HEADERS: list[str] = []
    STRING_HEADERS: list[str] = []
    BOOLEAN_HEADERS: list[str] = []

    MAPPER: np.ndarray = np.zeros(shape=len(D_TYPE.keys()), dtype=np.int8)

    for index, (header, data_type) in enumerate(D_TYPE.items()):
        match data_type:
            case 'string':
                MAPPER[index] = len(STRING_HEADERS)
                STRING_HEADERS.append(header)
            case 'int16':
                MAPPER[index] = len(NUMERICAL_HEADERS)
                NUMERICAL_HEADERS.append(header)
            case _:
                MAPPER[index] = len(BOOLEAN_HEADERS)
                BOOLEAN_HEADERS.append(header)
