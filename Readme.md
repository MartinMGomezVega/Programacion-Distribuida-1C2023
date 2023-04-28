<!-- Ejecutar el cliente y servidor -->

Shell 1 - Servidor
$ python server.py

Shell 2 - Cliente
$ python client.py

<!-- Ejecutar el manejo de multiples conexiones -->

Shell 1 - Servidor
$ python multiconn-server.py 127.0.0.1 65432

Shell 2 - Cliente
$ python multiconn-client.py 127.0.0.1 65432 2

<!-- Cliente y servidor de aplicaciones -->

Shell 1 - Servidor
python app-server.py '127.0.0.1' 65432

Shell 2 - Cliente
v

<!-- Troubleshooting - Solución de problemas-->
<!-- ping -->

Shell
ping -c 3 127.0.0.1

<!-- netstat -->

Shell
netstat -an | grep 65432

<!-- Wireshark -->

Shell
tshark -i lo0 'tcp port 65432'
