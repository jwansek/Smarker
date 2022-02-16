import datetime

class Animal:
    def __init__(self):
        self.birthday = datetime.datetime.now()

    def move(self):
        return "*moves*"

class Dog(Animal):
    """Some

    multiline

    docs"""
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

kitten = Kitten()
with open("animals.txt", "w") as f:
    f.write(kitten.speak())