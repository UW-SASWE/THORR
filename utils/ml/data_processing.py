import tensorflow as tf
import numpy as np
import pandas as pd

# TODO: refine this class
class MySQLGenerator(tf.keras.utils.Sequence):
    def __init__(self, batch_size, sql_connection, query, shuffle=True):
        self.batch_size = batch_size
        self.conn = sql_connection
        self.cursor = self.conn.cursor()
        self.query = query
        self.shuffle = shuffle
        self.num_rows = self.count_rows()
        self.on_epoch_end()

    def __len__(self):
        return int(np.ceil(self.num_rows / self.batch_size))

    def __getitem__(self, index):
        return self.cursor.fetchmany(self.batch_size)

    def on_epoch_end(self):
        # add sql shuffle to the query if the shuffle flag is true
        if self.shuffle:
            self.cursor.execute(f"""{self.query} ORDER BY RAND()""")
        else:
            self.cursor.execute(self.query)

    def count_rows(self):
        self.cursor.execute(f"""SELECT COUNT(*) FROM ({self.query}) AS T""")
        num_rows = self.cursor.fetchone()[0][0]

        return num_rows

    # def __load_data(self):
    #     connection = mysql.connector.connect(**self.db_config)
    #     cursor = connection.cursor()
    #     query = f"SELECT {self.columns} FROM {self.table_name} WHERE {self.where} ORDER BY {self.order_by};"
    #     cursor.execute(query)
    #     data = cursor.fetchall()
    #     cursor.close()
    #     connection.close()
    #     return data