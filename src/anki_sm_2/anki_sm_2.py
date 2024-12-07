"""
anki_sm_2.anki_sm_2

This module defines each of the classes used in the anki-sm-2 package.

Classes:
    State: Enum representing the learning state of a Card object.
    Rating: Enum representing the four possible Anki ratings when reviewing a card.
    Card: Represents a flashcard in the Anki system.
    Scheduler: The Anki SM-2 scheduler.
"""

from enum import IntEnum
from datetime import datetime, timezone, timedelta
from copy import deepcopy
from typing import Any
import math
import random


class State(IntEnum):
    """
    Enum representing the learning state of a Card object.
    """

    Learning = 1
    Review = 2
    Relearning = 3


class Rating(IntEnum):
    """
    Enum representing the four possible Anki ratings when reviewing a card.
    """

    Again = 1  # incorrect
    Hard = 2  # correct - had doubts about answer/or took long time to recall
    Good = 3  # correct - took some amount of mental effort to recall
    Easy = 4  # correct - recalled effortlessly


class Card:
    """
    Represents a flashcard in the Anki system.

    Attributes:
        card_id (int): The id of the card. Defaults to the epoch miliseconds of when the card was created.
        state (State): The card's current learning state.
        step (int | None): The card's current learning or relearning step or None if the card is in the Review state.
        ease (float | None): The card's current ease factor or None if the card is still in the Learning state.
        due (datetime): When the card is due for review.
        current_interval (int | None): The card's current interval length in days or None if the card is still in the Learning state.
                                       Note that when a card is lapsed, its current_interval is preserved through the relearning steps.
    """

    card_id: int
    state: State
    step: int | None
    ease: float | None
    due: datetime
    current_interval: int | None

    def __init__(
        self,
        card_id: int | None = None,
        state: State = State.Learning,
        step: int | None = None,
        ease: float | None = None,
        due: datetime | None = None,
        current_interval: int | None = None,
    ) -> None:
        if card_id is None:
            # epoch miliseconds of when the card was created
            card_id = int(datetime.now(timezone.utc).timestamp() * 1000)
        self.card_id = card_id

        self.state = state

        if self.state == State.Learning and step is None:
            step = 0
        self.step = step

        self.ease = ease

        if due is None:
            due = datetime.now(timezone.utc)
        self.due = due

        self.current_interval = current_interval

    def to_dict(self) -> dict[str, int | float | str | None]:
        return_dict = {
            "card_id": self.card_id,
            "state": self.state.value,
            "step": self.step,
            "ease": self.ease,
            "due": self.due.isoformat(),
            "current_interval": self.current_interval,
        }

        return return_dict

    @staticmethod
    def from_dict(source_dict: dict[str, Any]) -> "Card":
        card_id = int(source_dict["card_id"])
        state = State(int(source_dict["state"]))
        step = source_dict["step"]
        ease = source_dict["ease"]
        due = datetime.fromisoformat(source_dict["due"])
        current_interval = source_dict["current_interval"]

        return Card(
            card_id=card_id,
            state=state,
            step=step,
            ease=ease,
            due=due,
            current_interval=current_interval,
        )


class ReviewLog:
    """
    Represents the log entry of a Card object that has been reviewed.

    Attributes:
        card (Card): Copy of the card object that was reviewed.
        rating (Rating): The rating given to the card during the review.
        review_datetime (datetime): The date and time of the review.
        review_duration (int | None): The number of miliseconds it took to review the card or None if unspecified.
    """

    card: Card
    rating: Rating
    review_datetime: datetime
    review_duration: int | None

    def __init__(
        self,
        card: Card,
        rating: Rating,
        review_datetime: datetime,
        review_duration: int | None = None,
    ) -> None:
        self.card = deepcopy(card)
        self.rating = rating
        self.review_datetime = review_datetime
        self.review_duration = review_duration

    def to_dict(
        self,
    ) -> dict[str, dict[str, int | float | str | None] | int | str | None]:
        return_dict = {
            "card": self.card.to_dict(),
            "rating": self.rating.value,
            "review_datetime": self.review_datetime.isoformat(),
            "review_duration": self.review_duration,
        }

        return return_dict

    @staticmethod
    def from_dict(source_dict: dict[str, Any]) -> "ReviewLog":
        card = Card.from_dict(source_dict["card"])
        rating = Rating(int(source_dict["rating"]))
        review_datetime = datetime.fromisoformat(source_dict["review_datetime"])
        review_duration = source_dict["review_duration"]

        return ReviewLog(
            card=card,
            rating=rating,
            review_datetime=review_datetime,
            review_duration=review_duration,
        )


