from enum import IntEnum
from datetime import datetime, timezone
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

# TODO: implement scheduler class
class AnkiSM2Scheduler:
    
    # TODO: implement __init__
    def __init__(self):
        pass

    # TODO: implement review_card
    def review_card(self, card: Card, rating: Rating, review_datetime: Optional[datetime]=None):

        if review_datetime is None:
            review_datetime = datetime.now()

        review_log = ReviewLog(card=card, rating=rating, review_datetime=review_datetime)

        return None, review_log
    
    # TODO: implement to_dict
    def to_dict(self):
        pass

    # TODO: implement from_dict
    @staticmethod
    def from_dict():
        pass