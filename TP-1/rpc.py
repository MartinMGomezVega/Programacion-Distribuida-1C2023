import sys
import re
import p
import funciones
import cliente.py

SERVER_FILE_NAME = "p_server.py"
CLIENT_FILE_NAME = "p_client.py"
CONFIG_RPC_NAME = "rpc.conf"

def main(file_name):
    create_client_file(file_name)
    create_server_file()

def create_client_file(file_name):
    config_lines = open_file(CONFIG_RPC_NAME)
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
            p_client.append(line)
    
    p_client.insert(0, "import cliente \n")
    create_file(CLIENT_FILE_NAME, p_client)

def open_file(file_name):
    with open(file_name) as f:
        return f.readlines()

def create_server_file():
    config_lines = open_file(CONFIG_RPC_NAME)

    print(config_lines)
    p_server = []
    p_server.append("import funciones \n")
    p_server.append("\n")
    p_server.append("def atenderCliente(msg):\n")
    p_server.append("\tfunc, param1, param2 = msg.split(',')\n")
    p_server.append("\tresultado = funciones.func(param1, param2)\n")
    p_server.append("\t#comunicamos con el cliente y le mandamos el resultado")

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