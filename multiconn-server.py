import sys
import socket
import selectors
import types

'''
el servidor utiliza el módulo selectors para monitorear múltiples conexiones de forma eficiente, 
mientras que el cliente utiliza el módulo selectors para manejar múltiples conexiones de forma asincrónica. 
El servidor escucha en un socket, acepta conexiones entrantes y las agrega al selector. 
Cuando se recibe un evento de lectura en una conexión, se lee y se envía una respuesta de vuelta. 
El cliente inicia múltiples conexiones y las agrega al selector. 
Cuando se recibe un evento de escritura en una conexión, se envía
'''

sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)


# bucle de eventos
try:
    while True:
        #  El bucle espera indefinidamente nuevos eventos (sel.select(timeout=None)) y,
        # cuando se produce un evento, llama a la función correspondiente (accept_wrapper o service_connection) para manejarlo.
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                #  La función acepta la conexión y la configura en modo no bloqueante, 
                # y luego registra la conexión en el selector para notificar cuando hay datos de entrada o salida disponibles.
                accept_wrapper(key.fileobj)
            else:
                #  se invoca cuando se notifica al selector que hay datos de entrada/salida disponibles en una conexión de cliente registrada
                # Si hay datos de entrada disponibles, se leen y se agregan a los datos de salida, y si hay datos de salida disponibles, se envían de vuelta al cliente.
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
    
