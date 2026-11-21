# seed_places.py
#
# Reads data/places.csv and puts every place into MongoDB.
# Uses "upsert" — this means:
#   - If the place already exists (same id) → UPDATE it with the latest data
#   - If the place is new → INSERT it
#
# This makes the script safe to run any number of times.
# Running it again after adding new columns to the CSV will update all
# existing documents with the new fields — no duplicates created.
#
# How to run:
#   py seed_places.py
#
# Expected output (first run):
#   Reading places from data/places.csv ...
#   Found 53 places in CSV.
#   Inserted 53 new places. Updated 0 existing.
#   Done! Total documents in 'places' collection: 53
#
# Expected output (second run after adding new columns):
#   Reading places from data/places.csv ...
#   Found 53 places in CSV.
#   Inserted 0 new places. Updated 53 existing.
#   Done! Total documents in 'places' collection: 53

import csv                              # built-in module to read CSV files
from database import get_places_collection  # our function from database.py


def read_csv():
    """
    Reads data/places.csv and returns a list of dictionaries.
    Each dictionary is one place.

    csv.DictReader picks up ALL columns automatically — if new columns
    are added to the CSV (like entry_fee, timings, etc.), they will be
    included in each dictionary without any code change needed here.
    """
    places = []

    with open("data/places.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Convert numeric columns from text to real numbers.
            # Text columns (entry_fee, timings, etc.) stay as strings —
            # csv.DictReader already reads them as strings, which is correct.
            row["id"]        = int(row["id"])
            row["latitude"]  = float(row["latitude"])
            row["longitude"] = float(row["longitude"])
            row["rating"]    = float(row["rating"])
            places.append(row)

    return places


def seed():
    """
    Main seeding function.

    For each place in the CSV:
      - Call update_one with upsert=True.
      - upsert=True means: "update if the document exists, insert if it does not."
      - The filter {"id": place["id"]} finds the document by its id field.
      - {"$set": place} replaces all fields with the latest CSV values.

    This is better than the old insert-or-skip approach because it also
    UPDATES existing places when new columns are added to the CSV.
    """
    print("Reading places from data/places.csv ...")
    places = read_csv()
    print(f"Found {len(places)} places in CSV.")

    collection = get_places_collection()

    inserted = 0   # count new documents created
    updated  = 0   # count existing documents updated

    for place in places:
        # update_one with upsert=True is the key:
        #   {"id": place["id"]}  → find the document with this id
        #   {"$set": place}      → set ALL fields to the latest CSV values
        #   upsert=True          → if not found, insert as a new document
        result = collection.update_one(
            {"id": place["id"]},
            {"$set": place},
            upsert=True
        )

        # result.upserted_id is set only if a NEW document was inserted.
        # If it is None, an existing document was updated.
        if result.upserted_id:
            inserted += 1
        else:
            updated += 1

    print(f"Inserted {inserted} new places. Updated {updated} existing.")

    total = collection.count_documents({})
    print(f"Done! Total documents in 'places' collection: {total}")


# Run seed() when this file is executed directly.
if __name__ == "__main__":
    seed()
