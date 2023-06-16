ENUNCIADO:
Se requiere implementar una API REST para el carrito de compra de una tienda de ropa. A continuación se describen los servicios:

GET /productos : Devuelve la lista de productos
GET /carritos/<carrito_id> : Devuelve el carrito de compra con dicho id
POST /carritos: Parametro: user_id -> Crea un carrito de compra
PUT /carritos/<carrito_id> : Parametro: carrito -> Sobreescribe el carrito con dicho id
PATCH /carritos/<carrito_id>: Parametro: lista productos -> Agrega la lista de productos al carrito
DELETE /carritos/<carrito_id> : Elimina el carrito con dicho id
POST /carritos/<carrito_id>/pago : Genera el pago de un carrito. Resta el stock de la lista de productos y devuelve un número de seguimiento del pedido. Elimina el carrito del sistema.

Las características del sistema son las siguientes:

- Cada producto es una lista de atributos: <producto_id (entero), nombre (string), stock (entero)>
- El contenido de un carrito es el siguiente: <user_id (entero), carrito_id (entero), lista de ítems <producto_id, cantidad>>
- El pago devuelve un único atributo: <seguimiento_id (entero)>
- No hay control de usuarios, es decir que el carrito se crea con cualquier nro. de usuario.

Los casos de error posibles son:

- No puede haber dos carritos para un mismo usuario al mismo tiempo.
- No puede haber un carrito con una lista de más de 15 ítems (se considera que es fraude).
- No pueden realizarse más de 20 operaciones sobre un mismo carrito (se considera que es fraude). En este caso el carrito debería eliminarse.
- La lista de ítems puede contener tuplas con el mismo producto_id aunque la suma de todas las cantidades (para un mismo producto) no puede exceder el total de 10 unidades (de lo contrario se considera que es fraude).
- Un carrito que tenga un período de más de X minutos de inactividad debe ser eliminado del sistema (el plazo queda a criterio personal para poder realizar el test correspondiente).
- En todo momento debe controlarse que la lista de ítems no exceda el stock. Ej. si se hace un PUT de un carrito que contiene 15 unidades de un producto y el stock es 10, se debe reportar un error.

Se deben realizar tests de unidad que controlen todas las situaciones posibles incluyendo:

- Que no se puedan crear dos carritos simultáneamente para un mismo usuario, pero si se borra/elimina un carrito o si se realiza el pago del mismo,se debería poder crear otro para el mismo usuario.
- Verificar que luego del pago del carrito, el stock de lista de productos se haya decrementado correctamente.

Se requiere implementar los tests de unidad de acuerdo a la librería unittest de python:

- https://docs.python.org/3/library/unittest.html
- https://machinelearningmastery.com/a-gentle-introduction-to-unit-testing-in-python/

Como correr el proyecto:
Para ejecutar la API REST que creamos previamente, sigue estos pasos:

1. Asegúrate de tener instalado Python en tu sistema. Puedes verificarlo ejecutando el comando `python --version` en tu terminal. Si no lo tienes instalado, descárgalo e instálalo desde el sitio web oficial de Python.

2. Crea un nuevo directorio en tu sistema y coloca el archivo `app.py` en ese directorio.

3. Abre una terminal y navega hasta el directorio donde colocaste el archivo `app.py`.

4. Crea un entorno virtual ejecutando el siguiente comando en la terminal:

   `python3 -m venv venv`

5. Activa el entorno virtual. En Windows, ejecuta el siguiente comando:

   `venv\Scripts\activate`

   En macOS y Linux, ejecuta el siguiente comando:

   `source venv/bin/activate`

6. Instala las dependencias necesarias ejecutando el siguiente comando en la terminal:

   `pip install flask`

7. Una vez instaladas las dependencias, puedes ejecutar la aplicación Flask con el siguiente comando:

   `python3 app.py`

   Verás un mensaje en la terminal que indica que la aplicación se está ejecutando en un puerto determinado, por ejemplo, `Running on http://127.0.0.1:5000/`. Eso significa que la API REST está en funcionamiento.

8. Ahora puedes realizar solicitudes a la API REST utilizando herramientas como cURL, Postman o incluso un navegador web.

Notas:
Si ya tienes otro servicio ejecutándose en el mismo puerto (por ejemplo, el puerto 5000), puede producirse un conflicto. Intenta cambiar el puerto en el que se ejecuta la aplicación Flask modificando el código en app.py. Por ejemplo, puedes usar el puerto 8080 cambiando app.run() por app.run(port=8080).
