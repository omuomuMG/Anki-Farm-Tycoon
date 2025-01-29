from .animal import Animal

class Field:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.animal = None

    def add_animal(self, animal: Animal) -> bool:
        if self.animal is None:
            self.animal = animal
            return True
        return False

    def remove_animal(self) -> Animal:
        animal = self.animal
        self.animal = None
        return animal