import json
import random
import os
from datetime import datetime, timedelta

def generate_transactions(customer_id, persona, monthly_income, start_date):
    transactions = []
    current_date = start_date
    tx_id_counter = 1
    
    # Generate transactions over 180 days (6 months)
    for day in range(180):
        current_date = start_date + timedelta(days=day)
        
        # 1. Monthly Salary (Credit)
        if current_date.day == 1:
            salary = monthly_income
            employer = "SBI Corp"
            description = f"NEFT Credit - Salary - {employer}"
            
            # Job Change modification
            if persona == "JOB_CHANGE" and day >= 120:
                salary = monthly_income * 1.40
                employer = "Google India Private Ltd"
                description = f"NEFT Credit - Salary - {employer}"
            # Salary Hike modification
            elif persona == "SALARY_HIKE" and day >= 120:
                salary = monthly_income * 1.20
                description = f"NEFT Credit - Salary - {employer}"
            # Pre-retirement modification
            elif persona == "PRE_RETIREMENT" and day >= 120:
                salary = monthly_income * 0.40 # Pension or reduced credit
                description = f"NEFT Credit - Pension/Gratuity - {employer}"
                
            transactions.append({
                "transaction_id": f"TX_{customer_id}_{tx_id_counter:04d}",
                "date": current_date.strftime("%Y-%m-%dT10:00:00Z"),
                "amount": round(salary, 2),
                "merchant_category": "Salary",
                "merchant_name": employer,
                "transaction_type": "credit",
                "channel": "NEFT",
                "description": description
            })
            tx_id_counter += 1

        # 2. Weekly Groceries (Debit)
        if current_date.weekday() == 6: # Sunday
            amount = random.uniform(1500, 3000)
            if persona == "MARRIAGE" and day >= 120:
                amount *= 1.8 # grocery spike for couples
            transactions.append({
                "transaction_id": f"TX_{customer_id}_{tx_id_counter:04d}",
                "date": current_date.strftime("%Y-%m-%dT11:30:00Z"),
                "amount": round(amount, 2),
                "merchant_category": "Groceries",
                "merchant_name": "DMart Supermarket",
                "transaction_type": "debit",
                "channel": "card",
                "description": "Weekly Groceries DMart"
            })
            tx_id_counter += 1

        # 3. Monthly Utilities (Debit)
        if current_date.day == 5:
            transactions.append({
                "transaction_id": f"TX_{customer_id}_{tx_id_counter:04d}",
                "date": current_date.strftime("%Y-%m-%dT09:15:00Z"),
                "amount": round(random.uniform(2000, 4500), 2),
                "merchant_category": "Utilities",
                "merchant_name": "MSEDCL Electricity",
                "transaction_type": "debit",
                "channel": "net_banking",
                "description": "Electricity Bill Payment"
            })
            tx_id_counter += 1

        # 4. Standard dining/entertainment (UPI)
        if current_date.weekday() in [4, 5] and random.random() < 0.4: # Friday or Saturday
            amount = random.uniform(500, 2000)
            if persona == "MARRIAGE" and day >= 120:
                amount *= 2.0 # double for dates
            transactions.append({
                "transaction_id": f"TX_{customer_id}_{tx_id_counter:04d}",
                "date": current_date.strftime("%Y-%m-%dT20:30:00Z"),
                "amount": round(amount, 2),
                "merchant_category": "Dining",
                "merchant_name": random.choice(["Barbeque Nation", "Swiggy", "Zomato", "Starbucks"]),
                "transaction_type": "debit",
                "channel": "UPI",
                "description": "Weekend Food & Dining"
            })
            tx_id_counter += 1

        # 5. Embedded Life Event Spikes (mostly in months 5 and 6: days 120-180)
        if day >= 120:
            if persona == "MARRIAGE" and day % 12 == 0:
                # Wedding hall payment, jewelry, honeymoon
                merchants = [
                    ("Shopping", "Tanishq Jewellers", random.uniform(80000, 150000), "card", "Purchase - Jewelry"),
                    ("Entertainment", "Taj Wedding Hall", random.uniform(100000, 250000), "net_banking", "Booking - Event Venue"),
                    ("Travel", "MakeMyTrip Honeymoon", random.uniform(50000, 120000), "card", "Flight + Resort Booking Maldives"),
                    ("Shopping", "Manyavar Brides", random.uniform(30000, 60000), "card", "Wedding Sarees & Lehenga")
                ]
                item = merchants[(day // 12) % len(merchants)]
                transactions.append({
                    "transaction_id": f"TX_{customer_id}_{tx_id_counter:04d}",
                    "date": current_date.strftime("%Y-%m-%dT15:00:00Z"),
                    "amount": round(item[2], 2),
                    "merchant_category": item[0],
                    "merchant_name": item[1],
                    "transaction_type": "debit",
                    "channel": item[3],
                    "description": item[4]
                })
                tx_id_counter += 1

            elif persona == "JOB_CHANGE" and day % 15 == 0:
                merchants = [
                    ("Shopping", "Zara & Raymonds", random.uniform(10000, 25000), "card", "Corporate Attire Purchases"),
                    ("Utilities", "LinkedIn Premium", 1500.0, "card", "Professional Network Subscription"),
                    ("Finance", "HDFC Car Loan EMI", random.uniform(12000, 18000), "net_banking", "New Car Loan EMI Debited"),
                    ("Shopping", "Apple Store India", random.uniform(80000, 130000), "card", "MacBook Pro Purchase")
                ]
                item = merchants[(day // 15) % len(merchants)]
                transactions.append({
                    "transaction_id": f"TX_{customer_id}_{tx_id_counter:04d}",
                    "date": current_date.strftime("%Y-%m-%dT12:00:00Z"),
                    "amount": round(item[2], 2),
                    "merchant_category": item[0],
                    "merchant_name": item[1],
                    "transaction_type": "debit",
                    "channel": item[3],
                    "description": item[4]
                })
                tx_id_counter += 1

            elif persona == "NEW_BABY" and day % 10 == 0:
                merchants = [
                    ("Healthcare", "Fortis Maternity Hospital", random.uniform(40000, 90000), "net_banking", "Delivery & Medical Charges"),
                    ("Shopping", "FirstCry Baby Products", random.uniform(8000, 20000), "card", "Crib, Stroller, Baby Essentials"),
                    ("Shopping", "Mothercare India", random.uniform(5000, 12000), "UPI", "Baby Clothes & Diaper Bags"),
                    ("Healthcare", "Apollo Pharmacy", random.uniform(3000, 7000), "UPI", "Maternity Vitamins & Infant Care"),
                    ("Finance", "SBI Family Health Insurance Premium", 22000.0, "net_banking", "Annual Policy Upgrade")
                ]
                item = merchants[(day // 10) % len(merchants)]
                transactions.append({
                    "transaction_id": f"TX_{customer_id}_{tx_id_counter:04d}",
                    "date": current_date.strftime("%Y-%m-%dT14:00:00Z"),
                    "amount": round(item[2], 2),
                    "merchant_category": item[0],
                    "merchant_name": item[1],
                    "transaction_type": "debit",
                    "channel": item[3],
                    "description": item[4]
                })
                tx_id_counter += 1

            elif persona == "HOME_PURCHASE" and day % 12 == 0:
                merchants = [
                    ("Finance", "Sobha Developers Escrow", random.uniform(300000, 600000), "RTGS", "Part Payment - Flat Purchase"),
                    ("Finance", "Sub-Registrar Stamp Duty", random.uniform(100000, 200000), "net_banking", "Registration & Stamp Duty Fees"),
                    ("Shopping", "IKEA Bangalore", random.uniform(40000, 120000), "card", "Modular Wardrobes & Sofas"),
                    ("Shopping", "Pepperfry Furnishings", random.uniform(25000, 70000), "card", "Dining Table & Bed Set"),
                    ("Finance", "SBI Home Loan Valuation Fee", 5000.0, "net_banking", "Home Loan Processing Charge")
                ]
                item = merchants[(day // 12) % len(merchants)]
                transactions.append({
                    "transaction_id": f"TX_{customer_id}_{tx_id_counter:04d}",
                    "date": current_date.strftime("%Y-%m-%dT16:00:00Z"),
                    "amount": round(item[2], 2),
                    "merchant_category": item[0],
                    "merchant_name": item[1],
                    "transaction_type": "debit",
                    "channel": item[3],
                    "description": item[4]
                })
                tx_id_counter += 1

            elif persona == "PRE_RETIREMENT" and day % 15 == 0:
                merchants = [
                    ("Finance", "NPS contribution - SBI Pension", random.uniform(20000, 50000), "net_banking", "Tier-1 Account Voluntary Deposit"),
                    ("Finance", "Public Provident Fund", random.uniform(30000, 70000), "net_banking", "Annual PPF Limit Topup"),
                    ("Travel", "Thomas Cook Pilgrimage", random.uniform(40000, 90000), "card", "Char Dham Yatra Booking"),
                    ("Healthcare", "Star Health Insurance Premium", 28000.0, "net_banking", "Senior Citizen Rider Upgrade")
                ]
                item = merchants[(day // 15) % len(merchants)]
                transactions.append({
                    "transaction_id": f"TX_{customer_id}_{tx_id_counter:04d}",
                    "date": current_date.strftime("%Y-%m-%dT11:00:00Z"),
                    "amount": round(item[2], 2),
                    "merchant_category": item[0],
                    "merchant_name": item[1],
                    "transaction_type": "debit",
                    "channel": item[3],
                    "description": item[4]
                })
                tx_id_counter += 1

            elif persona == "TRAVEL_PHASE" and day % 8 == 0:
                merchants = [
                    ("Travel", "MakeMyTrip Flights", random.uniform(15000, 35000), "card", "Air Ticket Booking"),
                    ("Travel", "Airbnb India", random.uniform(12000, 28000), "card", "Home Stay Booking"),
                    ("Travel", "Niyo Global Forex", random.uniform(20000, 50000), "card", "Load Travel Card"),
                    ("Travel", "Uber India", random.uniform(1000, 3000), "UPI", "Airport Transfers")
                ]
                item = merchants[(day // 8) % len(merchants)]
                transactions.append({
                    "transaction_id": f"TX_{customer_id}_{tx_id_counter:04d}",
                    "date": current_date.strftime("%Y-%m-%dT13:00:00Z"),
                    "amount": round(item[2], 2),
                    "merchant_category": item[0],
                    "merchant_name": item[1],
                    "transaction_type": "debit",
                    "channel": item[3],
                    "description": item[4]
                })
                tx_id_counter += 1

    # Sort transactions chronologically
    transactions.sort(key=lambda x: x["date"])
    return transactions

def generate_all_data():
    start_date = datetime.now() - timedelta(days=180)
    
    personas_info = [
        {"id": "CUS_001", "name": "Priya Sharma", "age": 28, "city": "Mumbai", "monthly_income": 75000, "risk_profile": "moderate", "existing_products": ["savings_account", "debit_card"], "persona": "MARRIAGE"},
        {"id": "CUS_002", "name": "Rahul Mehta", "age": 32, "city": "Pune", "monthly_income": 85000, "risk_profile": "aggressive", "existing_products": ["savings_account", "credit_card"], "persona": "JOB_CHANGE"},
        {"id": "CUS_003", "name": "Anjali Verma", "age": 35, "city": "Delhi", "monthly_income": 95000, "risk_profile": "moderate", "existing_products": ["savings_account", "debit_card", "personal_loan"], "persona": "NEW_BABY"},
        {"id": "CUS_004", "name": "Sanjay Patil", "age": 45, "city": "Bangalore", "monthly_income": 150000, "risk_profile": "conservative", "existing_products": ["savings_account", "credit_card", "car_loan"], "persona": "HOME_PURCHASE"},
        {"id": "CUS_005", "name": "Meena Krishnan", "age": 58, "city": "Chennai", "monthly_income": 110000, "risk_profile": "conservative", "existing_products": ["savings_account", "fixed_deposit"], "persona": "PRE_RETIREMENT"},
        {"id": "CUS_006", "name": "Vikram Singh", "age": 31, "city": "Jaipur", "monthly_income": 80000, "risk_profile": "aggressive", "existing_products": ["savings_account", "debit_card"], "persona": "SALARY_HIKE"},
        {"id": "CUS_007", "name": "Shreya Ghoshal", "age": 25, "city": "Kolkata", "monthly_income": 50000, "risk_profile": "moderate", "existing_products": ["savings_account"], "persona": "TRAVEL_PHASE"},
        {"id": "CUS_008", "name": "Amit Patel", "age": 40, "city": "Ahmedabad", "monthly_income": 65000, "risk_profile": "moderate", "existing_products": ["savings_account", "fixed_deposit"], "persona": "NONE"},
        {"id": "CUS_009", "name": "Neha Gupta", "age": 30, "city": "Hyderabad", "monthly_income": 85000, "risk_profile": "moderate", "existing_products": ["savings_account", "credit_card"], "persona": "NONE"},
        {"id": "CUS_010", "name": "Rajesh Iyer", "age": 50, "city": "Cochin", "monthly_income": 120000, "risk_profile": "conservative", "existing_products": ["savings_account", "credit_card", "home_loan"], "persona": "NONE"}
    ]
    
    customers = []
    all_transactions = []
    
    for p in personas_info:
        txs = generate_transactions(p["id"], p["persona"], p["monthly_income"], start_date)
        all_transactions.extend(txs)
        
        customer_profile = {
            "customer_id": p["id"],
            "name": p["name"],
            "age": p["age"],
            "city": p["city"],
            "account_number": f"XXXX{random.randint(1000, 9999)}",
            "monthly_income": p["monthly_income"],
            "risk_profile": p["risk_profile"],
            "existing_products": p["existing_products"],
            "transactions": txs,
            "detected_life_event": None,
            "engagement_status": "pending"
        }
        customers.append(customer_profile)
        
    return customers, all_transactions

if __name__ == "__main__":
    customers, transactions = generate_all_data()
    
    os.makedirs("../../data", exist_ok=True)
    
    with open("../../data/sample_customers.json", "w") as f:
        json.dump(customers, f, indent=2)
        
    with open("../../data/sample_transactions.json", "w") as f:
        json.dump(transactions, f, indent=2)
        
    print(f"Generated {len(customers)} customers.")
    print(f"Generated {len(transactions)} transactions.")
