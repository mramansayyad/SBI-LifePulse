import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

logger = logging.getLogger("lifepulse.bigquery")

class BigQueryService:
    """
    Simulates BigQuery Behavioral Pipeline.
    Analyzes transaction patterns over a 6-month window to extract signals
    used by Vertex AI and Gemini for life event classification.
    """
    def __init__(self):
        logger.info("BigQuery Pipeline Service initialized (Local Simulator Mode).")

    def extract_behavioral_signals(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes 6-month transaction history and extracts signals.
        """
        if not transactions:
            return {
                "signals": {
                    "merchant_categories_spike": [],
                    "salary_change_pct": 0.0,
                    "new_recurring_merchants": [],
                    "spending_pattern_shift": "stable",
                    "top_categories_last_30d": [],
                    "anomaly_score": 0.0
                },
                "raw_stats": {}
            }

        # Parse dates and amounts
        parsed_txs = []
        for t in transactions:
            try:
                date_obj = datetime.strptime(t["date"], "%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                try:
                    date_obj = datetime.fromisoformat(t["date"].replace("Z", "+00:00"))
                except Exception:
                    date_obj = datetime.now()
            
            parsed_txs.append({
                **t,
                "date_obj": date_obj,
                "amount": float(t["amount"])
            })

        # Sort transactions by date
        parsed_txs.sort(key=lambda x: x["date_obj"])
        latest_date = parsed_txs[-1]["date_obj"]
        thirty_days_ago = latest_date - timedelta(days=30)
        sixty_days_ago = latest_date - timedelta(days=60)
        one_twenty_days_ago = latest_date - timedelta(days=120)

        # 1. Split transactions into historical window (first 4 months) and recent window (last 2 months)
        history_txs = [t for t in parsed_txs if t["date_obj"] < sixty_days_ago]
        recent_txs = [t for t in parsed_txs if t["date_obj"] >= sixty_days_ago]
        last_30d_txs = [t for t in parsed_txs if t["date_obj"] >= thirty_days_ago]

        # 2. Analyze salaries
        history_salaries = [t["amount"] for t in history_txs if t["merchant_category"] == "Salary" and t["transaction_type"] == "credit"]
        recent_salaries = [t["amount"] for t in recent_txs if t["merchant_category"] == "Salary" and t["transaction_type"] == "credit"]
        
        avg_hist_salary = sum(history_salaries) / len(history_salaries) if history_salaries else 0.0
        avg_rec_salary = sum(recent_salaries) / len(recent_salaries) if recent_salaries else 0.0
        
        salary_change_pct = 0.0
        if avg_hist_salary > 0:
            salary_change_pct = round((avg_rec_salary - avg_hist_salary) / avg_hist_salary, 2)

        # 3. Calculate category spending averages
        hist_cat_totals = {}
        for t in history_txs:
            if t["transaction_type"] == "debit":
                hist_cat_totals[t["merchant_category"]] = hist_cat_totals.get(t["merchant_category"], 0.0) + t["amount"]
                
        # Average monthly category spending in history (assuming ~4 months in history)
        hist_cat_monthly_avg = {cat: total / 4.0 for cat, total in hist_cat_totals.items()}

        recent_cat_totals = {}
        for t in recent_txs:
            if t["transaction_type"] == "debit":
                recent_cat_totals[t["merchant_category"]] = recent_cat_totals.get(t["merchant_category"], 0.0) + t["amount"]
                
        # Average monthly category spending in recent window (assuming ~2 months in recent)
        recent_cat_monthly_avg = {cat: total / 2.0 for cat, total in recent_cat_totals.items()}

        # Identify Spikes (recent spend is > 2.0x history average AND substantial)
        merchant_categories_spike = []
        for cat, rec_avg in recent_cat_monthly_avg.items():
            hist_avg = hist_cat_monthly_avg.get(cat, 0.0)
            if hist_avg > 0:
                if rec_avg > hist_avg * 1.8:
                    merchant_categories_spike.append(cat)
            elif rec_avg > 5000: # New substantial spending category
                merchant_categories_spike.append(cat)

        # 4. Identify Top Categories in last 30 days
        cat_30d = {}
        for t in last_30d_txs:
            if t["transaction_type"] == "debit":
                cat_30d[t["merchant_category"]] = cat_30d.get(t["merchant_category"], 0.0) + t["amount"]
        sorted_cat_30d = sorted(cat_30d.items(), key=lambda x: x[1], reverse=True)
        top_categories_last_30d = [item[0] for item in sorted_cat_30d[:3]]

        # 5. New Recurring Merchants (e.g. EMIs, Subscriptions)
        hist_merchants = set(t["merchant_name"] for t in history_txs)
        recent_merchants = set(t["merchant_name"] for t in recent_txs)
        new_merchants = recent_merchants - hist_merchants
        
        # Filter for recurring/special merchants in description
        new_recurring = []
        for t in recent_txs:
            if t["merchant_name"] in new_merchants:
                desc = t["description"].lower()
                if "emi" in desc or "subscription" in desc or "premium" in desc or "policy" in desc:
                    if t["merchant_name"] not in new_recurring:
                        new_recurring.append(t["merchant_name"])

        # 6. Overall spending shift
        hist_debits = sum(t["amount"] for t in history_txs if t["transaction_type"] == "debit")
        recent_debits = sum(t["amount"] for t in recent_txs if t["transaction_type"] == "debit")
        hist_monthly = hist_debits / 4.0 if hist_debits else 0.0
        rec_monthly = recent_debits / 2.0 if recent_debits else 0.0
        
        spending_pattern_shift = "stable"
        if rec_monthly > hist_monthly * 1.25:
            spending_pattern_shift = "increase"
        elif rec_monthly < hist_monthly * 0.75:
            spending_pattern_shift = "decrease"

        # 7. Anomaly / Event Likelihood Score
        # Higher score if multiple spikes, high salary changes, or large custom merchant transactions
        anomaly_score = 0.0
        if len(merchant_categories_spike) > 0:
            anomaly_score += 0.3
        if abs(salary_change_pct) > 0.1:
            anomaly_score += 0.3
        if len(new_recurring) > 0:
            anomaly_score += 0.2
        # Check for single very large debit transaction relative to income
        large_debits = [t["amount"] for t in recent_txs if t["transaction_type"] == "debit" and t["amount"] > avg_hist_salary * 0.5]
        if large_debits:
            anomaly_score += 0.2
            
        anomaly_score = min(round(anomaly_score, 2), 1.0)

        # 8. Detailed breakdown for the front-end charts
        raw_stats = {
            "total_spend_6m": round(sum(t["amount"] for t in parsed_txs if t["transaction_type"] == "debit"), 2),
            "monthly_avg_spend": round(rec_monthly, 2),
            "historical_monthly_avg_spend": round(hist_monthly, 2),
            "recent_salary": round(avg_rec_salary, 2),
            "previous_salary": round(avg_hist_salary, 2),
            "recent_transactions_count": len(recent_txs)
        }

        return {
            "signals": {
                "merchant_categories_spike": merchant_categories_spike,
                "salary_change_pct": salary_change_pct,
                "new_recurring_merchants": new_recurring,
                "spending_pattern_shift": spending_pattern_shift,
                "top_categories_last_30d": top_categories_last_30d,
                "anomaly_score": anomaly_score
            },
            "raw_stats": raw_stats
        }
