from flask import Flask, jsonify, request
import time

app = Flask(__name__)

# Datos de ejemplo
productos = [
    {"producto_id": 1, "nombre": "Camisa", "stock": 10},
    {"producto_id": 2, "nombre": "Pantalón", "stock": 5},
]

carritos = []

# Ruta para obtener la lista de productos
@app.route('/productos', methods=['GET'])
def obtener_productos():
    return jsonify(productos)

# Ruta para obtener un carrito de compra por su ID
@app.route('/carritos/<int:carrito_id>', methods=['GET'])
def obtener_carrito(carrito_id):
    for carrito in carritos:
        if carrito['carrito_id'] == carrito_id:
            return jsonify(carrito)
    return jsonify({"message": "Carrito no encontrado"}), 404

# Ruta para crear un carrito de compra
@app.route('/carritos', methods=['POST'])
def crear_carrito():
    user_id = request.json.get('user_id')
    # Verificar si ya existe un carrito para el usuario
    for carrito in carritos:
        if carrito['user_id'] == user_id:
            return jsonify({"message": "Ya existe un carrito para el usuario"}), 400
    carrito_id = len(carritos) + 1
    nuevo_carrito = {"user_id": user_id, "carrito_id": carrito_id, "items": []}
    carritos.append(nuevo_carrito)
    return jsonify(nuevo_carrito), 201

# Ruta para sobreescribir un carrito de compra
@app.route('/carritos/<int:carrito_id>', methods=['PUT'])
def sobreescribir_carrito(carrito_id):
    for carrito in carritos:
        # Verifica que la lista de ítems no exceda el stock disponible antes de actualizar el carrito
        if carrito['carrito_id'] == carrito_id:
            nuevos_items = request.json.get('carrito')
            for item in nuevos_items:
                producto_id = item['producto_id']
                cantidad = item['cantidad']
                producto = obtener_producto(producto_id)
                if producto:
                    if cantidad > producto['stock']:
                        return jsonify({"message": "La cantidad de productos con ID {} excede el stock disponible".format(producto_id)}), 400
                else:
                    return jsonify({"message": "Producto con ID {} no encontrado".format(producto_id)}), 404

            carrito['items'] = nuevos_items
            for item in nuevos_items:
                producto_id = item['producto_id']
                cantidad = item['cantidad']
                producto = obtener_producto(producto_id)
                producto['stock'] -= cantidad
            return jsonify(carrito)
    return jsonify({"message": "Carrito no encontrado"}), 404


# Ruta para agregar una lista de productos a un carrito
@app.route('/carritos/<int:carrito_id>', methods=['PATCH'])
def agregar_productos_carrito(carrito_id):
    for carrito in carritos:
        if carrito['carrito_id'] == carrito_id:
            lista_productos = request.json.get('lista_productos')

            # Verificar límite de ítems en el carrito
            if len(carrito['items']) + len(lista_productos) > 15:
                return jsonify({"message": "Se ha excedido el límite de ítems en el carrito, se considera fraude"}), 400
            # Verificar límite de operaciones sobre el carrito
            if carrito.get('operaciones', 0) >= 20:
                carritos.remove(carrito)
                return jsonify({"message": "Se ha alcanzado el límite de operaciones sobre el carrito, es fraude y se eliminará el carrito."}), 400

            for item in lista_productos:
                producto_id = item['producto_id']
                cantidad = item['cantidad']
                producto = obtener_producto(producto_id)
                if producto:
                    cantidad_existente = 0
                    for carrito_item in carrito['items']:
                        if carrito_item[0] == producto_id:
                            cantidad_existente += carrito_item[1]

                    # Verifica la suma de las cantidades para un mismo producto y
                    # garantizará que no exceda el límite de 10 unidades
                    if cantidad_existente + cantidad <= 10:
                        carrito['items'].append(
                            (producto_id, cantidad))
                        producto['stock'] -= cantidad
                    else:
                        return jsonify({"message": "La cantidad total para el producto con ID {} excede el límite de 10 unidades".format(producto_id)}), 400
                else:
                    return jsonify({"message": "Producto con ID {} no encontrado".format(producto_id)}), 404
            return jsonify(carrito)
    return jsonify({"message": "Carrito no encontrado"}), 404

# Ruta para eliminar un carrito de compra
@app.route('/carritos/<int:carrito_id>', methods=['DELETE'])
def eliminar_carrito(carrito_id):
    for carrito in carritos:
        if carrito['carrito_id'] == carrito_id:
            carritos.remove(carrito)
            return jsonify({"message": "Carrito eliminado"})
    return jsonify({"message": "Carrito no encontrado"}), 404

# Ruta para generar el pago de un carrito
@app.route('/carritos/<int:carrito_id>/pago', methods=['POST'])
def generar_pago(carrito_id):
    for carrito in carritos:
        if carrito['carrito_id'] == carrito_id:
            # Realizar lógica de generación de pago y actualización de stock aquí

            # Verificar período de inactividad
            if carrito.get('last_activity') and (time.time() - carrito['last_activity']) / 60 > X:
                carritos.remove(carrito)
                return jsonify({"message": "El carrito ha sido eliminado debido a inactividad"})

            seguimiento_id = generar_numero_seguimiento()
            carritos.remove(carrito)
            return jsonify({"seguimiento_id": seguimiento_id})
    return jsonify({"message": "Carrito no encontrado"}), 404

# Función para obtener un producto por su ID
def obtener_producto(producto_id):
    for producto in productos:
        if producto['producto_id'] == producto_id:
            return producto
    return None

# Función para generar un número de seguimiento ficticio
def generar_numero_seguimiento():
    return 12345

if __name__ == '__main__':
    app.run()
