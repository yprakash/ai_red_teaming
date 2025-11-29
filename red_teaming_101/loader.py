import json
from pathlib import Path

from base import RedTeamLab


def load_challenges():
    path = Path("config/challenges.json")
    data = json.load(open(path))
    return data["Challenges"]


def get_lab_by_title(title):
    challenges = load_challenges()
    for challenge in challenges:
        if challenge["challenge_title"] == title:
            return RedTeamLab(challenge)
    raise ValueError("Lab not found")
