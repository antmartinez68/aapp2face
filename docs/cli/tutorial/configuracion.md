El primer paso recomendado es la configuración de la interfaz de línea
de comandos para interactuar con FACe. De esta forma evitarás tener que
suministrar los parámetros de configuración cada vez que invoques un
comando.

Puedes crear manualmente el archivo de configuración o usar el comando
`init` para lanzar un asistente que te ayudará en el proceso.

### Configuración manual

Para configurar manualmente la interfaz de línea de comandos de
AAPP2FACe debes crear un archivo de texto llamado `config.ini` en la
siguiente ubicación, dependiendo de tu sistema operativo:

- Linux: `~/.config/aapp2face`
- macOS: `~/Library/Application Support/aapp2face`
- Windows: `C:/Users/<USER>/AppData/Roaming/aapp2face`

El archivo debe tener la siguiente estructura:

```ini
[FACe]
url_prod = https://webservice.face.gob.es/facturasrcf2?wsdl
url_staging = https://se-face-webservice.redsara.es/facturasrcf2?wsdl
use_staging = True

[X509]
cert_file = /home/usuario/face/credenciales/cert.pem
key_file = /home/usuario/face/credenciales/key.pem

[App]
download_dir = /home/usuario/face/descargas

[Debug]
enabled = False
log_dir = /home/usuario/face/logs
```

En la sección `[FACe]` puedes encontrar los siguientes valores:

- `url_prod`: Es la URL del WSDL de FACe para el entorno de producción
  usando codificación RCP-Literal.

- `url_staging`: Es la URL del WSDL de FACe para el entorno de pruebas
  usando codificación RCP-Literal.

- `use_staging`: Si es `True` la peticiones serán enviadas al entorno de
  pruebas. Este es el valor por defecto. Cuando estés preparado para
  usar el entorno de producción, deberás establecer este valor a
  `False`.

En la sección `[X509]` puedes encontrar los siguientes valores:

- `cert_file`: Es la ruta que apunta al certificado digital que será
  usado para firmar las peticiones a FACe. La clave pública de este
  certificado tiene que haber sido comunicada a FACe previamente para su
  autorización.

- `key_file`: Es la ruta que apunta a la clave privada del certificado
  anterior y que permite realizar la firma de las peticiones. La clave
  privada no debe tener contraseña para facilitar un uso ágil desde la
  terminal o en scripts de automatización de tareas. Por tanto, debes
  proveer al archivo de algún sistema de protección a nivel de sistema
  operativo.

En la sección `[App]` puedes encontrar los siguientes valores:

- `download_dir`: Es la ruta donde serán descargados los archivos XSIG
  de las facturas y otros archivos anexos que pudieran contener.

En la sección `[Debug]` puedes encontrar los siguientes valores:

- `enabled`: Permite activar el modo depuración. Su valor por defecto es
  `False` (desactivado). Si se activa con `True`, las peticiones y
  respuestas SOAP, así como las estructuras de datos enviadas y
  recibidas, serán guardas en la ruta indicada con el parámetro
  `log_dir`.

- `log_dir`: Indica la ruta donde serán guardados los archivos de
  registro generados teniendo activo el modo depuración.


### Configuración asistida

Si usas el comando `init`, el programa creará el archivo de
configuración por ti. Solo tienes que responder a una serie de preguntas
confirmando los valores por defecto o usando los valores personalizados
adaptados a tus necesidades:

<div class="termy">

```console
$ aapp2face init
URL Producción FACe [https://webservice.face.gob.es/facturasrcf2?wsdl]: ↩
URL Staging FACe [https://se-face-webservice.redsara.es/facturasrcf2?wsdl]: ↩
¿Usar entorno de pruebas por defecto? [S/n]: ↩
Archivo con el certificado de firma [./cert.pem]: <b>~/face/cert.pem</b>
Archivo con la clave privada del certificado [./key.pem]: <b>~/face/key.pem</b>
Directorio descarga facturas [./descargas]: <b>~/face/descargas</b>
<span style="color:#A6E22E">Archivo de configuración generado!!</span>
```

</div>
