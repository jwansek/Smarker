import tkinter as tk

class Application(tk.Tk):
    """An example class, which implements a GUI by inheriting from tkinter.Tk
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Hello World!")

    def a_method_with_defaults(self, arg_1 = "hello", arg_2 = "world"):
        """Adds two strings together with a space between them.

        Args:
            arg_1 (str, optional): The first string to add. Defaults to "hello".
            arg_2 (str, optional): The second string to add. Defaults to "world".

        Returns:
            str: A concatinated string.
        """
        return "%s %s" % (arg_1, arg_2)

    def add(self, num1:int, num2:int) -> int:
        """Adds two numbers together and returns the output

        Args:
            num1 (int): The first number to add
            num2 (int): The second number to add

        Returns:
            int: The two numbers added together
        """
        return num1 + num2

def hello_world(times):
    """Prints 'hello world!' to stdout. Prints it out `times` times.

    Args:
        times (int): The number of times to print out hello world.

    Returns:
        str: Hello world, repeated as many times as nessicary
    """
    return "hello world! " * 3

def an_undocumented_function():
    return 3.14156

if __name__ == "__main__":
    app = Application()
    app.mainloop()