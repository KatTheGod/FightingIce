import datetime
import os
from enum import StrEnum

GLOBAL_SEED: int = 42

NO_GAMES: int = 1
NO_ENGINES: int = 1
PLAYER_HP: int = 400
PLAYER_MAX_ENERGY: int = 300
POLL_INTERVAL_SEC: int = 1
GAME_DURATION_SEC: int = 60
EXPERIMENT_NAME: str = 'adhoc'
ZIP_FILES: bool = True

NODES: int = 1
# We actually have 20, but wanna say 15 to align to cluster
CORES: int = 20
EST_RAM_PER_ENGINE_GB: int = 2
PARTITION: str = 'regular'
SCHEDULER_FILE: str | None = None
BASE_PATH: str | None = None

DEFAULT_MOTIONS_PATH: str = os.path.join('data', 'characters')
MOTIONS_FILE_NAME: str = 'Motion.csv'
CUSTOM_MOTION_PATH: str = 'custom_motions'

MAX_ATTACK_SPEED_X: int = 25
MAX_ATTACK_SPEED_Y: int = 15
MAX_PROJECTILE_FRAME_COUNT: int = 600

MAX_HIT_BOX_WIDTH: int = 300
MAX_HIT_BOX_HEIGHT: int = 200

class LOGS:
    ENGINES: str = 'engines'
    FRAME_DATA: str = 'frameData'
    MOTIONS: str = 'motions'
    POINT: str = 'point'
    REPLAY: str = 'replay'
    SOUND: str = 'sound'
    DASK_LOGS: str = 'dask_logs'
    SOLUTION_EXPLORER: str = 'solution_explorer'
    PLOTS: str = 'plots'

    # Experiments related content
    EXPERIMENTS_FOLDER: str = 'experiments'
    ROUND_ROBIN: str = 'round_robin'
    META_DISCOVERY: str = 'meta_discovery'

    KNOWN_LOGS: list[str] = [
        ENGINES,
        FRAME_DATA,
        MOTIONS,
        POINT,
        REPLAY,
        SOUND,  # We dont really use this though...
    ]

GAME_TIME: str = datetime.datetime.now().strftime('%Y.%m.%d_%H.%M.%S')


class CHARACTERS(StrEnum):
    ZEN: str = 'ZEN'
    GARNET: str = 'GARNET'
    LUD: str = 'LUD'

CHARACTER_ORDER: dict[str, int] = {
    CHARACTERS.ZEN.name: 0,
    CHARACTERS.GARNET.name: 1,
    CHARACTERS.LUD.name: 2,
}

CHARACTER_ORDER_REVERSE: dict[int, str] = {
    0: CHARACTERS.ZEN.name,
    1: CHARACTERS.GARNET.name,
    2: CHARACTERS.LUD.name,
}


CHARACTER_MOTION_PATHS: list[str | None] = [
    None,
    None,
]

DEFAULT_MOTIONS_PATH: str = os.path.join('data', 'characters')


class PointHeaderNames:
    INSTANCE = 'instance'
    ROUND = 'round'
    HP_ONE = 'hp_one'
    HP_TWO = 'hp_two'
    DRAIN = 'drain'
    WINNER = 'winner'
    SIMULATION_NUMBER = 'simulation_number'

    D_TYPE = {
        INSTANCE: 'int16',
        ROUND: 'int16',
        HP_ONE: 'int16',
        HP_TWO: 'int16',
        DRAIN: 'int16',
        WINNER: 'int16',
    }


class AgentNames:
    MCTS_AGENT = 'MctsAi23i'
    CONSISTENT_MCTS_AGENT = 'MctsAi23i.MctsAi23i'
    KAT_MCTS_AGENT = 'katai.mcts.basic.MCTSAgent'
    KAY_MCTS_MX_AGENT = 'katai.mcts.mx_mcts_acc.MCTSAgent'
    KAT_KICK_AI = 'kat kick'

class ScreenDimensions:
    WIDTH: int = 960
    HEIGHT: int = 640


class MotionData:
    rows: int = 56
    # Note, the first column doesn't really exist. We can never do anything about a motion_name
    cols: int = 34
    shape: tuple[int, int] = (rows, cols)

class pymoo:
    class TERMINATION:
        EVALUATION_LIMIT = 'n_eval'
        GENERATION_LIMIT = 'n_gen'
        OBJECTIVE_THRESHOLD = 'fmin'
        TIME_LIMIT = 'time'
        DEFAULT_MOO_TERMINATION = 'moo'

    class MOEAD:
        class SpreadType:
            UNIFORM: str = "uniform"
            DAS_DENNIS: str = "das-dennis"
            ENERGY: str = "energy"
            MULTI_LAYER: str = "multi-layer"
            LAYER_ENERGY: str = "layer-energy"
            REDUCTION: str = "reduction"
            INCREMENTAL: str = "incremental"

# Delete these, lazy way to track time
start_time = 0
end_time = 0