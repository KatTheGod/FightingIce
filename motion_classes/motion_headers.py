from enum import StrEnum
from typing import ClassVar

import numpy as np

from motion_classes.motion_names import MotionNamesEnum


class MotionHeadersEnum(StrEnum):
    MOTION_NAME = "motionName"
    FRAME_NUMBER = "frameNumber"
    SPEED_X = "speedX"
    SPEED_Y = "speedY"
    HIT_AREA_LEFT = "hitAreaLeft"
    HIT_AREA_RIGHT = "hitAreaRight"
    HIT_AREA_UP = "hitAreaUp"
    HIT_AREA_DOWN = "hitAreaDown"
    STATE = "state"
    ATTACK_HIT_AREA_LEFT = "attack.hitAreaLeft"
    ATTACK_HIT_AREA_RIGHT = "attack.hitAreaRight"
    ATTACK_HIT_AREA_UP = "attack.hitAreaUp"
    ATTACK_HIT_AREA_DOWN = "attack.hitAreaDown"
    ATTACK_SPEED_X = "attack.speedX"
    ATTACK_SPEED_Y = "attack.speedY"
    ATTACK_START_UP = "attack.StartUp"
    ATTACK_ACTIVE = "attack.Active"
    ATTACK_HIT_DAMAGE = "attack.HitDamage"
    ATTACK_GUARD_DAMAGE = "attack.GuardDamage"
    ATTACK_START_ADD_ENERGY = "attack.StartAddEnergy"
    ATTACK_HIT_ADD_ENERGY = "attack.HitAddEnergy"
    ATTACK_GUARD_ADD_ENERGY = "attack.GuardAddEnergy"
    ATTACK_GIVE_ENERGY = "attack.GiveEnergy"
    ATTACK_IMPACT_X = "attack.ImpactX"
    ATTACK_IMPACT_Y = "attack.ImpactY"
    ATTACK_GIVE_GUARD_RECOV = "attack.GiveGuardRecov"
    ATTACK_ATTACK_TYPE = "attack.AttackType"
    ATTACK_DOWN_PROP = "attack.DownProp"
    CANCEL_ABLE_FRAME = "cancelAbleFrame"
    CANCEL_ABLE_MOTION_LEVEL = "cancelAbleMotionLevel"
    MOTION_LEVEL = "motionLevel"
    CONTROL = "control"
    LANDING_FLAG = "landingFlag"
    IMAGE = "Image"

    # NOTE: From here, these are going to be motion names that need to be mapped
    HIT_BOX_WIDTH = "hitBoxWidth"
    HIT_BOX_HEIGHT = "hitBoxHeight"


