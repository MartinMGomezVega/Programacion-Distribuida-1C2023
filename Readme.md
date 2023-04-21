<!-- Ejecutar el cliente y servidor Echo
Se ejecutará el cliente y el servidor para ver cómo se comportan e inspeccionar lo que sucede.

Abra una terminal o símbolo del sistema, navegue hasta el directorio que contiene sus scripts,
asegúrese de tener Python 3.6 o superior instalado y en su ruta, luego ejecute el servidor: -->

$ python server.py

% Su terminal parecerá colgarse. Eso es porque el servidor está bloqueado o suspendido el .accept():

% Está esperando una conexión de cliente. Ahora, abra otra ventana de terminal o símbolo del sistema y ejecute el cliente:
$ python client.py
