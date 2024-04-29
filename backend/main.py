from flask import Flask, Request, jsonify, request, Response
from flask_cors import CORS
import xml.etree.ElementTree as ET
from objects.banco import Banco
from objects.cliente import Cliente
from objects.factura import Factura
from objects.pago import Pago
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString

import os
from db import *
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

#ARREGLOS
ClientesRegistrados = []
NITsRegistrados = []
BancosRegistrados = []
CodigosBanco = []
FacturasRegistradas = []
PagosRegistrados = []

meses_español = {
    'Enero': 'January', 'Febrero': 'February', 'Marzo': 'March', 'Abril': 'April',
    'Mayo': 'May', 'Junio': 'June', 'Julio': 'July', 'Agosto': 'August',
    'Septiembre': 'September', 'Octubre': 'October', 'Noviembre': 'November', 'Diciembre': 'December'
}

def verificar_factura_con_error(factura):
    global ClientesRegistrados
    global NITsRegistrados
 
    if factura.NITcliente not in NITsRegistrados:
        return True
    try:
        valor = float(factura.valor)
        if valor < 0:
            return True
    except ValueError:
        return True
    
    try:
        datetime.strptime(factura.fecha, '%d/%m/%Y')
    except ValueError:
        return True
    
    return False

def obtener_meses_anteriores(fecha, num_meses):
   
    meses = [fecha - timedelta(days=30 * i) for i in range(num_meses)]
    return [(mes.month, mes.year) for mes in meses]

def verificar_pago_con_error(pago):
    global ClientesRegistrados
    global NITsRegistrados
    global CodigosBanco
    if pago.NITcliente not in NITsRegistrados:
        return True
    if pago.codigoBanco not in CodigosBanco:
        return True
    try:
        valor = float(pago.valor)
        if valor < 0:
            return True
    except ValueError:
        return True
    
    try:
        datetime.strptime(pago.fecha, '%d/%m/%Y')
    except ValueError:
        return True
    
    return False


#Leer del xml DB
def agregar_info_clientes(ruta_archivo_clientes):
    global ClientesRegistrados
    global BancosRegistrados
    tree = ET.parse(ruta_archivo_clientes)
    raiz = tree.getroot()
    lista_clientes = raiz.find("clientes")
    lista_bancos = raiz.find("bancos")
    if lista_clientes is not None:
        for cliente in lista_clientes:
            nit = cliente.find("NIT").text.strip()
            nombre = cliente.find("nombre").text.strip()
            nuevo_cliente = Cliente(nombre, nit)
            ClientesRegistrados.append(nuevo_cliente)
    if lista_bancos is not None:
        for banco in lista_bancos:
            codigo = banco.find("codigo").text.strip()
            nombre = banco.find("nombre").text.strip()
            nuevo_banco = Banco(nombre, codigo)
            BancosRegistrados.append(nuevo_banco)
            CodigosBanco.append(nuevo_banco.codigo)

def agregar_info_transacciones(ruta_archivo_transacciones):
    global ClientesRegistrados
    global BancosRegistrados
    global FacturasRegistradas
    global PagosRegistrados
    tree = ET.parse(ruta_archivo_transacciones)
    raiz = tree.getroot()
    lista_pagos = raiz.find("pagos")
    lista_facturas = raiz.find("facturas")
    if lista_facturas is not None:
        for factura in lista_facturas:
            nit = factura.find("NITcliente").text.strip()
            for cliente in ClientesRegistrados:
                if cliente.nit == nit:
                    numeroFactura = factura.find("numeroFactura").text.strip()
                    NITcliente = factura.find("NITcliente").text.strip()
                    fecha = factura.find("fecha").text.strip()
                    valor = factura.find("valor").text.strip()
                    nueva_factura = Factura(numeroFactura, NITcliente, fecha, valor)
                    cliente.transacciones.append(nueva_factura)
                    cliente.saldo-=float(nueva_factura.valor)
                    FacturasRegistradas.append(nueva_factura)
                    break

    if lista_pagos is not None:
        for pago in lista_pagos:
            nit = pago.find("NITcliente").text.strip()
            for cliente in ClientesRegistrados:
                if cliente.nit == nit:
                    codigoBanco = pago.find("codigoBanco").text.strip()
                    fecha = pago.find("fecha").text.strip()
                    NITcliente = pago.find("NITcliente").text.strip()
                    valor = pago.find("valor").text.strip()
                    nuevo_pago = Pago(codigoBanco, fecha, NITcliente, valor)
                    cliente.pagos.append(nuevo_pago)
                    cliente.saldo+=float(nuevo_pago.valor)
                    PagosRegistrados.append(nuevo_pago)
                    break
    


@app.route("/limpiarDatos", methods=["POST"])
def reinicio():
    global ClientesRegistrados
    global BancosRegistrados
    global FacturasRegistradas
    global PagosRegistrados
    ClientesRegistrados = []
    BancosRegistrados = []
    FacturasRegistradas = []
    PagosRegistrados = []
    limpiar_archivo_clientes("backend/db.clientes.xml")
    limpiar_archivo_transacciones("backend/db.transacciones.xml")
    respuesta = {"msg": "Se Reinició la Aplicación correctamente", "status": 200}
    return jsonify(respuesta)


