from flask import Flask, Request, jsonify, request, Response
from flask_cors import CORS
import xml.etree.ElementTree as ET
from banco import Banco
from cliente import Cliente

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
    #datos_transaccion = request.get_json(True)
    root = ET.Element("data")
    ET.SubElement(root, "field1").text = "Valor 1"
    ET.SubElement(root, "field2").text = "Valor 2"
    ET.SubElement(root, "field3").text = "Valor 3"

    # Convertir el elemento XML a una cadena
    xmlstr = ET.tostring(root, encoding='utf8', method='xml')

    # Retornar la respuesta con el contenido XML y el header correcto
    return Response(xmlstr, mimetype='application/xml')

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
    xmlstr = ET.tostring(respuesta, encoding='utf8', method='xml').decode('utf-8')
    xml_response = xmlstr
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