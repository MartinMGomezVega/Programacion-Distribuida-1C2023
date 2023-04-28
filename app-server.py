# Script principal del servidor

import sys
import socket
import selectors
import traceback
import libserver

# selectors es para manejar multiples conexiones de clientes simultaneamente
sel = selectors.DefaultSelector()

# accept_wrapper: acepta una conexión entrante en un socket, establece el socket en modo no bloqueante y registra el socket
def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False) #  establece el socket en modo no bloqueante
    # libserver.Message: maneja los eventos de lectura y escritura en el socket
    message = libserver.Message(sel, conn, addr) 
    # registro del socket
    sel.register(conn, selectors.EVENT_READ, data=message)

# Verificacion del nro de argumentos pasados en la linea de comandos sea 3  (el nombre del script, el host y el puerto)
if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

# Asignacion del host y el puerto utilizando los argumentos pasados en la línea de comandos
host, port = sys.argv[1], int(sys.argv[2])
# Creacion del socket TCP en el host y el puerto:
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Avoid bind() exception: OSError: [Errno 48] Address already in use
# Establecer la opción de socket para permitir la reutilización de direcciones de socket.
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# asocia el socket lsock a la dirección especificada por host y port
lsock.bind((host, port))
#  Escucha de las conexiones entrantes:
lsock.listen()
print(f"Listening on {(host, port)}")
# modo no bloqueante
lsock.setblocking(False)
# Registrar el socket de escucha lsock en el selector sel para monitorear eventos de lectura:
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        # Esperar eventos de entrada/salida en los sockets registrados y devuelve una lista de tuplas (key, mask)
        events = sel.select(timeout=None) 
        for key, mask in events:
            if key.data is None:
                # el objeto listo es el socket de escucha
                accept_wrapper(key.fileobj)
            else:
                # el objeto listo es una conexión establecida 
                message = key.data
                try:
                    # procesa los eventos pendientes en la conexión
                    message.process_events(mask)
                except Exception:
                    # En caso de que se produzca una excepción durante el procesamiento de los eventos de una conexión:
                    print(
                        f"Main: Error: Exception for {message.addr}:\n"
                        f"{traceback.format_exc()}"
                    )
                    message.close()
                    
# En caso de que se produzca una excepción durante el procesamiento de los eventos de una conexión:
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    # Cierra el selector
    sel.close()
