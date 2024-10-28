from enum import IntEnum
from datetime import datetime, timezone
from typing import Optional

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

# TODO: implement ReviewLog class
class ReviewLog:
    pass

# TODO: implement scheduler class
class AnkiSM2Scheduler:
    pass