'''Client for the UINames.com service.'''

# Imports
import sys, re, traceback, requests

# Function
def SampleRecord():
    r = requests.get("http://uinames.com/api?ext&region=United%20States", timeout=2.0)
    # Decode JSON from the response.
    j = r.json()

    return "My name is {} {} and the PIN on my card is {}.".format(
        j["name"],
        j['surname'],
        j['credit_card']['pin']
    )

# Output
sample = SampleRecord()
pat = re.compile(r'My name is (\S+) (\S+) and the PIN on my card is (\S+).')
match = pat.match(sample)

if not match:
    print("Output didn't look quite right:")
    print(sample)

print("Tests pass!  Here are the fields I found in your code's output:")
print("Name:", match.group(1))
print("Surname:", match.group(2))
print("PIN:", match.group(3))