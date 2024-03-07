class Face:
    def __init__(self, face, eyes):
        self.face = face
        self.eyes = eyes

    def __str__(self):
        return f"Face: face = {self.face}, eyes = {self.eyes}"