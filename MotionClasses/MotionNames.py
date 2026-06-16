from enum import Enum


class MotionNamesEnum(Enum):
    NEUTRAL: str = 'NEUTRAL'
    STAND: str = 'STAND'
    FORWARD_WALK: str = 'FORWARD_WALK'
    DASH: str = 'DASH'
    BACK_STEP: str = 'BACK_STEP'
    CROUCH: str = 'CROUCH'
    JUMP: str = 'JUMP'
    FOR_JUMP: str = 'FOR_JUMP'
    BACK_JUMP: str = 'BACK_JUMP'
    AIR: str = 'AIR'
    STAND_GUARD: str = 'STAND_GUARD'
    CROUCH_GUARD: str = 'CROUCH_GUARD'
    AIR_GUARD: str = 'AIR_GUARD'
    STAND_GUARD_RECOV: str = 'STAND_GUARD_RECOV'
    CROUCH_GUARD_RECOV: str = 'CROUCH_GUARD_RECOV'
    AIR_GUARD_RECOV: str = 'AIR_GUARD_RECOV'
    STAND_RECOV: str = 'STAND_RECOV'
    CROUCH_RECOV: str = 'CROUCH_RECOV'
    AIR_RECOV: str = 'AIR_RECOV'
    CHANGE_DOWN: str = 'CHANGE_DOWN'
    DOWN: str = 'DOWN'
    RISE: str = 'RISE'
    LANDING: str = 'LANDING'
    THROW_A: str = 'THROW_A'
    THROW_B: str = 'THROW_B'
    THROW_HIT: str = 'THROW_HIT'
    THROW_SUFFER: str = 'THROW_SUFFER'
    STAND_A: str = 'STAND_A'
    STAND_B: str = 'STAND_B'
    CROUCH_A: str = 'CROUCH_A'
    CROUCH_B: str = 'CROUCH_B'
    AIR_A: str = 'AIR_A'
    AIR_B: str = 'AIR_B'
    AIR_DA: str = 'AIR_DA'
    AIR_DB: str = 'AIR_DB'
    STAND_FA: str = 'STAND_FA'
    STAND_FB: str = 'STAND_FB'
    CROUCH_FA: str = 'CROUCH_FA'
    CROUCH_FB: str = 'CROUCH_FB'
    AIR_FA: str = 'AIR_FA'
    AIR_FB: str = 'AIR_FB'
    AIR_UA: str = 'AIR_UA'
    AIR_UB: str = 'AIR_UB'
    STAND_D_DF_FA: str = 'STAND_D_DF_FA'
    STAND_D_DF_FB: str = 'STAND_D_DF_FB'
    STAND_F_D_DFA: str = 'STAND_F_D_DFA'
    STAND_F_D_DFB: str = 'STAND_F_D_DFB'
    STAND_D_DB_BA: str = 'STAND_D_DB_BA'
    STAND_D_DB_BB: str = 'STAND_D_DB_BB'
    AIR_D_DF_FA: str = 'AIR_D_DF_FA'
    AIR_D_DF_FB: str = 'AIR_D_DF_FB'
    AIR_F_D_DFA: str = 'AIR_F_D_DFA'
    AIR_F_D_DFB: str = 'AIR_F_D_DFB'
    AIR_D_DB_BA: str = 'AIR_D_DB_BA'
    AIR_D_DB_BB: str = 'AIR_D_DB_BB'
    STAND_D_DF_FC: str = 'STAND_D_DF_FC'


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
    MotionNamesEnum.AIR_UB,
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
class MotionNames:
    NEUTRAL: str = MotionNamesEnum.NEUTRAL.value
    STAND: str = MotionNamesEnum.STAND.value
    FORWARD_WALK: str = MotionNamesEnum.FORWARD_WALK.value
    DASH: str = MotionNamesEnum.DASH.value
    BACK_STEP: str = MotionNamesEnum.BACK_STEP.value
    CROUCH: str = MotionNamesEnum.CROUCH.value
    JUMP: str = MotionNamesEnum.JUMP.value
    FOR_JUMP: str = MotionNamesEnum.FOR_JUMP.value
    BACK_JUMP: str = MotionNamesEnum.BACK_JUMP.value
    AIR: str = MotionNamesEnum.AIR.value
    STAND_GUARD: str = MotionNamesEnum.STAND_GUARD.value
    CROUCH_GUARD: str = MotionNamesEnum.CROUCH_GUARD.value
    AIR_GUARD: str = MotionNamesEnum.AIR_GUARD.value
    STAND_GUARD_RECOV: str = MotionNamesEnum.STAND_GUARD_RECOV.value
    CROUCH_GUARD_RECOV: str = MotionNamesEnum.CROUCH_GUARD_RECOV.value
    AIR_GUARD_RECOV: str = MotionNamesEnum.AIR_GUARD_RECOV.value
    STAND_RECOV: str = MotionNamesEnum.STAND_RECOV.value
    CROUCH_RECOV: str = MotionNamesEnum.CROUCH_RECOV.value
    AIR_RECOV: str = MotionNamesEnum.AIR_RECOV.value
    CHANGE_DOWN: str = MotionNamesEnum.CHANGE_DOWN.value
    DOWN: str = MotionNamesEnum.DOWN.value
    RISE: str = MotionNamesEnum.RISE.value
    LANDING: str = MotionNamesEnum.LANDING.value
    THROW_A: str = MotionNamesEnum.THROW_A.value
    THROW_B: str = MotionNamesEnum.THROW_B.value
    THROW_HIT: str = MotionNamesEnum.THROW_HIT.value
    THROW_SUFFER: str = MotionNamesEnum.THROW_SUFFER.value
    STAND_A: str = MotionNamesEnum.STAND_A.value
    STAND_B: str = MotionNamesEnum.STAND_B.value
    CROUCH_A: str = MotionNamesEnum.CROUCH_A.value
    CROUCH_B: str = MotionNamesEnum.CROUCH_B.value
    AIR_A: str = MotionNamesEnum.AIR_A.value
    AIR_B: str = MotionNamesEnum.AIR_B.value
    AIR_DA: str = MotionNamesEnum.AIR_DA.value
    AIR_DB: str = MotionNamesEnum.AIR_DB.value
    STAND_FA: str = MotionNamesEnum.STAND_FA.value
    STAND_FB: str = MotionNamesEnum.STAND_FB.value
    CROUCH_FA: str = MotionNamesEnum.CROUCH_FA.value
    CROUCH_FB: str = MotionNamesEnum.CROUCH_FB.value
    AIR_FA: str = MotionNamesEnum.AIR_FA.value
    AIR_FB: str = MotionNamesEnum.AIR_FB.value
    AIR_UA: str = MotionNamesEnum.AIR_UA.value
    AIR_UB: str = MotionNamesEnum.AIR_UB.value
    STAND_D_DF_FA: str = MotionNamesEnum.STAND_D_DF_FA.value
    STAND_D_DF_FB: str = MotionNamesEnum.STAND_D_DF_FB.value
    STAND_F_D_DFA: str = MotionNamesEnum.STAND_F_D_DFA.value
    STAND_F_D_DFB: str = MotionNamesEnum.STAND_F_D_DFB.value
    STAND_D_DB_BA: str = MotionNamesEnum.STAND_D_DB_BA.value
    STAND_D_DB_BB: str = MotionNamesEnum.STAND_D_DB_BB.value
    AIR_D_DF_FA: str = MotionNamesEnum.AIR_D_DF_FA.value
    AIR_D_DF_FB: str = MotionNamesEnum.AIR_D_DF_FB.value
    AIR_F_D_DFA: str = MotionNamesEnum.AIR_F_D_DFA.value
    AIR_F_D_DFB: str = MotionNamesEnum.AIR_F_D_DFB.value
    AIR_D_DB_BA: str = MotionNamesEnum.AIR_D_DB_BA.value
    AIR_D_DB_BB: str = MotionNamesEnum.AIR_D_DB_BB.value
    STAND_D_DF_FC: str = MotionNamesEnum.STAND_D_DF_FC.value

    MOTION_NAMES: list[str] = [
        NEUTRAL,
        STAND,
        FORWARD_WALK,
        DASH,
        BACK_STEP,
        CROUCH,
        JUMP,
        FOR_JUMP,
        BACK_JUMP,
        AIR,
        STAND_GUARD,
        CROUCH_GUARD,
        AIR_GUARD,
        STAND_GUARD_RECOV,
        CROUCH_GUARD_RECOV,
        AIR_GUARD_RECOV,
        STAND_RECOV,
        CROUCH_RECOV,
        AIR_RECOV,
        CHANGE_DOWN,
        DOWN,
        RISE,
        LANDING,
        THROW_A,
        THROW_B,
        THROW_HIT,
        THROW_SUFFER,
        STAND_A,
        STAND_B,
        CROUCH_A,
        CROUCH_B,
        AIR_A,
        AIR_B,
        AIR_DA,
        AIR_DB,
        STAND_FA,
        STAND_FB,
        CROUCH_FA,
        CROUCH_FB,
        AIR_FA,
        AIR_FB,
        AIR_UA,
        AIR_UB,
        STAND_D_DF_FA,
        STAND_D_DF_FB,
        STAND_F_D_DFA,
        STAND_F_D_DFB,
        STAND_D_DB_BA,
        STAND_D_DB_BB,
        AIR_D_DF_FA,
        AIR_D_DF_FB,
        AIR_F_D_DFA,
        AIR_F_D_DFB,
        AIR_D_DB_BA,
        AIR_D_DB_BB,
        STAND_D_DF_FC,
    ]

    MAPPER: dict[str, int] = {}
    for index, motion_name in enumerate(MOTION_NAMES):
        MAPPER[motion_name] = index
