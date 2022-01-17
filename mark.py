import configparser
import argparse
import tempfile
import zipfile
import reflect
import yaml
import json
import os

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

        output = reflect.gen_reflection_report(submission_files, assessment_struct)
        output_file = kwargs["out"]
        if kwargs["format"] == "yaml":
            strout = yaml.dump(output)
        elif kwargs["format"] == "json":
            strout = json.dumps(output, indent = 4)

        if output_file == "stdout":
            print(strout)
            exit()

        if output_file == "auto":
            output_file = "%s_report.%s" % (student_no, kwargs["format"])

        with open(output_file, "w") as f:
            f.write(strout)

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
        choices = ["yaml", "json"],
        required = True
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
        