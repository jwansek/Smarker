import argparse
import tempfile
import zipfile
import yaml
import os

def main(assessment_path, submission_path, student_no):
    print(student_no)

    with open(assessment_path, "r") as f:
        assessment_struct = yaml.safe_load(f)

    print(assessment_struct)

    for required_file in assessment_struct["files"]:
        required_file = list(required_file.keys())[0]
        print(required_file, required_file in os.listdir(submission_path))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", "--assessment",
        help = "Path to an assessment .yml file",
        type = str,
        required = True
    )
    parser.add_argument(
        "-s", "--submission",
        help = "Path to a zip of a student's code",
        type = str,
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
            os.path.splitext(os.path.split(args["submission"])[-1])[0]
        )
        