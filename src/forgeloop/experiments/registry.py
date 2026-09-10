class ExperimentRegistry:
    def __init__(self):
        self.experiments = {}
    
    def register(self, experiment):
        self.experiments[experiment.id] = experiment
        
    def get_next_id(self):
        return f"EXP-{len(self.experiments) + 1:03d}"
