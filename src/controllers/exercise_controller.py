from models.exercise import Exercise

class ExerciseController:

    EXERCISE_LIST = ['Squats', 'Push ups']

    EXERCISE_BASE_REPS = {
    'Squats': 10,
    'Push ups': 5
    }

    def assign_exercises(self, body, type):
        
        if type not in self.EXERCISE_LIST:
            raise ValueError("Unsupported exercise type")

        base_reps = self.EXERCISE_BASE_REPS[type]
        is_pro = False
        
        # Age adjustments
        if body.age in ['0-2', '4-6', '8-12']:
            reps_modifier = 0.5
        elif body.age in ['15-20', '25-32']:
            reps_modifier = 1
        elif body.age in ['38-43', '48-53']:
            reps_modifier = 0.75
        elif body.age in ['60-100']:
            reps_modifier = 0.5
            is_pro = False  # Safety for the elderly
        
        # Gender adjustments
        gender_modifier = 1.2 if body.gender == 'Man' else 1

        # Adjustments for complexion
        if body.complexion == 'Ectomorph':
            complexion_modifier = 1.1
            is_pro = True
        elif body.complexion == 'Mesomorph':
            complexion_modifier = 1
            is_pro = True
        else:  # Endomorph
            complexion_modifier = 0.9

        # Calculate adjusted repetitions
        target_reps = int(base_reps * reps_modifier * gender_modifier * complexion_modifier)
        return Exercise(type=type, target_reps=target_reps, is_pro=is_pro)
    