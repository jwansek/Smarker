import reportWriter
import argparse
import tempfile
import zipfile
import reflect
import yaml
import os

def main(assessment_path, submission_path, student_no):
    print(student_no)

    with open(assessment_path, "r") as f:
        assessment_struct = yaml.safe_load(f)

    reflection = reflect.Reflect(submission_path)
    present_module_names = [i.name for i in reflection.client_modules]
    writer = reportWriter.MarkDownReportWriter(student_no)
    
    for i, required_file in enumerate(assessment_struct["files"], 0):
        required_file = list(required_file.keys())[0]
        module_name = os.path.splitext(required_file)[0]

        if module_name not in present_module_names:
            writer.append_module(module_name, False)
            continue
        
        reflection.import_module(module_name)
        writer.append_module(module_name, True, reflection.get_module_doc(module_name))

        this_files_features = assessment_struct["files"][i][required_file]
        if "classes" in this_files_features.keys():

            present_classes = reflection.get_classes(module_name)
            for j, class_name in enumerate(this_files_features["classes"], 0):
                class_name = list(class_name.keys())[0]
                
                if class_name not in present_classes.keys():
                    writer.append_class(class_name, False)
                    continue

                writer.append_class(class_name, True, present_classes[class_name][1])

                present_methods = reflection.get_class_methods(module_name, class_name)
                print(present_methods)
                for required_method in this_files_features["classes"][j][class_name]["methods"]:
                    print(required_method)

    # print(submission_path)
    # reflection = reflect.Reflect(submission_path)
    # # reflection.import_module("pjtool")
    # # print(reflection.get_classes("pjtool"))
    # # print(reflection.get_class_methods("pjtool", "Date")["__eq__"])
    # reflection.import_module("tester")
    # print(reflection.get_functions("tester"))


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
        