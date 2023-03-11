# Instrucciones

Este juego de pruebas puede usarse en el modo simulación de AAPP2FACe.
Consiste en una colección de respuestas de datos equivalentes a las que
retornaría el servicio web de FACe. Pueden ser usadas directamente o
como base para crear otras respuestas.

Más abajo se detallan los archivos que contiene este juego de pruebas y
los comandos de ejemplo que pueden invocarse con ellas. Obsérvese que en
los ejemplo se usa la opción general `-f`, por lo que es necesario
configurar la ubicación del juego de pruebas en el archivo de
configuración. Otra alternativa es usar `--fake-set DIRECTORIO` en cada
invocación, para indicar la ubicación donde se ha copiado el juego de
pruebas.

Resumen de los comandos que pueden invocarse con este juego de pruebas
son:

```shell
$ aapp2face -f unidades
$ aapp2face -f estados
$ aapp2face -f facturas nuevas
$ aapp2face -f facturas nuevas P99999999
$ aapp2face -f facturas descargar 202001020718
$ aapp2face -f facturas descargar 202001020719
$ aapp2face -f facturas descargar 1111
$ aapp2face -f facturas confirmar P00000010 202001020718 RCF1234
$ aapp2face -f facturas consultar 202001020718 9999
$ aapp2face -f facturas estado P00000010 1300 "Comentario" 202001020718 202001017112 9999
$ aapp2face -f facturas crcf 202001020718 1200
$ aapp2face -f facturas rcf 202001017112
$ aapp2face -f facturas rcf 202001020718
$ aapp2face -f anulaciones nuevas
$ aapp2face -f anulaciones nuevas P99999999
$ aapp2face -f anulaciones gestionar P00000010 4300 "" 202001029111 202001019122 9999
$ aapp2face -f cesiones consultar 202001020718
$ aapp2face -f cesiones consultar 202001020719
$ aapp2face -f cesiones documento CSV1 CGN 99999999R NOMBRE APELLIDOS
$ aapp2face -f cesiones documento CSV2 CGN 99999999R NOMBRE APELLIDOS
$ aapp2face -f cesiones cesiones gestionar 6200 "" 202001020718
$ aapp2face -f cesiones cesiones gestionar 6200 "" 202001020719
```


### Archivo `consultarUnidades.json`

Respuesta a consulta de las relaciones vinculadas al RCF.

```shell
$ aapp2face -f unidades
```


### Archivo `consultarEstados.json`

Respuesta a consulta de los códigos y descripción de los estados que
maneja FACe.

```shell
$ aapp2face -f estados
```


### Archivo `solicitarNuevasFacturas.json`

Respuesta a petición de nuevas facturas registradas en la plataforma.

```shell
$ aapp2face -f facturas nuevas
```


### Archivo `solicitarNuevasFacturas.P99999999.json`

Respuesta a petición de nuevas facturas registradas en la plataforma
para una oficina contable no existente.

```shell
$ aapp2face -f facturas nuevas P99999999
```


### Archivo `descargarFactura.202001020718.json`

Respuesta a petición de descarga de una factura con número de registro
202001020718 que contiene el archivo XSIG y un anexo PDF incorporado.
Por tanto, se generarán en el directorio de descargas.

```shell
$ aapp2face -f facturas descargar 202001020718
```


### Archivo `descargarFactura.202001020719.json`

Respuesta a petición de descarga de una factura con número de registro
202001020719 que no contiene archivos incorporados. Sólo mostrará el
listado.

```shell
$ aapp2face -f facturas descargar 202001020719
```


### Archivo `descargarFactura.1111.json`

Respuesta a intento de descarga de una factura ya descargada
anteriormente que tiene por número de registro 1111.

```shell
$ aapp2face -f facturas descargar 1111
```


### Archivo `confirmarDescargaFactura.P00000010.202001020718.json`

Respuesta a confirmación de la descarga de una factúra correspondiente a
la oficina contable P00000010 y número de registro 202001020718.

```shell
$ aapp2face -f facturas confirmar P00000010 202001020718 RCF1234
```


### Archivo `consultarListadoFacturas.202001020718.9999.json`

Respuesta a consulta del estado de varias facturas con números de
registro 202001020718 y 9999, siendo este último correspondiente a una
factura no existente.

```shell
$ aapp2face -f facturas consultar 202001020718 9999
```


### Archivo `cambiarEstadoListadoFacturas.P00000010.202001020718.202001017112.9999.json`

Respuesta a la solicitud de cambio de estado de las facturas de la
oficina contable P00000010 con números de registro 202001020718,
202001017112 y 9999. En el ejemplo se usa como nuevo código de estado
1300 pero puede usarse cualquier otro.

