from anki_sm_2 import AnkiSM2Scheduler, Card, Rating, ReviewLog
import json

class TestAnkiSM2:

    def test_card_serialize(self):

        card = Card()

        # card is json-serializable
        assert type(json.dumps(card.to_dict())) == str

        card_dict = card.to_dict()
        copied_card = Card.from_dict(card_dict)
        assert vars(card) == vars(copied_card)
        assert card.to_dict() == copied_card.to_dict()