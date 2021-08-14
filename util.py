from pymongo import MongoClient
import config_handler

def get_client() -> MongoClient:
  config = config_handler.Config()
  username = config.get_string_value("database", "username")
  password = config.get_string_value("database", "password")
  endpoint = config.get_string_value("database", "endpoint")
  database = config.get_string_value("database", "database")
  return MongoClient(
    f"mongodb+srv://{username}:{password}@{endpoint}/{database}?retryWrites=true&w=majority")

def get_collection(database, collection):
  return get_client().get_database(database).get_collection(collection)