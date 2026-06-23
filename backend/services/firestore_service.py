import os
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from google.cloud import firestore
from backend.models.customer import CustomerProfile, Transaction
from backend.models.life_event import LifeEventDetection
from backend.models.engagement import EngagementPlan, ProductRecommendation

logger = logging.getLogger("lifepulse.firestore")

class LocalJsonDb:
    """
    Simulates a Firestore database locally using a JSON file.
    This guarantees that the SBI LifePulse app works without GCP/Firebase setup.
    """
    def __init__(self, file_path: str = "data/local_db.json"):
        # Resolve path relative to backend root or workspace if needed
        self.file_path = file_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            initial_data = {
                "customers": {},
                "life_events": {},
                "engagement_plans": {},
                "conversations": {},
                "engagement_feed": []
            }
            with open(self.file_path, "w") as f:
                json.dump(initial_data, f, indent=2)

    def _read_data(self) -> Dict[str, Any]:
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except Exception:
            return {
                "customers": {},
                "life_events": {},
                "engagement_plans": {},
                "conversations": {},
                "engagement_feed": []
            }

    def _write_data(self, data: Dict[str, Any]):
        try:
            with open(self.file_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing to local JSON DB: {e}")

    def save(self, collection: str, doc_id: str, data: Dict[str, Any]):
        db_data = self._read_data()
        if collection not in db_data:
            db_data[collection] = {}
        db_data[collection][doc_id] = data
        self._write_data(db_data)

    def get(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        db_data = self._read_data()
        return db_data.get(collection, {}).get(doc_id)

    def list_collection(self, collection: str) -> List[Dict[str, Any]]:
        db_data = self._read_data()
        coll = db_data.get(collection, {})
        return list(coll.values())

    def append_feed(self, item: Dict[str, Any]):
        db_data = self._read_data()
        if "engagement_feed" not in db_data:
            db_data["engagement_feed"] = []
        db_data["engagement_feed"].insert(0, item) # Newest first
        self._write_data(db_data)

    def get_feed(self) -> List[Dict[str, Any]]:
        db_data = self._read_data()
        return db_data.get("engagement_feed", [])


class FirestoreService:
    def __init__(self):
        self.db = None
        self.local_db = None
        
        # Try to initialize Firestore Client
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("FIREBASE_PROJECT_ID")
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if project_id:
            try:
                # If credentials path is provided and exists
                if cred_path and os.path.exists(cred_path):
                    self.db = firestore.Client.from_service_account_json(cred_path)
                else:
                    self.db = firestore.Client(project=project_id)
                logger.info(f"FirestoreService initialized successfully for GCP Project: {project_id}")
            except Exception as e:
                logger.error(f"Failed to initialize Firestore Client: {e}. Falling back to LocalJsonDb.")
        
        if not self.db:
            # Fallback to local DB
            self.local_db = LocalJsonDb()
            logger.info("Running FirestoreService in LOCAL SIMULATOR mode (data/local_db.json)")

    async def save_customer(self, customer: CustomerProfile) -> str:
        data = customer.model_dump()
        # Convert datetime objects to ISO strings for JSON storage
        for tx in data.get("transactions", []):
            if isinstance(tx.get("date"), datetime):
                tx["date"] = tx["date"].isoformat()
                
        if self.db:
            doc_ref = self.db.collection("customers").document(customer.customer_id)
            doc_ref.set(data)
        else:
            self.local_db.save("customers", customer.customer_id, data)
        return customer.customer_id

    async def get_customer(self, customer_id: str) -> Optional[CustomerProfile]:
        if self.db:
            doc_ref = self.db.collection("customers").document(customer_id)
            doc = doc_ref.get()
            if doc.exists:
                return CustomerProfile.model_validate(doc.to_dict())
            return None
        else:
            data = self.local_db.get("customers", customer_id)
            if data:
                return CustomerProfile.model_validate(data)
            return None

    async def save_life_event(self, event: LifeEventDetection) -> str:
        data = event.model_dump()
        if isinstance(data.get("detected_at"), datetime):
            data["detected_at"] = data["detected_at"].isoformat()
            
        if self.db:
            # Update customer status
            cust_ref = self.db.collection("customers").document(event.customer_id)
            cust_ref.update({"detected_life_event": event.detected_event})
            
            # Save life event
            doc_ref = self.db.collection("life_events").document(event.customer_id)
            doc_ref.set(data)
        else:
            # Update customer
            cust = await self.get_customer(event.customer_id)
            if cust:
                cust.detected_life_event = event.detected_event
                await self.save_customer(cust)
                
            self.local_db.save("life_events", event.customer_id, data)
            
        return event.customer_id

    async def get_life_event(self, customer_id: str) -> Optional[LifeEventDetection]:
        if self.db:
            doc_ref = self.db.collection("life_events").document(customer_id)
            doc = doc_ref.get()
            if doc.exists:
                return LifeEventDetection.model_validate(doc.to_dict())
            return None
        else:
            data = self.local_db.get("life_events", customer_id)
            if data:
                return LifeEventDetection.model_validate(data)
            return None

    async def save_engagement_plan(self, plan: EngagementPlan) -> str:
        data = plan.model_dump()
        if isinstance(data.get("created_at"), datetime):
            data["created_at"] = data["created_at"].isoformat()
            
        if self.db:
            doc_ref = self.db.collection("engagement_plans").document(plan.customer_id)
            doc_ref.set(data)
        else:
            self.local_db.save("engagement_plans", plan.customer_id, data)
        return plan.customer_id

    async def get_engagement_plan(self, customer_id: str) -> Optional[EngagementPlan]:
        if self.db:
            doc_ref = self.db.collection("engagement_plans").document(customer_id)
            doc = doc_ref.get()
            if doc.exists:
                return EngagementPlan.model_validate(doc.to_dict())
            return None
        else:
            data = self.local_db.get("engagement_plans", customer_id)
            if data:
                return EngagementPlan.model_validate(data)
            return None

    async def log_engagement_activity(self, activity: Dict[str, Any]) -> str:
        activity["timestamp"] = datetime.now().isoformat()
        if self.db:
            doc_ref = self.db.collection("engagement_feed").document()
            doc_ref.set(activity)
            activity_id = doc_ref.id
        else:
            activity_id = f"FEED_{int(datetime.now().timestamp())}"
            activity["id"] = activity_id
            self.local_db.append_feed(activity)
        return activity_id

    async def get_engagement_feed(self) -> List[Dict[str, Any]]:
        if self.db:
            feed_ref = self.db.collection("engagement_feed").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(50)
            docs = feed_ref.stream()
            return [doc.to_dict() for doc in docs]
        else:
            return self.local_db.get_feed()

    async def save_conversation_turn(self, customer_id: str, role: str, message: str) -> str:
        turn = {
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        if self.db:
            doc_ref = self.db.collection("conversations").document(customer_id)
            doc = doc_ref.get()
            history = []
            if doc.exists:
                history = doc.to_dict().get("history", [])
            history.append(turn)
            doc_ref.set({"history": history})
        else:
            data = self.local_db.get("conversations", customer_id) or {"history": []}
            data["history"].append(turn)
            self.local_db.save("conversations", customer_id, data)
        return customer_id

    async def get_conversation_history(self, customer_id: str) -> List[Dict[str, Any]]:
        if self.db:
            doc_ref = self.db.collection("conversations").document(customer_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict().get("history", [])
            return []
        else:
            data = self.local_db.get("conversations", customer_id)
            return data.get("history", []) if data else []

    async def reset_conversation(self, customer_id: str):
        if self.db:
            doc_ref = self.db.collection("conversations").document(customer_id)
            doc_ref.delete()
        else:
            data = {"history": []}
            self.local_db.save("conversations", customer_id, data)

    async def get_all_customers_with_events(self) -> List[Dict[str, Any]]:
        if self.db:
            customers_ref = self.db.collection("customers")
            docs = customers_ref.stream()
            results = []
            for doc in docs:
                cust_data = doc.to_dict()
                # Fetch life event if exists
                event_ref = self.db.collection("life_events").document(cust_data["customer_id"])
                event_doc = event_ref.get()
                if event_doc.exists:
                    cust_data["life_event_details"] = event_doc.to_dict()
                results.append(cust_data)
            return results
        else:
            customers = self.local_db.list_collection("customers")
            results = []
            for cust in customers:
                event_data = self.local_db.get("life_events", cust["customer_id"])
                if event_data:
                    cust["life_event_details"] = event_data
                results.append(cust)
            return results
