# seed_trails.py
#
# ONE-TIME script: inserts the 4 themed trails into the MongoDB "trails" collection.
# Safe to run again — uses upsert so it updates existing, never creates duplicates.
#
# How to run:
#   py seed_trails.py
#
# Each trail has:
#   id          -- unique number
#   name        -- English name
#   name_mr     -- Marathi name
#   description -- English description
#   description_mr -- Marathi description
#   place_ids   -- ordered list of place ids from the places collection

from database import get_database

# ── Trail data ────────────────────────────────────────────────────────────
# place_ids are ordered for the route. For the Fort Trail, we order
# roughly south to north for a logical driving route.

TRAILS = [
    {
        "id": 1,
        "name": "Ashtavinayak Trail",
        "name_mr": "अष्टविनायक यात्रा",
        "description": "A pilgrimage circuit of the eight sacred Ganpati temples of Maharashtra. Traditionally done in a fixed order starting from Morgaon.",
        "description_mr": "महाराष्ट्राच्या आठ पवित्र गणपती मंदिरांचा यात्रामार्ग. परंपरेने मोरगावपासून एका निश्चित क्रमाने केली जाते.",
        "place_ids": [54, 55, 56, 57, 58, 59, 60, 61]
        # Order: Morgaon → Siddhatek → Pali → Mahad → Theur → Lenyadri → Ozar → Ranjangaon
    },
    {
        "id": 2,
        "name": "Jyotirlinga Trail",
        "name_mr": "ज्योतिर्लिंग यात्रा",
        "description": "The five Jyotirlingas of Maharashtra — ancient Shiva temples of immense spiritual significance. Bhimashankar and Trimbakeshwar are already on the map.",
        "description_mr": "महाराष्ट्राची पाच ज्योतिर्लिंगे — अपार आध्यात्मिक महत्त्वाची प्राचीन शिव मंदिरे. भीमाशंकर आणि त्र्यंबकेश्वर आधीच नकाशावर आहेत.",
        "place_ids": [14, 19, 62, 63, 64]
        # Order: Bhimashankar (Pune) → Trimbakeshwar (Nashik) → Grishneshwar (Aurangabad) → Aundha Nagnath (Hingoli) → Parli Vaijnath (Beed)
    },
    {
        "id": 3,
        "name": "Fort Trail",
        "name_mr": "किल्ला यात्रा",
        "description": "A journey through the great forts of Maharashtra — from the Maratha heartland near Pune to Kolhapur and Nagpur. Each fort tells a chapter of Maratha history.",
        "description_mr": "महाराष्ट्राच्या महान किल्ल्यांचा प्रवास — पुण्याजवळच्या मराठा भूमीपासून कोल्हापूर आणि नागपूरपर्यंत. प्रत्येक किल्ला मराठा इतिहासाचा एक अध्याय सांगतो.",
        "place_ids": [10, 12, 16, 18, 38, 44, 35, 47, 48]
        # Order: Shaniwar Wada → Sinhagad → Torna → Tikona → Panhala → Vishalgad → Sitabuldi → Nanded Fort → Kandhar
    },
    {
        "id": 4,
        "name": "Caves Trail",
        "name_mr": "लेणी यात्रा",
        "description": "Maharashtra's greatest cave temples — from ancient Buddhist shrines in Mumbai and Nashik to the UNESCO World Heritage masterpieces of Ajanta and Ellora.",
        "description_mr": "महाराष्ट्रातील सर्वात महान गुहा मंदिरे — मुंबई आणि नाशिकमधील प्राचीन बौद्ध धर्मस्थळांपासून अजिंठा आणि एलोराच्या UNESCO जागतिक वारसा उत्कृष्ट कृतींपर्यंत.",
        "place_ids": [9, 2, 15, 21, 59, 65, 66]
        # Order: Kanheri (Mumbai) → Elephanta (Mumbai) → Karla (Pune) → Pandavleni (Nashik) → Lenyadri (Nashik, cave temple) → Ajanta → Ellora
    },
]


def seed_trails():
    """
    Inserts or updates all 4 trails in the MongoDB 'trails' collection.
    Uses upsert=True so running this script again is safe — no duplicates.
    """
    db         = get_database()
    collection = db["trails"]    # get the 'trails' collection (created automatically)

    inserted = 0
    updated  = 0

    for trail in TRAILS:
        result = collection.update_one(
            {"id": trail["id"]},     # find by trail id
            {"$set": trail},          # update all fields
            upsert=True               # insert if not found
        )
        if result.upserted_id:
            inserted += 1
        else:
            updated += 1

    total = collection.count_documents({})
    print(f"Trails: inserted {inserted}, updated {updated}. Total: {total}")


if __name__ == "__main__":
    seed_trails()
