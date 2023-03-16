El primer paso en un flujo ordinario de trabajo suele ser la consulta de
las nuevas facturas registradas en la plataforma FACe por los
proveedores. Para realizar esta consulta, solo tienes que invocar el
comando `aapp2face facturas nuevas`. Este comando acepta como parámetro
el codigo DIR3 de la oficina contable para la que quieres realizar la
consulta. Si no indicas la oficina contable, el comando devolverá todas
las facturas del RCF.

<div class="termy">

```console
$ aapp2face facturas nuevas

<span style="color:#66D9EF"><b>Número registro:</b></span>    <span style="color:#A6E22E"><b>202001015624</b></span>
<span style="color:#66D9EF"><b>Fecha registro:</b></span>     2023-01-19 10:57:38
<span style="color:#66D9EF"><b>Oficina contable:</b></span>   P00000010
<span style="color:#66D9EF"><b>Órgano gestor:</b></span>      P00000010
<span style="color:#66D9EF"><b>Unidad tramitadora:</b></span> P00000010

<span style="color:#66D9EF"><b>Número registro:</b></span>    <span style="color:#A6E22E"><b>202001017112</b></span>
<span style="color:#66D9EF"><b>Fecha registro:</b></span>     2013-01-20 11:05:51
<span style="color:#66D9EF"><b>Oficina contable:</b></span>   P00000010
<span style="color:#66D9EF"><b>Órgano gestor:</b></span>      P00000010
<span style="color:#66D9EF"><b>Unidad tramitadora:</b></span> P00000010

<span style="color:#A6E22E"><b>2</b></span> nuevas facturas disponibles

```

</div>