class MotionHeaders:
    HEADERS: ClassVar[list[str]] = [
        # We are doing this because motion_name is the index, might adjust in the future
        # MOTION_NAME,
        MotionHeadersEnum.FRAME_NUMBER,
        MotionHeadersEnum.SPEED_X,
        MotionHeadersEnum.SPEED_Y,
        MotionHeadersEnum.HIT_AREA_LEFT,
        MotionHeadersEnum.HIT_AREA_RIGHT,
        MotionHeadersEnum.HIT_AREA_UP,
        MotionHeadersEnum.HIT_AREA_DOWN,
        MotionHeadersEnum.STATE,
        MotionHeadersEnum.ATTACK_HIT_AREA_LEFT,
        MotionHeadersEnum.ATTACK_HIT_AREA_RIGHT,
        MotionHeadersEnum.ATTACK_HIT_AREA_UP,
        MotionHeadersEnum.ATTACK_HIT_AREA_DOWN,
        MotionHeadersEnum.ATTACK_SPEED_X,
        MotionHeadersEnum.ATTACK_SPEED_Y,
        MotionHeadersEnum.ATTACK_START_UP,
        MotionHeadersEnum.ATTACK_ACTIVE,
        MotionHeadersEnum.ATTACK_HIT_DAMAGE,
        MotionHeadersEnum.ATTACK_GUARD_DAMAGE,
        MotionHeadersEnum.ATTACK_START_ADD_ENERGY,
        MotionHeadersEnum.ATTACK_HIT_ADD_ENERGY,
        MotionHeadersEnum.ATTACK_GUARD_ADD_ENERGY,
        MotionHeadersEnum.ATTACK_GIVE_ENERGY,
        MotionHeadersEnum.ATTACK_IMPACT_X,
        MotionHeadersEnum.ATTACK_IMPACT_Y,
        MotionHeadersEnum.ATTACK_GIVE_GUARD_RECOV,
        MotionHeadersEnum.ATTACK_ATTACK_TYPE,
        MotionHeadersEnum.ATTACK_DOWN_PROP,
        MotionHeadersEnum.CANCEL_ABLE_FRAME,
        MotionHeadersEnum.CANCEL_ABLE_MOTION_LEVEL,
        MotionHeadersEnum.MOTION_LEVEL,
        MotionHeadersEnum.CONTROL,
        MotionHeadersEnum.LANDING_FLAG,
        MotionHeadersEnum.IMAGE,
    ]

    D_TYPE: ClassVar[dict[str, str]] = {
        MotionHeadersEnum.MOTION_NAME: "string",
        MotionHeadersEnum.FRAME_NUMBER: "int16",
        MotionHeadersEnum.SPEED_X: "int16",
        MotionHeadersEnum.SPEED_Y: "int16",
        MotionHeadersEnum.HIT_AREA_LEFT: "int16",
        MotionHeadersEnum.HIT_AREA_RIGHT: "int16",
        MotionHeadersEnum.HIT_AREA_UP: "int16",
        MotionHeadersEnum.HIT_AREA_DOWN: "int16",
        MotionHeadersEnum.STATE: "string",
        MotionHeadersEnum.ATTACK_HIT_AREA_LEFT: "int16",
        MotionHeadersEnum.ATTACK_HIT_AREA_RIGHT: "int16",
        MotionHeadersEnum.ATTACK_HIT_AREA_UP: "int16",
        MotionHeadersEnum.ATTACK_HIT_AREA_DOWN: "int16",
        MotionHeadersEnum.ATTACK_SPEED_X: "int16",
        MotionHeadersEnum.ATTACK_SPEED_Y: "int16",
        MotionHeadersEnum.ATTACK_START_UP: "int16",
        MotionHeadersEnum.ATTACK_ACTIVE: "int16",
        MotionHeadersEnum.ATTACK_HIT_DAMAGE: "int16",
        MotionHeadersEnum.ATTACK_GUARD_DAMAGE: "int16",
        MotionHeadersEnum.ATTACK_START_ADD_ENERGY: "int16",
        MotionHeadersEnum.ATTACK_HIT_ADD_ENERGY: "int16",
        MotionHeadersEnum.ATTACK_GUARD_ADD_ENERGY: "int16",
        MotionHeadersEnum.ATTACK_GIVE_ENERGY: "int16",
        MotionHeadersEnum.ATTACK_IMPACT_X: "int16",
        MotionHeadersEnum.ATTACK_IMPACT_Y: "int16",
        MotionHeadersEnum.ATTACK_GIVE_GUARD_RECOV: "int16",
        MotionHeadersEnum.ATTACK_ATTACK_TYPE: "int16",
        MotionHeadersEnum.ATTACK_DOWN_PROP: "boolean",
        MotionHeadersEnum.CANCEL_ABLE_FRAME: "int16",
        MotionHeadersEnum.CANCEL_ABLE_MOTION_LEVEL: "int16",
        MotionHeadersEnum.MOTION_LEVEL: "int16",
        MotionHeadersEnum.CONTROL: "boolean",
        MotionHeadersEnum.LANDING_FLAG: "boolean",
        MotionHeadersEnum.IMAGE: "string",
    }

    NUMERICAL_HEADERS: ClassVar[list[str]] = []
    STRING_HEADERS: ClassVar[list[str]] = []
    BOOLEAN_HEADERS: ClassVar[list[str]] = []

    MAPPER: np.ndarray = np.zeros(shape=len(D_TYPE.keys()), dtype=np.int8)

    for index, (header, data_type) in enumerate(D_TYPE.items()):
        match data_type:
            case "string":
                MAPPER[index] = len(STRING_HEADERS)
                STRING_HEADERS.append(header)
            case "int16":
                MAPPER[index] = len(NUMERICAL_HEADERS)
                NUMERICAL_HEADERS.append(header)
            case _:
                MAPPER[index] = len(BOOLEAN_HEADERS)
                BOOLEAN_HEADERS.append(header)
