from pymongo import MongoClient
from util import config

mongo_client = None

def get_client() -> MongoClient:
  global mongo_client
  if mongo_client is None:
    username = config.get_string_value("database", "username")
    password = config.get_string_value("database", "password")
    endpoint = config.get_string_value("database", "endpoint")
    database = config.get_string_value("database", "database")
    mongo_client = MongoClient( f"mongodb+srv://{username}:{password}@{endpoint}/{database}?retryWrites=true&w=majority")
  return mongo_client

def get_collection(database, collection):
  return get_client().get_database(database).get_collection(collection)
