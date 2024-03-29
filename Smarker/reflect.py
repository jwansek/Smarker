import xml.etree.ElementTree as etree
from dataclasses import dataclass
from functools import reduce
from operator import getitem
import jinja_helpers
import misc_classes
import subprocess
import importlib
import traceback
import tempfile
import database
import inspect
import pkgutil
import shutil
import jinja2
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
        # print("client moduules ", self.client_modules)

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
                try:
                    self.imported_modules[module_name] = importlib.import_module(module.name)
                except ModuleNotFoundError as e:
                    print("Missing library dependency for client module:")
                    print(e)
                    exit()
                # except Exception as e:
                #     print("CRITICAL ERROR IN CLIENT CODE - CANNOT CONTINUE")
                #     raise ClientCodeException(e)

    def get_module_doc(self, module_name):
        """Gets the documentation provided for a module.

        Args:
            module_name (str): The student's module name to get documentation for

        Returns:
            str: Provided documentation
        """
        return {
            "comments": self.__format_doc(inspect.getcomments(self.imported_modules[module_name])), 
            "doc": self.__format_doc(inspect.getdoc(self.imported_modules[module_name]))
        }

    def get_module_source(self, module_name):
        return inspect.getsource(self.imported_modules[module_name]).rstrip()

    def get_classes(self, module_name):
        """Gets the classes in a given module. The module must be imported first.

        Args:
            module_name (str): The name of an imported module to get the name of.

        Returns:
            dict: Dictionary of classes. The name of the class is the index, followed by
            a tuple containing the class object and the classes' documentation.
        """
        return {
            i[0]: (i[1], {"comments": self.__format_doc(inspect.getcomments(i[1])), "doc": self.__format_doc(inspect.getdoc(i[1]))}) 
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
                {"comments": self.__format_doc(inspect.getcomments(i[1])), "doc": self.__format_doc(inspect.getdoc(i[1]))}, 
                str(inspect.signature(i[1])),
                inspect.getsource(i[1]).rstrip()
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
                {"comments": self.__format_doc(inspect.getcomments(i[1])), "doc": self.__format_doc(inspect.getdoc(i[1]))}, 
                str(inspect.signature(i[1])),
                inspect.getsource(i[1]).rstrip() 
            )
            for i in inspect.getmembers(self.imported_modules[module_name]) 
            if inspect.isfunction(i[1])
        }

    def get_class_full_name(self, class_):
        """Returns the name of a class object as a nice string. e.g. modulename.classname
        except if it's a builtin there'll be no module name.

        Args:
            class_ (class): A class to get the name of

        Returns:
            str: A nicely formatted class name.
        """
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

        # print(tree)
        # return inspect.getclasstree(classes)
        return tree

    def run_tests(self, tests, run_colourful = False):
        """Build and run pytests from the configuration yaml. Indentation needs to 
        be four spaces only otherwise it won't work. We recommend running this last
        so all modules are already imported.

        Args:
            tests (dict): dict with the filename as the key followed by a list of 
            python code to make the test
            run_colourful (bool, optional): Run pytest again, printing out the 
            exact output of pytest as soon as it's ready. Has the advantage that 
            colours are preserved, but is only useful for when the user wants to 
            print out the report to stdout. Defaults to False.

        Returns:
            [dict]: A dictionary consisting of the pytest output string, junit xml
            output (which might be useful for rendering nicely in some output formats)
            and some nice meta information.
        """
        test_results = {}
        test_results["pytest_report"] = ""
        
        with open(os.path.join(os.path.split(__file__)[0], "pytest_template.jinja2"), "r") as f:
            jinja_template = jinja2.Template(f.read())

        for filename, filestests in tests.items():
            with open(os.path.join(self.client_code_path, "test_" + filename), "w") as f:
                f.write(jinja_template.render(
                    module = os.path.splitext(filename)[0], 
                    filestests = filestests, 
                    enumerate = enumerate       # a function thats needed
                ))

        with tempfile.TemporaryDirectory() as tmp:
            junitxmlpath = os.path.join(tmp, "report.xml")
            test_files = [os.path.join(self.client_code_path, "test_%s" % f) for f in tests.keys()]
            cmd = ["pytest", "-vv"] + test_files + ["--junitxml=%s" % junitxmlpath]
            # print("cmd: ", " ".join(cmd))
            if test_files == []:
                test_results["pytest_report"] = "*** No Tests ***"
                return test_results
            proc = subprocess.Popen(cmd, stdout = subprocess.PIPE)
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                test_results["pytest_report"] += line.decode()

            with open(junitxmlpath, "r") as f:
                test_results["junitxml"] = f.read()
        root = etree.fromstring(test_results["junitxml"])
        test_results["meta"] = root.findall("./testsuite")[0].attrib

        if run_colourful:
            subprocess.run(cmd)

        return test_results

    def __format_doc(*doc):
        return str(doc[1]).rstrip()
            
