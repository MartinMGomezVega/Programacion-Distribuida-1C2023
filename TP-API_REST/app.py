from flask import Flask, abort, jsonify, request
from datetime import datetime
import enum
from functools import reduce
import random

app = Flask(__name__)

# Datos de ejemplo
PRODUCTOS = [
    {"producto_id": 1, "nombre": "Camisa", "stock": 15},
    {"producto_id": 2, "nombre": "Pantalón", "stock": 5},
]

CARRITOS = []

class TIPO_OPERACION(enum.Enum):
    DESCONTAR_STOCK = 1
    REESTABLECER_STOCK = 2

PRODUCTO_ID = 0
CANTIDAD = 1
STATUS_CODE_BAD_REQUEST = 400
STATUS_CODE_CREATED = 201
STATUS_CODE_OK = 200
STATUS_CODE_NOT_FOUND = 404

# Ruta para obtener la lista de productos
@app.route('/productos', methods=['GET'])
def obtener_productos():
    return jsonify(PRODUCTOS)

# Ruta para obtener un carrito de compra por su ID
@app.route('/carritos/<int:carrito_id>', methods=['GET'])
def obtener_carrito(carrito_id):
    for carrito in CARRITOS:
        if carrito['carrito_id'] == carrito_id:
            validar_items_carrito(carrito, None)
            carrito['operaciones'] += 1 
            return jsonify(carrito)
    abort(STATUS_CODE_NOT_FOUND, "Carrito no encontrado")

# Ruta para crear un carrito de compra
@app.route('/carritos', methods=['POST'])
def crear_carrito():
    user_id = request.json.get('user_id')
    # Verificar si ya existe un carrito para el usuario
    for carrito in CARRITOS:
        if carrito['user_id'] == user_id:
            abort(STATUS_CODE_BAD_REQUEST,"Ya existe un carrito para el usuario con id {}".format(user_id))
    carrito_id = len(CARRITOS) + 1
    nuevo_carrito = {"user_id": user_id, "carrito_id": carrito_id, "items": [], "operaciones": 0, 'last_activity': datetime.now()}
    CARRITOS.append(nuevo_carrito)
    return jsonify(nuevo_carrito), STATUS_CODE_CREATED

def validar_items_carrito(carrito, items):

    # Verificar límite de operaciones sobre el carrito
    if carrito.get('operaciones', 0) >= 20:
        CARRITOS.remove(carrito)
        abort(STATUS_CODE_BAD_REQUEST,
              "Se ha alcanzado el límite de operaciones sobre el carrito, es fraude y se eliminará el carrito.")
    if items:
        # Verificar límite de ítems en el carrito
        if len(carrito['items']) + len(items) > 15:
            abort(STATUS_CODE_BAD_REQUEST,
                "Se ha excedido el límite de ítems en el carrito, se considera fraude")
            
        for item in items:
            producto_id = item['producto_id']
            cantidad_producto = item['cantidad']
            producto = obtener_producto(producto_id)
            cantidad_existente_en_carritos = sum(map(lambda item: item[CANTIDAD],
                                                            filter(lambda item: item[PRODUCTO_ID] == producto_id,
                                                                    reduce(lambda item1, item2: item1 + item2,
                                                                        map(lambda carrito: carrito['items'], CARRITOS)))))
            # Verificar stock del producto 
            if cantidad_producto > producto['stock']:
                abort(STATUS_CODE_BAD_REQUEST, 
                        "La cantidad de productos con ID {} excede el stock disponible".format(producto_id))

            # Verifica la suma de las cantidades para un mismo producto y
            # garantizará que no exceda el límite de 10 unidades
            if cantidad_existente_en_carritos + cantidad_producto > 10:
                abort(STATUS_CODE_BAD_REQUEST, 
                        "La cantidad total para el producto con ID {} excede el límite de 10 unidades".format(producto_id))

                
def modificar_stock(carrito, operacion=TIPO_OPERACION.DESCONTAR_STOCK, items=None):
    if items:
        for item in items:
                producto_id = item['producto_id']
                cantidad = item['cantidad']
                producto = obtener_producto(producto_id)
                producto['stock'] -= cantidad 
    else:
        for item in carrito['items']:
            producto_id, cantidad = (item[PRODUCTO_ID], item[CANTIDAD]) if type(item)==list else (item['producto_id'], item['cantidad'])
            producto = obtener_producto(producto_id)
            if (operacion == TIPO_OPERACION.DESCONTAR_STOCK):
                producto['stock'] -= cantidad
            else:
                if type(item)==list:
                    item[CANTIDAD] -= cantidad
                else:
                    item['cantidad'] -= cantidad
                producto['stock'] += cantidad

