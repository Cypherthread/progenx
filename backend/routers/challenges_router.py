import json
import random
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()

CHALLENGES_FILE = Path(__file__).parent.parent / "data" / "daily_challenges.json"


def load_challenges() -> list[dict]:
    with open(CHALLENGES_FILE) as f:
        return json.load(f)


@router.get("/daily")
def daily_challenge():
    """Return today's climate challenge prompt."""
    challenges = load_challenges()
    day_of_year = datetime.utcnow().timetuple().tm_yday
    challenge = challenges[day_of_year % len(challenges)]
    return challenge


@router.get("/random")
def random_challenge():
    """Return a random challenge prompt."""
    challenges = load_challenges()
    return random.choice(challenges)


@router.get("/all")
def all_challenges():
    """Return all challenge prompts."""
    return load_challenges()
