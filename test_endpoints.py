import requests
import time

BASE_URL = "https://market-monitor-api.onrender.com"

print("Testing API Endpoints...")
print("=" * 50)

# 1. Root Check
print("\n1. Testing / endpoint...")
response = requests.get(f"{BASE_URL}/")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"Response: {response.json()}")
else:
    print(f"Response: {response.text}")

# 2. Health Check
print("\n2. Testing /health endpoint...")
response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"Response: {response.json()}")
else:
    print(f"Response: {response.text}")

# 3. Trigger Sync
print("\n3. Testing /sync-symbols endpoint...")
response = requests.post(f"{BASE_URL}/sync-symbols")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"Response: {response.json()}")
else:
    print(f"Response: {response.text}")

# 4. Trigger Job
print("\n4. Testing /run-job endpoint...")
response = requests.post(f"{BASE_URL}/run-job")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"Response: {response.json()}")
else:
    print(f"Response: {response.text}")

# 5. Check Job Status
print("\n5. Checking /job-status...")
time.sleep(2)
response = requests.get(f"{BASE_URL}/job-status")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"Response: {response.json()}")
else:
    print(f"Response: {response.text}")

print("\n" + "=" * 50)
print("Test completed!")
