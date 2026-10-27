import httpx
import time

base = "http://127.0.0.1:8000/api/v1"

# 1. Trigger run
res = httpx.post(f"{base}/workflows/wf_standard_pipeline/runs", json={"brief_input": {"target": "playables"}})
print("Create run status:", res.status_code)
data = res.json()
run_id = data["id"]
print("Run ID:", run_id, "Initial State:", data.get("state"))

# 2. Wait for background execution to complete
time.sleep(1.2)

# 3. Query run state
res_state = httpx.get(f"{base}/runs/{run_id}")
state_data = res_state.json()
print("Final State:", state_data.get("state"))
print("Completed nodes:", state_data.get("completed_nodes"))

# 4. Check historical events published to sse_hub
res_events = httpx.get(f"{base}/runs/{run_id}/events")
events_data = res_events.json()
print("SSE events recorded count:", events_data.get("count"))
for ev in events_data.get("events", []):
    print(" - Event:", ev.get("event_type"), "Seq:", ev.get("run_seq"))
