import requests
import time

BASE_URL = "https://market-monitor-api.onrender.com"

print("Testing Background Job Execution...")
print("=" * 50)

# Trigger job
print("\n1. Triggering market scan job...")
response = requests.post(f"{BASE_URL}/run-job")
print(f"Response: {response.json()}")

# Poll status every 10 seconds for 5 minutes
print("\n2. Monitoring job status (polling every 10s)...")
for i in range(30):  # 30 * 10s = 5 minutes
    time.sleep(10)
    response = requests.get(f"{BASE_URL}/job-status")
    status_data = response.json()
    
    print(f"\n[{i+1}] Status: {status_data['status']}")
    print(f"    Message: {status_data['message']}")
    print(f"    Last Run: {status_data.get('last_run', 'N/A')}")
    
    if status_data['status'] in ['completed', 'failed']:
        print(f"\n✅ Job finished with status: {status_data['status']}")
        break
else:
    print("\n⚠️ Job still running after 5 minutes")

print("\n" + "=" * 50)
