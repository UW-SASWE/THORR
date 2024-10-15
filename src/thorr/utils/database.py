from mysql.connector import Error, connect
import pandas as pd

from thorr.utils import config as cfg


class Connect:
    def __init__(self, config_file, section="mysql", logger=None, return_conn=False):
        self.config_file = config_file
        self.section = section
        self.logger = logger
        self.createConnection()
        self.return_conn = return_conn
        # self.createEngine()s

    def createConnection(self):
        """Connect to MySQL database"""

        db_config = cfg.read_config(self.config_file, [self.section])
        self.connection = None

        try:
            if self.logger is not None:
                self.logger.info("Connecting to MySQL database...")
            else:
                print("Connecting to MySQL database...")
            self.connection = connect(
                user=db_config[self.section]["user"],
                database=db_config[self.section]["database"],
                password=db_config[self.section]["password"],
                host=db_config[self.section]["host"],
                port=db_config[self.section]["port"],
            )

            if self.connection.is_connected():
                if self.logger is not None:
                    self.logger.info("MySQL connection established.")
                else:
                    print("MySQL connection established.")
            else:
                if self.logger is not None:
                    self.logger.info("MySQL connection failed.")
                else:
                    print("MySQL connection failed.")

        except Error as error:
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

        except Error as error:
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
        except Error as error:
            if self.logger is not None:
                self.logger.error(error)
            else:
                print(error)


# if __name__ == '__main__':
#     # TODO: Make this a command line argument
#     Connect()
