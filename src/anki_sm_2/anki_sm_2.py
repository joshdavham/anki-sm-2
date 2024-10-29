from enum import IntEnum
from datetime import datetime, timezone, timedelta
from typing import Optional
from copy import deepcopy

class State(IntEnum):

    Learning = 1
    Review = 2
    Relearing = 3

class Rating(IntEnum):

    Again = 1 # incorrect
    Hard = 2 # correct - had doubts about answer/or took long time to recall
    Good = 3 # correct - took some amount of mental effort to recall
    Easy = 4 # correct - recalled effortlessly

class Card:
    
    card_id: int
    state: State
    step: Optional[int]
    ease: float
    due: datetime
    current_interval: Optional[int]

    def __init__(self, 
                 created_at: Optional[datetime]=None,
                 card_id: Optional[int]=None,
                 state: State=State.Learning,
                 step: Optional[int]=None,
                 ease: float=2.5,
                 due: Optional[datetime]=None,
                 current_interval: Optional[int]=None
                 ) -> None:
        
        if created_at is None:
            created_at = datetime.now(timezone.utc)

        if card_id is None:
            card_id = int(created_at.timestamp() * 1000)
        self.card_id = card_id

        self.state = state

        self.step = step

        self.ease = ease

        if due is None:
            due = created_at
        self.due = due

        self.current_interval = current_interval

    def to_dict(self):

        return_dict = {
            "card_id": self.card_id,
            "state": self.state.value,
            "step": self.step,
            "ease": self.ease,
            "due": self.due.isoformat(),
            "current_interval": self.current_interval
        }

        return return_dict
    
    @staticmethod
    def from_dict(source_dict) -> "Card":

        card_id = int(source_dict['card_id'])
        state = State(int(source_dict['state']))
        step = source_dict['step']
        ease = float(source_dict['ease'])
        due = datetime.fromisoformat(source_dict['due'])
        current_interval = source_dict['current_interval']

        return Card(card_id=card_id, state=state, step=step, ease=ease, due=due, current_interval=current_interval)

class ReviewLog:
    
    card: Card
    rating: Rating
    review_datetime: datetime

    def __init__(self, card: Card, rating: Rating, review_datetime: datetime) -> None:

        self.card = deepcopy(card)
        self.rating = rating
        self.review_datetime = review_datetime

    def to_dict(self):

        return_dict = {
            "card": self.card.to_dict(),
            "rating": self.rating.value,
            "review_datetime": self.review_datetime.isoformat()
        }

        return return_dict
    
    @staticmethod
    def from_dict(source_dict) -> "ReviewLog":

        card = Card.from_dict(source_dict['card'])
        rating = Rating(int(source_dict['rating']))
        review_datetime = datetime.fromisoformat(source_dict['review_datetime'])

        return ReviewLog(card=card, rating=rating, review_datetime=review_datetime)


class AnkiSM2Scheduler:
    
    learning_steps: list[timedelta]
    graduating_interval: int
    easy_interval: int

    relearning_steps: list[timedelta]
    minimum_interval: int

    maximum_interval: int
    starting_ease: float
    easy_bonus: float
    interval_modifier: float
    hard_interval: float
    new_interval: float

    def __init__(self, 
                 learning_steps: list[timedelta] = [timedelta(minutes=1), timedelta(minutes=10)],
                 graduating_interval: int = 1,
                 easy_interval: int = 4,
                 relearning_steps: list[timedelta] = [timedelta(minutes=10)],
                 minimum_interval: int = 1,
                 maximum_interval: int = 36500,
                 starting_ease: float = 2.5,
                 easy_bonus: float = 1.3,
                 interval_modifier: float = 1.0,
                 hard_interval: float = 1.2,
                 new_interval: float = 0.0):
        
        self.learning_steps = learning_steps
        self.graduating_interval = graduating_interval
        self.easy_interval = easy_interval
        self.relearning_steps = relearning_steps
        self.minimum_interval = minimum_interval
        self.maximum_interval = maximum_interval
        self.starting_ease = starting_ease
        self.easy_bonus = easy_bonus
        self.interval_modifier = interval_modifier
        self.hard_interval = hard_interval
        self.new_interval = new_interval

    # TODO: implement review_card
    def review_card(self, card: Card, rating: Rating, review_datetime: Optional[datetime]=None):

        if review_datetime is None:
            review_datetime = datetime.now()

        review_log = ReviewLog(card=card, rating=rating, review_datetime=review_datetime)

        return None, review_log
    
    def to_dict(self):
        
        return_dict = {
            "learning_steps": [int(learning_step.total_seconds()) for learning_step in self.learning_steps],
            "graduating_interval": self.graduating_interval,
            "easy_interval": self.easy_interval,
            "relearning_steps": [int(relearning_step.total_seconds()) for relearning_step in self.relearning_steps],
            "minimum_interval": self.minimum_interval,
            "maximum_interval": self.maximum_interval,
            "starting_ease": self.starting_ease,
            "easy_bonus": self.easy_bonus,
            "interval_modifier": self.interval_modifier,
            "hard_interval": self.hard_interval,
            "new_interval": self.new_interval
        }

        return return_dict

    @staticmethod
    def from_dict(source_dict):
        
        learning_steps = [timedelta(seconds=learning_step) for learning_step in source_dict['learning_steps']]
        graduating_interval = source_dict['graduating_interval']
        easy_interval = source_dict['easy_interval']
        relearning_steps = [timedelta(seconds=relearning_step) for relearning_step in source_dict['relearning_steps']]
        minimum_interval = source_dict['minimum_interval']
        maximum_interval = source_dict['maximum_interval']
        starting_ease = source_dict['starting_ease']
        easy_bonus = source_dict['easy_bonus']
        interval_modifier = source_dict['interval_modifier']
        hard_interval = source_dict['hard_interval']
        new_interval = source_dict['new_interval']

        return AnkiSM2Scheduler(
                    learning_steps = learning_steps,
                    graduating_interval = graduating_interval,
                    easy_interval = easy_interval,
                    relearning_steps = relearning_steps,
                    minimum_interval = minimum_interval,
                    maximum_interval = maximum_interval,
                    starting_ease = starting_ease,
                    easy_bonus = easy_bonus,
                    interval_modifier = interval_modifier,
                    hard_interval = hard_interval,
                    new_interval = new_interval
        )