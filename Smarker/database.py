from dataclasses import dataclass
import pymysql
import secrets
import yaml

@dataclass
class SmarkerDatabase:
    """Class for interfacing with a MariaDB database. Expected to be used with a `with`
    clause. Database will be built if it isn't found.

    Returns:
        SmarkerDatabase: Database object
    """
    host:str 
    user:str 
    passwd:str 
    db:str 
    port:int = 3306
    
    def __enter__(self):
        try:
            self.__connection = self.__get_connection()
        except Exception as e:
            print(e.args[1])
            if e.args[0] == 1049:
                self.__build_db()
        return self

    def __exit__(self, type, value, traceback):
        self.__connection.close()

    def __get_connection(self):
        return pymysql.connect(
            host = self.host,
            port = self.port,
            user = self.user,
            passwd = self.passwd,
            charset = "utf8mb4",
            database = self.db
        )

    def __build_db(self):
        self.__connection = pymysql.connect(
            host = self.host,
            port = self.port,
            user = self.user,
            passwd = self.passwd,
            charset = "utf8mb4",
        )
        with self.__connection.cursor() as cursor:
            # unsafe:
            cursor.execute("CREATE DATABASE %s" % self.db)
            cursor.execute("USE %s" % self.db)
            cursor.execute("""
            CREATE TABLE students(
                student_no VARCHAR(10) PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                email VARCHAR(50) NOT NULL,
                apikey VARCHAR(64) NOT NULL
            );
            """)
            cursor.execute("""
            CREATE TABLE assessment(
                assessment_name VARCHAR(30) PRIMARY KEY NOT NULL,
                yaml_path TEXT NOT NULL,
                num_enrolled INT UNSIGNED NULL
            );
            """)
            cursor.execute("""
            CREATE TABLE submissions(
                submission_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                student_no VARCHAR(10) NOT NULL,
                assessment_name VARCHAR(30) NOT NULL,
                submission_dt DATETIME NOT NULL default CURRENT_TIMESTAMP,
                report_yaml TEXT NOT NULL,
                FOREIGN KEY (student_no) REFERENCES students(student_no),
                FOREIGN KEY (assessment_name) REFERENCES assessment(assessment_name)
            );
            """)
            cursor.execute("""
            CREATE TABLE assessment_file(
                file_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                assessment_name VARCHAR(30) NOT NULL,
                file_name VARCHAR(30) NOT NULL,
                FOREIGN KEY (assessment_name) REFERENCES assessment(assessment_name)
            );
            """)
            cursor.execute("""
            CREATE TABLE submitted_files(
                submission_id INT UNSIGNED NOT NULL,
                file_id INT UNSIGNED NOT NULL,
                file_text TEXT NULL,
                FOREIGN KEY (submission_id) REFERENCES submissions(submission_id),
                FOREIGN KEY (file_id) REFERENCES assessment_file(file_id),
                PRIMARY KEY(submission_id, file_id)
            );
            """)
                
        self.__connection.commit()
        return self.__connection


    def get_tables(self):
        with self.__connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            return cursor.fetchall()

    def create_assessment(self, name, yaml_f, num_enrolled, files):
        """Add an assessment configuration to the database

        Args:
            name (str): The name of the assessment, which will be used from now on
            yaml_f (str): The yaml configuration as a string
            num_enrolled (int): (Optional) the number of students enrolled
            files (list): List of strings, the files required for this assessment
        """
        with self.__connection.cursor() as cursor:
            cursor.execute("INSERT INTO assessment VALUES (%s, %s, %s);", (
                name, yaml_f, num_enrolled
            ))
            
            for file_ in files:
                cursor.execute("INSERT INTO assessment_file (assessment_name, file_name) VALUES (%s, %s);", (
                    name, file_
                ))
        self.__connection.commit()

    def remove_assessment(self, name):
        """Removes an assessment. Submissions associated with the assessment will be removed
        too.

        Args:
            name (str): The name of the assessment to remove
        """
        with self.__connection.cursor() as cursor:
            cursor.execute("DELETE FROM submitted_files WHERE submission_id IN (SELECT submission_id FROM submissions WHERE assessment_name = %s);", (name, ))
            cursor.execute("DELETE FROM submissions WHERE assessment_name = %s;", (name, ))
            cursor.execute("DELETE FROM assessment_file WHERE assessment_name = %s;", (name, ))
            cursor.execute("DELETE FROM assessment WHERE assessment_name = %s;", (name, ))
        self.__connection.commit()

    def get_assessments(self):
        """Get assessments in the database.

        Returns:
            tuple - a tuple of tuples in the format ((assessment_name, number_enrolled, number_of_files), )
        """
        with self.__connection.cursor() as cursor:
            cursor.execute("""
            SELECT assessment.assessment_name, num_enrolled, COUNT(assessment.assessment_name) 
            FROM assessment 
            INNER JOIN assessment_file 
            ON assessment.assessment_name = assessment_file.assessment_name 
            GROUP BY assessment.assessment_name;
            """)
            return cursor.fetchall()
    
    def get_assessment_yaml(self, name):
        """Returns the configuration file for a given assessment name.

        Args:
            name (str): The name of the assessment to get

        Returns:
            dict: Configuration yaml struct
        """
        with self.__connection.cursor() as cursor:
            cursor.execute("SELECT yaml_path FROM assessment WHERE assessment_name = %s;", (name, ))
        return yaml.safe_load(cursor.fetchone()[0])

    def add_student(self, student_id, name, email):
        """Adds a student to the database.

        Args:
            student_id (int): Student Number
            name (str): Student's name
            email (str): Student's email
        """
        with self.__connection.cursor() as cursor:
            cursor.execute("INSERT INTO students VALUES (%s, %s, %s, %s);",
            (student_id, name, email, secrets.token_urlsafe(32)))
        self.__connection.commit()

    def add_submission(self, student_id, assessment_name, report_yaml, files):
        """Adds a submission to the database.

        Args:
            student_id (int): Student Number
            assessment_name (str): Assessment name
            report_yaml (dict): Produced yaml report as a dict
            files (dict): Student's code in the format {"<file name>": "<file contents>"}
        """
        with self.__connection.cursor() as cursor:
            cursor.execute("INSERT INTO submissions (student_no, assessment_name, report_yaml) VALUES (%s, %s, %s);", (
                student_id, assessment_name, yaml.dump(report_yaml)
            ))
            submission_id = cursor.lastrowid

            for file_name, file_contents in files.items():
                cursor.execute("""
                INSERT INTO submitted_files
                (submission_id, file_id, file_text)
                VALUES (%s, (SELECT file_id FROM assessment_file WHERE file_name = %s AND assessment_name = %s), %s);
                """, (
                    submission_id, file_name, assessment_name, file_contents
                ))
        self.__connection.commit()

    def get_submission_codes(self, submission_ids):
        out = {}
        with self.__connection.cursor() as cursor:
            for submission_id in submission_ids:
                cursor.execute("""
                SELECT 
                    submitted_files.file_text, 
                    submitted_files.file_id, 
                    assessment_file.file_name, 
                    submissions.student_no 
                FROM submitted_files 
                INNER JOIN assessment_file 
                ON submitted_files.file_id = assessment_file.file_id 
                INNER JOIN submissions 
                ON submissions.submission_id = submitted_files.submission_id
                WHERE submitted_files.submission_id = %s;
                """, (submission_id))
                
                for file_contents, id_, file_name, student_no in cursor.fetchall():
                    if file_contents is not None:
                        try:
                            out[file_name].append((int(student_no), file_contents))
                        except KeyError:
                            out[file_name] = [(int(student_no), file_contents)]
        return out

    def get_submissions(self, assessment_name):
        with self.__connection.cursor() as cursor:
            cursor.execute("SELECT student_no, submission_dt, report_yaml, submission_id FROM submissions WHERE assessment_name = %s;", (assessment_name, ))
            return {(int(i[0]), i[1]): (yaml.safe_load(i[2]), int(i[3])) for i in cursor.fetchall()}

    def get_assessments_required_files(self, assessment_name):
        with self.__connection.cursor() as cursor:       
            cursor.execute("SELECT file_name FROM assessment_file WHERE assessment_name = %s;", (assessment_name, ))   
            return [i[0] for i in cursor.fetchall()]

    def valid_apikey(self, key):
        with self.__connection.cursor() as cursor:
            cursor.execute("SELECT apikey FROM students WHERE apikey = %s", (key, ))
            return key in [i[0] for i in cursor.fetchall()]

if __name__ == "__main__":
    with SmarkerDatabase(host = "vps.eda.gay", user="root", passwd=input("Input password: "), db="Smarker", port=3307) as db:
        # print(db.get_assessments_required_files("example"))
        import json
        print(json.dumps(db.get_submission_codes((24, 21)), indent = 4))
