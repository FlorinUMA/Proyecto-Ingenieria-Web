# Control de robots asistenciales
Este es un trabajo de la Universidad de Málaga, para la asignatura de Ingeniería web, del grado Ingeniería de la salud (mención en Bioinformática). El proyecto ha sido realizado por: **Florín Babusca Voicu, Pablo Molina Sánchez, Juan Carlos Ruiz Ruiz y Claudia Vega Rodríguez**.

----
## Descripción del proyecto

En este proyecto se propone una implementación de una página web utilizable en hospitales para controlar robots asistenciales, ya sean robots para videollamadas, limpieza o transporte de medicamentos; entre otros. Para ello ofrecemos esta web que permite controlar en todo momento las tareas que se están realizando. Y si se trata de un técnico, podrá crear nuevas tareas, modificar las existentes, incluso añadir nuevos tipos.

## Técnologías utilizadas

Para ello hemos utilizado `HTML5`, `CSS` y `Javascript` para la implementación del frontend apoyándonos además en el framework de CSS y Javascript `Bootstrap`.
Para el backend hemos utilizado `Python` y su framework `Flask`, en el que hemos implementado además una pequeña base de datos que nos permita guardar información acerca de los robots y las tareas que se utilizan en el hospital, para lo que hemos utilizado `SQLalchemy`.

----

## Modo de uso

Para poder lanzar la aplicación en local primero tendremos que cargar las librerías necesarias uasndo `pip`, usando el siguiente comando(Si nos encontramos en la carpeta principal del repositorio):
```
pip install -r ./requirements.txt
```
A continuación solo necesitas ejecutar el código de la aplicación, usando el comando.

```
python ./project/app.py
```
o
```
python3 ./project/app.py
```

Una vez hemos ejecutado el comando, podremos acceder a la web a través de la dirección `http://localhost:5000/` y deberíamos encontrarnos con la pantalla de inicio.

![Página principal](https://github.com/FlorinUMA/Proyecto-Ingenieria-Web/blob/main/Memoria_LaTex/Latex_Source/images/Home.png))

### API

La página web también posee una pequeña API que permite a los robots contactar con la web para modificar el estado de una tarea y para añadir nuevos robots. Podemos observar una pequeña demostración ejecutando el archivo `robot_client.py`, usando el siguiente comando mientras la web esté levantada:

```
python ./project/robot_client.py
```
o
```
python3 ./project/robot_client.py
```

Los endpoints son:

**POST** `/api/status/{id_tarea}`
```
{
  "status": {nuevo_estado}
}
```
Donde id tarea es el identificador numérico de la tarea a modificar y el cuerpo es de la forma:
---
**POST** `/api/robot`
```
{
  "nombre": {nombre_robot}, 
  "tipos": {lista_tipos}
}
```
El cuerpo es de la forma (la lista de tipos de tareas solo admitirá aquellos que hayan sido previamente añadidos por un técnico):
