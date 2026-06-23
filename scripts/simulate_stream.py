import time
import random
import httpx
import logging

# Config
API_URL = "http://localhost:8080"
CUSTOMERS = ["CUS_001", "CUS_002", "CUS_003", "CUS_004", "CUS_005", "CUS_006", "CUS_007"]
EVENT_NAMES = {
    "CUS_001": "MARRIAGE",
    "CUS_002": "JOB_CHANGE",
    "CUS_003": "NEW_BABY",
    "CUS_004": "HOME_PURCHASE",
    "CUS_005": "PRE_RETIREMENT",
    "CUS_006": "SALARY_HIKE",
    "CUS_007": "TRAVEL_PHASE"
}

def simulate_realtime_traffic():
    print("Starting SBI LifePulse Real-time Transaction Stream Simulator...")
    print(f"Target API Endpoint: {API_URL}")
    print("Press Ctrl+C to terminate.")
    
    client = httpx.Client()
    
    # Verify API is reachable
    try:
        res = client.get(f"{API_URL}/customers")
        if res.status_code != 200:
            print("Warning: API returned status code", res.status_code)
    except Exception as e:
        print(f"Error: Could not connect to API at {API_URL}. Start the FastAPI backend first with: uvicorn backend.main:app --reload")
        return

    iteration = 0
    while True:
        iteration += 1
        # 1. Pick a random customer
        cust_id = random.choice(CUSTOMERS)
        event = EVENT_NAMES[cust_id]
        
        print(f"\n[{iteration}] Simulating transaction stream for {cust_id}...")
        
        try:
            # 2. Trigger Event detection manually (Layer 1 + Layer 2)
            detect_res = client.post(f"{API_URL}/customers/{cust_id}/analyze")
            if detect_res.status_code == 200:
                data = detect_res.json()
                print(f"      -> Event Detected: {data['detected_event']} (Confidence: {data['confidence_score']})")
                
                # 3. Auto trigger outreach mock
                engage_res = client.post(f"{API_URL}/engage/{cust_id}/trigger")
                if engage_res.status_code == 200:
                    print(f"      -> Outreach successfully dispatched via WhatsApp and logged in banker stream.")
            else:
                print(f"      -> API Error: {detect_res.text}")
                
        except Exception as e:
            print(f"      -> Connection Error: {e}")
            
        # Wait between 5 to 10 seconds before next transaction
        sleep_time = random.randint(5, 10)
        print(f"Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    simulate_realtime_traffic()
