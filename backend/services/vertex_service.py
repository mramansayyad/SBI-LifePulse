import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("lifepulse.vertex")

class VertexService:
    """
    Simulates Vertex AI AutoML Classifier.
    Analyzes BigQuery behavioral signals using high-performance heuristics
    and returns initial life event classifications with probability distributions.
    """
    def __init__(self):
        logger.info("Vertex AI Classification Service initialized (Local Simulator Mode).")

    def classify_signals(self, signals_data: Dict[str, Any], transactions: list) -> Tuple[str, float]:
        """
        Classifies behavioral signals and returns (detected_event, confidence).
        This acts as the Layer 1 ML classifier before the Gemini Agent refines details.
        """
        signals = signals_data.get("signals", {})
        spikes = [s.lower() for s in signals.get("merchant_categories_spike", [])]
        salary_change = signals.get("salary_change_pct", 0.0)
        recurring = [m.lower() for m in signals.get("new_recurring_merchants", [])]
        
        # Scan transaction descriptions for strong signals
        tx_desc = " ".join([t.get("description", "").lower() for t in transactions[-20:]])
        tx_merchants = " ".join([t.get("merchant_name", "").lower() for t in transactions[-20:]])
        
        # 1. Marriage Signals
        if "marriage" in spikes or "wedding" in spikes or "tanishq" in tx_merchants or "wedding" in tx_desc or "bride" in tx_desc or "honeymoon" in tx_desc:
            score = 0.6
            if "tanishq" in tx_merchants: score += 0.2
            if "wedding" in tx_desc: score += 0.15
            return "MARRIAGE", min(score, 0.98)
            
        # 2. New Baby Signals
        if "firstcry" in tx_merchants or "mothercare" in tx_merchants or "maternity" in tx_desc or "baby" in tx_desc or "delivery" in tx_desc or "family health insurance" in tx_desc:
            score = 0.7
            if "fortis" in tx_merchants: score += 0.15
            if "firstcry" in tx_merchants: score += 0.1
            return "NEW_BABY", min(score, 0.98)

        # 3. Home Purchase Signals
        if "sobha" in tx_merchants or "ikea" in tx_merchants or "pepperfry" in tx_merchants or "registration" in tx_desc or "stamp duty" in tx_desc or "home loan valuation" in tx_desc:
            score = 0.65
            if "sobha" in tx_merchants: score += 0.2
            if "registration" in tx_desc: score += 0.1
            return "HOME_PURCHASE", min(score, 0.98)

        # 4. Job Change / Promotion
        if salary_change >= 0.3 or "linkedin premium" in tx_desc or "zara" in tx_merchants or "raymond" in tx_merchants:
            score = 0.5
            if salary_change >= 0.35: score += 0.3
            if "linkedin" in tx_desc: score += 0.1
            if score >= 0.6:
                return "JOB_CHANGE", min(score, 0.95)

        # 5. Pre-Retirement
        if salary_change <= -0.4 and salary_change > -1.0 or "pension" in tx_desc or "gratuity" in tx_desc or "nps" in tx_desc or "public provident fund" in tx_desc or "char dham" in tx_desc:
            score = 0.6
            if "pension" in tx_desc or "gratuity" in tx_desc: score += 0.25
            if "nps" in tx_desc: score += 0.1
            return "PRE_RETIREMENT", min(score, 0.94)

        # 6. Travel Phase
        if "travel" in spikes or "indigo" in tx_merchants or "airbnb" in tx_merchants or "niyo global" in tx_merchants or "makemytrip flights" in tx_merchants:
            score = 0.7
            if "airbnb" in tx_merchants: score += 0.1
            if "forex" in tx_desc: score += 0.1
            return "TRAVEL_PHASE", min(score, 0.95)

        # 7. Salary Hike (no employer change)
        if 0.1 <= salary_change < 0.3:
            return "SALARY_HIKE", 0.85

        return "NONE", 1.0
