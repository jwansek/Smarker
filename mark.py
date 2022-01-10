import argparse
import tempfile
import zipfile
import reflect
import yaml
import json
import os

def main(assessment_path, submission_path, student_no, output_format):
    # print(student_no)

    with open(assessment_path, "r") as f:
        assessment_struct = yaml.safe_load(f)

    output = reflect.gen_reflection_report(submission_path, assessment_struct)
    if output_format == "yaml":
        print(yaml.dump(output))
    elif output_format == "json":
        print(json.dumps(output, indent = 4))

if __name__ == "__main__":
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
    args = vars(parser.parse_args())

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

        main(
            args["assessment"], 
            submission_files, 
            os.path.splitext(os.path.split(args["submission"])[-1])[0],
            args["format"]
        )
        