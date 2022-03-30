"""Functions in this module will be avaliable to call in jinja templates"""
import subprocess
import lxml.html
import datetime
import tempfile
import shutil
import pdfkit
import yaml
import json
import re
import os

def get_datetime():
    return str(datetime.datetime.now())

def recurse_class_tree_text(tree, indent = 4):
    return yaml.dump(tree, indent = indent).replace(": {}", "")

def recurse_class_tree_forest(tree):
    return re.sub(r"\"|:|\{\}|,", "", json.dumps(tree, indent=4)).replace("{", "[").replace("}", "]")

def junit_xml_to_html(junit_xml, student_id):
    # setup tempfiles for the junit xml and html
    with tempfile.NamedTemporaryFile(suffix = ".xml", mode = "w", delete = False) as xml_f:
        xml_f.write(junit_xml)
    html_path = os.path.join(tempfile.mkdtemp(), "junit.html")

    # convert the junit xml to html
    subprocess.run(["junit2html", xml_f.name, html_path])

    # remove the html elements we don't like
    root = lxml.html.parse(html_path)
    for toremove in root.xpath("/html/body/h1"):
        toremove.getparent().remove(toremove)
    for toremove in root.xpath("/html/body/table"):
        toremove.getparent().remove(toremove)
    for toremove in root.xpath("/html/body/p"):
        toremove.getparent().remove(toremove)

    # convert the html to pdf
    out_fname = "%s_test_report.pdf" % student_id
    pdfkit.from_string(lxml.etree.tostring(root).decode(), out_fname)

    # remove the tempfiles
    # input("%s continue..." % html_path)
    shutil.rmtree(os.path.split(html_path)[0])
    os.remove(xml_f.name)

    return out_fname

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

#https://stackoverflow.com/questions/16259923/how-can-i-escape-latex-special-characters-inside-django-templates
def tex_escape(text):
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key = lambda item: - len(item))))
    # print(text, regex.sub(lambda match: conv[match.group()], text))
    return regex.sub(lambda match: conv[match.group()], text)

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

    
    