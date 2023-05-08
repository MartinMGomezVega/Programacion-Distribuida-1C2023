import sys
import socket
import selectors
import types

# Es muy similar al servidor, pero en lugar de escuchar conexiones, comienza iniciando conexiones a través de start_connections()

sel = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]

# start_connections: 
def start_connections(host, port, num_conns):
    server_addr = (host, port)
    for i in range(0, num_conns):
        # cada iteración, crea una conexión con un ID de conexión 'connid' que se incrementa en 1 para cada nueva conexión
        connid = i + 1
        print(f"Starting connection {connid} to {server_addr}")
        # crea un socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # , el socket se configura en modo no bloqueante
        sock.setblocking(False)
        # establece una conexión con el servidor
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        # se crea un objeto data de tipo types.SimpleNamespace que contiene información sobre la conexión
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=messages.copy(),
            outb=b"", # buffer de salida para almacenar datos que se enviarán a través de la conexión
        )
        sel.register(sock, events, data=data)

# service_connection: es un callback que se utiliza para atender una conexión establecida con un servidor
# se invoca automáticamente cuando se detecta un evento de lectura o escritura en una conexión registrada con el selector de eventos
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    # mask indica qué eventos se han activado
    if mask & selectors.EVENT_READ:
        # se intenta leer datos del socket
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            # se imprime un mensaje indicando la cantidad de datos recibidos y se actualiza la variable recv_total del objeto de datos
            print(f"Received {recv_data!r} from connection {data.connid}")
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            # Si no se recibe nada (recv_data es falso), o si se han recibido todos los datos esperados, se imprime un mensaje de cierre de la conexión y se cierra el socket
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        # se intenta enviar datos por el socket
        if not data.outb and data.messages:
            #  Si no hay datos pendientes de enviar y todavía hay mensajes por enviar en la cola, se obtiene el siguiente mensaje de la cola
            data.outb = data.messages.pop(0)
        if data.outb:
            # Si hay datos pendientes de enviar, se intenta enviar tantos bytes como sea posible
            print(f"Sending {data.outb!r} to connection {data.connid}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

# Verificacion del nro de argumentos pasados en la linea de comandos sea 4  (el nombre del script, el host, el puerto y el nro de conexiones)
if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <host> <port> <num_connections>")
    sys.exit(1)

host, port, num_conns = sys.argv[1:4]
start_connections(host, int(port), int(num_conns))

try:
    while True: # se ejecuta continuamente hasta que se interrumpe mediante la excepción KeyboardInterrupt
        # esperar eventos de lectura o escritura en los sockets registrados en el objeto sel
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                # se produce un evento, se recupera el objeto key que contiene el socket y la información asociada (mask) y se llama a la función service_connection() para atender el evento
                service_connection(key, mask)
        # Si no hay sockets en el objeto sel que estén siendo monitoreados, se sale del ciclo
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
