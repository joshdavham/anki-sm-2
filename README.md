<div align="center">
  <img src="https://avatars.githubusercontent.com/u/96821265?s=200&v=4" height="100" alt="Open Spaced Repetition logo"/>
</div>
<div align="center">

# Anki SM-2
</div>

<div align="center">
  <em>🌟 Anki's legacy SM-2-based spaced repetition algorithm 🌟</em>
</div>
<br />
<div align="center" style="text-decoration: none;">
    <a href="https://pypi.org/project/anki-sm-2/"><img src="https://img.shields.io/pypi/v/anki-sm-2"></a>
    <a href="https://github.com/open-spaced-repetition/anki-sm-2/blob/main/LICENSE" style="text-decoration: none;"><img src="https://img.shields.io/badge/License-AGPL--3.0-brightgreen.svg"></a>
</div>
<br />

<div align="left">
    <strong>
    Python package implementing Anki's <a href="https://docs.ankiweb.net/deck-options.html#new-cards">SM-2-based algorithm</a> for spaced repetition scheduling.
    </strong>
</div>

## Installation

You can install the anki-sm-2 python package from [PyPI](https://pypi.org/project/anki-sm-2/) using pip:
```
pip install anki-sm-2
```

## Quickstart

Import and initialize the Anki SM-2 Scheduler

```python
from anki_sm_2 import Scheduler, Card, Rating

scheduler = Scheduler()
```

Create a new Card object

```python
card = Card()
```

Choose a rating and review the card

```python
"""
Rating.Again # (==0) forgot the card
Rating.Hard # (==1) remembered the card, but with serious difficulty
Rating.Good # (==2) remembered the card after a hesitation
Rating.Easy # (==3) remembered the card easily
"""

rating = Rating.Good

card, review_log = scheduler.review_card(card, rating)

print(f"Card rated {review_log.rating} at {review_log.review_datetime}")
# > Card rated 3 at 2024-10-31 01:36:57.080934+00:00
```

See when the card is due next
```python
from datetime import datetime, timezone

due = card.due

# how much time between when the card is due and now
time_delta = due - datetime.now(timezone.utc)

print(f"Card due: at {due}")
print(f"Card due in {time_delta.seconds / 60} minutes")
# > Card due: at 2024-10-31 01:46:57.080934+00:00
# > Card due in 9.983333333333333 minutes
```

## Usage

### Timezone

Anki SM-2 uses UTC time only. You can still specify custom datetimes, but they must be UTC.

```python
from anki_sm_2 import Scheduler, Card, Rating, ReviewLog
from datetime import datetime, timezone

scheduler = Scheduler()

# create a new card to be due on Jan. 1, 2024
card = Card(due=datetime(2024, 1, 1, 0, 0, 0, 0, timezone.utc)) # right
#card = Card(due=datetime(2024, 1, 1, 0, 0, 0, 0)) # wrong

# review the card on Jan. 2, 2024
card, review_log = scheduler.review_card(card=card, rating=Rating.Good, review_datetime=datetime(2024, 1, 2, 0, 0, 0, 0, timezone.utc)) # right
#card, review_log = scheduler.review_card(card=card, rating=Rating.Good, review_datetime=datetime(2024, 1, 2, 0, 0, 0, 0)) # wrong
```

### Serialization

`Scheduler`, `Card` and `ReviewLog` objects are all json-serializable via their `to_dict` and `from_dict` methods for easy database storage:
```python
# serialize before storage
scheduler_dict = scheduler.to_dict()
card_dict = card.to_dict()
review_log_dict = review_log.to_dict()

# deserialize from dict
scheduler = Scheduler.from_dict(scheduler_dict)
card = Card.from_dict(card_dict)
review_log = ReviewLog.from_dict(review_log_dict)
```

## Versioning

This python package is currently unstable and adheres to the following versioning scheme:

- **Minor** version will increase when a backward-incompatible change is introduced.
- **Patch** version will increase when a bug is fixed, a new feature is added or when anything else backward compatible warrants a new release.

Once this package is considered stable, the **Major** version will be bumped to 1.0.0 and will follow [semver](https://semver.org/).

## Contribute

Checkout [CONTRIBUTING](https://github.com/open-spaced-repetition/anki-sm-2/blob/main/CONTRIBUTING.md) to help improve Anki SM-2!

## Official implementation

You can find the code for Anki's official Rust-based scheduler [here](https://github.com/ankitects/anki/tree/main/rslib/src/scheduler).