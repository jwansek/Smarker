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
        for module in self.client_modules:
            if module.name == module_name:
                self.imported_modules[module_name] = importlib.import_module(module.name)

    def get_module_doc(self, module_name):
        return inspect.getdoc(self.imported_modules[module_name])


if __name__ == "__main__":
    user_code_path = "/media/veracrypt1/Nextcloud/UniStuff/3.0 - CMP 3rd Year Project/ExampleSubmissions/Submission_A"
    
    reflect = Reflect(user_code_path)
    reflect.import_module("pjtool")
    print(reflect.get_module_doc("pjtool"))
