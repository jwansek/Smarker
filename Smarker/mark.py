from dataclasses import dataclass
import jinja_helpers
import configparser
import misc_classes
import subprocess
import argparse
import tempfile
import zipfile
import reflect
import jinja2
import shutil
import yaml
import json
import os

def main(**kwargs):
    student_no = os.path.splitext(os.path.split(args["submission"])[-1])[0]

    with misc_classes.ExtractZipToTempDir(args["submission"]) as submission_files:
        with open(kwargs["assessment"], "r") as f:
            assessment_struct = yaml.safe_load(f)

        with misc_classes.FileDependencies(assessment_struct):
            output = reflect.gen_reflection_report(submission_files, assessment_struct, student_no, kwargs, args["submission"])
        output_file = kwargs["out"]
        
        if kwargs["format"] == "yaml":
            strout = yaml.dump(output)
        elif kwargs["format"] == "json":
            strout = json.dumps(output, indent = 4)
        else:
            fp = os.path.join(os.path.split(__file__)[0], "templates", "%s.jinja2" % kwargs["format"])
            if kwargs["format"] in ("tex", "pdf"):
                jinja_template = misc_classes.latex_jinja_env.get_template("tex.jinja2")
            else:
                with open(fp, "r") as f:
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

        if kwargs["format"] == "pdf":
            os.environ["TEXINPUTS"] = os.path.join(os.path.split(__file__)[0], "python-latex-highlighting") + ":"

            os.rename(output_file, os.path.splitext(output_file)[0] + ".tex")
            output_file = os.path.splitext(output_file)[0] + ".tex"
            subprocess.run(["pdflatex", output_file])

            os.remove(os.path.splitext(output_file)[0] + ".tex")
            os.remove(os.path.splitext(output_file)[0] + ".log")
            os.remove(os.path.splitext(output_file)[0] + ".aux")

        # input("\n\n[tempdir: %s] Press any key to close..." % tempdir)

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.split(__file__)[0], "smarker.conf"))

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
        choices = ["yaml", "json", "pdf"] + [os.path.splitext(f)[0] for f in os.listdir(os.path.join(os.path.split(__file__)[0], "templates"))],
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
        