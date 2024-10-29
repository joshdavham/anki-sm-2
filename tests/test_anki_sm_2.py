from anki_sm_2 import AnkiSM2Scheduler, Card, Rating, ReviewLog
import json

class TestAnkiSM2:

    def test_serialize(self):

        scheduler = AnkiSM2Scheduler()

        card = Card()

        # card and scheduler are json-serializable
        assert type(json.dumps(card.to_dict())) == str
        assert type(json.dumps(scheduler.to_dict())) == str

        card_dict = card.to_dict()
        copied_card = Card.from_dict(card_dict)
        assert vars(card) == vars(copied_card)
        assert card.to_dict() == copied_card.to_dict()

        # scheduler can be serialized and de-serialized while remaining the same
        scheduler_dict = scheduler.to_dict()
        copied_scheduler = AnkiSM2Scheduler.from_dict(scheduler_dict)
        assert vars(scheduler) == vars(copied_scheduler)
        assert scheduler.to_dict() == copied_scheduler.to_dict()

        rating = Rating.Good
        _, review_log = scheduler.review_card(card, rating)

        # review log is json-serializable
        assert type(json.dumps(review_log.to_dict())) == str
        review_log_dict = review_log.to_dict()
        copied_review_log = ReviewLog.from_dict(review_log_dict)
        assert review_log.to_dict() == copied_review_log.to_dict()

        # TODO: show that you can use the review log to recreate the card that was reviewed

        # TODO: show that the new card can be serialized and de-serialized while remaining the same