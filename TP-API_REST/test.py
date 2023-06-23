import unittest
from flask import Flask
from app import app

PRODUCTOS = [
    {"producto_id": 1, "nombre": "Camisa", "stock": 15},
    {"producto_id": 2, "nombre": "Pantalón", "stock": 5},
]

ITEMS= [
    {"producto_id": 1,"cantidad": 1},
    {"producto_id": 1,"cantidad": 1},
    {"producto_id": 1,"cantidad": 1},
    {"producto_id": 1,"cantidad": 1},
    {"producto_id": 1,"cantidad": 1},
    {"producto_id": 1,"cantidad": 1},
    {"producto_id": 1,"cantidad": 1},
    {"producto_id": 1,"cantidad": 1},
    {"producto_id": 1,"cantidad": 1},
    {"producto_id": 1,"cantidad": 1},
    {"producto_id": 1,"cantidad": 1},
    {"producto_id": 1,"cantidad": 1},
    {"producto_id": 1,"cantidad": 1},
    {"producto_id": 1,"cantidad": 1}
]

NUEVO_CARRITO ={
    "user_id": 123,
    "carrito_id": 1,
    "items": [
      {
        "producto_id": 1,
        "cantidad": 10
      }
    ]
  }


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()
    
    def tearDown(self):
        self.app.delete('/carritos')
        
    def test_crear_carrito_usuario_repetido(self):
        data ={"user_id": 456}
        self.app.post('/carritos',json=data)
        response2 = self.app.post('/carritos',json=data)
        self.assertEqual(response2.status_code, 400)

    
    def test_cantidad_operaciones_mayor(self):
        #Creamos carrito
        self.app.post('/carritos',json={"user_id": 123})
        #hacemos mas de 20 operaciones sobre el carrito, de get en este caso
        for _ in range(20):
            self.app.get('/carritos/{}'.format(1))
        response = self.app.get('/carritos/{}'.format(1))
        self.assertEqual(response.status_code, 400)
    
    def test_cantidad_items_sobrepasada(self):
        #Creamos carrito
        self.app.post('/carritos',json={"user_id": 456})
        #agrego productos al carrito
        data ={
            "items": ITEMS
            }
        self.app.patch('/carritos/{}'.format(1), json=data)
        # agregamos un item mas para obtener el error
        response = self.app.patch('/carritos/{}'.format(1), json={'items':[{"producto_id": 1,"cantidad": 1}]})
        self.assertEqual(response.status_code, 400)

    def test_cantidad_mayor_stock_disponible(self):
        #Creamos carrito
        self.app.post('/carritos',json={"user_id": 456})
        #agrego productos al carrito
        data ={
            "items": [
                {"producto_id": 1,"cantidad": 100}
            ]
            }
        response = self.app.patch('/carritos/{}'.format(1), json=data)
        self.assertEqual(response.status_code, 400)
    
    def test_descontar_stock_al_pagar_carrito(self):
        #Creamos carrito
        self.app.post('/carritos',json={"user_id": 456})
        #agrego productos al carrito
        data ={
            "items": [
                {"producto_id": 1,"cantidad": 10}
            ]
            }
        #agregamos items al carrito
        productos_antes = self.app.get('/productos').get_json()
        stock_original = productos_antes[0]['stock']
        self.app.patch('/carritos/{}'.format(1), json=data)
        #pago del carrito
        response = self.app.post('/carritos/{}/pago'.format(1))
        productos_despues = self.app.get('/productos').get_json()
        stock_despues_pago = productos_despues[0]['stock']
        decremento = stock_original > stock_despues_pago
        stock_obtenido = stock_original - 10
        self.assertEqual(stock_despues_pago, stock_obtenido)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(decremento, True)

    def test_reestablecer_descontar_stock_sobreescritura_carrito(self):
        valor_esperado_stock_disponible=5
        #Creamos carrito
        self.app.post('/carritos',json={"user_id": 123})
        #agrego productos al carrito
        data ={
            "items": [
                {"producto_id": 1,"cantidad": 5}
            ]
            }
        self.app.patch('/carritos/{}'.format(1), json=data)
        #sobreescribimos el carrito
        response = self.app.put('/carritos/{}'.format(1), json={"carrito": NUEVO_CARRITO})
        productos = self.app.get('/productos').get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(productos[0]['stock'], valor_esperado_stock_disponible)

    def test_aumentar_cantidad_al_agregar_mismo_producto(self):
        cantidad_esperada_antes_agregar = 5
        cantidad_esperada_antes_agregar_adicional = 10
        longitud_esperada = 1
        #Creamos carrito
        self.app.post('/carritos',json={"user_id": 123})
        #agrego productos al carrito
        data ={
            "items": [
                {"producto_id": 1,"cantidad": 5}
            ]
            }
        self.app.patch('/carritos/{}'.format(1), json=data)
        #verificamos la cantidad del producto agregado al carrito
        items = self.app.get('/carritos/{}'.format(1)).get_json()['items']
        cantidad_en_carrito = items[0][1]
        self.assertEqual(cantidad_en_carrito, cantidad_esperada_antes_agregar)
        #agregamos otro producto con el mismo id
        self.app.patch('/carritos/{}'.format(1), json=data)
        items = self.app.get('/carritos/{}'.format(1)).get_json()['items']
        cantidad_en_carrito_al_agregar_adicional = items[0][1]
        self.assertEqual(cantidad_en_carrito_al_agregar_adicional, cantidad_esperada_antes_agregar_adicional)
        self.assertEqual(len(items), 1)

    def test_error_al_pagar_carrito_vacio(self):
        #Creamos carrito
        self.app.post('/carritos',json={"user_id": 456})

        #pago del carrito
        response = self.app.post('/carritos/{}/pago'.format(1))
        self.assertEqual(response.status_code, 400)
        #verificamos carrito sin items
        items = self.app.get('/carritos/{}'.format(1)).get_json()['items']
        self.assertEqual(len(items), 0)

    def test_inactividad_carrito(self):
        pass
        

if __name__ == '__main__':
    unittest.main()