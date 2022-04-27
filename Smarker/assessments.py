import misc_classes
import configparser
import jinja_helpers
import database
import argparse
import yaml
import os

if __name__ == "__main__":
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
    
    for option in config.options("mysql"):
        parser.add_argument(
            "--%s_%s" % ("mysql", option),
            action = misc_classes.EnvDefault,
            envvar = "--%s_%s" % ("mysql", option),
            default = config.get("mysql", option),
            help = "Optional argument inherited from config file. Read smarker.conf for details."
        )

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

        
        # print(db.get_assessment_yaml("CMP-4009B-2020-A2"))

