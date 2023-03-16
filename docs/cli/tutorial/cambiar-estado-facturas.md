Con la tramitación de una factura en la unidad correspondiente, está
transitará por diferentes estados que deben ser comunicados a FACe para
que esta información esté disponible para los proveedores.

Cada vez que una factura cambie de estado puedes usar el comando
`aapp2face facturas estado` para comunicar este cambio a FACe.

Para el siguiente ejemplo, imagina que la factura con número de registro
202001020718, correspondiente a la oficina contable P00000010, ha
llegado al final de su tramitación y se ha cursado el pago al proveedor.
Este cambio lo notificaremos a FACe indicando el estado "Pagada" (2500).
Así mismo, es posible facilitar un comentario asociado al cambio de
estado, en el ejemplo, "Orden de pago ejecutada".


<div class="termy">

```console
$ aapp2face facturas estado P00000010 2500 "Orden de pago ejecutada" 202001020718
<span style="color:#66D9EF"><b>Número de registro:</b></span> <span style="color:#A6E22E"><b>202001020718</b></span>
<span style="color:#66D9EF"><b>Código de estado:</b></span>   2500
```
</div>
