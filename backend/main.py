from flask import Flask, Request, jsonify, request, Response
from flask_cors import CORS
import xml.etree.ElementTree as ET
from objects.banco import Banco
from objects.cliente import Cliente
from objects.factura import Factura
from objects.pago import Pago
import os

app = Flask(__name__)
CORS(app)

ClientesRegistrados = []
BancosRegistrados = []
FacturasRegistradas = []
PagosRegistrados = []



def verificar_y_crear_archivos():
    directorio = './backend'
    archivos = [os.path.join(directorio, "db.clientes.xml"), os.path.join(directorio, "db.transacciones.xml")]

    for archivo in archivos:
        if not os.path.exists(archivo):
            print(f"\nEl archivo {archivo} no existe, creando...")
            root = ET.Element("Base_Datos")
            tree = ET.ElementTree(root)
            if 'clientes' in archivo:
                ET.SubElement(root, 'clientes')
                ET.SubElement(root, 'bancos')
            elif 'transacciones' in archivo:
                ET.SubElement(root, 'facturas')
                ET.SubElement(root, 'pagos')
            tree.write(archivo)
        else:
            tree = ET.parse(archivo)
            root = tree.getroot()
            updated = False
            if 'clientes' in archivo:
                if root.find('clientes') is None:
                    ET.SubElement(root, 'clientes')
                    updated = True
                if root.find('bancos') is None:
                    ET.SubElement(root, 'bancos')
                    updated = True
            elif 'transacciones' in archivo:
                if root.find('facturas') is None:
                    ET.SubElement(root, 'facturas')
                    updated = True
                if root.find('pagos') is None:
                    ET.SubElement(root, 'pagos')
                    updated = True
            if updated:
                tree.write(archivo)

def limpiar_contenido_xml(*nombres_archivos):
    for nombre_archivo in nombres_archivos:
        if os.path.exists(nombre_archivo):
            with open(nombre_archivo, 'w') as file:
                file.write('<?xml version="1.0" encoding="UTF-8"?>\n')


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
    limpiar_contenido_xml("backend/db.clientes.xml","backend/db.transacciones.xml")
    respuesta = {"msg": "Se Reinició la Aplicación correctamente", 
                 "status": 200}
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
        if float(valor) < 0:
            factura_con_error = True

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
                    break
                elif factura_duplicada is True:
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

        if float(valor) < 0:
            pago_con_error = True

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

        if pago_con_error is True:
            pagosConError.append(nuevo_pago)

        if pago_duplicado is True:
            pagosDuplicados.append(nuevo_pago)

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
                ClientesRegistrados.remove(antiguo_cliente)
                actualizacion_cliente = True
                break
        ClientesRegistrados.append(nuevo_cliente)
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
                BancosRegistrados.remove(antiguo_banco)
                actualizacion_banco = True
                break
        BancosRegistrados.append(nuevo_banco)
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
            return jsonify(cliente.parseDiccionario())


@app.route("/EstadosCuentas", methods=["GET"])
def devolver_estado_cuentas():
    global ClientesRegistrados
    return jsonify([cliente.parseDiccionario() for cliente in ClientesRegistrados])


@app.route("/devolverResumenPagos", methods=["GET"])
def devolver_resumen_pagos():
    respuesta = {"msg": "Devuelto", "status": 200}
    return jsonify(respuesta)


# INICIAR
if __name__ == ("__main__"):
    verificar_y_crear_archivos()
    app.run(port=8880, debug=True)
