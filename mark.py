from dataclasses import dataclass
import jinja_helpers
import configparser
import argparse
import tempfile
import zipfile
import reflect
import jinja2
import shutil
import yaml
import json
import os

@dataclass
class FileDependencies:
    assessment_struct:dict

    def __enter__(self):
        try:
            for file_dep in self.assessment_struct["dependencies"]["files"]:
                if os.path.isfile(file_dep):
                    shutil.copy(file_dep, os.path.split(file_dep)[-1])
                else:
                    shutil.copytree(file_dep, os.path.split(file_dep)[-1])
                # print("%s --> %s" % (file_dep, os.path.join(os.getcwd(), os.path.split(file_dep)[-1])))
        except KeyError:
            pass

    def __exit__(self, type, value, traceback):
        stuff_to_remove = []
        try:
            stuff_to_remove += [os.path.split(f)[-1] for f in self.assessment_struct["dependencies"]["files"]]
        except KeyError:
            pass
        try:
            stuff_to_remove += self.assessment_struct["produced_files"]
        except KeyError:
            pass

        for file_dep in stuff_to_remove:
            if os.path.isfile(file_dep):
                os.remove(file_dep)
            else:
                shutil.rmtree(file_dep)

def main(**kwargs):
    student_no = os.path.splitext(os.path.split(args["submission"])[-1])[0]

    with tempfile.TemporaryDirectory() as tempdir:
        with zipfile.ZipFile(args["submission"]) as z:
            z.extractall(tempdir)

        # some zipping applications make a folder inside the zip with the files in that folder.
        # try to deal with this here.
        submission_files = tempdir
        if os.path.isdir(
            os.path.join(submission_files, os.listdir(submission_files)[0])
        ) and len(os.listdir(submission_files)) == 1:
            submission_files = os.path.join(submission_files, os.listdir(submission_files)[0])

        with open(kwargs["assessment"], "r") as f:
            assessment_struct = yaml.safe_load(f)

        with FileDependencies(assessment_struct):
            output = reflect.gen_reflection_report(submission_files, assessment_struct, student_no, kwargs)
        output_file = kwargs["out"]
        
        if kwargs["format"] == "yaml":
            strout = yaml.dump(output)
        elif kwargs["format"] == "json":
            strout = json.dumps(output, indent = 4)
        else:
            with open(os.path.join("templates", "%s.jinja2" % kwargs["format"]), "r") as f:
                jinja_template = jinja2.Template(f.read())

            strout = jinja_template.render(**output, **jinja_helpers._get_helpers(), **kwargs)

        if output_file == "stdout":
            print(strout)
            # input("\n\n[tempdir: %s] Press any key to close..." % tempdir)
            exit()

        if output_file == "auto":
            output_file = "%s_report.%s" % (student_no, kwargs["format"])

        with open(output_file, "w") as f:
            f.write(strout)

        # input("\n\n[tempdir: %s] Press any key to close..." % tempdir)

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("smarker.conf")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", "--assessment",
        help = "Path to an assessment .yml file",
        type = os.path.abspath,
        required = True
    )
    parser.add_argument(
        "-s", "--submission",
        help = "Path to a zip of a student's code",
        type = os.path.abspath,
        required = True
    )
    parser.add_argument(
        "-f", "--format",
        help = "Output format type",
        type = str,
        choices = ["yaml", "json"] + [os.path.splitext(f)[0] for f in os.listdir("templates")],
        default = "txt"
    )
    parser.add_argument(
        "-o", "--out",
        help = "Path to write the output to, or, by default write to stdout. 'auto' automatically generates a file name.",
        default = "stdout",
    )

    for section in config.sections():
        for option in config.options(section):
            parser.add_argument(
                "--%s_%s" % (section, option),
                default = config.get(section, option),
                help = "Optional argument inherited from config file. Read smarker.conf for details."
            )

    args = vars(parser.parse_args())
    main(**args)
        