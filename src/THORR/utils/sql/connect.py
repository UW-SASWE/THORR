from mysql.connector import MySQLConnection, Error, connect

# import sqlalchemy
import pandas as pd

from configparser import ConfigParser


def read_db_config(filename="config.ini", section="mysql"):
    """Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception("{0} not found in the {1} file".format(section, filename))

    return db


class Connect:
    def __init__(self, config_file, section="mysql", logger=None):
        self.config_file = config_file
        self.section = section
        self.logger = logger
        self.createConnection()
        # self.createEngine()s

    def createConnection(self):
        """Connect to MySQL database"""

        db_config = read_db_config(self.config_file, self.section)
        conn = None
        try:
            print("Connecting to MySQL database...")
            # conn = MySQLConnection(**db_config)
            conn = connect(
                user=db_config["user"],
                database=db_config["database"],
                password=db_config["password"],
                host=db_config["host"],
                port=db_config["port"],
            )

            if conn.is_connected():
                if self.logger is not None:
                    self.logger.info("MySQL connection established.")
                else:
                    print("MySQL connection established.")
                self.conn = conn
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

    # def createEngine(self):
    #     """Create a SQLAlchemy engine"""
    #     db_config = read_db_config(self.config_file, self.section)
    #     try:
    #         print("Connecting to MySQL database...")
    #         url_object = sqlalchemy.engine.URL.create(
    #             "mysql+pymysql",
    #             username=db_config["user"],
    #             password=db_config["password"],
    #             host=db_config["host"],
    #             port=db_config["port"],
    #             database=db_config["database"],
    #         )
    #         engine = sqlalchemy.create_engine(url_object)
    #         print(url_object)
    #         print("Engine created.")
    #         self.engine = engine
    #     except Error as error:
    #         print(error)

    def query_with_fetchmany(self, query, chunksize=100):
        try:
            # dbconfig = read_db_config()
            # conn = MySQLConnection(**dbconfig)
            cursor = self.conn.cursor()

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
            self.conn.close()
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
