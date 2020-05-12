import pymongo
import os


class DBManager:
    """
    Class used to manage database connection.
    """
    def __init__(self, rc_main):
        self.main = rc_main
        self.db = None

        self.connect_to_db()

    def connect_to_db(self):
        """
        Creates connection to database.
        In case of failure, stops app.
        """
        try:
            c_string = os.getenv("CONNECTION_STRING")
            client = pymongo.MongoClient(c_string)
            self.db = client.get_database("smarthome")
        except:
            print("Nie udało się połączyć z bazą danych!")
            exit()

    def is_connected(self):
        """Checks if connection is established"""
        return self.db is not None

    def collection(self, name):
        """Returns collection with a given name from database"""
        if self.is_connected():
            return self.db.get_collection(name)

    def register(self, user):
        """Inserts user to database"""
        if self.is_connected():
            self.collection("users").insert_one(user)

    def find_user(self, user):
        """Gets user from database"""
        if self.is_connected():
            return self.collection("users").find_one({"username": user})