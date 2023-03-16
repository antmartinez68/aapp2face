# Introducción

AAPP2FACe es una librería que permite abstraer los procesos de
comunicación que deben realizar las AAPP para comunicarse con FACe,
dotando a los desarrolladores de una interfaz moderna en Python fácil de
usar. Se trata de liberar al desarrollador de conocer los detalles
subyacentes del proceso y evitar que tengan que lidiar con el protocolo
SOAP y la forma de acceso a este tipo de servicios web, pero sin perder
el control de la granularidad de las operaciones.

Para ello la librería proporciona el conector `FACeSoapClient`, que
facilita el acceso a los métodos SOAP disponibles en el servicio web de
FACe. Esta clase es una implementación de la interfaz `FACeClient` que
asegura el nivel de coherencia y uniformidad requerido por el diseño.

Sin embargo, normalmente no querrás interactuar directamente con estas
clases, sino que lo harás principalmente con la interfaz pública
ofrecida por la clase `FACeConnection`. Esta clase realiza las
conversiones y adaptaciones adecuadas para ofrecer métodos y tipos de
datos al estilo Python.

Para hacer uso de esta clase, durante su creación, será necesario
inyectar a través de su constructor una instancia de `FACeClient` que, a
modo de conector, contiene la configuración de acceso al servicio web.
Puedes verlo en el siguiente ejemplo:

```python
from aapp2face import FACeConnection, FACeSoapClient

cliente = FACeSoapClient(
    "https://se-face-webservice.redsara.es/facturasrcf2?wsdl",
    "cert.pem",
    "key.pem"
)

face = FACeConnection(cliente)
```

En el ejemplo se crea un objeto `FACeSoapClient` al que se le
proporciona la URL del WSDL que describe el servicio web y que en el
ejemplo corresponde con el entorno de pruebas de FACe. Junto a la URL es
necesario facilitar la ruta a los archivos que contienen el certificado
digital y su correspondiente clave privada para firmar las peticiones al
servicio web. Este certificado debe haber sido previamente registrado y
autorizado en FACe para identificar al RCF del Organismo que realiza la
petición.

Posteriormente, se crea un objeto `FACeConnection` inyectando la
instancia de `FACeSoapClient` a través de un argumento del constructor.
A partir de este momento, ya se puede interactuar con instancia de
`FACeConnection` creada.

A continuación se muestra un ejemplo sencillo de un script que consulta
la nuevas facturas disponibles en la plataforma y seguidamente las
descarga. Para cada factura crea un directorio que tiene como nombre el
número de registro de la factura. Dentro del directorio descargará el
archivo principal de la factura electrónica, normalmente un archivo
XSIG, y los anexos que esta pudiera contener, normalmente archivos PDF.

```python
from aapp2face import FACeConnection, FACeSoapClient

cliente = FACeSoapClient(
    "https://se-face-webservice.redsara.es/facturasrcf2?wsdl",
    "cert.pem",
    "key.pem"
)

face = FACeConnection(cliente)

nuevas_facturas = face.solicitar_nuevas_facturas()

for factura in nuevas_facturas:
    print(f"Descargando factura {factura.numero_registro}")
    factura_descargada = face.descargar_factura(factura.numero_registro)

    ruta_descarga = Path.cwd().joinpath(factura.numero_registro)
    ruta_descarga.mkdir()

    factura_descargada.guardar(ruta_descarga)

    for anexo in factura_descargada.anexos:
        anexo.guardar(ruta_descarga)
```
