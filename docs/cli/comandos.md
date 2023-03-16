**Interfaz de línea de comandos AAPP2FACe**

**Uso**:

```console
$ aapp2face [OPCIONES] COMANDO [ARGUMENTOS]...
```

**Opciones**:

* `-c, --config PATH`: Permite indicar un archivo de configuración alternativo.
* `--url-prod TEXT`: URL de ubicación del WSDL para el entorno de producción de FACe.
* `--url-staging TEXT`: URL de ubicación del WSDL para el entorno de pruebas de FACe.
* `-u, --use-staging / -U, --use-prod`: Fuerza el uso del entorno de pruebas en la peticiones a FACe.
* `--cert-file FILE`: Archivo que contiene el certificado para firma peticiones.
* `--key-file FILE`: Archivo que contiene la clave privada del certificado.
* `-d, --download-dir PATH`: Ruta donde se alojarán los archivos descargados.
* `--version`: Muestra la versión de la aplicación y sale.
* `--install-completion`: Instala autocompletado para el shell actual.
* `--show-completion`: Muestra autocompletado para el shell actual, para copiar o personalizar la instalación.
* `--help`: Muestra la ayuda y sale.

**Comandos**:

* `anulaciones`: Gestión de solicitudes de anulación.
* `cesiones`: Gestión de las cesiones de crédito.
* `config`: Muestra los valores de configuración que están siendo aplicados.
* `estados`: Lista los estados que maneja FACe para la gestión de las facturas.
* `facturas`: Gestión de facturas.
* `init`: Genera un archivo de configuración nuevo mediante asistente.
* `unidades`: Lista las relaciones OG-UT-OC asociadas al RCF.

## `aapp2face anulaciones`

Gestión de solicitudes de anulación.

**Uso**:

```console
$ aapp2face anulaciones [OPCIONES] COMANDO [ARGUMENTOS]...
```

**Opciones**:

* `--help`: Muestra la ayuda y sale.

**Comandos**:

* `gestionar`: Gestiona las solicitudes de anulación de...
* `nuevas`: Devuelve las facturas que se encuentran en...

### `aapp2face anulaciones gestionar`

Gestiona las solicitudes de anulación de facturas.

Si se indican varias facturas, todas ellas deben pertenecer a la
misma Oficina Contable. El nuevo estado y comentario facilitados
serán asignados a todas las facturas indicadas. Obsérvese que el
parámetro comentario es obligatorio. Si se desea dejar en blanco se
de indicar explícitamente, por ejemplo, usando comillas ("").

**Uso**:

```console
$ aapp2face anulaciones gestionar [OPCIONES] OFICINA_CONTABLE CODIGO COMENTARIO NUMEROS_REGISTRO...
```

**Argumentos**:

* `OFICINA_CONTABLE`: Código DIR3 de la Oficina Contable.  [required]
* `CODIGO`: Identificador del estado a asignar.  [required]
* `COMENTARIO`: Comentario asociado al cambio de estado.  [required]
* `NUMEROS_REGISTRO...`: Números de registro de las facturas con solicitud de anulación.  [required]

**Opciones**:

* `--help`: Muestra la ayuda y sale.

### `aapp2face anulaciones nuevas`

Devuelve las facturas que se encuentran en estado "solicitada anulación".

Si no se pasa el código de la Oficina Contable, retornará todas las
facturas en este estado del RCF.

El RCF deberá solicitar periódicamente este servicio para conocer
las solicitudes de anulación de facturas recibidas en FACe por parte
de los proveedores.

El resultado está limitado a un máximo de 500 facturas. Las
solicitudes deben ser procesadas para que entren el resto de
solicitudes encoladas.

**Uso**:

```console
$ aapp2face anulaciones nuevas [OPCIONES] [OFICINA_CONTABLE]
```

**Argumentos**:

* `[OFICINA_CONTABLE]`: Código DIR3 de la Oficina Contable.

**Opciones**:

* `-e, --export PATH`: Exporta la salida a un archivo CSV.
* `--help`: Muestra la ayuda y sale.

## `aapp2face cesiones`

Gestión de las cesiones de crédito.

**Uso**:

```console
$ aapp2face cesiones [OPCIONES] COMANDO [ARGUMENTOS]...
```

**Opciones**:

* `--help`: Muestra la ayuda y sale.

**Comandos**:

* `consultar`: Consulta el estado de la cesión de una...
* `documento`: Obtiene el documento de la cesión.
* `gestionar`: Gestiona la cesión de crédito de una factura.

### `aapp2face cesiones consultar`

Consulta el estado de la cesión de una factura.

Consulta el estado de la cesión de una factura cuyo identificador
es facilitado.

