import json
import logging
from datetime import datetime
from backend.models.customer import CustomerProfile
from backend.models.life_event import LifeEventDetection
from backend.services.bigquery_service import BigQueryService
from backend.services.vertex_service import VertexService
from backend.services.gemini_service import GeminiService
from backend.services.firestore_service import FirestoreService
from backend.utils.prompt_templates import LIFE_EVENT_DETECTION_PROMPT

logger = logging.getLogger("lifepulse.agents.life_event")

class LifeEventAgent:
    def __init__(
        self,
        bq_service: BigQueryService,
        vertex_service: VertexService,
        gemini_service: GeminiService,
        firestore_service: FirestoreService
    ):
        self.bq_service = bq_service
        self.vertex_service = vertex_service
        self.gemini_service = gemini_service
        self.firestore_service = firestore_service

    async def detect_life_event(self, customer_id: str) -> LifeEventDetection:
        """
        Runs the multi-layer detection pipeline for a customer:
        1. Extract behavioral signals from BigQuery.
        2. Heuristic ML classification via Vertex AI.
        3. Generates refined classification and hooks using Gemini 3.5 Flash.
        4. Saves and returns the LifeEventDetection result.
        """
        logger.info(f"Triggering life event detection for customer: {customer_id}")
        
        # Load profile
        customer = await self.firestore_service.get_customer(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found in database.")

        # Layer 1: BigQuery signal extraction
        transactions_dict = [t.model_dump() for t in customer.transactions]
        signals_data = self.bq_service.extract_behavioral_signals(transactions_dict)
        
        # Layer 1b: Heuristic classification via Vertex
        heur_event, heur_conf = self.vertex_service.classify_signals(signals_data, transactions_dict)
        logger.info(f"Vertex heuristic result: {heur_event} with confidence {heur_conf}")

        # Layer 2: Gemini Refinement
        # Render prompt
        prompt = LIFE_EVENT_DETECTION_PROMPT.format(
            name=customer.name,
            age=customer.age,
            city=customer.city,
            monthly_income=customer.monthly_income,
            risk_profile=customer.risk_profile,
            existing_products=", ".join(customer.existing_products),
            signals=json.dumps(signals_data["signals"], indent=2)
        )

        detected_event = heur_event
        confidence_score = heur_conf
        key_signals = signals_data["signals"].get("merchant_categories_spike", [])[:3]
        recommended_products = []
        urgency = "LOW"
        hook = f"Plan your financial future with SBI's premier savings options, {customer.name}."

        # Make LLM Call
        response_text = self.gemini_service.call_model(prompt, json_mode=True)
        
        try:
            res_json = json.loads(response_text)
            
            # Extract values from Gemini JSON
            detected_event = res_json.get("detected_event", heur_event)
            confidence_score = float(res_json.get("confidence_score", heur_conf))
            key_signals = res_json.get("key_signals", key_signals)
            recommended_products = res_json.get("recommended_products", recommended_products)
            urgency = res_json.get("engagement_urgency", urgency)
            hook = res_json.get("personalized_hook", hook)
            
            logger.info("Successfully classified event via Gemini API.")
        except Exception as e:
            logger.error(f"Error parsing Gemini classification JSON response. Using Vertex fallback: {e}")
            
            # Map products deterministically for fallback
            if heur_event == "MARRIAGE":
                recommended_products = ["SBI Happy Home Loan", "SBI Joint Savings Account", "SBI Life - Smart Shield"]
                urgency = "HIGH"
                hook = f"Badhaai ho, {customer.name}! Let's make managing your new joint finances seamless."
            elif heur_event == "JOB_CHANGE":
                recommended_products = ["SBI Wealth Savings Account", "SBI Card ELITE", "SBI Mutual Fund SIP"]
                urgency = "HIGH"
                hook = f"Congratulations on the new job, {customer.name}! Ready to elevate your savings plan?"
            elif heur_event == "NEW_BABY":
                recommended_products = ["SBI Life - Smart Champ Insurance", "SBI Family Floater Health Insurance"]
                urgency = "HIGH"
                hook = f"Welcoming a little one, {customer.name}? Secure their bright education future with SBI."
            elif heur_event == "HOME_PURCHASE":
                recommended_products = ["SBI Home Loan", "SBI Home Shield Insurance"]
                urgency = "HIGH"
                hook = f"Buying a home, {customer.name}? Protect your dream home with SBI Suraksha."
            elif heur_event == "PRE_RETIREMENT":
                recommended_products = ["SBI Senior Citizen Savings Scheme", "SBI Annuity Deposit Scheme"]
                urgency = "MEDIUM"
                hook = f"Approaching your golden years, {customer.name}? Plan a steady monthly income stream."
            elif heur_event == "TRAVEL_PHASE":
                recommended_products = ["SBI Multi-Currency Travel Card", "SBI Card miles"]
                urgency = "MEDIUM"
                hook = f"Planning your next journey, {customer.name}? Travel smart with SBI Multi-Currency card benefits."
            elif heur_event == "SALARY_HIKE":
                recommended_products = ["SBI Magnum Midcap Mutual Fund SIP", "SBI Card Prime"]
                urgency = "MEDIUM"
                hook = f"Congratulations on the salary hike, {customer.name}! Put it to work in high-performing SIPs."
            else:
                recommended_products = ["SBI Savings Account", "SBI Fixed Deposit"]
                urgency = "LOW"
                hook = f"Save for your dreams with SBI's premier savings options, {customer.name}."

        # Create model instance
        detection_result = LifeEventDetection(
            customer_id=customer_id,
            detected_event=detected_event,
            confidence_score=confidence_score,
            key_signals=key_signals,
            recommended_products=recommended_products,
            engagement_urgency=urgency,
            personalized_hook=hook,
            detected_at=datetime.now()
        )

        # Save event to DB
        await self.firestore_service.save_life_event(detection_result)
        
        return detection_result
