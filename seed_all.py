import random
from datetime import date, time, timedelta, datetime, timezone
from app import create_app, db
from app.models.user import User, UserRole, VerificationStatus
from app.models.dive_site import DiveSite
from app.models.store import Store, DivingSchedule

def seed():
    app = create_app()
    with app.app_context():
        # 1. Create Admin
        admin = User.query.filter_by(email="admin@divina.com").first()
        if not admin:
            admin = User(
                first_name="Admin",
                last_name="User",
                email="admin@divina.com",
                role=UserRole.ADMIN
            )
            admin.set_password("admin123")
            db.session.add(admin)
            print("Admin created.")

        # 2. Create Dive Operators and Stores
        operators_data = [
            {"first": "Juan", "last": "Dela Cruz", "email": "juan@diveshop.com", "shop": "Cebu Dive Center"},
            {"first": "Maria", "last": "Santos", "email": "maria@blueocean.com", "shop": "Blue Ocean Divers"},
            {"first": "Pedro", "last": "Penduko", "email": "pedro@islandhop.com", "shop": "Island Hopping Adventure"},
            {"first": "Elena", "last": "Gomez", "email": "elena@deepsea.com", "shop": "Deep Sea Explorers"},
        ]

        dive_sites = DiveSite.query.all()
        if not dive_sites:
            print("No dive sites found. Please run seed_dive_sites.py first.")
            return

        for op in operators_data:
            user = User.query.filter_by(email=op["email"]).first()
            if not user:
                user = User(
                    first_name=op["first"],
                    last_name=op["last"],
                    email=op["email"],
                    role=UserRole.DIVE_OPERATOR,
                    verification_status=VerificationStatus.APPROVED,
                    verified_at=datetime.now(timezone.utc)
                )
                user.set_password("password123")
                db.session.add(user)
                db.session.flush() # To get user.id

                # Create Store
                # Pick a random dive site to center the store around
                base_site = random.choice(dive_sites)
                
                store = Store(
                    owner_id=user.id,
                    name=op["shop"],
                    description=f"Welcome to {op['shop']}! We provide the best diving experience in the region.",
                    contact_number=f"+63 917 {random.randint(100, 999)} {random.randint(1000, 9999)}",
                    address=f"Street {random.randint(1, 100)}, {base_site.name} Area",
                    latitude=base_site.latitude + random.uniform(-0.01, 0.01),
                    longitude=base_site.longitude + random.uniform(-0.01, 0.01),
                    type=random.choice(["popular", "regular", "boutique", "budget"]),
                    rating=round(random.uniform(3.5, 5.0), 1),
                    price_level=random.randint(1, 4),
                    has_rental=random.choice([True, False]),
                    has_nitrox=random.choice([True, False]),
                    has_training=random.choice([True, False]),
                    is_tech_friendly=random.choice([True, False])
                )
                
                # Link to 3-5 random dive sites
                store.dive_sites = random.sample(dive_sites, k=random.randint(3, 5))
                db.session.add(store)
                db.session.flush()

                # Add some schedules
                for i in range(5):
                    sched_date = date.today() + timedelta(days=random.randint(1, 30))
                    schedule = DivingSchedule(
                        store_id=store.id,
                        title=f"Exploring {random.choice(store.dive_sites).name}",
                        description="Join us for an amazing underwater adventure!",
                        date=sched_date,
                        start_time=time(hour=random.randint(7, 10), minute=0),
                        end_time=time(hour=random.randint(11, 15), minute=0),
                        price=float(random.randint(1500, 5000)),
                        max_slots=random.randint(5, 15),
                        booked_slots=random.randint(0, 5)
                    )
                    db.session.add(schedule)

                print(f"Operator {op['first']} and Store {op['shop']} created.")

        # 3. Create Regular Users
        regulars = [
            {"first": "Alice", "last": "Smith", "email": "alice@gmail.com"},
            {"first": "Bob", "last": "Johnson", "email": "bob@gmail.com"},
            {"first": "Charlie", "last": "Brown", "email": "charlie@gmail.com"},
        ]
        from app.models.user_preferences import UserDivePreferences
        for reg in regulars:
            user = User.query.filter_by(email=reg["email"]).first()
            if not user:
                user = User(
                    first_name=reg["first"],
                    last_name=reg["last"],
                    email=reg["email"],
                    role=UserRole.REGULAR
                )
                user.set_password("password123")
                db.session.add(user)
                db.session.flush()
                print(f"Regular user {reg['first']} created.")

            # Create Preferences
            if not user.dive_preferences:
                marine_life = random.sample(
                    ["Thresher Shark", "Whale Shark", "Sea Turtle", "Nudibranch", "Manta Ray"],
                    k=random.randint(1, 3)
                )
                prefs = UserDivePreferences(
                    user_id=user.id,
                    skill_level=random.randint(1, 5),
                    preferred_marine_life=", ".join(marine_life),
                    photography_priority=round(random.uniform(1.0, 10.0), 1),
                    depth_preference=round(random.uniform(10.0, 40.0), 1),
                    max_travel_distance=round(random.uniform(20.0, 100.0), 1),
                    requires_rental=random.choice([True, False]),
                    requires_nitrox=random.choice([True, False]),
                    requires_training=random.choice([True, False]),
                    is_tech_diver=random.choice([True, False]),
                    preferred_price_level=random.randint(1, 4)
                )
                db.session.add(prefs)
                print(f"Preferences for {reg['first']} created.")

        db.session.commit()
        print("Successfully seeded all mock data!")

if __name__ == "__main__":
    seed()
