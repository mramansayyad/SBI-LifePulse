import logging
import math
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.models.customer import CustomerProfile
from backend.services.firestore_service import FirestoreService
from backend.services.gemini_service import GeminiService
from backend.utils.prompt_templates import CONVERSATION_SYSTEM_PROMPT

logger = logging.getLogger("lifepulse.agents.conversation")

# Define actual Python functions for the tools
async def get_account_summary_fn(customer_id: str, db_service: FirestoreService) -> Dict[str, Any]:
    customer = await db_service.get_customer(customer_id)
    if not customer:
        return {"error": f"Customer {customer_id} not found."}
    
    # Compute balance
    balance = 50000.0 # Base balance
    for tx in customer.transactions:
        if tx.transaction_type == "credit":
            balance += tx.amount
        else:
            balance -= tx.amount
            
    recent_txs = []
    for tx in customer.transactions[-5:]:
        recent_txs.append({
            "date": tx.date.strftime("%Y-%m-%d") if isinstance(tx.date, datetime) else str(tx.date)[:10],
            "merchant": tx.merchant_name,
            "category": tx.merchant_category,
            "type": tx.transaction_type,
            "amount": tx.amount
        })
        
    return {
        "account_number": customer.account_number,
        "current_balance_inr": round(balance, 2),
        "recent_transactions": recent_txs
    }

def get_product_details_fn(product_name: str) -> Dict[str, Any]:
    prod_lower = product_name.lower()
    if "home" in prod_lower or "house" in prod_lower:
        return {
            "product_name": "SBI Happy Home Loan",
            "interest_rate": "8.50% - 9.15% p.a.",
            "processing_fee": "Zero processing fee for online applications",
            "max_tenure": "30 Years",
            "eligibility": "Salaried individuals age 18-70 with stable income history."
        }
    elif "sip" in prod_lower or "mutual fund" in prod_lower:
        return {
            "product_name": "SBI Mutual Fund Child Fund / Regular SIP",
            "min_investment": "INR 500 per month",
            "expected_returns": "12.5% - 15% p.a. (Historical 5-year average)",
            "lock_in_period": "None (except tax-saving equity plans)",
            "benefits": "Compound interest, rupee-cost averaging, managed by SBI Funds Management."
        }
    elif "joint" in prod_lower:
        return {
            "product_name": "SBI Joint Savings Account",
            "interest_rate": "3.00% p.a.",
            "min_balance": "Zero balance for salary account link",
            "features": "Dual debit cards, internet banking for both, instant UPI transfers."
        }
    elif "senior" in prod_lower or "retirement" in prod_lower:
        return {
            "product_name": "SBI Senior Citizen Savings Scheme (SCSS)",
            "interest_rate": "8.20% p.a. (Quarterly Interest Payout)",
            "tenure": "5 Years (extendable by 3 years)",
            "min_deposit": "INR 1,000",
            "max_deposit": "INR 30 Lakhs"
        }
    elif "elite" in prod_lower or "credit card" in prod_lower:
        return {
            "product_name": "SBI Card ELITE",
            "annual_fee": "INR 4,999",
            "benefits": "Welcome e-Gift voucher worth INR 5,000, 5X reward points on dining/department stores, free movie tickets.",
            "lounge_access": "6 complimentary international lounge visits per year."
        }
    
    return {
        "product_name": product_name,
        "details": "Please speak with our SBI branch Representative or Relationship Manager for the latest features and current interest rates."
    }

def calculate_emi_fn(loan_amount: float, tenure_years: int, rate_pct: float) -> Dict[str, Any]:
    n = int(tenure_years * 12)
    r = (rate_pct / 12.0) / 100.0
    
    try:
        emi = (loan_amount * r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)
        total_payment = emi * n
        total_interest = total_payment - loan_amount
        return {
            "loan_amount": loan_amount,
            "monthly_emi": round(emi, 2),
            "total_interest_payable": round(total_interest, 2),
            "total_amount_payable": round(total_payment, 2)
        }
    except Exception:
        return {"error": "Invalid input parameters for EMI calculation."}

