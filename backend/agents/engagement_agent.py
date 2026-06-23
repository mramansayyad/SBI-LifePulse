import json
import logging
from datetime import datetime
from backend.models.customer import CustomerProfile
from backend.models.life_event import LifeEventDetection
from backend.models.engagement import EngagementPlan, ProductRecommendation
from backend.services.gemini_service import GeminiService
from backend.services.firestore_service import FirestoreService
from backend.utils.prompt_templates import ENGAGEMENT_GENERATION_PROMPT

logger = logging.getLogger("lifepulse.agents.engagement")

class EngagementAgent:
    def __init__(self, gemini_service: GeminiService, firestore_service: FirestoreService):
        self.gemini_service = gemini_service
        self.firestore_service = firestore_service

    async def generate_engagement_plan(
        self,
        customer: CustomerProfile,
        life_event: LifeEventDetection
    ) -> EngagementPlan:
        """
        Generates a hyper-personalized, emotionally intelligent engagement plan using Gemini.
        Saves the plan in Firestore and returns it.
        """
        logger.info(f"Generating engagement plan for customer {customer.customer_id} based on {life_event.detected_event}")

        # Render prompt
        prompt = ENGAGEMENT_GENERATION_PROMPT.format(
            name=customer.name,
            city=customer.city,
            life_event=life_event.detected_event,
            key_signals=", ".join(life_event.key_signals),
            existing_products=", ".join(customer.existing_products),
            recommended_products=", ".join(life_event.recommended_products)
        )

        # Call Gemini Service
        response_text = self.gemini_service.call_model(prompt, json_mode=True)

        try:
            res_json = json.loads(response_text)
            
            # Map recommendations
            prod_recs = []
            for rec in res_json.get("product_recommendations", []):
                prod_recs.append(
                    ProductRecommendation(
                        product_name=rec.get("product_name", "SBI Product"),
                        product_id=rec.get("product_id", "PROD_GEN"),
                        why_now=rec.get("why_now", "Fits your financial stage."),
                        expected_benefit=rec.get("expected_benefit", "High savings or protections."),
                        cta_text=rec.get("cta_text", "Apply")
                    )
                )

            # Build EngagementPlan
            plan = EngagementPlan(
                customer_id=customer.customer_id,
                life_event=life_event.detected_event,
                opening_message=res_json.get("opening_message", ""),
                conversation_starters=res_json.get("conversation_starters", []),
                product_recommendations=prod_recs,
                channel_priority=res_json.get("channel_priority", ["whatsapp", "app_notification"]),
                best_contact_time=res_json.get("best_contact_time", "12:00 PM"),
                created_at=datetime.now()
            )
            
            logger.info("Successfully generated engagement plan via Gemini API.")
            
        except Exception as e:
            logger.error(f"Error parsing Gemini engagement plan JSON: {e}. Using fallback generator.")
            
            # Fallback engagement plan logic based on event type
            opening = f"Namaste {customer.name}! Hope you are doing well. I noticed some interesting patterns in your account. As a personal helper, I'd love to chat about SBI products that could support your goals."
            starters = ["How can I help you save more today?", "Are you planning any major purchases soon?"]
            prods = life_event.recommended_products or ["SBI Joint Savings Account", "SBI Home Loan"]
            
            if life_event.detected_event == "MARRIAGE":
                opening = f"Namaste {customer.name}! 💍 Badhaai ho on this beautiful milestone of marriage. I'm Arya, your SBI personal financial companion. We have tailored joint plans that can help you and your partner organize your finances together. Can I share some ideas?"
                starters = ["Would you like to explore setting up an SBI Joint Account?", "Are you planning a new house together?"]
            elif life_event.detected_event == "JOB_CHANGE":
                opening = f"Namaste {customer.name}! Congratulations on your new career step! 💼 Ready to accelerate your savings? I'm Arya, your SBI personal companion. Let's make your salary hike work for your financial security."
                starters = ["Shall we set up an automatic SIP for your new income level?", "Would you like a premium credit card like SBI Card ELITE?"]
            elif life_event.detected_event == "NEW_BABY":
                opening = f"Namaste {customer.name}! 👶 Congratulations on welcoming a new baby to your family! I'm Arya, your SBI personal companion. Let's make sure your family's health and education plans are sorted so you can focus on your little one."
                starters = ["Would you like to learn about SBI Smart Champ child plans?", "Would you like to review SBI Family Floater insurance?"]
            elif life_event.detected_event == "HOME_PURCHASE":
                opening = f"Namaste {customer.name}! 🏠 Heartiest congratulations on your new home booking! I'm Arya from SBI. Buying a home is a huge step. Let's secure it and look into loan terms to ease your mind."
                starters = ["Would you like to estimate your EMI for an SBI Home Loan top-up?", "Should we check out SBI Home Shield insurance policies?"]
            elif life_event.detected_event == "PRE_RETIREMENT":
                opening = f"Namaste {customer.name}! Warm greetings. 🌅 As you prepare for your next rewarding phase of life, I'm Arya, your SBI companion, here to ensure you have a secure, worry-free income structure."
                starters = ["Would you like to discuss the Senior Citizen Savings Scheme?", "Shall we set up a Fixed Deposit laddering schedule?"]

            prod_recs = []
            for i, p_name in enumerate(prods):
                prod_recs.append(
                    ProductRecommendation(
                        product_name=p_name,
                        product_id=f"PROD_{life_event.detected_event}_{i+1}",
                        why_now="Specially mapped for your current life phase.",
                        expected_benefit="Maximize growth, ease tax burden, and secure your family.",
                        cta_text="Check Eligibility"
                    )
                )

            plan = EngagementPlan(
                customer_id=customer.customer_id,
                life_event=life_event.detected_event,
                opening_message=opening,
                conversation_starters=starters,
                product_recommendations=prod_recs,
                channel_priority=["whatsapp", "app_notification", "call"],
                best_contact_time="12:00 PM - 2:00 PM",
                created_at=datetime.now()
            )

        # Save to DB
        await self.firestore_service.save_engagement_plan(plan)
        return plan
