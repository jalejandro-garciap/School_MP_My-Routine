class User:
    def __init__(self, first_name=None, last_name=None, email=None, type=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.type = type  # Results: Children (1), Student (2), Teacher (3), Disabled (4), Elderly (5)

    def __str__(self):
        return f"User: first_name = {self.first_name}, last_name = {self.last_name}, email = {self.email}, type = {self.type}"