**Uso**:

```console
$ aapp2face cesiones consultar [OPCIONES] NUMERO_REGISTRO
```

**Argumentos**:

* `NUMERO_REGISTRO`: Número de registro de la facturas a consultar.  [required]

**Opciones**:

* `--help`: Muestra la ayuda y sale.

### `aapp2face cesiones documento`

Obtiene el documento de la cesión.

Obtiene el documento de la cesión conectando al servicio de notarios.

**Uso**:

```console
$ aapp2face cesiones documento [OPCIONES] CSV REPOSITORIO NIF NOMBRE APELLIDOS
```

**Argumentos**:

* `CSV`: CSV del documento a obtener.  [required]
* `REPOSITORIO`: Repositorio desde el que se obtiene el documento.  [required]
* `NIF`: NIF del solicitante.  [required]
* `NOMBRE`: Nombre del solicitante.  [required]
* `APELLIDOS`: Apellidos del solicitante.  [required]

**Opciones**:

* `-f, --force`: Sobrescribe los archivos de factura o anexos si existen.
* `--help`: Muestra la ayuda y sale.

### `aapp2face cesiones gestionar`

Gestiona la cesión de crédito de una factura.

Obsérvese que el parámetro comentario es obligatorio. Si se desea
dejar en blanco se de indicar explícitamente, por ejemplo, usando
comillas ("").

**Uso**:

```console
$ aapp2face cesiones gestionar [OPCIONES] CODIGO COMENTARIO NUMERO_REGISTRO
```

**Argumentos**:

* `CODIGO`: Identificador del estado a asignar.  [required]
* `COMENTARIO`: Comentario asociado al cambio de estado.  [required]
* `NUMERO_REGISTRO`: Números de registro de la factura de la cesión.  [required]

**Opciones**:

* `--help`: Muestra la ayuda y sale.

## `aapp2face config`

Muestra los valores de configuración que están siendo aplicados.

**Uso**:

```console
$ aapp2face config [OPCIONES]
```

**Opciones**:

* `--help`: Muestra la ayuda y sale.

## `aapp2face estados`

Lista los estados que maneja FACe para la gestión de las facturas.

Existen dos flujos principales, el ordinario y el de anulación. El
flujo ordinario corresponde al ciclo de vida de la factura, y el
flujo de anulación corresponde al ciclo de solicitud de anulación.

**Uso**:

```console
$ aapp2face estados [OPCIONES]
```

**Opciones**:

* `-e, --export PATH`: Exporta la salida a un archivo CSV.
* `--help`: Muestra la ayuda y sale.

## `aapp2face facturas`

Gestión de facturas.

**Uso**:

```console
$ aapp2face facturas [OPCIONES] COMANDO [ARGUMENTOS]...
```

**Opciones**:

* `--help`: Muestra la ayuda y sale.

**Comandos**:

* `confirmar`: Confirma la descarga de una factura.
* `consultar`: Consulta el estado de facturas.
* `crcf`: Cambia el código RCF asginado a una factura.
* `descargar`: Descarga facturas.
* `estado`: Cambia el estado de las facturas.
* `nuevas`: Devuelve las nuevas facturas registradas...
* `rcf`: Consulta el código RCF de una factura.

### `aapp2face facturas confirmar`

Confirma la descarga de una factura.

Tras la descarga de una factura debe utilizarse este comando para
confirmar que el proceso de descarga se ha realizado con éxito, de
forma que la plataforma FACe pueda realizar todas las acciones
relacionadas con la descarga de la factura por parte del RCF.

Tras confirmar la descarga de una factura, su estado queda
actualizado automáticamente a 1300.

**Uso**:

```console
$ aapp2face facturas confirmar [OPCIONES] OFICINA_CONTABLE NUMERO_REGISTRO CODIGO_RCF
```

**Argumentos**:

* `OFICINA_CONTABLE`: Código DIR3 de la Oficina Contable.  [required]
* `NUMERO_REGISTRO`: Número de registro de la factura a confirmar.  [required]
* `CODIGO_RCF`: Código RCF que se asignará a la factura.  [required]

**Opciones**:

* `--help`: Muestra la ayuda y sale.

### `aapp2face facturas consultar`

Consulta el estado de facturas.

Consulta el estado de las facturas cuyos identificadores son
facilitados.

**Uso**:

```console
$ aapp2face facturas consultar [OPCIONES] NUMEROS_REGISTRO...
```

**Argumentos**:

* `NUMEROS_REGISTRO...`: Números de registro de las facturas a consultar.  [required]

**Opciones**:

* `-e, --export PATH`: Exporta la salida a un archivo CSV.
* `--help`: Muestra la ayuda y sale.

