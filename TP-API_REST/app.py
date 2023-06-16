from flask import Flask, jsonify, request

app = Flask(__name__)

# Datos de ejemplo
productos = [
    {"producto_id": 1, "nombre": "Camisa", "stock": 10},
    {"producto_id": 2, "nombre": "Pantalón", "stock": 5},
]

carritos = [{
    "carrito_id":1,
    "user_id":1,
    "items":productos
}]

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
    carrito_id = len(carritos) + 1
    nuevo_carrito = {"user_id": user_id, "carrito_id": carrito_id, "items": []}
    carritos.append(nuevo_carrito)
    return jsonify(nuevo_carrito), 201

# Ruta para sobreescribir un carrito de compra
@app.route('/carritos/<int:carrito_id>', methods=['PUT'])
def sobreescribir_carrito(carrito_id):
    for carrito in carritos:
        if carrito['carrito_id'] == carrito_id:
            carrito['items'] = request.json.get('carrito')
            return jsonify(carrito)
    return jsonify({"message": "Carrito no encontrado"}), 404

# Ruta para agregar una lista de productos a un carrito
@app.route('/carritos/<int:carrito_id>', methods=['PATCH'])
def agregar_productos_carrito(carrito_id):
    for carrito in carritos:
        if carrito['carrito_id'] == carrito_id:
            lista_productos = request.json.get('lista_productos')
            for item in lista_productos:
                producto_id = item['producto_id']
                cantidad = item['cantidad']
                producto = obtener_producto(producto_id)
                if producto:
                    if producto['stock'] >= cantidad:
                        carrito['items'].append(
                            {"producto_id": producto_id, "cantidad": cantidad})
                        producto['stock'] -= cantidad
                    else:
                        return jsonify({"message": "No hay suficiente stock para el producto con ID {}".format(producto_id)}), 400
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