def gen_reflection_report(client_code_path, assessment_struct, student_no, configuration, zip_file):
    reflection = Reflect(client_code_path)
    present_module_names = [i.name for i in reflection.client_modules]
    out = assessment_struct
    out["student_no"] = student_no
    tests_to_run = {}
    files_sources = {}

    try:
        produced_files = assessment_struct["produced_files"]
    except KeyError:
        produced_files = []

    for i, required_file in enumerate(assessment_struct["files"], 0):
        required_file = list(required_file.keys())[0]
        module_name = os.path.splitext(required_file)[0]

        files_sources[required_file] = None

        if module_name in present_module_names:
            out["files"][i][required_file]["present"] = True
        else:
            out["files"][i][required_file]["present"] = False
            continue

        try:
            reflection.import_module(module_name)
        except Exception as e:
            out["files"][i][required_file]["has_exception"] = True
            out["files"][i][required_file]["exception"] = {}
            out["files"][i][required_file]["exception"]["type"] = str(type(e))
            out["files"][i][required_file]["exception"]["str"] = str(e)
            # TODO: test this indexing so we can be sure we're getting client code only
            e_list = traceback.format_exception(None, e, e.__traceback__)
            out["files"][i][required_file]["exception"]["traceback"] = ''.join([e_list[0]] + e_list[12:])

            continue

        required_files_features = assessment_struct["files"][i][required_file]
        out["files"][i][required_file]["has_exception"] = False
        out["files"][i][required_file]["documentation"] = reflection.get_module_doc(module_name)
        files_sources[required_file] = reflection.get_module_source(module_name)
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

                    out["files"][i][required_file]["classes"][j][class_name]["methods"][k][required_method]["arguments"] = present_methods[method_name][-2]
                    out["files"][i][required_file]["classes"][j][class_name]["methods"][k][required_method]["minimum_arguments"] = present_methods[method_name][-2].count(",") + 1
                    out["files"][i][required_file]["classes"][j][class_name]["methods"][k][required_method]["documentation"] = present_methods[method_name][-3]
                    out["files"][i][required_file]["classes"][j][class_name]["methods"][k][required_method]["source_code"] =  present_methods[method_name][-1]

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

                out["files"][i][required_file]["functions"][j][required_function]["documentation"] = present_functions[function_name][-3]    
                out["files"][i][required_file]["functions"][j][required_function]["arguments"] = present_functions[function_name][-2]    
                out["files"][i][required_file]["functions"][j][required_function]["minimum_arguments"] = present_functions[function_name][-2].count(",") + 1    
                out["files"][i][required_file]["functions"][j][required_function]["source_code"] = present_functions[function_name][-1]

        if "tests" in required_files_features.keys():
            filename = list(assessment_struct["files"][i].keys())[0]
            if not out["files"][i][filename]["has_exception"]:
                for j, test in enumerate(assessment_struct["files"][i][required_file]["tests"], 0):
                    try:
                        tests_to_run[filename].append(test)
                    except KeyError:
                        tests_to_run[filename] = [test]

        if "run" in required_files_features.keys():
            filename = list(assessment_struct["files"][i].keys())[0]
            with misc_classes.ExtractZipToTempDir(zip_file) as tempdir:
                with misc_classes.FileDependencies(assessment_struct, tempdir):
                    with misc_classes.ChangeDirectory(tempdir):
                        for j, runtime in enumerate(assessment_struct["files"][i][required_file]["run"], 0):
                            for cmd, contents in runtime.items():
                                lines = ""
                                if "monitor" in contents.keys():

                                    if contents["monitor"] not in produced_files:
                                        raise MonitoredFileNotInProducedFilesException("The monitored file %s is not in the list of produced files. It needs to be added." % contents["monitor"])

                                    subprocess.run(cmd.split())
                                    if os.path.exists(contents["monitor"]):
                                        with open(contents["monitor"], "r") as f:
                                            lines = f.read()
                                    else:
                                        lines = "*** File not produced ***"
                                        # yes, this could potentially cause regexes to still be found
                                    
                                else:
                                    proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)
                                    while True:
                                        line = proc.stdout.readline()
                                        if not line:
                                            break
                                        lines += line.decode()
                                
                                lines = lines.replace("\r", "")
                                matches = {}
                                for regex_ in contents["regexes"]:
                                    matches[regex_] = re.findall(str(regex_), lines)
                                required_files_features["run"][j][cmd]["regexes"] = matches
                                required_files_features["run"][j][cmd]["full_output"] = lines

    out["test_results"] = reflection.run_tests(tests_to_run, configuration["out"] == "stdout" and configuration["format"] in ["text", "txt"])
    out["class_tree"] = reflection.get_class_tree()

    with database.SmarkerDatabase(
        configuration["mysql_host"], configuration["mysql_user"], configuration["mysql_passwd"], 
        "Smarker", int(configuration["mysql_port"])) as db:
        
        db.add_submission(student_no, out["name"], out, files_sources)
    return out

class MonitoredFileNotInProducedFilesException(Exception):
    pass

if __name__ == "__main__":
    # user_code_path = "D:\\Edencloud\\UniStuff\\3.0 - CMP 3rd Year Project\\Smarker\\../ExampleSubmissions/Submission_A"
    
    # reflect = Reflect(user_code_path)
    # reflect.import_module("pjtool")
    # # for c, v in reflect.get_classes(("pjtool")).items():
    # #     print(c, v)
    # for k, v in reflect.get_functions("pjtool").items():
    #     print(k, v)

    reflect = Reflect(os.getcwd())
    print(reflect.client_modules)
    reflect.import_module("jinja_helpers")
    print({k: v for k, v in reflect.get_functions("jinja_helpers").items()})