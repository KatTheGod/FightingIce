from dataclasses import dataclass
from motion_classes.motion_names import MotionNamesEnum


@dataclass
class Vector:
    x: float
    y: float


@dataclass
class HitArea:
    top: int
    bottom: int
    left: int
    right: int


@dataclass
class Projectile:
    playerNumber: bool
    hitArea: HitArea
    speed: Vector


@dataclass
class PlayerActions:
    p1_action: MotionNamesEnum
    p2_action: MotionNamesEnum


@dataclass
class FrameData:
    frame: int
    hitPoints: list[int]
    energy: list[int]
    attackHitBoxes: list[HitArea | None]
    characterSpeeds: list[Vector]
    projectileInformation: list[Projectile | None]
    characterHitBoxes: list[HitArea]
    playerActions: PlayerActions


def parse_frame_data(raw_data: list[dict[str, any]]) -> tuple[list[FrameData | None], int]:
    frames: list[FrameData] = []
    if isinstance(raw_data, int):
        print("INT incoming", raw_data)
    max_frame: int = len(raw_data)
    for frame_index, frame in enumerate(raw_data):
        if frame is None:
            # frames.append(None)
            max_frame = frame_index
            break

        attack_hit_boxes: list[None | HitArea] = [
            HitArea(**box)  #
            if box
            else None
            for box in frame.get("attackHitBoxes", [])
        ]

        character_speeds: list[Vector] = [
            Vector(**vec)  #
            for vec in frame.get("characterSpeeds", [])
        ]

        projectile_information: list[Projectile | None] = []
        for projectile in frame.get("projectileInformation", []):
            if projectile is not None:
                projectile_information.append(
                    Projectile(
                        playerNumber=projectile["playerNumber"],
                        hitArea=HitArea(**projectile["hitArea"]),
                        speed=Vector(**projectile["speed"]),
                    )
                )
            else:
                projectile_information.append(None)

        character_hit_boxes: list[HitArea] = [
            HitArea(**box)  #
            for box in frame.get("characterHitBoxes", [])
        ]

        raw_player_actions = frame.get(
            "playerActions",
            [
                MotionNamesEnum.NEUTRAL.value,
                MotionNamesEnum.NEUTRAL.value,
            ],
        )
        player_actions = PlayerActions(
            MotionNamesEnum(raw_player_actions[0]),
            MotionNamesEnum(raw_player_actions[1]),
        )

        frames.append(
            FrameData(
                frame=frame["frame"],
                hitPoints=frame["hitPoints"],
                energy=frame["energy"],
                attackHitBoxes=attack_hit_boxes,
                characterSpeeds=character_speeds,
                projectileInformation=projectile_information,
                characterHitBoxes=character_hit_boxes,
                playerActions=player_actions,
            )
        )

    return frames, max_frame
