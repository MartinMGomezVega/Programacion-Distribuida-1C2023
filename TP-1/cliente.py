import socket
import json

class Cliente:
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
    
    def ejecutarRemoto(self, function_name, param1, param2 ):
        try:
            params = []
            params.append(param1)
            params.append(param2)
            
            # Crear una conexión TCP con el servidor
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("127.0.0.1", 8080))

            # Crear el mensaje de solicitud en formato JSON
            request = {
                "funcion": function_name,
                "params": list(params)
            }
            message = json.dumps(request).encode("utf-8")

            # Enviar el mensaje al servidor
            sock.sendall(message)

            # Recibir la respuesta del servidor
            response = b""
            data = sock.recv(4096)
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