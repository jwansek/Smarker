from dataclasses import dataclass
import pymysql

@dataclass
class SmarkerDatabase:
    host:str 
    user:str 
    passwd:str 
    db:str 
    port:int = 3306
    
    def __enter__(self):
        try:
            self.__connection = self.__get_connection()
        except pymysql.err.OperationalError as e:
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
                email VARCHAR(50) NOT NULL
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
                submission_zip_path TEXT NOT NULL,
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
                file_text TEXT NOT NULL,
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
