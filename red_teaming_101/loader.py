import json
from pathlib import Path

from base import RedTeamLab


def load_challenges():
    challenges = []
    with open("json_paths.txt") as f:
        lab_file_paths = f.read().strip().splitlines()

    for lab_json in lab_file_paths:
        if not Path(lab_json).exists():
            raise FileNotFoundError(f"Lab configuration file not found: {lab_json}")
        with open(lab_json) as lab_file:
            lab_data = json.load(lab_file)
            challenges.append(lab_data)

    print(f"Loaded {len(challenges)} challenges from: {lab_file_paths}")
    return challenges


def get_lab_by_title(title):
    challenges = load_challenges()
    for challenge in challenges:
        if challenge["challenge_title"] == title:
            return RedTeamLab(challenge)
    raise ValueError("Lab not found")
