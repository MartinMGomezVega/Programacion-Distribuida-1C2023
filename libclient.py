# Message la clase del cliente
import sys
import selectors
import json
import io
import struct


class Message:
    # Inicializacion de las variables
    def __init__(self, selector, sock, addr, request):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.request = request
        self._recv_buffer = b""
        self._send_buffer = b""
        self._request_queued = False
        self._jsonheader_len = None
        self.jsonheader = None
        self.response = None

    # _set_selector_events_mask: establece el modo en el que el objeto selector debe escuchar eventos de entrada o salida (r, w o rw)
    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            # modo de evento no válido
            raise ValueError(f"Invalid events mask mode {mode!r}.")
        self.selector.modify(self.sock, events, data=self)

    # _read: 
    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")
    # _write:    
    def _write(self):
        if self._send_buffer:
            print(f"Sending {self._send_buffer!r} to {self.addr}")
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                
    # _json_encode: codifica el objeto obj en formato JSON, y luego lo convierte a bytes utilizando el tipo de codificación especificado por el parámetro encoding
    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    # _create_message: crea un mensaje que contiene el encabezado JSON y los bytes de contenido proporcionados
    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    
    # _create_message: crea un mensaje que contiene el encabezado JSON y los bytes de contenido proporcionados
    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def _process_response_json_content(self):
        content = self.response
        result = content.get("result")
        print(f"Got result: {result}")

    def _process_response_binary_content(self):
        content = self.response
        print(f"Got response: {content!r}")

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.response is None:
                self.process_response()

    def write(self):
        if not self._request_queued:
            self.queue_request()

        self._write()

        if self._request_queued:
            if not self._send_buffer:
                # Set selector to listen for read events, we're done writing.
                self._set_selector_events_mask("r")

    def close(self):
        print(f"Closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"Error: selector.unregister() exception for "
                f"{self.addr}: {e!r}"
            )

        try:
            self.sock.close()
        except OSError as e:
            print(f"Error: socket.close() exception for {self.addr}: {e!r}")
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    # toma el contenido de la solicitud que se ha recibido a través del socket, lo empaqueta en un mensaje para que se pueda 
    # enviar a través de la conexión de socket y lo agrega al búfer de envío
    def queue_request(self):
        # extrae el contenido
        content = self.request["content"]
        # extrae el tipo de contenido
        content_type = self.request["type"]
        # extrae la codificación 
        content_encoding = self.request["encoding"]
        if content_type == "text/json":
            # se crea un diccionario de solicitud (req) que contiene el contenido y los detalles del tipo de contenido y codificación
            req = {
                "content_bytes": self._json_encode(content, content_encoding),
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        else:
            req = {
                "content_bytes": content,
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        
        # Crea el mensaje
        message = self._create_message(**req)
        # se agrega al bufer de envio
        self._send_buffer += message
        self._request_queued = True

    # process_protoheader: procesa el encabezado del protocolo y determina la longitud del encabezado JSON
    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    # process_jsonheader: Procesa el encabezado JSON y verifica que se proporcionen todos los encabezados necesarios
    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f"Missing required header '{reqhdr}'.")

    #  process_response: procesa una respuesta recibida del servidor
    def process_response(self):
        content_len = self.jsonheader["content-length"]
        # Verifica si hay suficientes bytes en el buffer de recepción para procesar el mensaje completo
        if not len(self._recv_buffer) >= content_len:
            return
        # se obtienen los datos del mensaje recibido que se encuentran en el búfer de recepción
        # se comprueba si la longitud del búfer de recepción es mayor o igual que la longitud del contenido del mensaje que se espera recibir (almacenado en la variable content_len). 
        # Si es así, se obtiene una subcadena de longitud content_len desde el inicio del búfer de recepción 
        data = self._recv_buffer[:content_len]
        #  se actualiza el buffer de recepción para eliminar los bytes procesados
        # Esto asegura que el próximo mensaje recibido sea procesado correctamente sin mezclar los bytes del mensaje anterior con los del nuevo.
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            # decodifica los datos en función del tipo de contenido especificado en el encabezado JSON
            self.response = self._json_decode(data, encoding)
            print(f"Received response {self.response!r} from {self.addr}")
            self._process_response_json_content()
        else:
            # Binary or unknown content-type
            self.response = data
            print(
                f"Received {self.jsonheader['content-type']} "
                f"response from {self.addr}"
            )
            self._process_response_binary_content()
        # Close when response has been processed
        self.close()
