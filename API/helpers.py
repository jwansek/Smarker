import tempfile
import docker
import json
import os

CLIENT = docker.from_env()

def run_smarker_simple(db, zip_name, assessment_name, volumes):
    with tempfile.TemporaryDirectory() as td:   # remember to passthru /tmp/ as a volume
        env = [                                 # probably need to find a better way tbh
            "submission=/tmp/%s" % zip_name,
            "assessment=%s" % assessment_name,
            "format=json",
            "output=/out/report.json"
        ]
        outjson = os.path.join(td, "report.json")
        volumes.append("%s:/out/report.json" % (outjson))
        # print("file_deps:", volumes)
        
        try:
            pypideps = db.get_assessment_yaml(assessment_name)["dependencies"]["libraries"]
            env.append("SMARKERDEPS=" + ",".join(pypideps))
        except KeyError:
            pass
        # print("env: ", env)

        open(outjson, 'a').close()  # make a blank file so docker doesnt make it as a directory
        log = CLIENT.containers.run(
            "smarker",
            remove = True,
            volumes = volumes,
            environment = env
        )
        print("log: ", log)

        for f in os.listdir(".uploads"):
            os.remove(os.path.join(".uploads", f))

        with open(outjson, "r") as f:
            return json.load(f)
