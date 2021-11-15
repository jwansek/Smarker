from dataclasses import dataclass
import datetime

@dataclass
class MarkDownReportWriter:
    student_no:str

    def __post_init__(self):
        self.__push_line("""
# %s Submission Report

Report automatically generated at %s

## Files\n\n""" % (self.student_no, datetime.datetime.now()))

    def __push_line(self, line):
        with open("%s_report.md" % self.student_no, "a") as f:
            f.write(line)

    def append_module(self, module_name, found = True, docs = None):
        self.__push_line("### File: `%s.py`\n\n" % module_name)
        if found:
            self.__push_line(" - [x] Present\n")
            if len(docs) > 2:
                self.__push_line(" - [x] Documented (%d characters)\n\n" % (len(docs)))
        else:
            self.__push_line(" - [ ] Present\n\n")

    def append_class(self, class_name, found = True, docs = None):
        self.__push_line("#### Class: `%s`\n\n" % class_name)
        if found:
            self.__push_line(" - [x] Present\n")
            if len(docs) > 2:
                self.__push_line(" - [x] Documented (%d characters)\n\n" % (len(docs)))
        else:
            self.__push_line(" - [ ] Present\n\n")