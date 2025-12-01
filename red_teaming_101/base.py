class RedTeamLab:
    def __init__(self, challenge):
        self.id = challenge["challenge_id"]
        self.title = challenge["challenge_title"]
        self.goal = challenge["goal"]
        self.metaprompt = challenge["metaprompt"]
        self.description = challenge["description"]
        self.desired_output = challenge["desired_output"]
        self.category = challenge["category"]
        self.scorer = challenge.get("Scorer", {})

        # internal chat log for this lab
        self.history = []

    def reset_history(self):
        self.history = []

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})

    def get_messages(self):
        """Combine system prompt + metaprompt + history"""
        messages = [
            {"role": "system", "content": self.metaprompt}
        ]
        messages.extend(self.history)
        return messages

    def evaluate(self, model_response):
        """Minimal regex evaluator"""
        import re

        if not self.scorer:
            print("[Evaluator] No scorer defined")
            return False, "No scorer defined"

        pattern = self.scorer.get("instruction")
        flags = 0 if self.scorer.get("isCaseSensitive", False) else re.IGNORECASE
        matched = re.search(pattern, model_response, flags)
        if matched:
            return True, self.scorer.get("message", "")

        print(f"[Evaluator] '{pattern}' did NOT match with response '{model_response}'")
        return False, "Try Again"
