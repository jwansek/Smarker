from dataclasses import dataclass
from functools import reduce
from operator import getitem
import importlib
import inspect
import pkgutil
import sys
import os
import re

@dataclass
class Reflect:
    client_code_path:str
    imported_modules = {}

    def __post_init__(self):
        self.client_code_path = os.path.normpath(self.client_code_path)
        sys.path.insert(1, self.client_code_path)
        self.client_modules = [p for p in pkgutil.iter_modules() if os.path.normpath(str(p[0])[12:-2]) == self.client_code_path]

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
        return {
            "comments": inspect.getcomments(self.imported_modules[module_name]), 
            "doc": inspect.getdoc(self.imported_modules[module_name])
        }

    def get_classes(self, module_name):
        """Gets the classes in a given module. The module must be imported first.

        Args:
            module_name (str): The name of an imported module to get the name of.

        Returns:
            dict: Dictionary of classes. The name of the class is the index, followed by
            a tuple containing the class object and the classes' documentation.
        """
        return {
            i[0]: (i[1], {"comments": inspect.getcomments(i[1]), "doc": inspect.getdoc(i[1])}) 
            for i in inspect.getmembers(self.imported_modules[module_name]) 
            if inspect.isclass(i[1]) and self.get_class_full_name(i[1]).split(".")[0] in self.imported_modules.keys()
        }

    def get_class_methods(self, module_name, class_name):
        """Gets the user generated methods of a given class. The module must be imported first.

        Args:
            module_name (str): The name of the module in which the class is contained.
            class_name (str): The name of the class.

        Returns:
            dict: A dictionary of the methods. The index is the function name, followed by a tuple
            containing the function object, the documentation, and the args as a nicely formatted string.
        """
        return {
            i[0]: (
                i[1], 
                {"comments": inspect.getcomments(i[1]), "doc": inspect.getdoc(i[1])}, 
                str(inspect.signature(i[1]))
            )
            for i in inspect.getmembers(
                self.get_classes(module_name)[class_name][0], 
                predicate=inspect.isfunction
            )
        }

    def get_functions(self, module_name):
        return {
            i[0]: (
                i[1], 
                {"comments": inspect.getcomments(i[1]), "doc": inspect.getdoc(i[1])}, 
                str(inspect.signature(i[1])) 
            )
            for i in inspect.getmembers(self.imported_modules[module_name]) 
            if inspect.isfunction(i[1])
        }

    def get_class_full_name(self, class_):
        if class_.__module__ in ['builtins', 'exceptions']:
            return class_.__name__
        return "%s.%s" % (class_.__module__, class_.__name__)

    # classes that inherit from two classes doesn't print out nicely here.
    # using this method is better https://pastebin.com/YuxkkTkv
    def get_class_tree(self):
        """Generates a dictionary based tree structure showing inheritance of classes
        of all the *imported modules*. WARNING: It doesn't deal well with multiple inheritance..
        Read the comments.
        """

        def expand(a:list):
            out = []
            for l in a:
                for i in reversed(range(0, len(l))):
                    out.append(l[:len(l) - i])
            return out

        # https://www.geeksforgeeks.org/python-convert-a-list-of-lists-into-tree-like-dict/
        def getTree(tree, mappings):
            return reduce(getitem, mappings, tree)
            
        # https://www.geeksforgeeks.org/python-convert-a-list-of-lists-into-tree-like-dict/
        def setTree(tree, mappings):
            getTree(tree, mappings[:-1])[mappings[-1]] = dict()

        unexpanded_class_paths = []
        for module in self.imported_modules.keys():
            for class_ in self.get_classes(module).values():
                unexpanded_class_paths.append([
                    self.get_class_full_name(i) 
                    for i in reversed(list(inspect.getmro(class_[0])))
                ])
        tree = {}
        added = []  # the expander makes duplicates. keep a list to remove them
                        # sadly a collections.Counter doesnt work with lists of lists    
        for s in expand(unexpanded_class_paths):
            if s not in added:
                setTree(tree, [i for i in reversed(s)][::-1])
                added.append(s)

        # return inspect.getclasstree(classes)
        return tree

