Enunciado

Dado un programa en python (p.py)  que tenga un conjunto de funciones anotadas para hacer RPC (remote procedure call), 
se pide generar automáticamente dos programas: 1) p_Cliente.py, 2) p_Servidor.py que permitan implementar dicha funcionalidad. 
Es decir, las funciones que tengan la anotación deben ser invocadas desde el cliente y ejecutadas en el servidor.

Características:
- El servidor p_Servidor.py debe aceptar múltiples conexiones multiplexando entrada/salida (utilizando select)
- El cliente debe ser sincrónico porque queremos ejecutar el programa original (p.py) independizandolo de si las implementaciones
de las funciones son locales o remotas.
- Hay que definir un protocolo simple para que se comunique el cliente con el servidor para realizar la invocación a la función 
remota, se sugiere el siguiente: 
    - cliente -> servidor:  “<nombre función>,<param1>, …,<paramN>”
    - servidor -> cliente: “<resultado>”
- Se debe implementar un programa en python (rpc.py p.py) que dado el programa anotado genere el cliente, el servidor correspondientes.
- Adicionalmente, se debe definir (a mano) un archivo de configuración rpc.conf que tenga la ip y el port que se utilice para la 
comunicación entre cliente y servidor.


Consideraciones
- La anotación #RPC indica que la función que está a continuación (en este caso “multiplicar”) debe ser invocada por el cliente y ejecutada en el servidor.
- La librería cliente.py tiene la función ejecutarRemoto() que se conecta al servidor,  envía los datos correspondientes de la llamada a
función y recibe el resultado. Adicionalmente puede arrojar excepciones para cortar la ejecución (en caso de error): errores de comunicación
(ej. servidor no levantado), errores de datos (ej.: función inválida/no implementada por el servidor, cantidad de params invalida)
- La librería funciones.py (puede no estar si agregan las funciones en el programa servidor directamente) son las funciones que va a resolver el
servidor (que son las mismas que tienen la anotación RPC en p.py).
- Se pueden utilizar expresiones regulares para que rpc.py genere el cliente y el servidor.
