from datetime import datetime, timezone, timedelta
from anki_sm_2 import Scheduler, Card, Rating, ReviewLog, State
import json
from copy import deepcopy
import random


class TestAnkiSM2:
    def test_good_learning_steps(self):
        scheduler = Scheduler()

        created_at = datetime.now(timezone.utc)
        card = Card()

        assert card.state == State.Learning
        assert card.step == 0

        rating = Rating.Good
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )

        assert card.state == State.Learning
        assert card.step == 1
        assert (
            round((card.due - created_at).total_seconds() / 100) == 6
        )  # card is due in approx. 10 minutes (600 seconds)

        rating = Rating.Good
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )
        assert card.state == State.Review
        assert card.step is None
        assert round((card.due - created_at).total_seconds() / 3600) == 24

    def test_again_learning_steps(self):
        scheduler = Scheduler()

        created_at = datetime.now(timezone.utc)
        card = Card()

        assert card.state == State.Learning
        assert card.step == 0

        rating = Rating.Again
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )

        assert card.state == State.Learning
        assert card.step == 0
        assert (
            round((card.due - created_at).total_seconds() / 10) == 6
        )  # card is due in approx. 1 minute (60 seconds)

    def test_hard_learning_steps(self):
        scheduler = Scheduler()

        created_at = datetime.now(timezone.utc)
        card = Card()

        assert card.state == State.Learning
        assert card.step == 0

        rating = Rating.Hard
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )

        assert card.state == State.Learning
        assert card.step == 0
        assert (
            round((card.due - created_at).total_seconds() / 10) == 33
        )  # card is due in approx. 5.5 minutes (330 seconds)

    def test_easy_learning_steps(self):
        scheduler = Scheduler()

        created_at = datetime.now(timezone.utc)
        card = Card()

        assert card.state == State.Learning
        assert card.step == 0

        rating = Rating.Easy
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )

        assert card.state == State.Review
        assert card.step is None
        assert (
            round((card.due - created_at).total_seconds() / 86400) == 4
        )  # card is due in approx. 4 days

    def test_review_state(self):
        scheduler = Scheduler()

        card = Card()

        rating = Rating.Good
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )

        rating = Rating.Good
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )

        assert card.state == State.Review
        assert card.step is None

        prev_due = card.due
        rating = Rating.Good
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )

        assert card.state == State.Review
        assert card.current_interval == 2
        assert (
            round((card.due - prev_due).total_seconds() / 3600) == 48
        )  # card is due in 2 days

        # rate the card again
        prev_due = card.due
        rating = Rating.Again
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )

        assert card.state == State.Relearning
        assert card.current_interval == 1
        assert (
            round((card.due - prev_due).total_seconds() / 60) == 10
        )  # card is due in 10 minutes

    def test_relearning(self):
        scheduler = Scheduler()

        card = Card()

        rating = Rating.Good
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )

        rating = Rating.Good
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )

        prev_due = card.due
        rating = Rating.Good
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )

        # rate the card again
        prev_due = card.due
        rating = Rating.Again
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )

        assert card.state == State.Relearning
        assert card.current_interval == 1
        assert card.step == 0
        assert (
            round((card.due - prev_due).total_seconds() / 60) == 10
        )  # card is due in 10 minutes

        prev_due = card.due
        rating = Rating.Again
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )

        assert card.state == State.Relearning
        assert card.current_interval == 1
        assert card.step == 0
        assert (
            round((card.due - prev_due).total_seconds() / 100) == 6
        )  # card is due in 10 minutes

        prev_due = card.due
        rating = Rating.Good
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_datetime=card.due
        )

        assert card.state == State.Review
        assert card.step is None
        assert card.current_interval == 2
        assert (
            round((card.due - prev_due).total_seconds() / 3600) == 48
        )  # card is due in 2 days

    def test_serialize(self):
        scheduler = Scheduler()

        card = Card()
        old_card = deepcopy(card)

        # card and scheduler are json-serializable
        assert type(json.dumps(card.to_dict())) == str
        assert type(json.dumps(scheduler.to_dict())) == str

        card_dict = card.to_dict()
        copied_card = Card.from_dict(card_dict)
        assert vars(card) == vars(copied_card)
        assert card.to_dict() == copied_card.to_dict()

        # scheduler can be serialized and de-serialized while remaining the same
        scheduler_dict = scheduler.to_dict()
        copied_scheduler = Scheduler.from_dict(scheduler_dict)
        assert vars(scheduler) == vars(copied_scheduler)
        assert scheduler.to_dict() == copied_scheduler.to_dict()

        rating = Rating.Good
        review_duration = 2000
        card, review_log = scheduler.review_card(
            card=card, rating=rating, review_duration=review_duration
        )

        # review log is json-serializable
        assert type(json.dumps(review_log.to_dict())) == str
        review_log_dict = review_log.to_dict()
        copied_review_log = ReviewLog.from_dict(review_log_dict)
        assert review_log.to_dict() == copied_review_log.to_dict()
        assert copied_review_log.review_duration == review_duration
        # can use the review log to recreate the card that was reviewed
        assert (
            old_card.to_dict() == Card.from_dict(review_log.to_dict()["card"]).to_dict()
        )
        assert card.to_dict() != old_card.to_dict()

    def test_fuzz(self):
        """
        Reviews a new card Good four times in a row with different random seeds.
        The size of the interval after the fourth review should be different.
        """

        scheduler = Scheduler()

        # seed 1
        random.seed(42)

        card = Card()
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Good, review_datetime=datetime.now(timezone.utc)
        )
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Good, review_datetime=card.due
        )
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Good, review_datetime=card.due
        )
        prev_due = card.due
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Good, review_datetime=card.due
        )
        interval = card.due - prev_due

        assert interval.days == 6

        # seed 2
        random.seed(12345)

        card = Card()
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Good, review_datetime=datetime.now(timezone.utc)
        )
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Good, review_datetime=card.due
        )
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Good, review_datetime=card.due
        )
        prev_due = card.due
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Good, review_datetime=card.due
        )
        interval = card.due - prev_due

        assert interval.days == 5

    def test_no_learning_steps(self):
        scheduler = Scheduler(learning_steps=())

        assert len(scheduler.learning_steps) == 0

        created_at = datetime.now(timezone.utc)
        card = Card()
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Again, review_datetime=datetime.now(timezone.utc)
        )

        assert card.state == State.Review
        interval = (card.due - created_at).days
        assert interval >= 1

    def test_no_relearning_steps(self):
        scheduler = Scheduler(relearning_steps=())

        assert len(scheduler.relearning_steps) == 0

        card = Card()
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Good, review_datetime=datetime.now(timezone.utc)
        )
        assert card.state == State.Learning
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Good, review_datetime=card.due
        )
        assert card.state == State.Review
        last_review = card.due
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Again, review_datetime=card.due
        )
        assert card.state == State.Review

        interval = (card.due - last_review).days
        assert interval >= 1

    def test_one_card_multiple_schedulers(self):
        scheduler_with_two_learning_steps = Scheduler(
            learning_steps=(timedelta(minutes=1), timedelta(minutes=10))
        )
        scheduler_with_no_learning_steps = Scheduler(learning_steps=())

        card = Card()

        assert len(scheduler_with_two_learning_steps.learning_steps) == 2
        card, _ = scheduler_with_two_learning_steps.review_card(
            card=card, rating=Rating.Good, review_datetime=datetime.now(timezone.utc)
        )
        assert card.state == State.Learning
        assert card.step == 1

        assert len(scheduler_with_no_learning_steps.learning_steps) == 0
        card, _ = scheduler_with_no_learning_steps.review_card(
            card=card, rating=Rating.Again, review_datetime=datetime.now(timezone.utc)
        )
        assert card.state == State.Review
        assert card.step is None

        scheduler_with_two_relearning_steps = Scheduler(
            relearning_steps=(
                timedelta(minutes=1),
                timedelta(minutes=10),
                timedelta(minutes=15),
            )
        )
        scheduler_with_no_relearning_steps = Scheduler(relearning_steps=())

        assert len(scheduler_with_two_relearning_steps.relearning_steps) == 3
        card, _ = scheduler_with_two_relearning_steps.review_card(
            card=card, rating=Rating.Again, review_datetime=datetime.now(timezone.utc)
        )
        assert card.state == State.Relearning
        assert card.step == 0

        card, _ = scheduler_with_two_relearning_steps.review_card(
            card=card, rating=Rating.Good, review_datetime=datetime.now(timezone.utc)
        )
        assert card.state == State.Relearning
        assert card.step == 1

        card, _ = scheduler_with_two_relearning_steps.review_card(
            card=card, rating=Rating.Good, review_datetime=datetime.now(timezone.utc)
        )
        assert card.state == State.Relearning
        assert card.step == 2

        card, _ = scheduler_with_no_relearning_steps.review_card(
            card=card, rating=Rating.Again, review_datetime=datetime.now(timezone.utc)
        )
        assert card.state == State.Review
        assert card.step is None

    def test_maximum_interval(self):
        maximum_interval = 100
        scheduler = Scheduler(maximum_interval=maximum_interval)

        card = Card()

        last_review = card.due
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Easy, review_datetime=card.due
        )
        assert (card.due - last_review).days <= scheduler.maximum_interval

        last_review = card.due
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Good, review_datetime=card.due
        )
        assert (card.due - last_review).days <= scheduler.maximum_interval

        last_review = card.due
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Easy, review_datetime=card.due
        )
        assert (card.due - last_review).days <= scheduler.maximum_interval

        last_review = card.due
        card, _ = scheduler.review_card(
            card=card, rating=Rating.Good, review_datetime=card.due
        )
        assert (card.due - last_review).days <= scheduler.maximum_interval
