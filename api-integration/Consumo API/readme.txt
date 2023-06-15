Una API REST expone un conjunto de direcciones URL públicas que utilizan las aplicaciones cliente para acceder a los recursos de un servicio web. 
Estas URL, en el contexto de una API, se denominan puntos finales.
Estos puntos finales son para un recurso de cliente que representa potencial customersen el sistema:

método HTTP	    punto final de la API	            Descripción
GET             /customers	                    Obtener una lista de clientes.
GET	            /customers/<customer_id>	    Consigue un solo cliente.
POST	        /customers	                    Crear un nuevo cliente.
PUT	            /customers/<customer_id>	    Actualizar un cliente.
PATCH	        /customers/<customer_id>	    Actualizar parcialmente un cliente.
DELETE	        /customers/<customer_id>	    Eliminar un cliente.