from dataclasses import dataclass
import importlib
import inspect
import pkgutil
import sys
import os

@dataclass
class Reflect:
    client_code_path:str
    imported_modules = {}

    def __post_init__(self):
        sys.path.insert(1, self.client_code_path)
        self.client_modules = [p for p in pkgutil.iter_modules() if str(p[0])[12:-2] == self.client_code_path]

    def import_module(self, module_name):
        """Imports a module. Before reflection can be conducted, a module
        must be imported. WARNING: This will execute module code if it isn't
        in a if __name__ == "__main__". Takes a module name (that the student made)
        as the first argument.

        Args:
            module_name (str): The name of a student's module to import
        """
        for module in self.client_modules:
            if module.name == module_name:
                self.imported_modules[module_name] = importlib.import_module(module.name)

    def get_module_doc(self, module_name):
        """Gets the documentation provided for a module.

        Args:
            module_name (str): The student's module name to get documentation for

        Returns:
            str: Provided documentation
        """
        return inspect.getdoc(self.imported_modules[module_name])

    def get_classes(self, module_name):
        """Gets the classes in a given module. The module must be imported first.

        Args:
            module_name (str): The name of an imported module to get the name of.

        Returns:
            dict: Dictionary of classes. The name of the class is the index, followed by
            a tuple containing the class object and the classes' documentation.
        """
        return {
            i[0]: (i[1], inspect.getdoc(i[1])) 
            for i in inspect.getmembers(self.imported_modules[module_name]) 
            if inspect.isclass(i[1])
        }

    def get_class_methods(self, module_name, class_name):
        """Gets the user generated methods of a given class. The module must be imported first.

        Args:
            module_name (str): The name of the module in which the class is contained.
            class_name (str): The name of the class.

        Returns:
            dict: A dictionary of the methods. The index is the function name, followed by a tuple
            containing the function object, the documentation, and a list of the named arguments. 
            WARNING: Does not deal with *args and **kwargs and stuff.
        """
        return {
            i[0]: (i[1], inspect.getdoc(i[1]), inspect.getfullargspec(i[1])[0]) 
            for i in inspect.getmembers(
                self.get_classes(module_name)[class_name][0], 
                predicate=inspect.isfunction
            )
        }

    def get_functions(self, module_name):
        return {
            i[0]: (i[1], inspect.getdoc(i[1]), inspect.getfullargspec(i[1])[0]) 
            for i in inspect.getmembers(self.imported_modules[module_name]) 
            if inspect.isfunction(i[1])
        }

if __name__ == "__main__":
    user_code_path = "/media/veracrypt1/Nextcloud/UniStuff/3.0 - CMP 3rd Year Project/ExampleSubmissions/Submission_A"
    
    reflect = Reflect(user_code_path)
    reflect.import_module("pjtool")
    print(reflect.get_class_methods("pjtool", "Date"))
