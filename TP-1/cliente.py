#  ejecutarRemoto: se conecta al servidor, envía los datos correspondientes de la llamada a función y recibe el resultado
def ejecutarRemoto(function_name, param1, param2 ):
    print("function name: ", function_name)
    print("param1: ", param1)
    print("param2: ", param2)
    

import socket
import json
   
def ejecutarRemoto2(host, port, funcion, *params):
    try:
        # Crear una conexión TCP con el servidor
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        # Crear el mensaje de solicitud en formato JSON
        request = {
            "funcion": funcion,
            "params": list(params)
        }
        message = json.dumps(request).encode("utf-8")

        # Enviar el mensaje al servidor
        sock.sendall(message)

        # Recibir la respuesta del servidor
        response = b""
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response += data

        # Cerrar la conexión
        sock.close()

        # Decodificar la respuesta del servidor en formato JSON
        response_data = json.loads(response.decode("utf-8"))

        # Manejar posibles errores en la respuesta
        if "error" in response_data:
            raise Exception(response_data["error"])

        # Devolver el resultado de la ejecución remota
        return response_data["result"]

    except (ConnectionRefusedError, socket.gaierror):
        raise Exception("No se pudo establecer conexión con el servidor.")
    except json.JSONDecodeError:
        raise Exception("Error al decodificar la respuesta del servidor.")
    except Exception as e:
        raise Exception("Error durante la ejecución remota: " + str(e))