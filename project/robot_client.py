from requests import post
from json import dumps

# Simulación de un robot interactuando con nuestra web


# Post 1 en el que el robot asigna un nuevo estado
id_tarea = 2
nuevo_estado = 3

response = post(
    f"http://localhost:5000/api/status/{id_tarea}",
    json={"status": nuevo_estado},
    headers={"Content-Type": "application/json"},
)
print(dumps(response.json(), indent=3))


# Post 2 en el que se crea un nuevo robot
response = post(
    "http://localhost:5000/api/robot",
    json={"nombre": "Nuevo_robot", "tipos": ["desinfeccion", "transporte"]},
    headers={"Content-Type": "application/json"},
)
print(dumps(response.json(), indent=3))
