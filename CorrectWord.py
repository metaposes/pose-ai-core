from enum import Enum, auto, unique


@unique
class CorrectWord(Enum):
    CORRECT = auto()
    LIFT_RIGHT_ARM = auto()
    DOWN_RIGHT_ARM = auto()
    LIFT_LEFT_ARM = auto()
    DOWN_LEFT_ARM = auto()
    BODY_UP = auto()
    BODY_DOWN = auto()

