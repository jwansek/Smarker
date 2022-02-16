from dataclasses import dataclass
import tempfile
import zipfile
import shutil
import os

@dataclass
class ExtractZipToTempDir(tempfile.TemporaryDirectory):
    zip_file:str

    def __post_init__(self):
        super().__init__()

    def __enter__(self):
        return self.extract()

    def __exit__(self, exc, value, tb):
        self.cleanup()

    def extract(self):
        with zipfile.ZipFile(self.zip_file) as z:
            z.extractall(self.name)

        # some zipping applications make a folder inside the zip with the files in that folder.
        # try to deal with this here.
        submission_files = self.name
        if os.path.isdir(
            os.path.join(submission_files, os.listdir(submission_files)[0])
        ) and len(os.listdir(submission_files)) == 1:
            submission_files = os.path.join(submission_files, os.listdir(submission_files)[0])

        return submission_files

@dataclass
class FileDependencies:
    assessment_struct:dict
    to_:str=str(os.getcwd())

    def __enter__(self):
        self.get_deps()

    def __exit__(self, type, value, traceback):
        self.rm_deps()

    def get_deps(self):
        try:
            for file_dep in self.assessment_struct["dependencies"]["files"]:
                if os.path.isfile(file_dep):
                    shutil.copy(file_dep, os.path.join(self.to_, os.path.split(file_dep)[-1]))
                else:
                    shutil.copytree(file_dep, os.path.join(self.to_, os.path.split(file_dep)[-1]))
        except KeyError:
            pass

    def rm_deps(self):
        stuff_to_remove = []
        try:
            stuff_to_remove += [os.path.split(f)[-1] for f in self.assessment_struct["dependencies"]["files"]]
        except KeyError:
            pass
        try:
            stuff_to_remove += self.assessment_struct["produced_files"]
        except KeyError:
            pass

        for file_dep in stuff_to_remove:
            file_dep = os.path.join(self.to_, file_dep)
            # print("rm: ", file_dep)
            if os.path.exists(file_dep):
                if os.path.isfile(file_dep):
                    os.remove(file_dep)
                else:
                    shutil.rmtree(file_dep)

@dataclass
class ChangeDirectory:
    target:str
    cwd:str=str(os.getcwd())

    def __enter__(self):
        os.chdir(self.target)

    def __exit__(self, type, value, traceback):
        os.chdir(self.cwd)
