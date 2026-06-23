import os
import sys
import json
import asyncio

# Adjust python path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.firestore_service import FirestoreService
from backend.services.bigquery_service import BigQueryService
from backend.services.vertex_service import VertexService
from backend.services.gemini_service import GeminiService
from backend.agents.life_event_agent import LifeEventAgent
from backend.agents.engagement_agent import EngagementAgent
from backend.models.customer import CustomerProfile

async def seed_data():
    print("Starting SBI LifePulse Database Seeding Process...")
    
    # 1. Initialize Services
    db_service = FirestoreService()
    bq_service = BigQueryService()
    vertex_service = VertexService()
    gemini_service = GeminiService()
    
    # 2. Initialize Agents
    life_event_agent = LifeEventAgent(bq_service, vertex_service, gemini_service, db_service)
    engagement_agent = EngagementAgent(gemini_service, db_service)
    
    # 3. Load synthetic customer data
    sample_file = "data/sample_customers.json"
    if not os.path.exists(sample_file):
        sample_file = "../data/sample_customers.json"
        
    if not os.path.exists(sample_file):
        print("Error: sample_customers.json not found! Run data_simulator.py first.")
        return
        
    with open(sample_file, "r") as f:
        customers_data = json.load(f)
        
    print(f"Loaded {len(customers_data)} customer profiles from json.")
    
    # 4. Save profiles and run classification + engagement planning
    seeded_count = 0
    events_detected = 0
    plans_created = 0
    
    for cust_dict in customers_data:
        try:
            cust_obj = CustomerProfile.model_validate(cust_dict)
            
            # Save customer first
            await db_service.save_customer(cust_obj)
            seeded_count += 1
            print(f"[{seeded_count}/10] Saved customer profile: {cust_obj.name}")
            
            # Run event detection
            event_result = await life_event_agent.detect_life_event(cust_obj.customer_id)
            events_detected += 1
            print(f"      -> Detected Event: {event_result.detected_event} (Confidence: {event_result.confidence_score})")
            
            # Run engagement plan generation
            # Load updated profile
            updated_cust = await db_service.get_customer(cust_obj.customer_id)
            plan_result = await engagement_agent.generate_engagement_plan(updated_cust, event_result)
            plans_created += 1
            print(f"      -> Engagement Plan created. Opening: '{plan_result.opening_message[:45]}...'")
            
        except Exception as e:
            print(f"Error seeding customer {cust_dict.get('name')}: {e}")
            
    print("\nDatabase Seeding Summary:")
    print(f"Saved {seeded_count} customers")
    print(f"Detected {events_detected} life events")
    print(f"Created {plans_created} engagement plans")
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
