from dataclasses import dataclass
from matplotlib import pyplot as plt
import numpy as np
import misc_classes
import configparser
import jinja_helpers
import pycode_similar
import pandas as pd
import pickle
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
    """Abstract class for getting a metric of similariry between two python objects.
    By default it uses pycode_similar as a metric, but this can be changed by overriding
    ``get_similarity()``. There is also the additional attribute ``details`` for getting
    a breakdown of similarity.
    """
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
        """Gets the similarity between the two codes.

        Returns:
            float: A percentage similarity metric
        """
        return float(re.findall(r"\d+\.\d+\s", self.details)[0])

def visualise_matrix(dataframe:pd.DataFrame, file_name):
    """Visualize and draw a similarity matrix. Simply shows the figure,
    therefore this doesn't work in docker.

    Args:
        dataframe (pandas.DataFrame): Pandas dataframe representing the similarity
        file_name (str): The file name that corrisponds to the dataframe. Used as the title
    """
    print(file_name)
    print(dataframe)

    values = dataframe.values

    fig, ax = plt.subplots()
    ax.matshow(values, alpha = 0.3, cmap = plt.cm.Reds)

    # axes labels
    xaxis = np.arange(len(dataframe.columns))
    ax.set_xticks(xaxis)
    ax.set_yticks(xaxis)
    ax.set_xticklabels(dataframe.columns)
    ax.set_yticklabels(dataframe.index)

    # labelling each point
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            if i == j:
                ax.text(x = j, y = i, s = "N/A", va = 'center', ha = 'center')
            else:
                ax.text(x = j, y = i, s = values[i, j], va = 'center', ha = 'center')
    
    plt.title(file_name)
    plt.show()


def generate_plagarism_report(assessment_name, db:database.SmarkerDatabase):
    """Generates a plagarism report for the given ``assessment_name``. Only
    fetches submissions with present files and without any exceptions.

    Args:
        assessment_name (str): The name of the assessment to fetch submissions from
        db (database.SmarkerDatabase): An open database object is required

    Returns:
        dict: dict of ``pandas.core.frame.DataFrame`` objects indexed by the required file name
    """
    # get submissions with files and no exception
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
    
    # get similarity matrix
    report = {}
    codes = db.get_submission_codes(submission_ids_to_get)
    for file_name, submissions in codes.items():
        d = {}
        d_details = {}
        with tempfile.TemporaryDirectory() as td:
            for student_id, code in submissions:
                d[student_id] = []
                d_details[student_id] = []
                for student_id_2, code_2 in submissions:
                    sm = SimilarityMetric(code, code_2, student_id, student_id_2)
                    # print("%i and %i = %.3f" % (student_id, student_id_2, SimilarityMetric(code, code_2, student_id, student_id_2).get_similarity()))
                    d[student_id].append(sm.get_similarity())
                    d_details[student_id].append(sm)
        index = [i[0] for i in submissions]
        visualise_matrix(pd.DataFrame(d, index = index), file_name)
        report[file_name] = pd.DataFrame(d_details, index = index)

    out_path = os.path.realpath("plagarism_report_details.pickle")
    with open(out_path, "wb") as f:
        pickle.dump(report, f)
    print("Written report to %s" % out_path)

    return report

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
        help = "Add a student in the form e.g. 123456789,Eden Attenborough,E.Attenborough@uea.ac.uk",
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

