class Body:
    def __init__(self, age=None, gender=None, height=None, complexion=None):
        self.age = age
        self.gender = gender
        self.height = height
        self.complexion = complexion  # Results: Endomorph, Mesomorph, Ectomorph

    def __str__(self):
        return f"Body: age = {self.age}, gender = {self.gender}, height = {self.height} cm, complexion = {self.complexion}"