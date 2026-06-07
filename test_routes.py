import urllib.request

base = "http://127.0.0.1:5000"
routes = [
    "/student/chapter/13",
    "/student/chapter/13/overview",
    "/student/chapter/13/key-points",
    "/student/chapter/13/formulas",
    "/student/chapter/13/reactions",
    "/student/chapter/13/experiments",
    "/student/chapter/13/practice",
    "/student/chapter/13/quiz",
    "/api/chapter/13/v4-state",
    "/api/chapter/13/complete-chapter",
]

for route in routes:
    try:
        req = urllib.request.Request(base + route)
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"OK  {resp.status}  {route}")
    except urllib.error.HTTPError as e:
        print(f"ERR {e.code}  {route}")
    except Exception as e:
        print(f"FAIL {route}: {e}")
