import random
from app import create_app, db
from app.models.dive_site import DiveSite

DIVE_SITES_DATA = [
    {"municipality": "Bogo", "name": "Capitancillo Islet", "coords": (11.05, 124.1)},
    {"municipality": "Daanbantayan", "name": "Bantigue Cove", "coords": (11.27, 124.03)},
    {"municipality": "Daanbantayan", "name": "Chocolate Island", "coords": (11.31, 124.06)},
    {"municipality": "Daanbantayan", "name": "Coral Garden", "coords": (11.28, 124.02)},
    {"municipality": "Daanbantayan", "name": "Dakit-Dakit", "coords": (11.29, 124.08)},
    {"municipality": "Daanbantayan", "name": "Gato Island", "coords": (11.45, 124.02)},
    {"municipality": "Daanbantayan", "name": "Kang Katao", "coords": (11.4, 124.1)},
    {"municipality": "Daanbantayan", "name": "Kimud Shoal", "coords": (11.35, 124.2)},
    {"municipality": "Daanbantayan", "name": "Lapus-Lapus", "coords": (11.32, 124.11)},
    {"municipality": "Daanbantayan", "name": "Lighthouse", "coords": (11.33, 124.12)},
    {"municipality": "Daanbantayan", "name": "Monad Shoal", "coords": (11.3, 124.19)},
    {"municipality": "Moalboal", "name": "Marine Sanctuary", "coords": (9.95, 123.36)},
    {"municipality": "Moalboal", "name": "White Beach", "coords": (9.98, 123.37)},
    {"municipality": "Moalboal", "name": "Dolphin House", "coords": (9.97, 123.37)},
    {"municipality": "Moalboal", "name": "Magpayong Rock", "coords": (9.96, 123.37)},
    {"municipality": "Moalboal", "name": "Tuble Point", "coords": (9.94, 123.36)},
    {"municipality": "Moalboal", "name": "Kasai Wall", "coords": (9.93, 123.36)},
    {"municipality": "Moalboal", "name": "White House", "coords": (9.92, 123.36)},
    {"municipality": "Moalboal", "name": "Oscas Cave", "coords": (9.91, 123.36)},
    {"municipality": "Moalboal", "name": "House Reef", "coords": (9.94, 123.37)},
    {"municipality": "Moalboal", "name": "Talisay Point", "coords": (9.9, 123.36)},
    {"municipality": "Moalboal", "name": "Pescador Island", "coords": (9.92, 123.33)},
    {"municipality": "Moalboal", "name": "Tongo Point", "coords": (9.89, 123.36)},
    {"municipality": "Moalboal", "name": "Sampaguita", "coords": (9.88, 123.36)},
    {"municipality": "Asturias", "name": "Langub Marine Sanctuary", "coords": (10.57, 123.72)},
    {"municipality": "Asturias", "name": "Looc Norte Marine Sanctuary", "coords": (10.58, 123.73)},
    {"municipality": "Asturias", "name": "Owak Marine Sanctuary", "coords": (10.59, 123.74)},
    {"municipality": "Asturias", "name": "San Roque Coral Garden", "coords": (10.6, 123.75)},
    {"municipality": "Asturias", "name": "Sta. Lucia Marine Protected Area", "coords": (10.61, 123.76)},
    {"municipality": "Asturias", "name": "Bagacawa Reef", "coords": (10.62, 123.77)},
    {"municipality": "Asturias", "name": "Tubigagmanok Marine Sanctuary", "coords": (10.63, 123.78)},
    {"municipality": "Catmon", "name": "Bachao Sanctuary", "coords": (10.67, 124.01)},
    {"municipality": "Catmon", "name": "Tinibgan", "coords": (10.68, 124.02)},
    {"municipality": "Catmon", "name": "Rañola Wall Dive", "coords": (10.69, 124.03)},
    {"municipality": "Catmon", "name": "Heramiz (Katmon Cove)", "coords": (10.7, 124.04)},
    {"municipality": "Catmon", "name": "Barangay Panalipan", "coords": (10.71, 124.05)},
    {"municipality": "Catmon", "name": "Barangay Binongkalan", "coords": (10.72, 124.06)},
    {"municipality": "Cordova", "name": "Gilutongan Marine Sanctuary", "coords": (10.2, 123.98)},
]

MARINE_LIFE_OPTIONS = [
    "Thresher Shark", "Whale Shark", "Sardine Run", "Sea Turtle", "Frogfish",
    "Nudibranch", "Pygmy Seahorse", "Manta Ray", "Lionfish", "Barracuda",
    "Moray Eel", "Clownfish", "Mandarin Fish", "Octopus", "Cuttlefish"
]

def seed():
    app = create_app()
    with app.app_context():
        # Optional: Clear existing dive sites
        # DiveSite.query.delete()
        
        for site in DIVE_SITES_DATA:
            # Check if site already exists by name
            existing = DiveSite.query.filter_by(name=site["name"]).first()
            if existing:
                print(f"Site '{site['name']}' already exists, skipping.")
                continue

            # Randomize some attributes
            lat, lon = site["coords"]
            # Add small random jitter to coordinates
            lat += random.uniform(-0.005, 0.005)
            lon += random.uniform(-0.005, 0.005)

            marine_life = random.sample(MARINE_LIFE_OPTIONS, k=random.randint(3, 7))
            
            new_site = DiveSite(
                name=site["name"],
                latitude=lat,
                longitude=lon,
                marine_biodiversity=round(random.uniform(3.5, 9.5), 1),
                difficulty=random.randint(1, 5),
                photography_score=round(random.uniform(4.0, 9.5), 1),
                max_depth=round(random.uniform(15, 45), 1),
                marine_life=", ".join(marine_life),
                crowd_level=round(random.uniform(0.1, 0.9), 1)
            )
            db.session.add(new_site)
        
        db.session.commit()
        print("Successfully seeded dive sites!")

if __name__ == "__main__":
    seed()
