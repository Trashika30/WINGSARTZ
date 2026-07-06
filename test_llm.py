import requests

BASE = "http://localhost:8000/api/v1"

# 1. Check LLM provider status
print("=== LLM Provider Status ===")
r = requests.get(f"{BASE}/chat/llm-status", timeout=10)
status = r.json()
for k, v in status.items():
    print(f"  {k}: {v}")
print()

# 2. Login as owner
r = requests.post(f"{BASE}/auth/login", json={"email": "owner@wingsartz.com", "password": "WingsOwner2026!"})
token = r.json().get("access_token", "")
H = {"Authorization": f"Bearer {token}"}
print(f"[LOGIN] {'OK' if token else 'FAILED'}")
print()

# 3. Admin chat — shipping question
print("=== Admin: Shipping Options Test ===")
r = requests.post(f"{BASE}/chat/admin/chat", headers=H, json={"query": "What are the shipping options and costs?"}, timeout=45)
data = r.json()
print(f"Agent   : {data.get('agent')}")
print(f"Response: {str(data.get('response')).encode('ascii', 'ignore').decode('ascii')}")
print()

# 4. Admin chat — greeting
print("=== Admin: Greeting Test ===")
r = requests.post(f"{BASE}/chat/admin/chat", headers=H, json={"query": "hi"}, timeout=45)
data = r.json()
print(f"Agent   : {data.get('agent')}")
print(f"Response: {str(data.get('response'))[:300].encode('ascii', 'ignore').decode('ascii')}")
print()

# 5. Customer support — shipping cost
print("=== Customer Support: Shipping Cost Test ===")
r = requests.post(f"{BASE}/chat/support", json={"query": "How much does shipping cost to Mumbai?"}, timeout=45)
data = r.json()
print(f"Agent   : {data.get('agent')}")
print(f"Response: {str(data.get('response')).encode('ascii', 'ignore').decode('ascii')}")
print()

print("=== ALL TESTS DONE ===")
