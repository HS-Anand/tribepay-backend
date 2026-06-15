import requests
import time
from concurrent.futures import ThreadPoolExecutor
from collections import Counter


# ================= CONFIG =================

URL = "https://tribepay-backend.onrender.com/wallets/me/"


HEADERS = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN"
}


TOTAL_REQUESTS = 1000
CONCURRENT_USERS = 20


# ==========================================


def make_request():

    start = time.time()

    try:
        response = requests.get(
            URL,
            headers=HEADERS,
            timeout=10
        )

        latency = time.time() - start


        if response.status_code >= 500:
            print("SERVER ERROR:")
            print(response.text[:300])


        return {
            "status": response.status_code,
            "latency": latency
        }


    except Exception as e:

        latency = time.time() - start

        return {
            "status": "TIMEOUT",
            "latency": latency
        }



# Start benchmark

start_time = time.time()


with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:

    results = list(
        executor.map(
            lambda _: make_request(),
            range(TOTAL_REQUESTS)
        )
    )


total_time = time.time() - start_time



# ================= RESULTS =================


status_codes = Counter(
    r["status"] for r in results
)


successful = sum(
    1 for r in results
    if isinstance(r["status"], int)
    and 200 <= r["status"] < 300
)


latencies = sorted(
    r["latency"]
    for r in results
)


print("\n========== TribePay Load Test ==========\n")


print("Status Codes:")
print(status_codes)


print()

print(f"Total Requests: {TOTAL_REQUESTS}")

print(f"Concurrent Users: {CONCURRENT_USERS}")

print(f"Successful Requests: {successful}")


print(
    f"Failure Rate: {(TOTAL_REQUESTS-successful)/TOTAL_REQUESTS*100:.2f}%"
)


print(
    f"Requests/sec: {TOTAL_REQUESTS/total_time:.2f}"
)


print(
    f"Average Latency: {sum(latencies)/len(latencies)*1000:.2f} ms"
)


print(
    f"P95 Latency: {latencies[int(0.95*(len(latencies)-1))]*1000:.2f} ms"
)


print(
    f"Max Latency: {max(latencies)*1000:.2f} ms"
)


print("\n========================================\n")