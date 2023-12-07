import psycopg2
from custom_errors import *



""" #################################################################### 
establish connection to database
#################################################################### """


def DB_Connect():
    """ Connecting to the PostgreSQL database server """
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="tpc",
            user="postgres",
            password="Ammulu@123",
            port=5432
        )
        cursor = connection.cursor()
        return connection, cursor

    except CustomError as e:
        raise CustomError(str(e))
    except:
        if connection is not None:
            connection.close()
        raise CustomError("Error in connect() - Database connection error.")


""" #################################################################### 
helper that processes a query and returns the data
#################################################################### """


def query(sql_string, explain=False):
    connection, cursor = DB_Connect()
    try:
        data = ""
        if connection is not None:
            cursor.execute(sql_string)
            data = cursor.fetchall()

        if explain:
            return data[0][0][0]
        else:
            return data[0]
    except CustomError as e:
        raise CustomError(str(e))
    except:
        raise CustomError(
            "Error in query() - Database has a problem executing query, check your SQL syntax."
        )
    finally:
        if connection is not None:
            connection.close()