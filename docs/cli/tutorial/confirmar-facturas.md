Una vez que has realizado la descarga de las facturas y has verificado
que esta se ha realizado correctamente, es necesario comunicarlo a FACe
para que la plataforma realice las operaciones correspondientes. La
confirmación de la descarga de una factura procará que FACe cambie su
estado de forma automática, pasando del estado "Registrada" (1200) a
"Registrada en RCF" (1300). Además, una vez confirmada una factura, esta
dejará de estar disponible para descarga.

Para confirmar la descarga debes invocar el comando `aapp2face facturas
confirmar` por cada una de las facturas. Con este comando debes
facilitar como argumentos el código DIR3 de la oficina contable, el
número de registro de la factura y el código asignado a la factura en el
RCF tras el proceso administrativo correspondiente.

A continuación usaremos un ejemplo de confirmación de la factura con
número de registro 202001020718, correspondiente a la oficina contable
P00000010 e indicaremos que le ha sido asignado, en el RCF, el número de
registro o código RCF123. La respuesta devuelta por la plataforma nos
confirma la identificación de la factura y su cambio al estado
"Registrada en RCF" (1300).

<div class="termy">

```console
$ aapp2face facturas confirmar P00000010 202001020718 RCF123
<span style="color:#66D9EF"><b>Oficina contable:</b></span>   P00000010
<span style="color:#66D9EF"><b>Número de registro:</b></span> 202001020718
<span style="color:#66D9EF"><b>Código de estado:</b></span>   1300
```
</div>