class Scheduler:
    """
    The Anki SM-2 scheduler.

    Enables the reviewing and future scheduling of cards according to the SM-2 based Anki scheduling algorithm.

    Attributes:
        learning_steps (tuple[timedelta, ...]): Small time intervals that schedule cards in the Learning state.
        graduating_interval (int): The number of days to wait before showing a card again, after the Good button is pressed on the final learning step.
        easy_interval (int): The number of days to wait before showing a card again, after the Easy button is used to immediately remove a card from learning.
        relearning_steps (tuple[timedelta, ...]): Small time intervals that schedule cards in the Relearning state.
        minimum_interval (int): The minimum interval (in days) given to a review card after answering Again.
        maximum_interval (int): The maximum number of days a Review-state card can be scheduled into the future.
        starting_ease (float): The initial ease factor given to cards that have completed the learning steps and become a Review-state card.
        easy_bonus (float): An extra multiplier that is applied to a review card's interval when you rate it Easy.
        interval_modifier (float): A factor used as a multiplier to determine future review interval lengths. It is used on Review-state cards and Relearning-state cards about to graduate the relearning steps.
        hard_interval (float): The multiplier applied to a review interval when answering Hard.
        new_interval (float): The multiplier applied to a review interval when answering Again.
    """

    learning_steps: tuple[timedelta, ...]
    graduating_interval: int
    easy_interval: int
    relearning_steps: tuple[timedelta, ...]
    minimum_interval: int
    maximum_interval: int
    starting_ease: float
    easy_bonus: float
    interval_modifier: float
    hard_interval: float
    new_interval: float

    def __init__(
        self,
        learning_steps: tuple[timedelta, ...] | list[timedelta] = (
            timedelta(minutes=1),
            timedelta(minutes=10),
        ),
        graduating_interval: int = 1,
        easy_interval: int = 4,
        relearning_steps: tuple[timedelta, ...] | list[timedelta] = (
            timedelta(minutes=10),
        ),
        minimum_interval: int = 1,
        maximum_interval: int = 36500,
        starting_ease: float = 2.5,
        easy_bonus: float = 1.3,
        interval_modifier: float = 1.0,
        hard_interval: float = 1.2,
        new_interval: float = 0.0,
    ) -> None:
        self.learning_steps = tuple(learning_steps)
        self.graduating_interval = graduating_interval
        self.easy_interval = easy_interval
        self.relearning_steps = tuple(relearning_steps)
        self.minimum_interval = minimum_interval
        self.maximum_interval = maximum_interval
        self.starting_ease = starting_ease
        self.easy_bonus = easy_bonus
        self.interval_modifier = interval_modifier
        self.hard_interval = hard_interval
        self.new_interval = new_interval

    def review_card(
        self,
        card: Card,
        rating: Rating,
        review_datetime: datetime | None = None,
        review_duration: int | None = None,
    ) -> tuple[Card, ReviewLog]:
        """
        Reviews a card with a given rating at a specified time and duration.

        Args:
            card (Card): The card being reviewed.
            rating (Rating): The chosen rating for the card being reviewed.
            review_datetime (datetime | None): The date and time of the review. If unspecified, the date and time will be the current time in UTC.
            review_duration (int | None): The number of miliseconds it took to review the card or None if unspecified.

        Returns:
            tuple: A tuple containing the updated, reviewed card and its corresponding review log.
        """

        card = deepcopy(card)

        if review_datetime is None:
            review_datetime = datetime.now(timezone.utc)

        review_log = ReviewLog(
            card=card,
            rating=rating,
            review_datetime=review_datetime,
            review_duration=review_duration,
        )

        if card.state == State.Learning:
            assert type(card.step) == int  # mypy

            # calculate the card's next interval
            # len(self.learning_steps) == 0: no learning steps defined so move card to Review state
            # card.step > len(self.learning_steps): handles the edge-case when a card was originally scheduled with a scheduler with more
            # learning steps than the current scheduler
            if len(self.learning_steps) == 0 or card.step > len(self.learning_steps):
                card.state = State.Review
                card.step = None
                card.ease = self.starting_ease
                card.current_interval = self.graduating_interval
                card.due = review_datetime + timedelta(days=card.current_interval)

            else:

                if rating == Rating.Again:
                    card.step = 0
                    card.due = review_datetime + self.learning_steps[card.step]

                elif rating == Rating.Hard:
                    # card step stays the same

                    if card.step == 0 and len(self.learning_steps) == 1:
                        card.due = review_datetime + (self.learning_steps[card.step] * 1.5)
                    elif card.step == 0 and len(self.learning_steps) >= 2:
                        card.due = review_datetime + (
                            (
                                self.learning_steps[card.step]
                                + self.learning_steps[card.step + 1]
                            )
                            / 2.0
                        )
                    else:
                        card.due = review_datetime + self.learning_steps[card.step]

                elif rating == Rating.Good:
                    if card.step + 1 == len(self.learning_steps):  # the last step
                        card.state = State.Review
                        card.step = None
                        card.ease = self.starting_ease
                        card.current_interval = self.graduating_interval
                        card.due = review_datetime + timedelta(days=card.current_interval)

                    else:
                        card.step += 1
                        card.due = review_datetime + self.learning_steps[card.step]

                elif rating == Rating.Easy:
                    card.state = State.Review
                    card.step = None
                    card.ease = self.starting_ease
                    card.current_interval = self.easy_interval
                    card.due = review_datetime + timedelta(days=card.current_interval)

        elif card.state == State.Review:
            assert type(card.ease) == float  # mypy
            assert type(card.current_interval) == int  # mypy

            if rating == Rating.Again: # the card is "lapsed"

                card.ease = max(1.3, card.ease * 0.80)  # reduce ease by 20%

                current_interval = max(
                    self.minimum_interval,
                    round(
                        card.current_interval
                        * self.new_interval
                        * self.interval_modifier
                    ),
                )
                card.current_interval = self._get_fuzzed_interval(current_interval)

                # if there are no relearning steps (they were left blank)
                if len(self.relearning_steps) > 0:

                    card.state = State.Relearning
                    card.step = 0

                    card.due = review_datetime + self.relearning_steps[card.step]

                else:

                    card.due = review_datetime + timedelta(days=card.current_interval)

            elif rating == Rating.Hard:
                card.ease = max(1.3, card.ease * 0.85)  # reduce ease by 15%
                current_interval = min(
                    self.maximum_interval,
                    round(
                        card.current_interval
                        * self.hard_interval
                        * self.interval_modifier
                    ),
                )
                card.current_interval = self._get_fuzzed_interval(current_interval)
                card.due = review_datetime + timedelta(days=card.current_interval)

            elif rating == Rating.Good:
                # ease stays the same

                days_overdue = (review_datetime - card.due).days
                if days_overdue >= 1:
                    current_interval = min(
                        self.maximum_interval,
                        round(
                            (card.current_interval + (days_overdue / 2.0))
                            * card.ease
                            * self.interval_modifier
                        ),
                    )

                else:
                    current_interval = min(
                        self.maximum_interval,
                        round(
                            card.current_interval * card.ease * self.interval_modifier
                        ),
                    )

                card.current_interval = self._get_fuzzed_interval(current_interval)

                card.due = review_datetime + timedelta(days=card.current_interval)

            elif rating == Rating.Easy:
                days_overdue = (review_datetime - card.due).days
                if days_overdue >= 1:
                    current_interval = min(
                        self.maximum_interval,
                        round(
                            (card.current_interval + days_overdue)
                            * card.ease
                            * self.easy_bonus
                            * self.interval_modifier
                        ),
                    )

                else:
                    current_interval = min(
                        self.maximum_interval,
                        round(
                            card.current_interval
                            * card.ease
                            * self.easy_bonus
                            * self.interval_modifier
                        ),
                    )

                card.current_interval = self._get_fuzzed_interval(current_interval)

                card.ease = card.ease * 1.15  # increase ease by 15%
                card.due = review_datetime + timedelta(days=card.current_interval)

        elif card.state == State.Relearning:
            assert type(card.step) == int  # mypy
            assert type(card.current_interval) == int  # mypy
            assert type(card.ease) == float  # mypy

            # calculate the card's next interval
            # len(self.relearning_steps) == 0: no relearning steps defined so move card to Review state
            # card.step > len(self.relearning_steps): handles the edge-case when a card was originally scheduled with a scheduler with more
            # relearning steps than the current scheduler
            if len(self.relearning_steps) == 0 or card.step > len(self.relearning_steps):
                card.state = State.Review
                card.step = None

                # don't update ease
                card.current_interval = min(
                    self.maximum_interval,
                    round(
                        card.current_interval * card.ease * self.interval_modifier
                    ),
                )
                card.due = review_datetime + timedelta(days=card.current_interval)

            else:

                if rating == Rating.Again:
                    card.step = 0
                    card.due = review_datetime + self.relearning_steps[card.step]

                elif rating == Rating.Hard:
                    # card step stays the same

                    if card.step == 0 and len(self.relearning_steps) == 1:
                        card.due = review_datetime + (
                            self.relearning_steps[card.step] * 1.5
                        )
                    elif card.step == 0 and len(self.relearning_steps) >= 2:
                        card.due = review_datetime + (
                            (
                                self.relearning_steps[card.step]
                                + self.relearning_steps[card.step + 1]
                            )
                            / 2.0
                        )
                    else:
                        card.due = review_datetime + self.relearning_steps[card.step]

                elif rating == Rating.Good:
                    if card.step + 1 == len(self.relearning_steps):  # the last step
                        card.state = State.Review
                        card.step = None
                        # don't update ease
                        card.current_interval = min(
                            self.maximum_interval,
                            round(
                                card.current_interval * card.ease * self.interval_modifier
                            ),
                        )
                        card.due = review_datetime + timedelta(days=card.current_interval)

                    else:
                        card.step += 1
                        card.due = review_datetime + self.relearning_steps[card.step]

                elif rating == Rating.Easy:
                    card.state = State.Review
                    card.step = None
                    # don't update ease
                    card.current_interval = min(
                        self.maximum_interval,
                        round(
                            card.current_interval
                            * card.ease
                            * self.easy_bonus
                            * self.interval_modifier
                        ),
                    )
                    card.due = review_datetime + timedelta(days=card.current_interval)

        return card, review_log

    def _get_fuzzed_interval(self, interval: int) -> int:
        """
        Takes the current calculated interval and adds a small amount of random fuzz to it.
        For example, a card that would've been due in 50 days, after fuzzing, might be due in 49, or 51 days.

        Args:
            interval (int): The calculated next interval, before fuzzing.

        Returns:
            int: The new interval, after fuzzing.
        """

        if interval < 2.5:  # fuzz is not applied to intervals less than 2.5
            return interval

        def _get_fuzz_range(interval: int) -> tuple[int, int]:
            """
            Helper function that computes the possible upper and lower bounds of the interval after fuzzing.
            """

            FUZZ_RANGES = [
                {
                    "start": 2.5,
                    "end": 7.0,
                    "factor": 0.15,
                },
                {
                    "start": 7.0,
                    "end": 20.0,
                    "factor": 0.1,
                },
                {
                    "start": 20.0,
                    "end": math.inf,
                    "factor": 0.05,
                },
            ]

            delta = 1.0
            for fuzz_range in FUZZ_RANGES:
                delta += fuzz_range["factor"] * max(
                    min(interval, fuzz_range["end"]) - fuzz_range["start"], 0.0
                )

            min_ivl = int(round(interval - delta))
            max_ivl = int(round(interval + delta))

            # make sure the min_ivl and max_ivl fall into a valid range
            min_ivl = max(2, min_ivl)
            max_ivl = min(max_ivl, self.maximum_interval)
            min_ivl = min(min_ivl, max_ivl)

            return min_ivl, max_ivl

        min_ivl, max_ivl = _get_fuzz_range(interval)

        fuzzed_interval = (
            random.random() * (max_ivl - min_ivl + 1)
        ) + min_ivl  # the next interval is a random value between min_ivl and max_ivl

        fuzzed_interval = min(round(fuzzed_interval), self.maximum_interval)

        return fuzzed_interval

    def to_dict(self) -> dict[str, Any]:
        return_dict = {
            "learning_steps": [
                int(learning_step.total_seconds())
                for learning_step in self.learning_steps
            ],
            "graduating_interval": self.graduating_interval,
            "easy_interval": self.easy_interval,
            "relearning_steps": [
                int(relearning_step.total_seconds())
                for relearning_step in self.relearning_steps
            ],
            "minimum_interval": self.minimum_interval,
            "maximum_interval": self.maximum_interval,
            "starting_ease": self.starting_ease,
            "easy_bonus": self.easy_bonus,
            "interval_modifier": self.interval_modifier,
            "hard_interval": self.hard_interval,
            "new_interval": self.new_interval,
        }

        return return_dict

    @staticmethod
    def from_dict(source_dict: dict[str, Any]) -> "Scheduler":
        learning_steps = [
            timedelta(seconds=learning_step)
            for learning_step in source_dict["learning_steps"]
        ]
        graduating_interval = source_dict["graduating_interval"]
        easy_interval = source_dict["easy_interval"]
        relearning_steps = [
            timedelta(seconds=relearning_step)
            for relearning_step in source_dict["relearning_steps"]
        ]
        minimum_interval = source_dict["minimum_interval"]
        maximum_interval = source_dict["maximum_interval"]
        starting_ease = source_dict["starting_ease"]
        easy_bonus = source_dict["easy_bonus"]
        interval_modifier = source_dict["interval_modifier"]
        hard_interval = source_dict["hard_interval"]
        new_interval = source_dict["new_interval"]

        return Scheduler(
            learning_steps=learning_steps,
            graduating_interval=graduating_interval,
            easy_interval=easy_interval,
            relearning_steps=relearning_steps,
            minimum_interval=minimum_interval,
            maximum_interval=maximum_interval,
            starting_ease=starting_ease,
            easy_bonus=easy_bonus,
            interval_modifier=interval_modifier,
            hard_interval=hard_interval,
            new_interval=new_interval,
        )
