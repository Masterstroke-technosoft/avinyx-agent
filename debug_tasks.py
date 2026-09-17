import httpx

res = httpx.get("http://127.0.0.1:8000/api/v1/agent-tasks/pending")
print(res.status_code, res.text)
