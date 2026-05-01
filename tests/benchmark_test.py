import requests
import time

BASE_URL = "http://127.0.0.1:5000"

# 🔥 Endpoints to test
endpoints = [
    {
        "name": "categorise",
        "method": "POST",
        "url": f"{BASE_URL}/categorise",
        "payload": {"text": "Multiple transactions from different countries"}
    },
    {
        "name": "query",
        "method": "POST",
        "url": f"{BASE_URL}/query",
        "payload": {"question": "What is fraud detection?"}
    },
    {
        "name": "generate-report",
        "method": "POST",
        "url": f"{BASE_URL}/generate-report",
        "payload": {"text": "Unauthorized credit card transaction detected"}
    },
    {
        "name": "health",
        "method": "GET",
        "url": f"{BASE_URL}/health",
        "payload": None
    }
]


def measure(endpoint, runs=50):
    times = []

    for i in range(runs):
        start = time.time()

        try:
            if endpoint["method"] == "POST":
                requests.post(endpoint["url"], json=endpoint["payload"])
            else:
                requests.get(endpoint["url"])

        except Exception as e:
            print(f"Error: {e}")
            continue

        end = time.time()
        times.append((end - start) * 1000)  # ms

    times.sort()

    if not times:
        return None

    p50 = times[len(times)//2]
    p95 = times[int(len(times)*0.95)]
    p99 = times[int(len(times)*0.99)]

    return p50, p95, p99


# 🔥 Run benchmark
print("\n🚀 Running Benchmark...\n")

for ep in endpoints:
    print(f"Testing {ep['name']}...")

    result = measure(ep)

    if result:
        p50, p95, p99 = result
        print(f"p50: {round(p50,2)} ms")
        print(f"p95: {round(p95,2)} ms")
        print(f"p99: {round(p99,2)} ms\n")
    else:
        print("Failed to collect data\n")