def calculate_sip_returns_fn(monthly_amount: float, years: int, expected_rate_pct: float) -> Dict[str, Any]:
    n = int(years * 12)
    i = (expected_rate_pct / 12.0) / 100.0
    
    try:
        # FV = P * [((1 + i)^n - 1) / i] * (1 + i)
        future_value = monthly_amount * ((math.pow(1 + i, n) - 1) / i) * (1 + i)
        total_invested = monthly_amount * n
        wealth_gain = future_value - total_invested
        return {
            "monthly_investment": monthly_amount,
            "tenure_years": years,
            "total_invested": round(total_invested, 2),
            "estimated_returns": round(wealth_gain, 2),
            "total_wealth": round(future_value, 2)
        }
    except Exception:
        return {"error": "Invalid input parameters for SIP calculation."}

async def book_rm_appointment_fn(customer_id: str, preferred_time: str, db_service: FirestoreService) -> Dict[str, Any]:
    customer = await db_service.get_customer(customer_id)
    name = customer.name if customer else "Customer"
    
    # Log to feed
    await db_service.log_engagement_activity({
        "customer_id": customer_id,
        "customer_name": name,
        "event_type": "APPOINTMENT_BOOKED",
        "message": f"{name} booked an appointment with a Relationship Manager for {preferred_time}.",
        "urgency": "HIGH"
    })
    
    return {
        "status": "success",
        "appointment_time": preferred_time,
        "rm_name": "Rajesh Sharma (SBI Senior RM)",
        "confirmation_code": f"RM_{random_code()}",
        "message": f"Appointment booked successfully for {preferred_time}. Our Relationship Manager will call you shortly."
    }

async def apply_product_interest_fn(customer_id: str, product_name: str, db_service: FirestoreService) -> Dict[str, Any]:
    customer = await db_service.get_customer(customer_id)
    if not customer:
        return {"error": "Customer not found."}
        
    customer.engagement_status = "converted"
    await db_service.save_customer(customer)
    
    # Log to feed
    await db_service.log_engagement_activity({
        "customer_id": customer_id,
        "customer_name": customer.name,
        "event_type": "PRODUCT_APPLICATION",
        "message": f"🎉 {customer.name} applied for {product_name}! Conversion recorded.",
        "urgency": "HIGH"
    })
    
    return {
        "status": "success",
        "customer_id": customer_id,
        "product_name": product_name,
        "status_logged": "applied_interest",
        "message": f"Thank you for showing interest in {product_name}. We have logged your request and a bank officer will assist you with the onboarding."
    }

def random_code() -> str:
    import random
    return "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=6))


