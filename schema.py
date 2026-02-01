class AdSchema:
    def __init__(self):
        self.data = {
            "campaign_name": None,
            "objective": None,
            "creative": {
                "text": None,
                "cta": None,
                "music_id": None
            }
        }

    def is_complete(self):
        return (
            self.data["campaign_name"] and
            self.data["objective"] and
            self.data["creative"]["text"] and
            self.data["creative"]["cta"]
        )

    def validate_rules(self):
        errors = []

        if len(self.data["campaign_name"]) < 3:
            errors.append("Campaign name must be at least 3 characters")

        if self.data["objective"] not in ["Traffic", "Conversions"]:
            errors.append("Objective must be Traffic or Conversions")

        if len(self.data["creative"]["text"]) > 100:
            errors.append("Ad text must be ≤ 100 characters")

        # 🎵 MUSIC RULE (PRIMARY EVALUATION)
        if not self.data["creative"]["music_id"]:
            if self.data["objective"] == "Conversions":
                errors.append("Music is REQUIRED for Conversions objective")

        return errors
