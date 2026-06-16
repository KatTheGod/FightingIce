import asyncio
import datetime
import os

import constants as c
import functions as f
import motion_classes.motion_editor as me
from motion_classes.motion_editor import MotionEditor
from motion_classes.motion_headers import MotionHeadersEnum as headers

"""
    TODO:
		* Maybe look into consolidating when you are orchestrating many tournaments
        * Get the overwriting thing working well.
        * Linter
        * create script / python to kill all active instances?????
			* Don't remember what this is
		* Investigate way to record multiple matches on multiple screens.
			* I'm sure we can get the frames themselves then draw.
			* Especially because the replay is just a recording of steps per frame, meaning that different meta states affect the efficacy.
"""

"""
	The objective right now is to have an orchestrator
	it can do everything in 1 shot. But I think we will maybe do it in parts.
	we will first setup an env where we incrementally increase Zen's kick range over 10 simulations, then afterwards, we will see how that affects win rate.
	Maybe we can consider using jupyter :new_moon
"""


async def start_orchestration(
    characters: list[str],
    agents: list[str],
    evolution_count: int,
    percentage: float,
    deterministic: bool = True,
) -> None:
    for i in range(evolution_count):
        c.GAME_TIME = datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
        # base_experiment_name = 'mcts_z_l_z_d_u_l_ge_u2_z_sx_u_z_hae2_u_l_hd_d02_z_har_u'
        base_experiment_name = "delete"
        experiment_name = f"{base_experiment_name}_{i}"

        custom_motion_file_name_player_one = os.path.join(
            "custom_motions",
            base_experiment_name,
            f"{characters[0].lower()}_{i}.csv",
        )

        custom_motion_file_name_player_two = os.path.join(
            "custom_motions",
            base_experiment_name,
            f"{characters[1].lower()}_{i}.csv",
        )

        player_one_motion_editor = MotionEditor(
            character_name=characters[0],
            custom_motion_path=custom_motion_file_name_player_one,
        )

        player_two_motion_editor = MotionEditor(
            character_name=characters[1],
            custom_motion_path=custom_motion_file_name_player_two,
        )

        me.modify_motion(
            player_one_motion_editor.motion_default,
            player_one_motion_editor.motion_custom,
            1 + ((float(i) / float(evolution_count)) * percentage),
            [headers.ATTACK_HIT_DAMAGE],
        )

        me.modify_motion(
            player_one_motion_editor.motion_default,
            player_one_motion_editor.motion_custom,
            1 + ((float(i) / float(evolution_count)) * percentage),
            [headers.ATTACK_SPEED_X],
        )

        me.modify_motion(
            player_one_motion_editor.motion_default,
            player_one_motion_editor.motion_custom,
            1 + ((float(i) / float(evolution_count)) * (percentage * 2)),
            [headers.ATTACK_HIT_ADD_ENERGY],
        )

        me.modify_motion(
            player_one_motion_editor.motion_default,
            player_one_motion_editor.motion_custom,
            1 + ((float(i) / float(evolution_count)) * (percentage * 2)),
            [headers.ATTACK_HIT_AREA_RIGHT],
        )

        me.modify_motion(
            player_two_motion_editor.motion_default,
            player_two_motion_editor.motion_custom,
            1 + ((float(i) / float(evolution_count)) * (percentage * 2)),
            [headers.ATTACK_GIVE_ENERGY],
        )

        me.modify_motion(
            player_two_motion_editor.motion_default,
            player_two_motion_editor.motion_custom,
            1 - ((float(i) / float(evolution_count)) * (percentage / 2.0)),
            [headers.ATTACK_HIT_DAMAGE],
        )

        # player_one_motion_editor.save_custom_motion()
        # player_two_motion_editor.save_custom_motion()

        custom_motions: list[MotionEditor] = [
            # player_one_motion_editor,
            # player_two_motion_editor,
        ]

        argument_for_custom_motions: list[str] = []
        for custom_motion in custom_motions:
            if len(argument_for_custom_motions) == 0:
                argument_for_custom_motions.append("--config-path")
                argument_for_custom_motions.append(f"{len(custom_motions)}")

            argument_for_custom_motions.append(custom_motion.character_name)
            argument_for_custom_motions.append(custom_motion.custom_motion_path)

        common_commands = [
            "java",
            "-cp",
            os.pathsep.join(["dare.jar", "."]),
            "Main",
            "--limithp",
            str(c.PLAYER_HP),
            str(c.PLAYER_HP),
            "-df",
            "-r",
            "1",
            "-f",
            str(c.GAME_DURATION_SEC * 60),
            "--time-stamp",
            c.GAME_TIME,
            *argument_for_custom_motions,
            # This is for the ai, so maybe turn on when you have those configured
            # '--headless-mode',
            "--input-sync",
            # '--lightweight-mode',
            "--pyftg-mode",
            "--non-delay",
            "2",
        ]

        print(f"Java jar command:{' '.join(common_commands)}")

        os.makedirs(os.path.join("log", "engines"), exist_ok=True)

        gateways = f.create_gateways(8000, 9000, limit=c.NO_ENGINES)
        await f.start_simulators(
            gateways,
            common_commands,
            characters,
            custom_motions,
            agents,
            experiment_name,
            deterministic=deterministic,
        )


if __name__ == "__main__":
    # c.GAME_TIME = c.GAME_TIME
    # c.GAME_DURATION_SEC = 1
    # c.PLAYER_HP = c.PLAYER_HP
    c.POLL_INTERVAL_SEC = 0
    c.NO_ENGINES = 1
    c.NO_GAMES = 1
    evolution_count = 10
    c.ZIP_FILES = True
    asyncio.run(
        start_orchestration(
            characters=[
                c.CHARACTERS.ZEN,
                c.CHARACTERS.LUD,
            ],
            agents=[
                c.AgentNames.CONSISTENT_MCTS_AGENT,
                c.AgentNames.CONSISTENT_MCTS_AGENT,
            ],
            evolution_count=evolution_count,
            percentage=1,
            deterministic=True,
        ),
    )
