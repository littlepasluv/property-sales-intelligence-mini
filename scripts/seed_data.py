import sys
import random
from pathlib import Path
from datetime import datetime, timedelta
from faker import Faker

# --- Add project root to Python path ---
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from app.core.database import SessionLocal, engine, Base
from app.models.lead import Lead
from app.models.followup import Followup

# --- Simulation Configuration ---
RANDOM_SEED = 42
NUM_LEADS = 28
DAYS_RANGE = 18
AVG_FOLLOWUPS_PER_LEAD = 3
LEAD_SOURCES = ["WhatsApp", "Instagram", "Facebook Ads", "Referral"]
LEAD_STATUSES = ["new", "contacted", "qualified", "closed", "lost"]

# Initialize Faker and set seed for deterministic data
fake = Faker("id_ID")  # Use Indonesian locale for names
random.seed(RANDOM_SEED)
Faker.seed(RANDOM_SEED)

def get_weighted_status(source: str) -> str:
    """
    Determines lead status with a higher probability of 'closed' for referrals.
    """
    if source == "Referral":
        # Higher chance for referrals to be qualified or closed
        return random.choices(
            LEAD_STATUSES, weights=[0.1, 0.2, 0.3, 0.3, 0.1], k=1
        )[0]
    else:
        # Standard distribution for other sources
        return random.choices(
            LEAD_STATUSES, weights=[0.3, 0.3, 0.2, 0.1, 0.1], k=1
        )[0]

def seed_data():
    """
    Generates and inserts realistic, production-like sales data for leads and follow-ups.
    """
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Clean existing data for a fresh seed
        print("Clearing old data...")
        db.query(Followup).delete()
        db.query(Lead).delete()
        db.commit()

        print(f"Seeding {NUM_LEADS} new leads...")

        # 1. Generate Leads
        leads = []
        for i in range(NUM_LEADS):
            created_date = datetime.now() - timedelta(days=random.randint(1, DAYS_RANGE))
            source = random.choice(LEAD_SOURCES)
            status = get_weighted_status(source)
            
            lead = Lead(
                name=fake.name(),
                phone=fake.unique.phone_number(),
                email=fake.unique.email(),
                source=source,
                status=status,
                created_at=created_date,
                notes=f"Initial inquiry from {source}."
            )
            leads.append(lead)
        
        db.add_all(leads)
        db.commit()
        
        # Refresh to get IDs
        for lead in leads:
            db.refresh(lead)
        
        print("Seeding follow-ups for each lead...")
        
        # 2. Generate Follow-ups for each Lead
        all_followups = []
        for lead in leads:
            num_followups = random.randint(1, AVG_FOLLOWUPS_PER_LEAD + 2)
            last_followup_date = lead.created_at

            for j in range(num_followups):
                # Determine delay for this follow-up
                # Social media leads might have longer delays
                delay_days = random.randint(0, 3)
                if lead.source in ["Instagram", "Facebook Ads"]:
                    delay_days += random.randint(0, 4) # Add extra delay

                followup_date = last_followup_date + timedelta(days=delay_days, hours=random.randint(1,12))

                # Ensure followup is not in the future
                if followup_date > datetime.now():
                    continue

                # Logic for status progression
                # This is a simplified example. A real-world scenario would be more complex.
                if j == 0:
                    followup_status = "contacted"
                    note = f"First contact made. Client seems interested."
                elif j == num_followups - 1:
                    # Last followup reflects the lead's final status
                    followup_status = lead.status
                    note = f"Final status: {lead.status}. Reason: {fake.sentence(nb_words=6)}"
                else:
                    followup_status = random.choice(["contacted", "qualified"])
                    note = f"Follow-up call scheduled. Client requested more details."

                # A lead can't be closed/lost and then have more follow-ups
                if lead.status in ["closed", "lost"] and j < num_followups -1:
                    break

                followup = Followup(
                    lead_id=lead.id,
                    note=note,
                    status=followup_status,
                    created_at=followup_date,
                    next_contact_date=(followup_date + timedelta(days=random.randint(3, 10))).date()
                )
                all_followups.append(followup)
                last_followup_date = followup_date

        db.add_all(all_followups)
        db.commit()
        print("Seed data inserted successfully!")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # This script requires 'Faker'. Install it with:
    # pip install Faker
    seed_data()
