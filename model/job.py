import mysql.connector
# Replace the following variables with your MySQL server information
host = 'localhost'
port = '3306'
user = 'root'
password = '159623'
database = 'seadata'

class Job:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()

    def add_job(self, job_title, country, city, job_description):
        query = "INSERT INTO JOBS (job_title, country, city, job_description) VALUES (%s, %s, %s, %s)"
        values = (job_title, country, city, job_description)
        self.cursor.execute(query, values)
        self.conn.commit()

    def get_job_by_id(self, job_id):
        query = "SELECT * FROM JOBS WHERE id = %s"
        self.cursor.execute(query, (job_id,))
        return self.cursor.fetchone()

    def get_all_jobs(self):
        query = "SELECT * FROM JOBS"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close_connection(self):
        self.conn.close()