import datetime

class Animal:
    def __init__(self):
        self.birthday = datetime.datetime.now()

    def move(self):
        return "*moves*"

class Dog(Animal):
    def speak(self):
        return "woof"

class Cat(Animal):
    def speak(self):
        return "meow"

class Kitten(Cat):
    """nyaa~~~
    """
    def speak(self):
        return "meow (but cuter)"
