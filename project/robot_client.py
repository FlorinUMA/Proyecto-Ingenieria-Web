from requests import post
from json import dumps

# Simulación de un robot interactuando con nuestra web

response = post(
    "http://localhost:5000/api/status/2",
    json={"status": 3},
    headers={"Content-Type": "application/json"},
)
print(dumps(response, indent=3))
