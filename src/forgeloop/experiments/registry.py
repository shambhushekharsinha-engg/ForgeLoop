class ExperimentRegistry:
    def __init__(self):
        self.experiments = {}

    def register(self, experiment):
        if experiment.id in self.experiments:
            raise ValueError(f"Experiment {experiment.id} is already registered")
        self.experiments[experiment.id] = experiment

    def get_next_id(self):
        suffixes = [
            int(key[4:])
            for key in self.experiments
            if key.startswith("EXP-") and key[4:].isdigit()
        ]
        return f"EXP-{max(suffixes, default=0) + 1:03d}"
