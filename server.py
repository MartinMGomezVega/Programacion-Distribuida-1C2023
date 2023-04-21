import socket

'''
El servidor escucha en la dirección IP 127.0.0.1 y en el puerto 65432. 
Cuando un cliente se conecta, se acepta la conexión y se crea un objeto de conexión conn. 
A continuación, el servidor entra en un bucle mientras espera a que lleguen datos del cliente. 
Cuando se reciben datos, se imprimen y se envía una respuesta al cliente.
'''

# Definir la dirección IP y el puerto del servidor
HOST = '127.0.0.1'
PORT = 65432

# Crear un objeto socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Enlazar el socket a la dirección IP y el puerto
    s.bind((HOST, PORT))
    # Escuchar por conexiones entrantes
    s.listen()
    # Esperar por una conexión
    conn, addr = s.accept()
    with conn:
        print('Conectado por', addr)
        while True:
            # Recibir datos del cliente
            data = conn.recv(1024)
            if not data:
                break
            # Imprimir los datos recibidos
            print('Mensaje recibido: ', repr(data))
            # Enviar una respuesta al cliente
            conn.sendall(b'Recibido: ' + data)
