import sys
import re

SERVER_FILE_NAME = "p_server.py"
CLIENT_FILE_NAME = "p_client.py"
CONFIG_RPC_NAME = "rpc.conf"
SERVERFILE = "servidor.py"

def main(file_name):
    create_client_file(file_name)
    create_server_file()

def create_client_file(file_name):
    host, port = get_port_and_host(open_file(CONFIG_RPC_NAME))
    p_client = []
    with open(file_name) as archivo:
        lines = archivo.readlines()
        function_name_index = -1
        return_index = -1
        for index, line in enumerate(lines):
            if "#RPC" in line:
                function_name_index = index + 1
                return_index = function_name_index + 1
                function_name, param1, param2 =get_function_properties(str(lines[function_name_index]))
                lines[return_index] = "\t return cliente.ejecutarRemoto('{}', {}, {}) \n".format(function_name, param1, param2)
                continue
            p_client.append(line)
    
    p_client.insert(0, "from cliente import Cliente \n")
    p_client.insert(3,"\ncliente = Cliente(\"{}\",{})\n\n".format(host.strip(), port.strip()))
    create_file(CLIENT_FILE_NAME, p_client)

def open_file(file_name):
    with open(file_name) as f:
        return f.readlines()
    
def get_port_and_host(config_lines):
    host = config_lines[0].split(":")[1].replace("\n","")
    port = config_lines[1].split(":")[1]
    return host, port

def create_server_file():
    server_file = open_file(SERVERFILE)
    host, port = get_port_and_host(open_file(CONFIG_RPC_NAME))

    p_server = server_file
    p_server.insert(0,"import funciones \n")
    p_server.append("\n")
    p_server.insert(7,"HOST= \"{}\"\n".format(host.strip()))
    p_server.insert(8,"PORT= {}\n".format(port.strip()))
    p_server.insert(9,"\n")
    p_server.insert(10,"def atenderCliente(msg):\n")
    p_server.insert(11,"\tfunc  = msg[\"funcion\"]\n")
    p_server.insert(12,"\tparam1 =msg[\"params\"][0]\n")
    p_server.insert(13,"\tparam2 =msg[\"params\"][1]\n")
    
    p_server.insert(14,'\tfunciones_module = __import__("funciones")\n')
    p_server.insert(15,'\tfunciones = getattr(funciones_module, func)\n')
    p_server.insert(16,'\tresultado = eval(f"{func}({param1}, {param2})", {"func": {funciones}, "param1": {param1}, "param2": {param2}})\n')
        
    p_server.insert(17,"\tresponse={\"result\":resultado}\n")
    p_server.insert(18,"\treturn json.dumps(response).encode(\"utf-8\")\n")
    
    create_file(SERVER_FILE_NAME, p_server)
    

def get_function_properties(line):
    match = re.search("\s([\w]+)(\((\w)).((\w)\))", line)
    name, param1, param2 = match.group(1,3,5)
    return name, param1, param2
    
def create_file(file_name, data: list):
    with open(file_name,"w") as f:
        f.writelines(data)


if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print(f"Forma de uso: {sys.argv[0]} <app.py>")
        sys.exit(1)

    main(sys.argv[1])