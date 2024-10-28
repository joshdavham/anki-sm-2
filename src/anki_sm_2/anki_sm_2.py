from enum import IntEnum

class State(IntEnum):

    Learning = 1
    Review = 2
    Relearing = 3

class Rating(IntEnum):

    Again = 1 # incorrect
    Hard = 2 # correct - had doubts about answer/or took long time to recall
    Good = 3 # correct - took some amount of mental effort to recall
    Easy = 4 # correct - recalled effortlessly

# TODO: implement Card class
class Card:
    pass

# TODO: implement ReviewLog class
class ReviewLog:
    pass

# TODO: implement scheduler class
class AnkiSM2Scheduler:
    pass