@app.route("/transaccion/guardarTransaccion", methods=["POST"])
def guardar_transaccion():
    global ClientesRegistrados
    global FacturasRegistradas
    global BancosRegistrados
    global PagosRegistrados
    facturasCreadas = []
    facturasDuplicadas = []
    facturasConError = []
    pagosCreados = []
    pagosConError = []
    pagosDuplicados = []
    xml_data = request.data
    try:
        raiz = ET.fromstring(xml_data)
    except ET.ParseError:
        return Response("Error al analizar XML", status=400)
    facturas = raiz.find("facturas")
    pagos = raiz.find("pagos")
    for factura in facturas.findall("factura"):
        factura_duplicada = False
        factura_con_error = False

        numeroFactura = factura.find("numeroFactura").text.strip()
        NITcliente = factura.find("NITcliente").text.strip()
        fecha = factura.find("fecha").text.strip()
        valor = factura.find("valor").text.strip()
        nueva_factura = Factura(numeroFactura, NITcliente, fecha, valor)
        
        factura_con_error = verificar_factura_con_error(nueva_factura)

        for factura in FacturasRegistradas:
            if nueva_factura.numeroFactura == factura.numeroFactura:
                factura_duplicada = True

        for cliente in ClientesRegistrados:
            if cliente.nit == nueva_factura.NITcliente:
                if factura_duplicada is False and factura_con_error is False:
                    cliente.transacciones.append(nueva_factura)
                    cliente.saldo = cliente.saldo - float(valor)
                    facturasCreadas.append(nueva_factura)
                    FacturasRegistradas.append(nueva_factura)
                    agregar_factura_DB(nueva_factura,"backend/db.transacciones.xml")
                    break
                
        if factura_duplicada is True and factura_con_error is False:
                    facturasDuplicadas.append(nueva_factura)
        if factura_con_error is True:
            facturasConError.append(nueva_factura)

    for pago in pagos.findall("pago"):
        pago_duplicado = False
        pago_con_error = False
        codigoBanco = pago.find("codigoBanco").text.strip()
        fecha = pago.find("fecha").text.strip()
        NITcliente = pago.find("NITcliente").text.strip()
        valor = pago.find("valor").text.strip()
        nuevo_pago = Pago(codigoBanco, fecha, NITcliente, valor)

        pago_con_error = verificar_pago_con_error(nuevo_pago)

        for cliente in ClientesRegistrados:
            if cliente.nit == NITcliente:
                for pago in cliente.pagos:
                    if pago.codigoBanco == codigoBanco and pago.fecha == fecha:
                        pago_duplicado = True

        for cliente in ClientesRegistrados:
            if (
                cliente.nit == NITcliente
                and pago_con_error is False
                and pago_duplicado is False
            ):
                cliente.pagos.append(nuevo_pago)
                cliente.saldo = cliente.saldo + float(valor)
                pagosCreados.append(nuevo_pago)
                PagosRegistrados.append(nuevo_pago)
                agregar_pago_DB(nuevo_pago, "backend/db.transacciones.xml")
                break

        if pago_duplicado is True and pago_con_error is False:
            pagosDuplicados.append(nuevo_pago)
            
        if pago_con_error is True:
            pagosConError.append(nuevo_pago)

        

    respuesta = ET.Element("transacciones")
    facturas_xml = ET.SubElement(respuesta, "facturas")
    ET.SubElement(facturas_xml, "nuevasFacturas").text = str(len(facturasCreadas))
    ET.SubElement(facturas_xml, "facturasDuplicadas").text = str(
        len(facturasDuplicadas)
    )
    ET.SubElement(facturas_xml, "facturasConError").text = str(len(facturasConError))
    pagos_xml = ET.SubElement(respuesta, "pagos")
    ET.SubElement(pagos_xml, "nuevosPagos").text = str(len(pagosCreados))
    ET.SubElement(pagos_xml, "pagosDuplicados").text = str(len(pagosDuplicados))
    ET.SubElement(pagos_xml, "pagosConError").text = str(len(pagosConError))
    xml_response = ET.tostring(respuesta, encoding="utf8", method="xml").decode("utf-8")
    return Response(xml_response, mimetype="application/xml")


