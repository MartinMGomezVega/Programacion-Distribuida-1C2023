import socket
import types
import json
import selectors

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
        recv_data = sock.recv(4096)  
        if recv_data:
            data.outb += atenderCliente(json.loads(recv_data.decode("utf-8")))
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print("Data de respuesta desde el server: ", data.outb)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]



lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind(("{}".format(HOST), PORT))
lsock.listen()
print(f"Listening on (127.0.0.1, 8080)")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

# bucle de eventos
try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
            break
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
