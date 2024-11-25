import mysql.connector
import psycopg
import pandas as pd

from thorr.utils import config as cfg


class Connect:
    def __init__(
        self,
        config_file,
        section="mysql",
        logger=None,
        return_conn=False,
        db_type="mysql",
    ):
        self.config_file = config_file
        self.section = section
        self.logger = logger
        self.db_type = db_type

        if self.db_type == "mysql":
            self.connect = mysql.connector.connect
            self.Error = mysql.connector.Error
        elif self.db_type == "postgresql":
            self.connect = psycopg.connect
            self.Error = psycopg.Error

        self.createConnection()
        self.return_conn = return_conn
        # self.createEngine()s

    def createConnection(self):
        """Connect to database"""

        db_config = cfg.read_config(self.config_file, [self.section])
        self.connection = None

        try:
            if self.logger is not None:
                self.logger.info("Connecting to database...")
            else:
                print("Connecting to database...")

            if self.db_type == "mysql":
                self.connection = self.connect(
                    user=db_config[self.section]["user"],
                    database=db_config[self.section]["database"],
                    password=db_config[self.section]["password"],
                    host=db_config[self.section]["host"],
                    port=db_config[self.section]["port"],
                )

                if self.connection.is_connected():
                    if self.logger is not None:
                        self.logger.info("Database connection established.")
                    else:
                        print("Database connection established.")
                else:
                    if self.logger is not None:
                        self.logger.info("Database connection failed.")
                    else:
                        print("Database connection failed.")
            elif self.db_type == "postgresql":
                self.connection = self.connect(
                    user=db_config[self.section]["user"],
                    dbname=db_config[self.section]["dbname"],
                    password=db_config[self.section]["password"],
                    host=db_config[self.section]["host"],
                    port=db_config[self.section]["port"],
                )

                if not self.connection.closed:
                    if self.logger is not None:
                        self.logger.info("Database connection established.")
                    else:
                        print("Database connection established.")
                else:
                    if self.logger is not None:
                        self.logger.info("Database connection failed.")
                    else:
                        print("Database connection failed.")

            # if self.connection.is_connected():
            #     if self.logger is not None:
            #         self.logger.info("Database connection established.")
            #     else:
            #         print("Database connection established.")
            # else:
            #     if self.logger is not None:
            #         self.logger.info("Database connection failed.")
            #     else:
            #         print("Database connection failed.")

        except self.Error as error:
            if self.logger is not None:
                self.logger.error(error)
            else:
                print(error)

    def query_with_fetchmany(self, query, chunksize=100):
        try:
            # dbconfig = read_db_config()
            # conn = MySQLConnection(**dbconfig)
            cursor = self.connection.cursor()

            cursor.execute(query)

            chunks = []

            while True:
                chunk = cursor.fetchmany(chunksize)
                if not chunk:
                    break
                chunks.append(pd.DataFrame(chunk))

            df = pd.concat(chunks, ignore_index=True)
            df.columns = [i[0] for i in cursor.description]

            return df

        except self.Error as error:
            if self.logger is not None:
                self.logger.error(error)
            else:
                print(error)

    def close(self):
        """Close MySQL database connection"""
        try:
            self.connection.close()
            if self.logger is not None:
                self.logger.info("Connection closed.")
            else:
                print("Connection closed.")
        except self.Error as error:
            if self.logger is not None:
                self.logger.error(error)
            else:
                print(error)


# if __name__ == '__main__':
#     # TODO: Make this a command line argument
#     Connect()