@app.route("/configuracion/guardarConfiguracion", methods=["POST"])
def guardar_configuracion():
    global ClientesRegistrados
    global BancosRegistrados
    ClientesCreados = []
    ClientesActualizados = []
    BancosCreados = []
    BancosActualizados = []
    contenido = request.data
    try:
        raiz = ET.fromstring(contenido)
    except ET.ParseError:
        return Response("Error al analizar XML", status=400)
    clientes = raiz.find("clientes")
    bancos = raiz.find("bancos")

    for cliente in clientes.findall("cliente"):
        actualizacion_cliente = False
        nit = cliente.find("NIT").text.strip()
        nombre = cliente.find("nombre").text.strip()
        nuevo_cliente = Cliente(nombre, nit)
        for antiguo_cliente in ClientesRegistrados:
            if antiguo_cliente.nit == nuevo_cliente.nit:
                ClientesActualizados.append(nuevo_cliente)
                actualizar_cliente_db("backend/db.clientes.xml", nit, nombre)
                ClientesRegistrados.remove(antiguo_cliente)
                actualizacion_cliente = True
                break
        ClientesRegistrados.append(nuevo_cliente)
        agregar_cliente_DB(nuevo_cliente, "backend/db.clientes.xml")
        NITsRegistrados.append(nuevo_cliente.nit)
        if actualizacion_cliente is False:
            ClientesCreados.append(nuevo_cliente)

    for banco in bancos.findall("banco"):
        actualizacion_banco = False
        codigo = banco.find("codigo").text.strip()
        nombre = banco.find("nombre").text.strip()
        nuevo_banco = Banco(nombre, codigo)
        for antiguo_banco in BancosRegistrados:
            if antiguo_banco.codigo == nuevo_banco.codigo:
                BancosActualizados.append(nuevo_banco)
                actualizar_banco_db("backend/db.clientes.xml", codigo, nombre)
                BancosRegistrados.remove(antiguo_banco)
                actualizacion_banco = True
                break
        BancosRegistrados.append(nuevo_banco)
        CodigosBanco.append(nuevo_banco.codigo)
        agregar_banco_DB(nuevo_banco, "backend/db.clientes.xml")
        if actualizacion_banco is False:
            BancosCreados.append(nuevo_banco)
    respuesta = ET.Element("respuesta")
    clientes_xml = ET.SubElement(respuesta, "clientes")
    ET.SubElement(clientes_xml, "creados").text = str(len(ClientesCreados))
    ET.SubElement(clientes_xml, "actualizados").text = str(len(ClientesActualizados))
    bancos_xml = ET.SubElement(respuesta, "bancos")
    ET.SubElement(bancos_xml, "creados").text = str(len(BancosCreados))
    ET.SubElement(bancos_xml, "actualizados").text = str(len(BancosActualizados))
    xml_response = ET.tostring(respuesta, encoding="utf8", method="xml").decode("utf-8")
    return Response(xml_response, mimetype="application/xml")


@app.route("/estado_cuenta/<nit>", methods=["GET"])
def devolver_estado_cuenta(nit):
    global ClientesRegistrados
    for cliente in ClientesRegistrados:
        if cliente.nit == nit:
            #return jsonify(cliente.parseDiccionario())
            cliente_dict = cliente.parseDiccionario()  # Asegúrate de que este método devuelve un diccionario
            xml = dicttoxml(cliente_dict, custom_root='cliente', attr_type=False)
            xml_pretty = parseString(xml).toprettyxml(indent="  ")
            return app.response_class(xml_pretty, content_type='application/xml')
    respuesta = {"msg": "Cliente no Encontrado", "status_code": 400}
    return jsonify(respuesta)


@app.route("/EstadosCuentas", methods=["GET"])
def devolver_estado_cuentas():
    global ClientesRegistrados
    return jsonify([cliente.parseDiccionario() for cliente in ClientesRegistrados])


@app.route("/estado_cuenta/<nit>/ResumenPago/<fecha>", methods=["GET"])
def devolver_resumen_pagos(fecha, nit):
    global ClientesRegistrados
    fecha_formateada = fecha.replace("-", "/")
    mes, anio = fecha_formateada.split('/')
    fecha_formateada = f"{meses_español[mes]}/{anio}"
    fecha_formateada = datetime.strptime(fecha_formateada, '%B/%Y')
    meses_a_verificar = obtener_meses_anteriores(fecha_formateada, 3)
    pagos_por_mes = {f"{mes}/{anio}": [] for mes, anio in meses_a_verificar}
    try:
        for cliente in ClientesRegistrados:
            if cliente.nit == nit:
                for pago in cliente.pagos:
                    fecha_pago_formateada = datetime.strptime(pago.fecha, '%d/%m/%Y')
                    clave_mes_anio = f"{fecha_pago_formateada.month}/{fecha_pago_formateada.year}"
                    if (fecha_pago_formateada.month, fecha_pago_formateada.year) in meses_a_verificar:
                        pagos_por_mes[clave_mes_anio].append(float(pago.valor))
                totales_por_mes = {mes_anio: sum(montos) if montos else 0 for mes_anio, montos in pagos_por_mes.items()}
        return jsonify(totales_por_mes)
    except ValueError:
        respuesta = {"msg": "El formato de la fecha es Incorrecto tiene que ser: mm/yyyy",
                     "status_code": 400}
        return jsonify(respuesta)


# INICIAR
if __name__ == ("__main__"):
    verificar_y_crear_archivos()
    agregar_info_clientes("backend/db.clientes.xml")
    agregar_info_transacciones("backend/db.transacciones.xml")
    app.run(port=8880, debug=True)
