import logging
import random

import pandas as pd
from pyftg import AIInterface, AudioData, CommandCenter, FrameData, GameData, Key, RoundResult, ScreenData
from pyftg.models.character_data import CharacterData

from motion_classes.motion_headers import MotionHeadersEnum as headers
from motion_classes.motion_names import MotionNamesEnum as motion_names

logger = logging.getLogger(__name__)

"""
    * This is going to be an AI that uses Zen and will always kick.
    * It will approach while it can then do a kick
"""


class KatKickAi(AIInterface):
    def __init__(
        self,
        motion: pd.DataFrame,
        use_kick: bool = False,
        interval: float = 1,
        character_name: str | None = None,
        deterministic: bool = True,
    ) -> None:
        super().__init__()
        self.blind_flag: bool = False
        self.use_kick: bool = use_kick
        self.interval_frames: float = interval * 60 * 5
        self.interval_frames_current: float
        self.heartbeat: int = -1
        self.character_name: str = character_name
        self.motion: pd.DataFrame = motion
        self.deterministic: bool = deterministic

        self.reset_interval()

    def reset_interval(self) -> None:
        self.interval_frames_current: float = (
            self.interval_frames  #
            if self.deterministic
            else random.uniform(1, self.interval_frames)
        )

    def name(self) -> str:
        return (
            self.__class__.__name__
            + (
                "kicker"  #
                if self.use_kick
                else "puncher"
            )
            + (
                self.character_name  #
                if self.character_name is not None
                else ""
            )
        )

    def is_blind(self) -> bool:
        return self.blind_flag

    def initialize(self, _: GameData, player_number: int) -> None:
        logger.info("initialize")
        self.cc: CommandCenter = CommandCenter()
        self.key: Key = Key()
        self.player: int = player_number
        self.opponent: int = (player_number + 1) % 2
        self.is_control: bool = True

    """
        * This is the "cheating" ai.
        * This is to mimic human reaction time.
        * Since we are simulating human players, should we keep this on?
    """

    # Comment to suppress error
    def get_non_delay_frame_data(self, frame_data: FrameData) -> None:
        pass

    def input(self) -> Key:
        return self.key

    # Game will give you this each frame
    def get_information(self, frame_data: FrameData, is_control: bool) -> None:
        self.frame_data = frame_data
        self.is_control = is_control
        self.cc.set_frame_data(self.frame_data, self.player)

    def get_screen_data(self, screen_data: ScreenData) -> None:
        self.screen_data = screen_data

    def get_audio_data(self, audio_data: AudioData) -> None:
        self.audio_data = audio_data

    def processing(self) -> None:
        # Don't do anything during the menu / initialization
        if self.frame_data.empty_flag or self.frame_data.current_frame_number <= 0:
            return

        allow_action_move: bool = self.frame_data.current_frame_number - self.heartbeat >= self.interval_frames_current

        if allow_action_move:
            self.heartbeat = (
                self.heartbeat + self.interval_frames_current  #
                if self.deterministic
                else self.frame_data.current_frame_number
            )
            self.reset_interval()

        if self.cc.get_skill_flag():
            self.key = self.cc.get_skill_key()
        else:
            self.key.empty()
            self.cc.skill_cancel()

            if self.is_control:
                character: CharacterData = self.frame_data.get_character(self.player)
                opponent: CharacterData = self.frame_data.get_character(self.opponent)

                distance: float = (
                    opponent.left - character.right  #
                    if self.frame_data.is_front(self.player)
                    else character.left - opponent.right
                )

                true_left: float = character.x - character.graphic_size_x / 2
                character_offset: float = abs(character.left - true_left)

                motion_name: str = (
                    motion_names.STAND_B  #
                    if self.use_kick
                    else motion_names.STAND_A
                )

                attack_range: float = self.motion.at[motion_name, headers.ATTACK_HIT_AREA_RIGHT] - character_offset

                if allow_action_move:
                    if distance >= attack_range:
                        self.cc.command_call(motion_names.FORWARD_WALK)
                    else:
                        self.cc.command_call(
                            motion_names.STAND_B  #
                            if self.use_kick
                            else motion_names.STAND_A,
                        )

    def round_end(self, round_result: RoundResult) -> None:
        logger.info(f"round end: {round_result}")

    def game_end(self) -> None:
        logger.info("game end")

    # Will add more stuff when it gets complicated
    def close(self) -> None:
        pass
