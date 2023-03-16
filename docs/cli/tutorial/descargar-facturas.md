Con la consulta de las nuevas facturas registradas en la plataforma
FACe, hemos obtenido sus números de registro. Ahora solo tienes que
invocar al comando `aapp2face facturas descargar` seguido de los números
de registro de las facturas que quieres descargar para que esta se
inicie.

En el directorio de descargas que hayas configurado se creará, por cada
factura, un directorio que tiene por nombre el número de registro de la
factura. Dentro de cada directorio, serán descargados los archivos XSIG
de las facturas electrónicas en formato *Factuae* y los anexos (por
ejemplo, archivos PDF) que puedieran acompañar a estas.

<div class="termy">

```console
$ aapp2face facturas descargar 2020FA00044914 2020FA00052749
<span style="color:#66D9EF"><b>Núm. Registro:</b></span> <span style="color:#A6E22E"><b>202001015624</b></span>
<span style="color:#66D9EF"><b>Núm. Factura:</b></span>  2020FA00044914
<span style="color:#66D9EF"><b>Serie:</b></span>         None
<span style="color:#66D9EF"><b>Importe:</b></span>       39.87
<span style="color:#66D9EF"><b>Proveedor:</b></span>     ESA88888888
<span style="color:#66D9EF"><b>Archivo:</b></span>       AGE_2062644_000053.F20200521.xsig
<span style="color:#66D9EF"><b>Anexos:</b></span>

<span style="color:#66D9EF"><b>Núm. Registro:</b></span> <span style="color:#A6E22E"><b>202001017112</b></span>
<span style="color:#66D9EF"><b>Núm. Factura:</b></span>  2020FA00052749
<span style="color:#66D9EF"><b>Serie:</b></span>         None
<span style="color:#66D9EF"><b>Importe:</b></span>       2601.25
<span style="color:#66D9EF"><b>Proveedor:</b></span>     ESA99999999
<span style="color:#66D9EF"><b>Archivo:</b></span>       AGE_2064077_000182.F20200526.xsig
<span style="color:#66D9EF"><b>Anexos:</b></span>

<span style="color:#A6E22E"><b>2</b></span> facturas descargadas
```

</div>

El siguiente paso es verificar las facturas y confirmar a FACe que el
proceso se ha realizado correctamente. Hasta que no confirmes a FACe la
descarga de las facturas, estas mantendrán en la plataforma el estado
"Registrada" (1200) y seguirán disponibles para que realices nuevos
intentos de descarga.

Puedes comprobar el estado de las facturas haciendo uso del comando
`aapp2face facturas consultar`. Con el siguiente ejemplo podrás observar
que, aunque se han descargado las facturas, estas mantienen el estado
"Registada" (1200) en la plataforma.

<div class="termy">

```console
$ aapp2face facturas consultar 2020FA00044914 2020FA00052749
<span style="color:#66D9EF"><b>Número registro:</b></span> <span style="color:#A6E22E"><b>202001015624</b></span>
<span style="color:#66D9EF"><b>Tramitación:</b></span>
<span style="color:#66D9EF"><b>  Código:</b></span>        1200
<span style="color:#66D9EF"><b>  Descripción:</b></span>   La factura ha sido registrada en el registro electrónico REC
<span style="color:#66D9EF"><b>  Motivo:</b></span>
<span style="color:#66D9EF"><b>Anulación:</b></span>
<span style="color:#66D9EF"><b>  Código:</b></span>        4100
<span style="color:#66D9EF"><b>  Descripción:</b></span>   No solicitada anulación
<span style="color:#66D9EF"><b>  Motivo:</b></span>

<span style="color:#66D9EF"><b>Número registro:</b></span> <span style="color:#A6E22E"><b>202001017112</b></span>
<span style="color:#66D9EF"><b>Tramitación:</b></span>
<span style="color:#66D9EF"><b>  Código:</b></span>        1200
<span style="color:#66D9EF"><b>  Descripción:</b></span>   La factura ha sido registrada en el registro electrónico REC
<span style="color:#66D9EF"><b>  Motivo:</b></span>
<span style="color:#66D9EF"><b>Anulación:</b></span>
<span style="color:#66D9EF"><b>  Código:</b></span>        4100
<span style="color:#66D9EF"><b>  Descripción:</b></span>   No solicitada anulación
<span style="color:#66D9EF"><b>  Motivo:</b></span>
```
</div>
