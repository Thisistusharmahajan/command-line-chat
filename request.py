import requests
import threading
import time
import random
from collections import Counter

# Configuration
URL = "http://localhost:8765/chat"
TOTAL_REQUESTS = 1000  # Updated from 100 to 1000
CONCURRENT_THREADS = 50  # Increased for higher load generation

# Results storage
results = []
results_lock = threading.Lock()
errors = []

# Generate random usernames
first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", 
               "Ivy", "Jack", "Kate", "Leo", "Mia", "Noah", "Olivia", "Paul", 
               "Quinn", "Ryan", "Sarah", "Tom", "Uma", "Victor", "Wendy", "Xavier",
               "Yara", "Zack", "Aaron", "Bella", "Caleb", "Daisy", "Ethan", "Fiona",
               "George", "Hannah", "Ian", "Julia", "Kevin", "Lily", "Mark", "Nina",
               "Oscar", "Penny", "Quentin", "Rachel", "Sam", "Tina", "Ulysses", "Vera",
               "Will", "Xena", "Yvonne", "Zane", "Adam", "Beth", "Carl", "Dana",
               "Eric", "Faith", "Gavin", "Holly", "Isaac", "Jade", "Kyle", "Laura",
               "Matt", "Nora", "Owen", "Piper", "Quincy", "Rose", "Sean", "Tara",
               "Uri", "Val", "Wade", "Xia", "York", "Zara", "Alex", "Blake",
               "Casey", "Drew", "Ellis", "Finn", "Gale", "Harper", "Indigo", "Jordan"]

messages = ["Hello!", "How are you?", "Nice to meet you!", "What's up?", 
              "Good morning!", "Hey there!", "How's it going?", "Greetings!",
              "Hi everyone!", "Welcome!", "Testing the server!", "Random message here",
              "Just saying hi!", "Anybody there?", "Server test!", "Hello world!",
              "Nice server!", "Working great!", "Concurrent test!", "Load test!"]

def send_request(request_id):
    """Send a single POST request to /chat"""
    username = random.choice(first_names)
    message = random.choice(messages)
    
    payload = {
        "username": username,
        "message": message
    }
    
    req_start = time.time()
    try:
        response = requests.post(URL, json=payload, timeout=10)
        req_end = time.time()
        
        data = response.json()
        
        with results_lock:
            results.append({
                "id": request_id,
                "username": username,
                "status": response.status_code,
                "reply": data.get("reply", ""),
                "thread": data.get("thread", "unknown"),
                "duration": round(req_end - req_start, 4),
                "timestamp": data.get("timestamp", "")
            })
    except Exception as e:
        req_end = time.time()
        with results_lock:
            errors.append({
                "id": request_id,
                "username": username,
                "error": str(e),
                "duration": round(req_end - req_start, 4)
            })

def worker(request_ids):
    """Worker thread that processes a batch of requests"""
    for req_id in request_ids:
        send_request(req_id)

# ==================== MAIN EXECUTION ====================
print("=" * 70)
print(f"🚀 SENDING {TOTAL_REQUESTS} CONCURRENT REQUESTS TO CHAT SERVER")
print("=" * 70)
print(f"URL: {URL}")
print(f"Total Requests: {TOTAL_REQUESTS}")
print(f"Concurrent Threads: {CONCURRENT_THREADS}")
print("=" * 70)
print()

# Divide requests among threads
request_ids = list(range(TOTAL_REQUESTS))
random.shuffle(request_ids)  # Randomize order

batch_size = TOTAL_REQUESTS // CONCURRENT_THREADS
batches = []
for i in range(CONCURRENT_THREADS):
    start = i * batch_size
    end = start + batch_size if i < CONCURRENT_THREADS - 1 else TOTAL_REQUESTS
    batches.append(request_ids[start:end])

# Record start time
overall_start = time.time()

# Launch all threads
threads = []
for batch in batches:
    t = threading.Thread(target=worker, args=(batch,))
    threads.append(t)
    t.start()

# Wait for all threads to complete
for t in threads:
    t.join()

overall_end = time.time()
total_duration = overall_end - overall_start

# ==================== RESULTS ====================
print("\n" + "=" * 70)
print("📊 RESULTS SUMMARY")
print("=" * 70)

print(f"\n⏱️  Timing:")
print(f"   Total time for {TOTAL_REQUESTS} requests: {total_duration:.3f}s")
print(f"   Average time per request: {total_duration/TOTAL_REQUESTS:.4f}s")
print(f"   Requests per second: {TOTAL_REQUESTS/total_duration:.2f}")

print(f"\n✅ Success: {len(results)} / {TOTAL_REQUESTS}")
print(f"❌ Errors: {len(errors)} / {TOTAL_REQUESTS}")

if results:
    # Thread usage analysis
    thread_counts = Counter(r["thread"] for r in results)
    print(f"\n🧵 Thread Usage:")
    print(f"   Unique threads used: {len(thread_counts)}")
    for thread, count in sorted(thread_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"   • {thread}: {count} requests")
    if len(thread_counts) > 10:
        print(f"   ... and {len(thread_counts) - 10} more threads")
    
    # Response time analysis
    durations = [r["duration"] for r in results]
    print(f"\n⏱️  Response Times:")
    print(f"   Min: {min(durations):.4f}s")
    print(f"   Max: {max(durations):.4f}s")
    print(f"   Avg: {sum(durations)/len(durations):.4f}s")
    
    # Username distribution
    username_counts = Counter(r["username"] for r in results)
    print(f"\n👤 Username Distribution (top 10):")
    for user, count in username_counts.most_common(10):
        print(f"   • {user}: {count} requests")
    
    # Sample responses
    print(f"\n📝 Sample Responses:")
    for r in results[:5]:
        print(f"   [{r['id']:3d}] {r['username']:10s} -> {r['reply']:20s} | {r['duration']:.4f}s | {r['thread']}")

if errors:
    print(f"\n❌ Error Details:")
    for e in errors[:5]:
        print(f"   [{e['id']:3d}] {e['username']:10s} -> {e['error'][:60]}")

print("\n" + "=" * 70)
print("🏁 LOAD TEST COMPLETE")
print("=" * 70)
