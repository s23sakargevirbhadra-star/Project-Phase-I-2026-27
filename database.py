# database.py
# This file handles the MongoDB connection.
# It has small functions — each does ONE thing.
# All other files (recommender.py, app.py) import from here.

import os                          # built-in module to read environment variables
from pymongo import MongoClient    # pymongo is the official Python driver for MongoDB
from dotenv import load_dotenv     # python-dotenv reads the .env file for us

# Read the .env file and load its values into environment variables.
# After this line, os.environ["MONGO_URI"] will contain your connection string.
load_dotenv()


def get_database():
    """
    Connects to MongoDB using the MONGO_URI from the .env file
    and returns the 'maharashtra_places' database object.

    For local MongoDB the URI is: mongodb://localhost:27017
    Think of a database like a folder that holds many collections (tables).
    This function opens that folder.

    Returns:
      A pymongo Database object, or raises an error if the connection fails.
    """
    # Read the connection string from the .env file — never hardcode it here
    uri = os.environ.get("MONGO_URI")

    if not uri:
        # If .env is missing or MONGO_URI is not set, give a clear message
        raise ValueError(
            "MONGO_URI not found. "
            "Create a .env file and add: MONGO_URI=mongodb://localhost:27017"
        )

    # MongoClient connects to MongoDB.
    # serverSelectionTimeoutMS=5000 means "give up after 5 seconds if unreachable"
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)

    # Return the database named 'maharashtra_places'.
    # MongoDB creates it automatically the first time data is inserted.
    return client["maharashtra_places"]


def get_places_collection():
    """
    Returns the 'places' collection from the database.

    A collection is like a table in a regular database.
    It holds all 45 Maharashtra place documents.

    Returns:
      A pymongo Collection object for 'places'.
    """
    db = get_database()      # connect to the database first
    return db["places"]      # then return the 'places' collection inside it


def get_users_collection():
    """
    Returns the 'users' collection from the database.
    Reserved for login / user-reviews feature.
    """
    db = get_database()
    return db["users"]


def get_trails_collection():
    """
    Returns the 'trails' collection from the database.
    Each document is one themed trail with an ordered list of place_ids.
    """
    db = get_database()
    return db["trails"]


def test_connection():
    """
    Tries to connect to MongoDB and prints a simple success or error message.
    Run this to check that MongoDB is running and your .env is correct.

    How to run:
      py database.py

    Good output:
      Connected to MongoDB!
      Database: maharashtra_places
      Collections available: []

    Bad output:
      Connection failed: ...
      Check that MongoDB is running and MONGO_URI is correct in .env
    """
    try:
        db = get_database()

        # ping is MongoDB's built-in "are you there?" command
        db.command("ping")

        print("Connected to MongoDB!")
        print(f"Database: {db.name}")
        print(f"Collections available: {db.list_collection_names()}")

    except Exception as error:
        print(f"Connection failed: {error}")
        print("Check that MongoDB is running and MONGO_URI is correct in .env")


# When you run   py database.py   this block runs.
# When another file does   import database   this block is skipped.
if __name__ == "__main__":
    test_connection()
