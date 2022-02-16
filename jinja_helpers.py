"""Functions in this module will be avaliable to call in jinja templates"""
import datetime
import yaml
import re

def get_datetime():
    return str(datetime.datetime.now())

def recurse_class_tree_text(tree, indent = 4):
    return yaml.dump(tree, indent = indent).replace(": {}", "")

def flatten_struct(struct):
    # print("Attempting to flatten: ", struct)
    out = {}
    for s in struct:
        key = list(s.keys())[0]
        out[key] = s[key]
    return out

def get_required_num_args(funcname):
    return int(re.findall(r"(?<=\()(\d+)(?=\))", funcname)[0])

def bool_to_yesno(b:bool):
    if b:
        return "YES"
    else:
        return "NO"

def bool_to_checkbox(b:bool):
    if b:
        return "[x]"
    else:
        return "[ ]"

def len_documentation(comments, docs):
    """This function isn't in jinja"""
    if comments == "None":
        commentlen = 0
    else:
        commentlen = len(comments)

    if docs == "None":
        docslen = 0
    else:
        docslen = len(docs)

    return commentlen + docslen

def len_(obj):
    return len(obj)

def get_source_numlines(source):
    return "%d lines (%d characters)" % (source.count("\n"), len(source))

def _get_helpers():
    import reflect
    import os

    r = reflect.Reflect(os.getcwd())
    r.import_module("jinja_helpers")
    return {k: v[0] for k, v in r.get_functions("jinja_helpers").items()}

if __name__ == "__main__":
    # import json
    # with open("100301654_report.json", "r") as f:
    #     init_struct = json.load(f)["files"]

    # print(flatten_struct(flatten_struct(init_struct)["example.py"]["functions"]))

    print(get_required_num_args("aFunctionThatIsntThere(2)"))

    
    