```shell
$ aapp2face -f facturas estado P00000010 1300 "Comentario" 202001020718 202001017112 9999
```


### Archivo `cambiarCodigoRCF.202001020718.json`

Respuesta a solicitud de cambio del código RCF asignado a la factura con
código de registro 202001020718. En el ejemplo se usa como nuevo código
RCF 1200 pero puede usarse cualquier otro.

```shell
$ aapp2face -f facturas crcf 202001020718 1200
```


### Archivo `consultarCodigoRCF.202001017112.json`

Respuesta a consulta del código RCF registrado en FACe para una factura
que con número de registro 202001017112 no tiene asignado código.

```shell
$ aapp2face -f facturas rcf 202001017112
```


### Archivo `consultarCodigoRCF.202001020718.json`

Respuesta a consulta del código RCF registrado en FACe para la factura
con número de registro 202001020718.

```shell
$ aapp2face -f facturas rcf 202001020718
```


### Archivo `solicitarNuevasAnulaciones.json`

Respuesta a petición de nuevas solicitudes de anulación de facturas
registradas en la plataforma.

```shell
$ aapp2face -f anulaciones nuevas
```


### Archivo `solicitarNuevasAnulaciones.P99999999.json`

Respuesta a petición de nuevas solicitudes de anulación de facturas
registradas en la plataforma indicando una oficina contable no
existente.

```shell
$ aapp2face -f anulaciones nuevas P99999999
```


### Archivo `gestionarSolicitudAnulacionListadoFacturas.P00000010.202001029111.202001019122.9999.json`

Respuesta a petición de gestión de solicitudes de anulación de facturas
de la oficina contable P00000010, registradas en la plataforma con
números de registro 202001029111, 202001019122 y 9999. En el ejemplo se
muestra un estado 4300 de aceptación de la anulación. Cada una de las
facturas representa un ejemplo de factura correcta, una factura con
estado que no permite esta transición y una factura no existente. Las
dobles comillas representan el comentario de la operación, con lo que en
el ejemplo se pretende dejar en blanco.

```shell
$ aapp2face -f anulaciones gestionar P00000010 4300 "" 202001029111 202001019122 9999
```


### Archivo `consultarEstadoCesion.202001020718.json`

Respuesta a petición de consulta del estado de la cesión de crédito de
una factura con número de registro 202001020718.

```shell
$ aapp2face -f cesiones consultar 202001020718
```


### Archivo `consultarEstadoCesion.202001020719.json`

Respuesta a petición de consulta del estado de la cesión de crédito de
una factura con número de registro 202001020719 y que no existe en la
plataforma.

```shell
$ aapp2face -f cesiones consultar 202001020719
```


### Archivo `obtenerDocumentoCesion.CSV1.CGN.99999999R.NOMBRE.APELLIDOS.json`

Respuesta a petición para obtención del documento de cesión de crédito
que tiene CSV1 como código, se encuentra en el repositorio CGN, y los
datos del solicitante son 999999999R, NOMBRE y APELLIDOS. El documento
es generado en el directorio de descargas.

```shell
$ aapp2face -f cesiones documento CSV1 CGN 99999999R NOMBRE APELLIDOS
```


### Archivo `obtenerDocumentoCesion.CSV2.CGN.99999999R.NOMBRE.APELLIDOS.json`

Respuesta a petición para obtención del documento de cesión de crédito
que tiene CSV1 como código, se encuentra en el repositorio CGN, y los
datos del solicitante son 999999999R, NOMBRE y APELLIDOS. Esta petición
simula un error de conexión con el respositorio de documentos.

```shell
$ aapp2face -f cesiones documento CSV2 CGN 99999999R NOMBRE APELLIDOS
```


### Archivo `gestionarCesion.202001020718.json`

Respuesta a petición para gestionar una cesión de crédito de la factura
que tiene como número de registro 202001020718 y que es aceptado
mediante el código 6200. Las dobles comillas indican el comentario de la
aceptación, que en este caso se deja en blanco.

```shell
$ aapp2face -f cesiones cesiones gestionar 6200 "" 202001020718
```


### Archivo `gestionarCesion.202001020719.json`

Respuesta a petición para gestionar una cesión de crédito de la factura
que tiene como número de registro 202001020719 y que es aceptado
mediante el código 6200. Las dobles comillas indican el comentario de la
aceptación, que en este caso se deja en blanco. Esta petición simula el
error producido cuando la factura indicada no existe en la plataforma.

```shell
$ aapp2face -f cesiones cesiones gestionar 6200 "" 202001020719
```
