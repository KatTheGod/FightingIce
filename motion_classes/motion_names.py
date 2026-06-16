from enum import StrEnum


class MotionNamesEnum(StrEnum):
    NEUTRAL = "NEUTRAL"
    STAND = "STAND"
    FORWARD_WALK = "FORWARD_WALK"
    DASH = "DASH"
    BACK_STEP = "BACK_STEP"
    CROUCH = "CROUCH"
    JUMP = "JUMP"
    FOR_JUMP = "FOR_JUMP"
    BACK_JUMP = "BACK_JUMP"
    AIR = "AIR"
    STAND_GUARD = "STAND_GUARD"
    CROUCH_GUARD = "CROUCH_GUARD"
    AIR_GUARD = "AIR_GUARD"
    STAND_GUARD_RECOV = "STAND_GUARD_RECOV"
    CROUCH_GUARD_RECOV = "CROUCH_GUARD_RECOV"
    AIR_GUARD_RECOV = "AIR_GUARD_RECOV"
    STAND_RECOV = "STAND_RECOV"
    CROUCH_RECOV = "CROUCH_RECOV"
    AIR_RECOV = "AIR_RECOV"
    CHANGE_DOWN = "CHANGE_DOWN"
    DOWN = "DOWN"
    RISE = "RISE"
    LANDING = "LANDING"
    THROW_A = "THROW_A"
    THROW_B = "THROW_B"
    THROW_HIT = "THROW_HIT"
    THROW_SUFFER = "THROW_SUFFER"
    STAND_A = "STAND_A"
    STAND_B = "STAND_B"
    CROUCH_A = "CROUCH_A"
    CROUCH_B = "CROUCH_B"
    AIR_A = "AIR_A"
    AIR_B = "AIR_B"
    AIR_DA = "AIR_DA"
    AIR_DB = "AIR_DB"
    STAND_FA = "STAND_FA"
    STAND_FB = "STAND_FB"
    CROUCH_FA = "CROUCH_FA"
    CROUCH_FB = "CROUCH_FB"
    AIR_FA = "AIR_FA"
    AIR_FB = "AIR_FB"
    AIR_UA = "AIR_UA"
    AIR_UB = "AIR_UB"
    STAND_D_DF_FA = "STAND_D_DF_FA"
    STAND_D_DF_FB = "STAND_D_DF_FB"
    STAND_F_D_DFA = "STAND_F_D_DFA"
    STAND_F_D_DFB = "STAND_F_D_DFB"
    STAND_D_DB_BA = "STAND_D_DB_BA"
    STAND_D_DB_BB = "STAND_D_DB_BB"
    AIR_D_DF_FA = "AIR_D_DF_FA"
    AIR_D_DF_FB = "AIR_D_DF_FB"
    AIR_F_D_DFA = "AIR_F_D_DFA"
    AIR_F_D_DFB = "AIR_F_D_DFB"
    AIR_D_DB_BA = "AIR_D_DB_BA"
    AIR_D_DB_BB = "AIR_D_DB_BB"
    STAND_D_DF_FC = "STAND_D_DF_FC"


# NOTE: IF you change the order of this stuff later, it could affect the quality of the code in the limits mapper
PRIMARY_ACTIONS_ATTACK: list[MotionNamesEnum] = [
    MotionNamesEnum.STAND_A,
    MotionNamesEnum.STAND_B,
    MotionNamesEnum.CROUCH_A,
    MotionNamesEnum.CROUCH_B,
    MotionNamesEnum.AIR_A,
    MotionNamesEnum.AIR_B,
    MotionNamesEnum.THROW_A,
    MotionNamesEnum.THROW_B,
]

SECONDARY_ACTIONS_ATTACK: list[MotionNamesEnum] = [
    MotionNamesEnum.STAND_FA,
    MotionNamesEnum.STAND_FB,
    MotionNamesEnum.CROUCH_FA,
    MotionNamesEnum.CROUCH_FB,
    MotionNamesEnum.AIR_FA,
    MotionNamesEnum.AIR_FB,
    MotionNamesEnum.AIR_DA,
    MotionNamesEnum.AIR_DB,
    MotionNamesEnum.AIR_UA,
    MotionNamesEnum.AIR_UB,
]

TERTIARY_ACTIONS_ATTACK: list[MotionNamesEnum] = [
    MotionNamesEnum.STAND_D_DF_FA,
    MotionNamesEnum.STAND_D_DF_FB,
    MotionNamesEnum.STAND_F_D_DFA,
    MotionNamesEnum.STAND_F_D_DFB,
    MotionNamesEnum.STAND_D_DB_BA,
    MotionNamesEnum.STAND_D_DB_BB,
    MotionNamesEnum.AIR_D_DF_FA,
    MotionNamesEnum.AIR_D_DF_FB,
    MotionNamesEnum.AIR_F_D_DFA,
    MotionNamesEnum.AIR_F_D_DFB,
    MotionNamesEnum.AIR_D_DB_BA,
    MotionNamesEnum.AIR_D_DB_BB,
]

ULTIMATE_ATTACK = MotionNamesEnum.STAND_D_DF_FC

MOVEMENT_ACTIONS: list[MotionNamesEnum] = [
    MotionNamesEnum.FORWARD_WALK,
    MotionNamesEnum.DASH,
    MotionNamesEnum.BACK_STEP,
    MotionNamesEnum.JUMP,
    MotionNamesEnum.FOR_JUMP,
    MotionNamesEnum.BACK_JUMP,
]

ATTACK_ACTIONS_ALL: list[MotionNamesEnum] = [
    *PRIMARY_ACTIONS_ATTACK,
    *SECONDARY_ACTIONS_ATTACK,
    *TERTIARY_ACTIONS_ATTACK,
    ULTIMATE_ATTACK,
]


MAPPER: dict[str, int] = {
    motion_name: index  #
    for index, motion_name in enumerate(MotionNamesEnum)
}
