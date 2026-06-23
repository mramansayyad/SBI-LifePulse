import os
import logging
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import routers
from backend.routers import customers, events, engage, chat

# Import services & agents
from backend.services.firestore_service import FirestoreService
from backend.services.bigquery_service import BigQueryService
from backend.services.vertex_service import VertexService
from backend.services.gemini_service import GeminiService
from backend.agents.life_event_agent import LifeEventAgent
from backend.agents.engagement_agent import EngagementAgent
from backend.agents.conversation_agent import ConversationAgent
from backend.models.customer import CustomerProfile

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("lifepulse.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Initialization
    logger.info("Initializing SBI LifePulse Backend Services...")
    
    # 1. Initialize Services
    app.state.firestore_service = FirestoreService()
    app.state.bq_service = BigQueryService()
    app.state.vertex_service = VertexService()
    app.state.gemini_service = GeminiService()
    
    # 2. Initialize Agents
    app.state.life_event_agent = LifeEventAgent(
        app.state.bq_service,
        app.state.vertex_service,
        app.state.gemini_service,
        app.state.firestore_service
    )
    app.state.engagement_agent = EngagementAgent(
        app.state.gemini_service,
        app.state.firestore_service
    )
    app.state.conversation_agent = ConversationAgent(
        app.state.gemini_service,
        app.state.firestore_service
    )
    
    # 3. Auto-seed Database if empty
    logger.info("Checking database state for seeding...")
    try:
        existing_customers = await app.state.firestore_service.get_all_customers_with_events()
        if not existing_customers:
            logger.info("No customers found in database. Auto-seeding from sample files...")
            # Try to load sample_customers.json
            sample_file = "../data/sample_customers.json"
            if not os.path.exists(sample_file):
                sample_file = "data/sample_customers.json"
                
            if os.path.exists(sample_file):
                with open(sample_file, "r") as f:
                    customers_data = json.load(f)
                
                for cust_dict in customers_data:
                    cust_obj = CustomerProfile.model_validate(cust_dict)
                    await app.state.firestore_service.save_customer(cust_obj)
                    logger.info(f"Auto-seeded customer: {cust_obj.name} ({cust_obj.customer_id})")
                logger.info("Auto-seeding completed successfully!")
            else:
                logger.warning(f"Could not find sample customer data file at {sample_file}. Run data_simulator.py first.")
        else:
            logger.info(f"Database contains {len(existing_customers)} customers. Skipping auto-seeding.")
    except Exception as e:
        logger.error(f"Error checking/seeding database: {e}")
        
    yield
    
    # Shutdown logic
    logger.info("Shutting down SBI LifePulse Services...")

app = FastAPI(
    title="SBI LifePulse API",
    description="Proactive Agentic Life Event Intelligence Platform Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(customers.router)
app.include_router(events.router)
app.include_router(engage.router)
app.include_router(chat.router)

@app.get("/health", tags=["system"])
def health_check():
    """
    Service health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat() if 'datetime' in globals() else "active",
        "service": "SBI LifePulse Backend"
    }

from datetime import datetime
