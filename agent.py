import asyncio

from pyftg.socket.aio.gateway import Gateway

from agents.DisplayInfo import DisplayInfo
from agents.KatKickAi import KatKickAi
from agents.KickAI import KickAI

gateway = Gateway(port=8000)

kick_ai = KickAI()
display_ai = DisplayInfo()
kat_ai = KatKickAi()


async def start_process() -> None:
    agent1 = KatKickAi(use_kick=False, interval=2)
    agent2 = KatKickAi(use_kick=True, interval=1)
    gateway.register_ai(agent1.name(), agent1)
    gateway.register_ai(agent2.name(), agent2)
    game_name = f"{'fishes'}-instance-{0}-{agent1.name()}-vs-{agent2.name()}"

    await gateway.run_game(
        [f"{game_name}<name>ZEN", "GARNET"],
        [agent1.name(), agent2.name()],
        1,
    )

    await gateway.close()


asyncio.run(start_process())
