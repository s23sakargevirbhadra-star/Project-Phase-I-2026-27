# recommender.py
# This file contains all the logic functions for the recommendation system.
# Each function does exactly ONE thing and is kept short and simple.
# No classes. No decorators. Just plain functions using lists and dictionaries.

import math  # built-in Python module for maths (sin, cos, sqrt, etc.)

# get_places_collection() gives us the MongoDB 'places' collection
from database import get_places_collection

# ─────────────────────────────────────────────
# PHASE 2 FUNCTIONS: Load data + Calculate distance
# ─────────────────────────────────────────────

def load_places():
    """
    Reads all NON-trail-only places from the MongoDB 'places' collection.

    Places with trail_only = "yes" are excluded from the main listing.
    They only appear inside trail pages, not in city searches or /api/places.

    {"_id": 0} hides MongoDB's internal _id field.
    {"trail_only": {"$ne": "yes"}} is a MongoDB filter: "not equal to yes".
    """
    collection = get_places_collection()
    results = collection.find(
        {"trail_only": {"$ne": "yes"}},   # exclude trail-only places
        {"_id": 0}
    )
    return list(results)


def load_all_places():
    """
    Reads ALL places including trail_only=yes from MongoDB.
    Used only by trail routes and get_trail_route().
    Regular search, recommend and filter functions use load_places().
    """
    collection = get_places_collection()
    return list(collection.find({}, {"_id": 0}))


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the straight-line distance (in kilometres) between two GPS points.

    Uses the Haversine formula because the Earth is round, not flat.
    Simple explanation:
      Imagine stretching a string along the surface of a globe between two pins.
      The Haversine formula tells you exactly how long that string would be.

    Parameters:
      lat1, lon1 -- GPS coordinates of the first point  (e.g. your location)
      lat2, lon2 -- GPS coordinates of the second point (e.g. a place in the CSV)

    Returns:
      Distance in kilometres, rounded to 2 decimal places.

    Example:
      calculate_distance(18.5204, 73.8567, 19.0760, 72.8777) -> 120.15 km
    """

    # The Earth's radius in kilometres
    EARTH_RADIUS_KM = 6371

    # Step 1: Convert degrees to radians.
    # Maths functions (sin, cos) expect angles in radians, not degrees.
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Step 2: Find the difference between the two latitudes and longitudes
    delta_lat = lat2 - lat1  # how far apart north-south
    delta_lon = lon2 - lon1  # how far apart east-west

    # Step 3: Apply the Haversine formula
    # 'a' is a value between 0 and 1 representing the fraction of the sphere
    a = (math.sin(delta_lat / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2)

    # 'c' is the central angle in radians between the two points
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Step 4: Multiply the angle by Earth's radius to get the actual distance
    distance = EARTH_RADIUS_KM * c

    return round(distance, 2)  # round to 2 decimal places, e.g. 120.15 km


# ─────────────────────────────────────────────
# SCOPE FUNCTION: Cities covered by this system
# ─────────────────────────────────────────────

def get_cities():
    """
    Returns the fixed list of the 6 cities covered by this system.
    This project covers Mumbai, Pune, Nashik, Nagpur, Kolhapur and Nanded.

    No input needed.
    Returns a plain Python list of city name strings.

    Example:
      get_cities() -> ['Mumbai', 'Pune', 'Nashik', 'Nagpur', 'Kolhapur', 'Nanded']
    """
    # Hardcoded on purpose — always correct and never depends on reading the CSV
    return ['Mumbai', 'Pune', 'Nashik', 'Nagpur', 'Kolhapur', 'Nanded']


def get_city_centres():
    """
    Returns a dictionary with the GPS centre coordinates of each of the 6 cities.
    These coordinates are used for two things:
      1. When the user picks a city from the dropdown, the system searches
         from that city's centre.
      2. The 'nearest city' feature: we calculate which city is closest to
         the user's GPS position and show it on the page.

    Returns:
      A dictionary where each key is a city name and the value is another
      dictionary with 'lat' and 'lon'.

    Example:
      get_city_centres()['Pune']  ->  {'lat': 18.5204, 'lon': 73.8567}
    """
    return {
        'Mumbai':   {'lat': 19.0760, 'lon': 72.8777},
        'Pune':     {'lat': 18.5204, 'lon': 73.8567},
        'Nashik':   {'lat': 20.0059, 'lon': 73.7897},
        'Nagpur':   {'lat': 21.1458, 'lon': 79.0882},
        'Kolhapur': {'lat': 16.7050, 'lon': 74.2433},
        'Nanded':   {'lat': 19.1383, 'lon': 77.3210},
    }


def get_nearest_city(user_lat, user_lon):
    """
    Finds which of the 6 cities is closest to the user's GPS position.

    How it works:
      - Get all city centres from get_city_centres().
      - For each city, calculate the distance from the user using calculate_distance().
      - Return the name of the city with the smallest distance.

    Parameters:
      user_lat -- user's latitude
      user_lon -- user's longitude

    Returns:
      The name of the nearest city as a string, e.g. "Nanded".

    Example:
      get_nearest_city(19.14, 77.32) -> "Nanded"
    """
    centres = get_city_centres()

    nearest_city = None
    nearest_dist = float('inf')   # start with infinity so any real distance is smaller

    for city_name, coords in centres.items():
        dist = calculate_distance(user_lat, user_lon, coords['lat'], coords['lon'])
        if dist < nearest_dist:
            nearest_dist = dist
            nearest_city = city_name

    return nearest_city


def get_trail_route(trail, all_places):
    """
    Given a trail document and the full places list, returns the ordered
    places with the distance of each step and the total distance.

    Parameters:
      trail      -- a trail dict with a 'place_ids' list (ordered)
      all_places -- the full list of place dicts (from load_all_places)

    Returns a dictionary:
      {
        "places":     [place1, place2, ...],   # ordered place dicts
        "steps":      [dist1, dist2, ...],     # km between each pair
        "total_km":   123.4                    # sum of all steps
      }

    Example:
      trail = {"name": "Fort Trail", "place_ids": [12, 10, 38]}
      result["total_km"]  ->  the sum of step distances
    """
    # Build a lookup dict: id -> place, so we can find each place by id fast
    place_by_id = {p["id"]: p for p in all_places}

    # Get the ordered list of places that are in this trail
    ordered = []
    for pid in trail["place_ids"]:
        place = place_by_id.get(pid)
        if place:
            ordered.append(place)

    # Calculate distance between each consecutive pair of places
    steps = []
    for i in range(len(ordered) - 1):
        p1 = ordered[i]
        p2 = ordered[i + 1]
        dist = calculate_distance(
            p1["latitude"], p1["longitude"],
            p2["latitude"], p2["longitude"]
        )
        steps.append(dist)

    total_km = round(sum(steps), 2)

    return {"places": ordered, "steps": steps, "total_km": total_km}


# ─────────────────────────────────────────────
# LANGUAGE HELPER: get_text
# ─────────────────────────────────────────────

def get_text(place, field, lang):
    """
    Returns the right language version of a text field from a place dictionary.

    How it works:
      - If lang is "mr", look for field + "_mr" (e.g. "name_mr", "description_mr").
      - If that Marathi field exists AND is not empty, return it.
      - Otherwise fall back to the English field (e.g. "name", "description").

    This means:
      - Places with Marathi translations show Marathi text in Marathi mode.
      - Places without a translation gracefully fall back to English.

    Parameters:
      place -- a place dictionary from MongoDB
      field -- the base field name, e.g. "name", "description", "local_tip"
      lang  -- "en" or "mr"

    Returns:
      A string — either the Marathi or English version of the field.

    Example:
      get_text(place, "name", "mr")  ->  "गेटवे ऑफ इंडिया"
      get_text(place, "name", "en")  ->  "Gateway of India"
      get_text(place, "name", "mr")  ->  "Gateway of India"  (if name_mr is empty)
    """
    if lang == "mr":
        mr_key   = field + "_mr"              # e.g. "name_mr"
        mr_value = place.get(mr_key, "")       # get Marathi value, default ""
        if mr_value and mr_value.strip():      # if not empty, return it
            return mr_value
    # Fall back to English field
    return place.get(field, "")


def apply_language(place, lang):
    """
    Returns a copy of the place dictionary with text fields replaced by
    the correct language version.

    Fields translated: name, description, local_tip
    All other fields (id, city, category, latitude, longitude, rating,
    entry_fee, timings, best_time, time_needed, seasons) stay unchanged.

    We use dict(place) to make a shallow copy so we do not modify the
    original dictionary stored in the calling function.

    Parameters:
      place -- a place dictionary from MongoDB
      lang  -- "en" or "mr"

    Returns:
      A new dictionary with translated text fields.
    """
    result = dict(place)   # shallow copy — changes here do not affect the original
    for field in ("name", "description", "local_tip"):
        result[field] = get_text(place, field, lang)
    return result


# ─────────────────────────────────────────────
# FEATURE 1: Search by place name
# ─────────────────────────────────────────────
def search_places(places, text):
    """
    Searches all places and keeps only those whose name, city or category
    contains the search text. The search is NOT case-sensitive.

    How it works:
      - Convert the search text to lowercase once.
      - For each place, check if the lowercase text appears anywhere in
        the name, city or category (also converted to lowercase).
      - Keep the place if any of those three fields contain the text.

    Parameters:
      places -- the full list of place dictionaries (from load_places)
      text   -- the text the user typed, e.g. "fort" or "Mumbai"

    Returns:
      A new list with only the matching places.
      Returns ALL places if text is empty or None (no filter applied).

    Example:
      search_places(places, "fort")   -> all places with "fort" in name/city/category
      search_places(places, "Mumbai") -> all Mumbai places
      search_places(places, "")       -> all 53 places (no filter)
    """
    # If nothing was typed, return everything unchanged
    if not text or not text.strip():
        return places

    # Convert to lowercase ONCE so we don't repeat .lower() inside the loop
    query = text.strip().lower()

    results = []
    for place in places:
        # Check if the query appears in name, city, category, OR Marathi name
        # str.lower() makes the comparison case-insensitive
        name_mr = place.get("name_mr", "").lower()
        if (query in place["name"].lower()
                or query in place["city"].lower()
                or query in place["category"].lower()
                or query in name_mr):
            results.append(place)

    return results


# ─────────────────────────────────────────────
# PHASE 3 FUNCTIONS: Recommendation logic
# ─────────────────────────────────────────────

def find_nearby_places(places, user_lat, user_lon, radius_km):
    """
    Keeps only places that are within radius_km kilometres of the user.
    Also adds a 'distance_km' key to each place dictionary.

    Parameters:
      places    -- the full list of place dictionaries (from load_places)
      user_lat  -- the user's latitude  (e.g. 18.5204 for Pune)
      user_lon  -- the user's longitude (e.g. 73.8567 for Pune)
      radius_km -- the maximum distance in km (e.g. 50)

    Returns:
      A new list containing only the places within the radius,
      each with a 'distance_km' key added.

    Example:
      find_nearby_places(places, 18.5204, 73.8567, 30)
      -> places within 30 km of Pune, each with distance_km added
    """
    nearby = []  # start with an empty result list

    for place in places:
        # Calculate how far this place is from the user
        dist = calculate_distance(user_lat, user_lon,
                                  place["latitude"], place["longitude"])

        # Only keep this place if it is within the radius
        if dist <= radius_km:
            place["distance_km"] = dist  # attach the distance to the dictionary
            nearby.append(place)

    return nearby


def filter_by_category(places, category):
    """
    Keeps only places that match the given category.
    If category is empty or None, returns all places unchanged.

    Parameters:
      places   -- list of place dictionaries
      category -- the category to filter by, e.g. "Fort" or "Temple"
                  pass "" or None to skip filtering

    Returns:
      A new list with only matching places.

    Example:
      filter_by_category(places, "Fort") -> only forts
      filter_by_category(places, "")     -> all places (no filter)
    """
    # If no category given, return everything as-is
    if not category:
        return places

    # Keep only places whose category matches (case-insensitive comparison)
    return [p for p in places if p["category"].lower() == category.lower()]


def filter_by_season(places, season):
    """
    Keeps only places that are good in the chosen season.
    The 'seasons' field in each place is a pipe-separated string,
    e.g. "monsoon|winter" or "winter|summer".

    If season is empty, "all", or None, returns all places unchanged.

    Parameters:
      places -- list of place dictionaries (each has a 'seasons' key)
      season -- the season to filter by: "monsoon", "winter", "summer"
                pass "" or "all" to skip filtering

    Returns:
      A new list with only matching places.

    Example:
      filter_by_season(places, "monsoon") -> only places good in monsoon
      filter_by_season(places, "")        -> all places (no filter)
    """
    # If no season given or "all", return everything as-is
    if not season or season.lower() == "all":
        return places

    # Convert to lowercase for case-insensitive comparison
    season_lower = season.lower()

    # Split the pipe-separated seasons and check if the chosen season is in the list
    results = []
    for place in places:
        # place["seasons"] looks like "monsoon|winter"
        # .split("|") turns it into ["monsoon", "winter"]
        # We check if season_lower is in that list
        season_list = place.get("seasons", "").lower().split("|")
        if season_lower in season_list:
            results.append(place)

    return results


def sort_by_rating(places):
    """
    Sorts a list of places so the best ones come first.
    Sorting rule: highest rating first.
    If two places have the same rating, the closer one comes first.

    Parameters:
      places -- list of place dictionaries, each must have 'rating'
                and 'distance_km' keys

    Returns:
      A new sorted list (does not change the original list).

    Example:
      sort_by_rating(places) -> [place with 4.9, place with 4.8, ...]
    """
    # sorted() with two keys: rating descending (-), distance ascending (+)
    # Python sorts by the first key first, then the second key for ties
    return sorted(places, key=lambda p: (-p["rating"], p["distance_km"]))


def get_all_categories(places):
    """
    Returns a sorted list of all unique category names found in the data.

    Parameters:
      places -- list of place dictionaries (from load_places)

    Returns:
      A sorted list of unique category strings.

    Example:
      get_all_categories(places)
      -> ['Beach', 'Cave', 'Fort', 'Hill Station', 'Monument', 'Nature', 'Other', 'Temple']
    """
    # Use a set to collect unique categories (sets do not allow duplicates)
    categories = set()

    for place in places:
        categories.add(place["category"])  # add each category to the set

    return sorted(categories)  # sort alphabetically and return as a list


def get_recommendations(user_lat, user_lon, radius_km, category="", season=""):
    """
    The main function that ties everything together.
    Loads data, finds nearby places, filters by category and season,
    sorts by rating, and returns the top 10.

    Parameters:
      user_lat  -- user's latitude  (e.g. 18.5204)
      user_lon  -- user's longitude (e.g. 73.8567)
      radius_km -- search radius in kilometres (e.g. 50)
      category  -- optional category filter, e.g. "Fort" (default: "" = all)
      season    -- optional season filter, e.g. "monsoon" (default: "" = all)

    Returns:
      A list of up to 10 place dictionaries, sorted best-first,
      each with a 'distance_km' key.

    Example:
      get_recommendations(18.5204, 73.8567, 50, "Fort", "monsoon")
      -> top monsoon forts within 50 km of Pune
    """
    # Step 1: Load all places from MongoDB
    all_places = load_places()

    # Step 2: Keep only places within the radius (also adds distance_km)
    nearby = find_nearby_places(all_places, user_lat, user_lon, radius_km)

    # Step 3: Filter by category (if a category was given)
    filtered = filter_by_category(nearby, category)

    # Step 4: Filter by season (if a season was given)
    filtered = filter_by_season(filtered, season)

    # Step 5: Sort by rating (best first), then by distance (closest first for ties)
    sorted_places = sort_by_rating(filtered)

    # Step 5: Return only the top 10 results
    return sorted_places[:10]


# ─────────────────────────────────────────────
# FUTURE FEATURE: Users collection
# ─────────────────────────────────────────────
#
# get_users_collection() in database.py is already set up and ready.
# It returns the MongoDB 'users' collection.
# The collection is currently empty — no login feature yet.
#
# When the login / user-reviews feature is built, it will work like this:
#
#   from database import get_users_collection
#
#   def save_user(name, email, password_hash):
#       """Saves a new user document to the 'users' collection."""
#       collection = get_users_collection()
#       collection.insert_one({
#           "name":          name,
#           "email":         email,
#           "password_hash": password_hash   # NEVER store plain passwords
#       })
#
#   def find_user_by_email(email):
#       """Looks up a user by their email address."""
#       collection = get_users_collection()
#       return collection.find_one({"email": email}, {"_id": 0})
#
# Nothing above is active code — it is here only as a guide for future work.
