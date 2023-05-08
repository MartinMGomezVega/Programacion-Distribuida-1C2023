# El guión principal del cliente.
import sys
import socket
import selectors
import traceback
import libclient

# selectors es para manejar multiples conexiones de clientes simultaneamente
sel = selectors.DefaultSelector()

# create_request: obtiene la solicitud que se va a enviar al servidor
def create_request(action, value):
    if action == "search":
        # se envía la solicitud en formato JSON
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value),
        )
    else:
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=bytes(action + value, encoding="utf-8"),
        )

# start_connection: Inicia una conexión de socket TCP con el servidor
def start_connection(host, port, request):
    addr = (host, port)
    print(f"Starting connection to {addr}")
    # crea un objeto de socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # se configura para no bloquear el flujo de datos
    sock.setblocking(False)
    # se establece la conexión al servidor 
    sock.connect_ex(addr)
    # se registra en el objeto de selección de eventos 
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    # crea un objeto de mensaje que contiene la información del socket, la dirección del servidor y la solicitud que se va a enviar
    message = libclient.Message(sel, sock, addr, request)
    # sel.register: permite que el selector pueda manejar el estado del socket y el objeto de mensaje asociado para llevar a cabo la comunicación con el servidor
    sel.register(sock, events, data=message)


# Verificacion del nro de argumentos pasados en la linea de comandos sea 5  (el nombre del script, el host, el puerto, la accion y el valor)
if len(sys.argv) != 5:
    print(f"Usage: {sys.argv[0]} <host> <port> <action> <value>")
    sys.exit(1)

# se obtiene el host y el puerto a partir de los argumentos de línea de comando
host, port = sys.argv[1], int(sys.argv[2])
action, value = sys.argv[3], sys.argv[4]
# crea una solicitud
request = create_request(action, value)
# Inicia la conexion
start_connection(host, port, request)

try:
    while True:
        # espera eventos
        events = sel.select(timeout=1)
        for key, mask in events:
            message = key.data
            try:
                # Si se produce algún evento, se procesa el evento llamando al método process_events asociado a la clave del selector que activó el evento.
                message.process_events(mask)
            except Exception:
                print(
                    f"Main: Error: Exception for {message.addr}:\n"
                    f"{traceback.format_exc()}"
                )
                message.close()
        # comprueba si aún hay algún socket siendo monitoreado:
        if not sel.get_map():
            # si no hay, se rompe el bucle y se sale del programa.
            break

# En caso de que se produzca una excepción durante el procesamiento de los eventos de una conexión:
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    # Cierra el selector
    sel.close()