def gen_reflection_report(client_code_path, assessment_struct):
    reflection = Reflect(client_code_path)
    present_module_names = [i.name for i in reflection.client_modules]
    out = assessment_struct

    for i, required_file in enumerate(assessment_struct["files"], 0):
        required_file = list(required_file.keys())[0]
        module_name = os.path.splitext(required_file)[0]

        if module_name in present_module_names:
            out["files"][i][required_file]["present"] = True
        else:
            out["files"][i][required_file]["present"] = False
            continue

        reflection.import_module(module_name)
        required_files_features = assessment_struct["files"][i][required_file]
        out["files"][i][required_file]["documentation"] = reflection.get_module_doc(module_name)
        if "classes" in required_files_features.keys():

            present_classes = reflection.get_classes(module_name)
            for j, class_name in enumerate(required_files_features["classes"], 0):
                class_name = list(class_name.keys())[0]
                
                stop_here_flag = False
                # surprised the yaml parser doesnt do this automatically...
                if out["files"][i][required_file]["classes"][j][class_name] is None:
                    out["files"][i][required_file]["classes"][j][class_name] = {}
                    stop_here_flag = True

                if class_name in present_classes.keys():
                    out["files"][i][required_file]["classes"][j][class_name]["present"] = True
                else:
                    out["files"][i][required_file]["classes"][j][class_name]["present"] = False
                    continue
                
                # print( present_classes[class_name][1])
                out["files"][i][required_file]["classes"][j][class_name]["documentation"] = present_classes[class_name][1]

                if stop_here_flag:
                    continue

                present_methods = reflection.get_class_methods(module_name, class_name)
                
                for k, required_method in enumerate(assessment_struct["files"][i][required_file]["classes"][j][class_name]["methods"], 0):
                    out["files"][i][required_file]["classes"][j][class_name]["methods"][k] = {required_method: {}}

                    method_name = re.sub(r"\(\d+\)", "", required_method)
                    if method_name in present_methods.keys():
                        out["files"][i][required_file]["classes"][j][class_name]["methods"][k][required_method]["present"] = True
                    else:
                        out["files"][i][required_file]["classes"][j][class_name]["methods"][k][required_method]["present"] = False
                        continue

                    out["files"][i][required_file]["classes"][j][class_name]["methods"][k][required_method]["arguments"] = present_methods[method_name][-1]
                    out["files"][i][required_file]["classes"][j][class_name]["methods"][k][required_method]["documentation"] = present_methods[method_name][-2]

        if "functions" in required_files_features.keys():
            present_functions = reflection.get_functions(module_name)
            for j, required_function in enumerate(assessment_struct["files"][i][required_file]["functions"], 0):
                function_name = re.sub(r"\(\d+\)", "", required_function)
                out["files"][i][required_file]["functions"][j] = {required_function: {}}

                if function_name in present_functions.keys():
                    out["files"][i][required_file]["functions"][j][required_function]["present"] = True
                else:
                    out["files"][i][required_file]["functions"][j][required_function]["present"] = False
                    continue

                out["files"][i][required_file]["functions"][j][required_function]["documentation"] = present_functions[function_name][-2]    
                out["files"][i][required_file]["functions"][j][required_function]["arguments"] = present_functions[function_name][-1]    

    out["class_tree"] = reflection.get_class_tree()
    return out

if __name__ == "__main__":
    user_code_path = "D:\\Edencloud\\UniStuff\\3.0 - CMP 3rd Year Project\\Smarker\\../ExampleSubmissions/Submission_A"
    
    reflect = Reflect(user_code_path)
    reflect.import_module("pjtool")
    for c, v in reflect.get_classes(("pjtool")).items():
        print(c, v)
