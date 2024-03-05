class Exercise:
    def __init__(self, type, target_reps, is_pro=None,):
        self.type = type  # Results: "Squats", "Push ups"
        self.target_reps = target_reps
        self.is_pro = is_pro
    
    def __str__(self):
        return f"Exercise: type = {self.type}, target_reps = {self.target_reps}, is_pro = {self.is_pro}"