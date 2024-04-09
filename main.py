from flask import Flask, Request, jsonify, request, Response
from flask_cors import CORS
import xml.etree.ElementTree as ET
from banco import Banco
from cliente import Cliente
from factura import Factura
from pago import Pago

app = Flask(__name__)
CORS(app)

ClientesRegistrados = []
BancosRegistrados = []


@app.route('/')
def inicio():
    return 'Menu principal'

@app.route('/limpiarDatos', methods=["POST"])
def reinicio():
    global ClientesRegistrados
    global BancosRegistrados
    ClientesRegistrados = []
    BancosRegistrados = []
    respuesta={
        "msg": "Se Reinició la Aplicación correctamente",
        "status": 200
    }
    return jsonify(respuesta)

@app.route('/guardarTransaccion', methods=["POST"])
def guardar_transaccion():
    global ClientesRegistrados
    xml_data = request.data
    try:
        raiz = ET.fromstring(xml_data)
    except ET.ParseError:
        return Response("Error al analizar XML", status=400)
    facturas = raiz.find('facturas')
    pagos = raiz.find('pagos')
    for factura in facturas.findall('factura'):
        numeroFactura = factura.find('numeroFactura').text.strip()
        NITcliente = factura.find('NITcliente').text.strip()
        fecha = factura.find('fecha').text.strip()
        valor = factura.find('valor').text.strip()
        nueva_factura = Factura(numeroFactura, NITcliente, fecha, valor)
        for cliente in ClientesRegistrados:
            if cliente.nit == NITcliente:
                cliente.transacciones.append(nueva_factura)

    for pago in pagos.findall('pago'):
        codigoBanco = pago.find('codigoBanco').text.strip()
        fecha = pago.find('fecha').text.strip()
        NITcliente = pago.find('NITcliente').text.strip()
        valor = pago.find('valor').text.strip()
        nuevo_pago = Pago(codigoBanco,fecha,NITcliente, valor)
        for cliente in ClientesRegistrados:
            if cliente.nit == NITcliente:
                cliente.pagos.append(nuevo_pago)
    respuesta = ET.Element('transacciones')
    facturas_xml = ET.SubElement(respuesta, 'facturas')
    ET.SubElement(facturas_xml, 'nuevasFacturas').text = str(0)
    ET.SubElement(facturas_xml, 'facturasDuplicadas').text = str(0)
    ET.SubElement(facturas_xml, 'facturasConError').text = str(0)
    pagos_xml = ET.SubElement(respuesta, 'pagos')
    ET.SubElement(pagos_xml, 'nuevosPagos').text = str(0)
    ET.SubElement(pagos_xml, 'pagosDuplicados').text = str(0)
    ET.SubElement(pagos_xml, 'pagosConError').text = str(0)
    xml_response = ET.tostring(respuesta, encoding='utf8', method='xml').decode('utf-8')
    return Response(xml_response, mimetype='application/xml')

@app.route('/guardarConfiguracion', methods=["POST"])
def guardar_configuracion():
    global ClientesRegistrados
    global BancosRegistrados
    ClientesCreados = []
    ClientesActualizados = []
    BancosCreados = []
    BancosActualizados = []
    xml_data = request.data
    try:
        raiz = ET.fromstring(xml_data)
    except ET.ParseError:
        return Response("Error al analizar XML", status=400)
    clientes = raiz.find('clientes')
    bancos = raiz.find('bancos')
    for cliente in clientes.findall('cliente'):
        actualizacion_cliente = False
        nit = cliente.find('NIT').text.strip()
        nombre = cliente.find('nombre').text.strip()
        nuevo_cliente = Cliente(nombre,nit)
        for antiguo_cliente in ClientesRegistrados:
            if antiguo_cliente.nit == nuevo_cliente.nit:
                ClientesActualizados.append(nuevo_cliente)
                ClientesRegistrados.remove(antiguo_cliente)
                actualizacion_cliente = True
                break
        ClientesRegistrados.append(nuevo_cliente)
        if actualizacion_cliente is False:
            ClientesCreados.append(nuevo_cliente)
    for banco in bancos.findall('banco'):
        actualizacion_banco = False
        codigo = banco.find('codigo').text.strip()
        nombre = banco.find('nombre').text.strip()
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
    respuesta = ET.Element('respuesta')
    clientes_xml = ET.SubElement(respuesta, 'clientes')
    ET.SubElement(clientes_xml, 'creados').text = str(len(ClientesCreados))
    ET.SubElement(clientes_xml, 'actualizados').text = str(len(ClientesActualizados))
    bancos_xml = ET.SubElement(respuesta, 'bancos')
    ET.SubElement(bancos_xml, 'creados').text = str(len(BancosCreados))
    ET.SubElement(bancos_xml, 'actualizados').text = str(len(BancosActualizados))
    xml_response = ET.tostring(respuesta, encoding='utf8', method='xml').decode('utf-8')
    return Response(xml_response, mimetype='application/xml')

@app.route('/devolverEstadoCuenta', methods=["GET"])
def devolver_estado_cuenta():
    respuesta={
        "msg": "Devuelto",
        "status": 200
    }
    return jsonify(respuesta)


@app.route('/devolverResumenPagos', methods=["GET"])
def devolver_resumen_pagos():
    respuesta={
        "msg": "Devuelto",
        "status": 200
    }
    return jsonify(respuesta)

#INICIAR
if __name__ == ('__main__'):
    app.run(port=8880, debug=True)