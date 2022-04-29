from dataclasses import dataclass
import misc_classes
import configparser
import jinja_helpers
import pycode_similar
import subprocess
import operator
import database
import argparse
import tempfile
import yaml
import json
import os
import re

@dataclass
class SimilarityMetric:
    code_text_1:str
    code_text_2:str
    id_1:int
    id_2:int

    def __post_init__(self):
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "%i.py" % self.id_1), "w") as f:
                f.write(self.code_text_1)

            with open(os.path.join(td, "%i.py" % self.id_2), "w") as f:
                f.write(self.code_text_2)

            proc = subprocess.Popen(["pycode_similar", "-p", "0", os.path.join(td, "%i.py" % self.id_1), os.path.join(td, "%i.py" % self.id_2)], stdout = subprocess.PIPE)
            self.details = ""
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                self.details += line.decode()

    def get_similarity(self):
        return float(re.findall(r"\d+\.\d+\s", self.details)[0])


def generate_plagarism_report(assessment_name, db):
    required_files = db.get_assessments_required_files(assessment_name)
    submission_ids_to_get = set()
    assessments = db.get_submissions(assessment_name)
    un_added_student_nos = {i[0] for i in assessments.keys()}
    for id_, dt in sorted(assessments.keys(), key=operator.itemgetter(0, 1), reverse=True):
        if id_ in un_added_student_nos:
            files = jinja_helpers.flatten_struct(assessments[(id_, dt)][0]["files"])

            for file_name in required_files:
                if files[file_name]["present"]:
                    if (not files[file_name]["has_exception"]):
                        submission_ids_to_get.add(assessments[(id_, dt)][1])

            un_added_student_nos.remove(id_)
    
    codes = db.get_submission_codes(submission_ids_to_get)
    for file_name, submissions in codes.items():
        with tempfile.TemporaryDirectory() as td:
            print(file_name, len(submissions))
            for student_id, code in submissions:
                with open(os.path.join(td, "%i.py" % student_id), "w") as f:
                    f.write(code)

            cmd = ["pycode_similar"] + [os.path.join(td, f) for f in os.listdir(td)]
            print(" ".join(cmd))
            proc = subprocess.Popen(cmd, stdout = subprocess.PIPE)
            stdout = ""
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                stdout += line.decode()

            print(stdout)
            input("skfhsk")
                    

def getparser():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.split(__file__)[0], "smarker.conf"))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l", "--list",
        action = misc_classes.EnvDefault,
        envvar = "list",
        help = "List assessment names, number enrolled, and number of files",
        required = False
    )
    parser.add_argument(
        "-c", "--create_assessment",
        action = misc_classes.EnvDefault,
        envvar = "create_assessment",
        help = "Path to an assessment .yml file",
        required = False
    )
    parser.add_argument(
        "-rm", "--remove_assessment",
        action = misc_classes.EnvDefault,
        envvar = "remove_assessment",
        help = "Name of an assessment to remove",
        required = False
    )
    parser.add_argument(
        "-e", "--number_enrolled",
        action = misc_classes.EnvDefault,
        envvar = "number_enrolled",
        help = "Number of students enrolled onto an assessment. Required argument to create.",
        required = False,
        type = int
    )
    parser.add_argument(
        "-s", "--create_student",
        action = misc_classes.EnvDefault,
        envvar = "create_student",
        help = "Add a student in the form e.g. 123456789,Eden,Attenborough,E.Attenborough@uea.ac.uk",
        required = False
    )
    parser.add_argument(
        "-p", "--plagarism_report",
        action = misc_classes.EnvDefault,
        envvar = "plagarism_report",
        help = "Generate a plagarism report for the given assessment",
        required = False
    )
    
    for option in config.options("mysql"):
        parser.add_argument(
            "--%s_%s" % ("mysql", option),
            action = misc_classes.EnvDefault,
            envvar = "--%s_%s" % ("mysql", option),
            default = config.get("mysql", option),
            help = "Optional argument inherited from config file. Read smarker.conf for details."
        )
    return parser

if __name__ == "__main__":
    parser = getparser()
    args = vars(parser.parse_args())

    with database.SmarkerDatabase(
        args["mysql_host"], args["mysql_user"], args["mysql_passwd"], 
        "Smarker", int(args["mysql_port"])) as db:
        
        if args["create_assessment"] is not None:
            with open(args["create_assessment"], "r") as f:
                assessment = yaml.safe_load(f)

            db.create_assessment(
                assessment["name"],
                yaml.dump(assessment), 
                args["number_enrolled"], 
                jinja_helpers.flatten_struct(assessment["files"]).keys()
            )

            print("Added assessment %s..." % assessment["name"])

        if args["remove_assessment"] is not None:
            db.remove_assessment(args["remove_assessment"])

            print("Removed %s..." % args["remove_assessment"])

        if args["list"] is not None:
            if args["list"] in ["True", "yes"]:
                print(yaml.dump(db.get_assessments(), indent = 4))

        if args["create_student"] is not None:
            sid, name, email = args["create_student"].split(",")
            db.add_student(int(sid), name, email)

            print("Added student %s" % name)

        if args["plagarism_report"] is not None:
            generate_plagarism_report(args["plagarism_report"], db)

        
        # print(db.get_assessment_yaml("CMP-4009B-2020-A2"))

