"""Smoke-test the App Engine apps with Flask's test client.

Datastore and users calls go to the App Engine SDK's local testbed stubs, so nothing leaves the runner.
Run from the repository root: python .github/ci/app_engine_smoke.py
"""

import importlib.util
import pathlib
import sys

from google.appengine.ext import testbed

ROOT = pathlib.Path(__file__).resolve().parents[2]
failures = []


def client(folder, module):
    spec = importlib.util.spec_from_file_location(f"{folder}_{module}", ROOT / folder / f"{module}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.app.test_client()


def check(name, response, status=200, contains=None, location=None):
    body = response.get_data(as_text=True)
    problems = []
    if response.status_code != status:
        problems.append(f"status {response.status_code}, expected {status}")
    if contains and contains not in body:
        problems.append(f"body lacks {contains!r}")
    if location and not response.headers.get("Location", "").endswith(location):
        problems.append(f"Location {response.headers.get('Location')!r}, expected …{location}")
    print(("FAIL " if problems else "ok   ") + name + (": " + "; ".join(problems) if problems else ""))
    if problems:
        failures.append(name)
    return response


bed = testbed.Testbed()
bed.activate()
bed.init_datastore_v3_stub()
bed.init_memcache_stub()
bed.init_user_stub()

for folder, module in [("Personal_Website", "personal"), ("Project_Compass", "compass"),
                       ("Resume", "resume"), ("Search", "search")]:
    check(f"{folder} GET /", client(folder, module).get("/"), contains="<")

c = client("Shopping_List", "shopping_list")
check("Shopping_List keeps items", c.get("/?food=apples&food=pears"), contains="pears")

c = client("Fizz_Buzz", "fizz_buzz")
check("Fizz_Buzz n=15", c.get("/?n=15"), contains="FizzBuzz")

c = client("My_Travel_Plans", "travel")
check("My_Travel_Plans n=3", c.get("/?n=3"))

c = client("Encryption", "encryption")
check("Encryption GET /", c.get("/"))
check("Encryption rot13", c.post("/", data={"text": "Hello"}), contains="Uryyb")

c = client("Signup", "signup")
check("Signup GET /", c.get("/"))
check("Signup rejects a bad username", c.post("/", data={"username": "x", "password": "abc", "verify": "abc"}),
      contains="That&#39;s not a valid username.")
check("Signup redirects to welcome", c.post("/", data={"username": "ada", "password": "abc", "verify": "abc"}),
      status=302, location="/welcome?username=ada")
check("Signup welcome", c.get("/welcome?username=ada"), contains="Welcome, ada!")

c = client("ASCII", "ascii")
check("ASCII needs both fields", c.post("/", data={"title": "only a title"}), contains="we need both")
check("ASCII saves art", c.post("/", data={"title": "Cat", "art": "=^.^="}), status=302, location="/")
check("ASCII lists art", c.get("/"), contains="=^.^=")

c = client("Blog", "blog")
posted = check("Blog new post", c.post("/newpost", data={"subject": "Hello", "content": "First post"}), status=302)
check("Blog post page", c.get(posted.headers.get("Location", "/0")), contains="First post")
check("Blog front page", c.get("/"), contains="Hello")

c = client("Guestbook", "guestbook")
check("Guestbook signs", c.post("/sign?guestbook_name=ci", data={"content": "hi from CI"}),
      status=302, location="/?guestbook_name=ci")
check("Guestbook shows greeting", c.get("/?guestbook_name=ci"), contains="hi from CI")

bed.deactivate()
sys.exit(1 if failures else 0)
