import socket

'''
Cliente se conecta al servidor en la dirección IP 127.0.0.1 y en el puerto 65432. 
Luego, el cliente envía un mensaje al servidor y espera a que llegue una respuesta. 
Cuando se recibe la respuesta, se imprime en la consola.
'''

# Definir la dirección IP y el puerto del servidor
HOST = '127.0.0.1'
PORT = 65432

# Crear un objeto socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Conectar al servidor
    s.connect((HOST, PORT))
    # Enviar datos al servidor
    s.sendall(b'Hola, servidor de socket en Python')
    # Recibir la respuesta del servidor
    data = s.recv(1024)

# Devolver la representacion canonica del objeto
print('Mensaje recibido: ', repr(data))