# Ruta para sobreescribir un carrito de compra
@app.route('/carritos/<int:carrito_id>', methods=['PUT'])
def sobreescribir_carrito(carrito_id):
    for carrito_original in CARRITOS:
        if carrito_original['carrito_id'] == carrito_id:
            nuevo_carrito = request.json.get('carrito')
            modificar_stock(carrito_original,TIPO_OPERACION.REESTABLECER_STOCK)
            validar_items_carrito(carrito_original, nuevo_carrito['items'])
            modificar_stock(nuevo_carrito,TIPO_OPERACION.DESCONTAR_STOCK)
            cantidad_operaciones= carrito_original.get('operaciones') + 1
            carrito_original = nuevo_carrito
            carrito_original['operaciones'] = cantidad_operaciones
            carrito_original['last_activity'] = datetime.now()
            return jsonify(carrito_original)
    abort(STATUS_CODE_NOT_FOUND,
          "Carrito con ID {} no encontrado".format(carrito_id))


# Ruta para agregar una lista de productos a un carrito
@app.route('/carritos/<int:carrito_id>', methods=['PATCH'])
def agregar_productos_carrito(carrito_id):
    for carrito in CARRITOS:
        if carrito['carrito_id'] == carrito_id:
            lista_productos_nuevos = request.json.get('items')
            validar_items_carrito(carrito, lista_productos_nuevos)
            for item_nuevo in lista_productos_nuevos:
                for item_carrito in carrito['items']:
                    if item_nuevo['producto_id'] == item_carrito[PRODUCTO_ID]:
                        item_carrito[CANTIDAD] += item_nuevo['cantidad']
                        break
                else:
                    carrito['items'].append([item_nuevo['producto_id'], item_nuevo['cantidad']])

            modificar_stock(None, None, lista_productos_nuevos)
            carrito['operaciones'] += 1
            carrito['last_activity'] = datetime.now()
            return jsonify(carrito)
    abort(STATUS_CODE_NOT_FOUND, "Carrito con ID {} no encontrado".format(carrito_id)) 

# Ruta para eliminar un carrito de compra
@app.route('/carritos/<int:carrito_id>', methods=['DELETE'])
def eliminar_carrito(carrito_id):
    for carrito in CARRITOS:
        if carrito['carrito_id'] == carrito_id:
            CARRITOS.remove(carrito)
            return jsonify({"message": "Carrito eliminado"})
    abort(STATUS_CODE_NOT_FOUND, "Carrito con ID {} no encontrado".format(carrito_id))

@app.route('/carritos', methods=['DELETE'])
def eliminar_carritos():
    CARRITOS = []
    return jsonify({"message": "Carritos eliminados"})

# Ruta para generar el pago de un carrito
@app.route('/carritos/<int:carrito_id>/pago', methods=['POST'])
def generar_pago(carrito_id):
    for carrito in CARRITOS:
        if carrito['carrito_id'] == carrito_id:
            # Verificar período de inactividad, el periodo de inactividad maximo es de 5 minutos
            if int((datetime.now() - carrito['last_activity']).total_seconds()) / 60 > 5:
                CARRITOS.remove(carrito)
                return jsonify({"message": "El carrito ha sido eliminado debido a inactividad"})
            if not carrito['items']:
                abort(STATUS_CODE_BAD_REQUEST, "Carrito con ID {} no tiene items para generar pago".format(carrito_id))

            seguimiento_id = generar_numero_seguimiento()
            CARRITOS.remove(carrito)
            return jsonify({"seguimiento_id": seguimiento_id})
    abort(STATUS_CODE_NOT_FOUND, "Carrito con ID {} no encontrado".format(carrito_id))

# Función para obtener un producto por su ID
def obtener_producto(producto_id):
    for producto in PRODUCTOS:
        if producto['producto_id'] == producto_id:
            return producto
    abort(STATUS_CODE_NOT_FOUND, "Producto con ID {} no encontrado".format(producto_id))

# Función para generar un número de seguimiento ficticio
def generar_numero_seguimiento():
    return random.random() * 1000

if __name__ == '__main__':
    app.run()
