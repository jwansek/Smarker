from dataclasses import dataclass
import jinja_helpers
import configparser
import misc_classes
import subprocess
import database
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
        with database.SmarkerDatabase(
            kwargs["mysql_host"], kwargs["mysql_user"], kwargs["mysql_passwd"], 
            "Smarker", int(kwargs["mysql_port"])) as db:

            assessment_struct = db.get_assessment_yaml(kwargs["assessment"])

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

        if kwargs["format"] == "pdf":
            os.environ["TEXINPUTS"] = os.path.join(os.path.split(__file__)[0], "python-latex-highlighting") + ":"


            output_file = os.path.splitext(output_file)[0] + ".tex"
            with open(output_file, "w") as f:
                f.write(strout)
            subprocess.run(["pdflatex", "-interaction=nonstopmode", output_file])
            subprocess.run(["mv", os.path.splitext(os.path.split(output_file)[-1])[0] + ".pdf", os.path.split(output_file)[0]])

            if os.path.exists(os.path.splitext(output_file)[0] + ".tex"):
                os.remove(os.path.splitext(output_file)[0] + ".tex")
            if os.path.exists(os.path.splitext(output_file)[0] + ".log"):
                os.remove(os.path.splitext(output_file)[0] + ".log")
            if os.path.exists(os.path.splitext(output_file)[0] + ".aux"):
                os.remove(os.path.splitext(output_file)[0] + ".aux")
        
        else:
            with open(output_file, "w") as f:
                f.write(strout)

        # input("\n\n[tempdir: %s] Press any key to close..." % tempdir)

def getparser():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.split(__file__)[0], "smarker.conf"))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", "--assessment",
        action = misc_classes.EnvDefault,
        envvar = "assessment",
        help = "Name of the assessment",
        # type = os.path.abspath,
        required = True
    )
    parser.add_argument(
        "-s", "--submission",
        action = misc_classes.EnvDefault,
        envvar = "submission",
        help = "Path to a zip of a student's code",
        # type = os.path.abspath,
        required = True
    )
    parser.add_argument(
        "-f", "--format",
        action = misc_classes.EnvDefault,
        default = "txt",
        envvar = "format",
        help = "Output format type",
        type = str,
        choices = ["yaml", "json", "pdf"] + [os.path.splitext(f)[0] for f in os.listdir(os.path.join(os.path.split(__file__)[0], "templates"))],
    )
    parser.add_argument(
        "-o", "--out",
        action = misc_classes.EnvDefault,
        default = "stdout",
        envvar = "output",
        help = "Path to write the output to, or, by default write to stdout. 'auto' automatically generates a file name.",
    )

    for section in config.sections():
        for option in config.options(section):
            parser.add_argument(
                "--%s_%s" % (section, option),
                action = misc_classes.EnvDefault,
                envvar = "--%s_%s" % (section, option),
                default = config.get(section, option),
                help = "Optional argument inherited from config file. Read smarker.conf for details."
            )

    try:
        for dependency in os.environ["SMARKERDEPS"].split(","):
            subprocess.run(["pip", "install", dependency])
    except KeyError:
        pass

    return parser

if __name__ == "__main__":
    parser = getparser()    

    args = vars(parser.parse_args())
    main(**args)
        