class ConversationAgent:
    def __init__(self, gemini_service: GeminiService, firestore_service: FirestoreService):
        self.gemini_service = gemini_service
        self.firestore_service = firestore_service

    async def get_history(self, customer_id: str) -> List[Dict[str, Any]]:
        return await self.firestore_service.get_conversation_history(customer_id)

    async def reset(self, customer_id: str):
        await self.firestore_service.reset_conversation(customer_id)

    async def respond(self, customer_id: str, user_message: str) -> str:
        """
        Processes user messages, handles tools, runs Gemini LLM dialog, 
        maintains history, and returns the response string.
        """
        # Save user message to history
        await self.firestore_service.save_conversation_turn(customer_id, "user", user_message)

        # Load profile and history
        customer = await self.firestore_service.get_customer(customer_id)
        if not customer:
            return "Error: Customer profile not found."
            
        history = await self.firestore_service.get_conversation_history(customer_id)

        # If in Mock Mode, we simulate stateful conversational logic with tool parsing
        if self.gemini_service.is_mock:
            response = await self._generate_mock_reply(customer, user_message, history)
        else:
            response = await self._generate_live_reply(customer, user_message, history)

        # Save AI reply to history
        await self.firestore_service.save_conversation_turn(customer_id, "assistant", response)
        
        return response

    async def _generate_live_reply(self, customer: CustomerProfile, message: str, history: List[Dict[str, Any]]) -> str:
        """
        Using Gemini 2.0 API with system instruction.
        For simplicity and absolute robustness during the hackathon, we simulate function calling
        using direct text analysis or system prompt, but can also run Gemini API calls.
        Let's construct a prompt containing the conversation context, history, and system instructions.
        """
        system_prompt = CONVERSATION_SYSTEM_PROMPT.format(
            customer_id=customer.customer_id,
            name=customer.name,
            city=customer.city,
            detected_life_event=customer.detected_life_event or "NONE",
            existing_products=", ".join(customer.existing_products)
        )
        
        # Build dialog log
        dialog_history = ""
        for turn in history[-10:]: # Keep last 10 turns
            role_label = "Customer" if turn["role"] == "user" else "Arya"
            dialog_history += f"{role_label}: {turn['message']}\n"
            
        prompt = f"""
{system_prompt}

Below is the recent dialog history. Respond to the user's latest query.
If they are asking to check their balance, calculate EMIs or SIPs, book an RM, or apply for a product, 
evaluate what results would be returned by the respective tool functions and output the final response 
with those computed numbers naturally in your answer.

Calculations for your use if requested:
- Account Summary for this customer: {json.dumps(await get_account_summary_fn(customer.customer_id, self.firestore_service))}
- Home Loan details: 8.5% interest rate, 20 years tenure.
- SIP expected return rates: 12% p.a.

Recent History:
{dialog_history}

Customer's Latest Query: {message}
Arya:"""

        return self.gemini_service.call_model(prompt, system_instruction=system_prompt)

    async def _generate_mock_reply(self, customer: CustomerProfile, message: str, history: List[Dict[str, Any]]) -> str:
        """
        Deterministic parser that handles chatbot responses locally.
        Extremely reliable fallback for mock testing.
        """
        msg = message.lower()
        
        # 1. Check Balance / Account Summary
        if "balance" in msg or "account" in msg or "transactions" in msg or "recent" in msg:
            summary = await get_account_summary_fn(customer.customer_id, self.firestore_service)
            return f"Hi {customer.name}! Sure, here is your account summary:\n\n" \
                   f"**Account Number:** {summary['account_number']}\n" \
                   f"**Current Balance:** INR {summary['current_balance_inr']:,}\n\n" \
                   f"Recent transactions include charges at **{summary['recent_transactions'][-1]['merchant']}** " \
                   f"for INR {summary['recent_transactions'][-1]['amount']} on {summary['recent_transactions'][-1]['date']}. " \
                   f"Is there anything else you would like to calculate or apply for?"

        # 2. EMI Calculator
        elif "emi" in msg or "calculate loan" in msg or "loan emi" in msg:
            # Parse digits if any, otherwise default
            amount = 5000000.0 # Default 50L
            tenure = 20 # 20 Years
            rate = 8.5 # 8.5%
            
            # Simple extractor
            import re
            numbers = re.findall(r'\d+', msg)
            if len(numbers) >= 1:
                amount = float(numbers[0])
                if amount < 100: # Probably tenure
                    tenure = int(amount)
                    amount = 5000000.0
            if len(numbers) >= 2:
                # If first is large, second is tenure
                if float(numbers[0]) > 1000:
                    amount = float(numbers[0])
                    tenure = int(numbers[1])
                else:
                    tenure = int(numbers[0])
                    amount = float(numbers[1])
                    
            emi_details = calculate_emi_fn(amount, tenure, rate)
            return f"Certainly, {customer.name}! Based on a loan amount of ₹{amount:,.2f} for a tenure of {tenure} years at {rate}% annual interest:\n\n" \
                   f"- **Monthly EMI:** ₹{emi_details['monthly_emi']:,.2f}\n" \
                   f"- **Total Interest Payable:** ₹{emi_details['total_interest_payable']:,.2f}\n" \
                   f"- **Total Amount Payable:** ₹{emi_details['total_amount_payable']:,.2f}\n\n" \
                   f"Would you like me to book an appointment with our Relationship Manager to proceed with your SBI Home Loan?"

        # 3. SIP Calculator
        elif "sip" in msg or "investment" in msg or "calculate returns" in msg:
            monthly = 10000.0 # 10k/month
            years = 10
            rate = 12.0 # 12%
            
            import re
            numbers = re.findall(r'\d+', msg)
            if len(numbers) >= 1:
                val = float(numbers[0])
                if val > 100:
                    monthly = val
                else:
                    years = int(val)
            if len(numbers) >= 2:
                if float(numbers[0]) > 100:
                    monthly = float(numbers[0])
                    years = int(numbers[1])
                else:
                    years = int(numbers[0])
                    monthly = float(numbers[1])

            sip_details = calculate_sip_returns_fn(monthly, years, rate)
            return f"Here is an estimate of your SIP investment growth, {customer.name} (assuming a steady {rate}% p.a. return):\n\n" \
                   f"- **Monthly Contribution:** ₹{monthly:,.2f}\n" \
                   f"- **Tenure:** {years} Years\n" \
                   f"- **Total Invested:** ₹{sip_details['total_invested']:,.2f}\n" \
                   f"- **Estimated Wealth Gain:** ₹{sip_details['estimated_returns']:,.2f}\n" \
                   f"- **Total Maturity Value:** ₹{sip_details['total_wealth']:,.2f}\n\n" \
                   f"Investing in SBI Child Fund or Equity Mutual Funds is a smart way to match your long-term milestones. Shall I help you apply for this SIP?"

        # 4. Book Appointment
        elif "book" in msg or "appointment" in msg or "meeting" in msg or "rm" in msg or "relationship manager" in msg:
            time_pref = "tomorrow at 11:00 AM"
            res = await book_rm_appointment_fn(customer.customer_id, time_pref, self.firestore_service)
            return f"Done, {customer.name}! I have booked an appointment for you with **{res['rm_name']}** for **{res['appointment_time']}**.\n\n" \
                   f"Your confirmation code is **{res['confirmation_code']}**. They will contact you on your registered mobile number shortly. Aapka din shubh ho!"

        # 5. Apply for Product
        elif "apply" in msg or "interest" in msg or "onboard" in msg or "open account" in msg:
            prod = "SBI Product"
            if "home" in msg or "house" in msg:
                prod = "SBI Happy Home Loan"
            elif "joint" in msg:
                prod = "SBI Joint Savings Account"
            elif "sip" in msg or "mutual" in msg:
                prod = "SBI Mutual Fund Child Fund"
            elif "senior" in msg or "retirement" in msg:
                prod = "SBI Senior Citizen Savings Scheme"
            elif "credit" in msg or "elite" in msg:
                prod = "SBI Card ELITE"
                
            res = await apply_product_interest_fn(customer.customer_id, prod, self.firestore_service)
            return f"Thank you, {customer.name}! I have successfully submitted your interest application for the **{res['product_name']}**.\n\n" \
                   f"A customer service officer from your local branch will get in touch with you shortly to complete the zero-paperwork digital onboarding. Is there anything else I can guide you through today?"

        # 6. Specific Life Event contextual queries
        elif "wedding" in msg or "marriage" in msg or "married" in msg:
            return f"Congratulations once again, {customer.name}! 💍 Wedding planning is an exciting time. I recommend setting up an **SBI Joint Savings Account** to easily pool your resources and track family budgets. We are also running a special discount on **SBI Happy Home Loans** (zero processing fees) if you're looking for a new nest. Would you like details on either of these?"
        elif "job" in msg or "career" in msg or "salary" in msg:
            return f"It is great to see the career growth, {customer.name}! With your increased monthly cash flow, it is a perfect opportunity to start a high-yield investment. The **SBI Wealth Savings Account** offers special features for high-earning individuals, or you could start an **SBI Mutual Fund SIP** starting at just ₹500/month. What fits your current planning?"
        elif "baby" in msg or "child" in msg:
            return f"Welcoming a new baby is a beautiful milestone, {customer.name}! 👶 To secure their future, many parents choose to start an **SBI Life - Smart Champ Insurance** (child education coverage) early on to capture maximum compounding benefits. I can also help you look into our family health floater insurance plans. Would you like me to calculate estimated benefits for you?"
        elif "home" in msg or "flat" in msg or "property" in msg:
            return f"Finding the right home is a key milestone, {customer.name}! 🏠 Our **SBI Home Loan** offers competitive rates (starting at 8.5% p.a.) and terms up to 30 years. Would you like me to calculate your estimated monthly EMI for a specific loan amount?"

        # 7. Default warm Hinglish fallback
        return f"Aapka swagat hai, {customer.name}! I'm here as your personal SBI financial companion. Ask me anything about your balance, transaction history, EMI/SIP calculations, or how to set up an appointment with a Relationship Manager. What's on your mind today?"
