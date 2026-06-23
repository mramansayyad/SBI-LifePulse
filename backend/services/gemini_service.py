import os
import json
import logging
from typing import Optional, Any, List
import google.generativeai as genai

logger = logging.getLogger("lifepulse.gemini")

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.is_mock = not self.api_key or self.api_key == "your_gemini_api_key_here"
        
        if self.is_mock:
            logger.warning("GEMINI_API_KEY not found or default placeholder. Running GeminiService in MOCK MODE.")
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model_name = "gemini-3.5-flash"
                logger.info(f"GeminiService initialized with api_key: {self.api_key[:5]}... using model: {self.model_name}")
            except Exception as e:
                logger.error(f"Error configuring Gemini SDK: {e}. Falling back to MOCK MODE.")
                self.is_mock = True

    def call_model(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None, 
        json_mode: bool = False
    ) -> str:
        """
        Calls Gemini 3.5 Flash to generate content.
        If in mock mode, returns a simulated JSON or text based on the prompt content.
        """
        if self.is_mock:
            return self._generate_mock_response(prompt, json_mode)

        try:
            generation_config = {}
            if json_mode:
                generation_config["response_mime_type"] = "application/json"
            
            # Configure model
            model = genai.GenerativeModel(
                model_name="gemini-3.5-flash",
                generation_config=generation_config if generation_config else None,
                system_instruction=system_instruction
            )
            
            response = model.generate_content(prompt)
            text_response = response.text.strip()
            
            # Strip markdown fence blocks if they exist (just in case)
            if json_mode and text_response.startswith("```"):
                lines = text_response.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                text_response = "\n".join(lines).strip()
                
            return text_response
            
        except Exception as e:
            logger.error(f"Error calling live Gemini API: {e}. Falling back to mock data.")
            return self._generate_mock_response(prompt, json_mode)

    def _generate_mock_response(self, prompt: str, json_mode: bool) -> str:
        """
        Generates simulated realistic outputs for local testing when API key is missing or calls fail.
        """
        if not json_mode:
            # Simple text chat fallback
            if "marriage" in prompt.lower() or "priya" in prompt.lower():
                return "Hi Priya! 💍 Congratulations on your recent marriage! I'm Arya, your SBI personal financial companion. I'd love to help you plan your joint finances, check out joint account options, or help with home loan estimates. What would you like to know?"
            return "Hello! I am Arya, your SBI Personal Financial Companion. How can I help you today?"

        # JSON mode fallbacks
        # 1. Life Event Detection prompt
        if "detected_event" in prompt or "behavioral signals" in prompt:
            # Deduce which event from prompt context
            event = "NONE"
            confidence = 0.85
            signals = ["Regular transaction activity"]
            products = ["SBI General Savings Account"]
            hook = "Start saving for your dreams with SBI's premier savings options."
            urgency = "LOW"

            if "priya sharma" in prompt.lower():
                event = "MARRIAGE"
                confidence = 0.94
                signals = ["Spike in jewelry spend (Tanishq)", "Booking transactions at Taj Wedding Hall", "Honeymoon booking MakeMyTrip"]
                products = ["SBI Happy Home Loan", "SBI Joint Savings Account", "SBI Life - Smart Shield"]
                urgency = "HIGH"
                hook = "Congratulations, Priya! Let us help you and your partner build a secure foundation together."
            elif "rahul mehta" in prompt.lower():
                event = "JOB_CHANGE"
                confidence = 0.92
                signals = ["Salary credit increase of +40% from Google India", "Professional clothing purchase Zara", "LinkedIn premium subscription"]
                products = ["SBI Wealth Savings Account", "SBI Card ELITE", "SBI Mutual Fund SIP"]
                urgency = "HIGH"
                hook = "New role, Rahul? Elevate your savings and investment matches for your higher income."
            elif "anjali verma" in prompt.lower():
                event = "NEW_BABY"
                confidence = 0.95
                signals = ["Fortis Maternity Hospital payment", "Firstcry Baby products purchase", "Family Floater premium upgrade"]
                products = ["SBI Life - Smart Champ Insurance", "SBI Mutual Fund Child Fund", "SBI Family Floater Health Insurance"]
                urgency = "HIGH"
                hook = "Welcoming a little one, Anjali? Plan ahead for their bright future."
            elif "sanjay patil" in prompt.lower():
                event = "HOME_PURCHASE"
                confidence = 0.96
                signals = ["Sobha Developers escrow payment", "Sub-Registrar stamp duty fee", "IKEA Bangalore purchases"]
                products = ["SBI Home Loan", "SBI Home Shield Insurance", "SBI Suraksha Plan"]
                urgency = "HIGH"
                hook = "Buying a home, Sanjay? Secure your new nest with SBI's trusted home financing."
            elif "meena krishnan" in prompt.lower():
                event = "PRE_RETIREMENT"
                confidence = 0.89
                signals = ["PPF limit topup", "NPS contribution spike", "Pilgrimage travel booking"]
                products = ["SBI Senior Citizen Savings Scheme", "SBI Annuity Deposit Scheme", "SBI Fixed Deposit Laddering"]
                urgency = "MEDIUM"
                hook = "Approaching retirement, Meena? Ensure a steady income stream for your golden years."
            elif "shreya ghoshal" in prompt.lower():
                event = "TRAVEL_PHASE"
                confidence = 0.90
                signals = ["MakeMyTrip flights booking", "Airbnb India accommodations", "Niyo Global Forex card load"]
                products = ["SBI Card miles", "SBI Multi-Currency Travel Card", "SBI Travel Insurance"]
                urgency = "MEDIUM"
                hook = "Planning your next adventure, Shreya? Travel smart with SBI Forex card benefits."
            elif "vikram singh" in prompt.lower():
                event = "SALARY_HIKE"
                confidence = 0.88
                signals = ["Salary credit increase +20% from Wipro", "Regular merchant categories stability"]
                products = ["SBI Flexi Savings Scheme", "SBI Magnum Midcap Mutual Fund SIP", "SBI Card Prime"]
                urgency = "MEDIUM"
                hook = "Congratulations on the salary bump, Vikram! Channel it into high-performing SIPs."

            res = {
                "detected_event": event,
                "confidence_score": confidence,
                "key_signals": signals,
                "recommended_products": products,
                "engagement_urgency": urgency,
                "personalized_hook": hook
            }
            return json.dumps(res)

        # 2. Engagement Plan prompt
        if "opening_message" in prompt or "engagement_plans" in prompt or "Arya" in prompt:
            name = "Valued Customer"
            event = "Milestone"
            prods = ["SBI Joint Savings Account", "SBI Happy Home Loan"]
            
            if "priya" in prompt.lower():
                name = "Priya"
                event = "MARRIAGE"
                prods = ["SBI Joint Savings Account", "SBI Happy Home Loan", "SBI Life - Smart Shield"]
            elif "rahul" in prompt.lower():
                name = "Rahul"
                event = "JOB_CHANGE"
                prods = ["SBI Wealth Savings Account", "SBI Card ELITE", "SBI Mutual Fund SIP"]
            elif "anjali" in prompt.lower():
                name = "Anjali"
                event = "NEW_BABY"
                prods = ["SBI Life - Smart Champ Insurance", "SBI Mutual Fund Child Fund", "SBI Family Floater Health Insurance"]
            elif "sanjay" in prompt.lower():
                name = "Sanjay"
                event = "HOME_PURCHASE"
                prods = ["SBI Home Loan", "SBI Home Shield Insurance", "SBI Suraksha Plan"]
            elif "meena" in prompt.lower():
                name = "Meena"
                event = "PRE_RETIREMENT"
                prods = ["SBI Senior Citizen Savings Scheme", "SBI Annuity Deposit Scheme", "SBI Fixed Deposit Laddering"]
            elif "vikram" in prompt.lower():
                name = "Vikram"
                event = "SALARY_HIKE"
                prods = ["SBI Flexi Savings Scheme", "SBI Magnum Midcap Mutual Fund SIP", "SBI Card Prime"]
            elif "shreya" in prompt.lower():
                name = "Shreya"
                event = "TRAVEL_PHASE"
                prods = ["SBI Card miles", "SBI Multi-Currency Travel Card", "SBI Travel Insurance"]

            # Mock Product Recs
            prod_recs = []
            for i, p_name in enumerate(prods):
                prod_recs.append({
                    "product_name": p_name,
                    "product_id": f"PROD_{event}_{i+1}",
                    "why_now": f"Perfect match for your current {event.lower()} stage.",
                    "expected_benefit": "Maximize returns and enjoy zero processing fees.",
                    "cta_text": "Apply Now"
                })

            res = {
                "opening_message": f"Namaste {name}! Badhaai ho on this new chapter. 💍 I noticed some wedding celebrations in your transactions. I'm Arya, your SBI companion. Let's make managing your new joint finances seamless! How can I assist you and your spouse today?",
                "conversation_starters": [
                    f"Hi {name}, would you like to explore setting up an SBI Joint Account for family expenses?",
                    f"Are you considering checking out home loan options or home planners as you settle in?"
                ],
                "product_recommendations": prod_recs,
                "channel_priority": ["whatsapp", "app_notification", "call"],
                "best_contact_time": "12:00 PM - 2:00 PM"
            }
            return json.dumps(res)

        return "{}"