### `aapp2face facturas crcf`

Cambia el código RCF asginado a una factura.

Asigna el código RCF facilitado a la factura con el número de
registro indicado.

**Uso**:

```console
$ aapp2face facturas crcf [OPCIONES] NUMERO_REGISTRO CODIGO_RCF
```

**Argumentos**:

* `NUMERO_REGISTRO`: Número de registro de la factura a actualizar.  [required]
* `CODIGO_RCF`: Código RCF que se asignará a la factura.  [required]

**Opciones**:

* `--help`: Muestra la ayuda y sale.

### `aapp2face facturas descargar`

Descarga facturas.

Descarga las facturas correspondientes a los indentificadores
facilitados. Si no se facilita ninguno se descargarán todas las
facturas nuevas del RCF.

En el directorio destino determinado por la configuración será
creado un nuevo directorio por cada fatura usando como nombre el
número de registro de esta y en él se descargarán tanto el archivo
de la factura como los archivos de los correspondientes anexos si
los tuviera.

**Uso**:

```console
$ aapp2face facturas descargar [OPCIONES] [NUMEROS_REGISTRO]...
```

**Argumentos**:

* `[NUMEROS_REGISTRO]...`: Números de registro de las facturas a descargar.

**Opciones**:

* `-f, --force`: Sobrescribe los archivos de factura o anexos si existen.
* `-e, --export PATH`: Exporta la salida a un archivo CSV.
* `--help`: Muestra la ayuda y sale.

### `aapp2face facturas estado`

Cambia el estado de las facturas.

Si se indican varias facturas, todas ellas deben pertenecer a la
misma Oficina Contable. El nuevo estado y comentario facilitados
serán asignados a todas las facturas indicadas. Obsérvese que el
parámetro comentario es obligatorio. Si se desea dejar en blanco se
de indicar explícitamente, por ejemplo, usando comillas ("").

Los estados 1300 y 3100 no pueden ser asignados mediante este
comando ya que estos estados son asignados de forma automática al
realizar las operaciones de confirmación de descarga de una factura
y gestión de la solicitud de anulación respectivamente. El estado
inicial 1200 tampoco es gestionable mediante este comando.

**Uso**:

```console
$ aapp2face facturas estado [OPCIONES] OFICINA_CONTABLE CODIGO COMENTARIO NUMEROS_REGISTRO...
```

**Argumentos**:

* `OFICINA_CONTABLE`: Código DIR3 de la Oficina Contable.  [required]
* `CODIGO`: Identificador del estado a asignar.  [required]
* `COMENTARIO`: Comentario asociado al cambio de estado.  [required]
* `NUMEROS_REGISTRO...`: Números de registro de las facturas a cambiar estado.  [required]

**Opciones**:

* `--help`: Muestra la ayuda y sale.

### `aapp2face facturas nuevas`

Devuelve las nuevas facturas registradas en FACe.

Consulta las facturas que se encuentran en el estado "registrada".
Periódicamente se deberá utilizar este comando para obtener las
facturas que posteriormente deberán ser recuperadas.

El resultado está limitado por el servicio de FACe a un máximo de
500 facturas. Se deben procesar las facturas para que entren el
resto de facturas encoladas.

**Uso**:

```console
$ aapp2face facturas nuevas [OPCIONES] [OFICINA_CONTABLE]
```

**Argumentos**:

* `[OFICINA_CONTABLE]`: Código DIR3 de la Oficina Contable.

**Opciones**:

* `-e, --export PATH`: Exporta la salida a un archivo CSV.
* `--help`: Muestra la ayuda y sale.

### `aapp2face facturas rcf`

Consulta el código RCF de una factura.

Consulta el código RCF asignado a una factura cuyo indentificador es
facilitado.

**Uso**:

```console
$ aapp2face facturas rcf [OPCIONES] NUMERO_REGISTRO
```

**Argumentos**:

* `NUMERO_REGISTRO`: Número de registro de la facturas a consultar.  [required]

**Opciones**:

* `--help`: Muestra la ayuda y sale.

## `aapp2face init`

Genera un archivo de configuración nuevo mediante asistente.

**Uso**:

```console
$ aapp2face init [OPCIONES]
```

**Opciones**:

* `--help`: Muestra la ayuda y sale.

## `aapp2face unidades`

Lista las relaciones OG-UT-OC asociadas al RCF.

Las relaciones OG-UT-OC obtenidas son las asociadas al RCF que firma
la petición.

**Uso**:

```console
$ aapp2face unidades [OPCIONES]
```

**Opciones**:

* `-e, --export PATH`: Exporta la salida a un archivo CSV.
* `--help`: Muestra la ayuda y sale.
