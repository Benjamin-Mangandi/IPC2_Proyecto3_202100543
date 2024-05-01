from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import xml.etree.ElementTree as ET
import json

import requests
from django.views.decorators.csrf import csrf_exempt
from xml.dom.minidom import parseString
from django.core.serializers.json import DjangoJSONEncoder

def home(request):
    return render(request, 'ITGSA/menu_principal.html')

@csrf_exempt
def configuracion(request):
    return render(request, 'ITGSA/configuracion.html')

@csrf_exempt
def transaccion(request):
    return render(request, 'ITGSA/transaccion.html')

@csrf_exempt
def clientes(request):
    return render(request, 'ITGSA/clientes.html')

@csrf_exempt
def ayuda(request):
    return render(request, 'ITGSA/ayuda.html')


@csrf_exempt
def reiniciar_datos(request):
    if request.method == 'POST':
        flask_endpoint = 'http://localhost:8880/limpiarDatos'
        response = requests.post(flask_endpoint)
        return render(request, 'ITGSA/datos_borrados.html')
    else:
        # Método no permitido
        return JsonResponse({'error': 'Método no permitido', 'status': 405})
    
@csrf_exempt
def estado_cuenta(request):
    cliente_nit = request.GET.get('NIT', None)
    if cliente_nit:
        response = requests.get(f'http://localhost:8880/estado_cuenta/{cliente_nit}')
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.content)
            except:
                return render(request, 'ITGSA/cliente_inexistente.html')
            if root.tag == 'error':
                return render(request, 'ITGSA/cliente_inexistente.html')
            else:
                cliente = {child.tag: child.text if child.tag not in ['transacciones', 'pagos'] else
                               [{subchild.tag: subchild.text for subchild in child} for child in child.findall('item')]
                               for child in root}
                return render(request, 'ITGSA/estado_cuenta.html', {'cliente': cliente})
        elif response.status_code == 400:
            return render(request, 'ITGSA/cliente_inexistente.html')
    else:
        return render(request, 'ITGSA/clientes.html')
    
def EstadosCuenta(request):
    if request.method == 'GET':
        response = requests.get('http://localhost:8880/EstadosCuentas')
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.content)
            except Exception as e:
                return JsonResponse({'error': str(e), 'status': 500})
            Clientes = []
            for item in root.findall('item'):
                cliente_dict = {
                    'nit': item.find('nit').text,
                    'nombre': item.find('nombre').text,
                    'saldo': item.find('saldo').text,
                    'transacciones': [{
                        'numeroFactura': transaccion.find('numeroFactura').text,
                        'NITcliente': transaccion.find('NITcliente').text,
                        'fecha': transaccion.find('fecha').text,
                        'valor': transaccion.find('valor').text
                    } for transaccion in item.find('transacciones')],
                    'pagos': [{
                        'codigoBanco': pago.find('codigoBanco').text,
                        'fecha': pago.find('fecha').text,
                        'NITcliente': pago.find('NITcliente').text,
                        'valor': pago.find('valor').text
                    } for pago in item.find('pagos')]
                }
                Clientes.append(cliente_dict)
            return render(request, 'ITGSA/EstadosCuenta.html', {'Clientes': Clientes})
        else:
            return JsonResponse({'error': 'Error al obtener los estados de cuenta', 'status': response.status_code})
    else:
        return JsonResponse({'error': 'Método no permitido', 'status': 405})
    


@csrf_exempt
def guardar_configuracion(request):
    if request.method == 'POST':
        archivo = request.FILES['Archivo_configuracion']
         # Enviar la solicitud al backend con el contenido del archivo
        flask_endpoint = 'http://localhost:8880/configuracion/guardarConfiguracion'
        response = requests.post(flask_endpoint, data=archivo.read(), headers={'Content-Type': 'text/xml'})
        parseado_string = parseString(response.content)
        xml_formateado = parseado_string.toprettyxml(indent= "      ")
        return render(request,'ITGSA/configuracion.html',{
            "respuesta_xml": xml_formateado
        } )
    else:
        # Método no permitido
        return JsonResponse({'error': 'Método no permitido', 'status': 405})
    
@csrf_exempt
def guardar_transaccion(request):
    if request.method == 'POST':
        archivo = request.FILES['Archivo_transaccion']
         # Enviar la solicitud al backend con el contenido del archivo
        flask_endpoint = 'http://localhost:8880/transaccion/guardarTransaccion'
        response = requests.post(flask_endpoint, data=archivo.read(), headers={'Content-Type': 'text/xml'})
        parseado_string = parseString(response.content)
        xml_formateado = parseado_string.toprettyxml(indent= "      ")
        return render(request,'ITGSA/transaccion.html',{
            "respuesta_xml": xml_formateado
        } )
    else:
        # Método no permitido
        return JsonResponse({'error': 'Método no permitido', 'status': 405})
    

@csrf_exempt
def ResumenPagos(request):
    if request.method == 'GET':
        fecha = request.GET.get('MES', None)
        fecha_formateada = fecha.replace("/","-")
        response = requests.get(f"http://localhost:8880/estado_cuenta/ResumenPagos/{fecha_formateada}")
        if response.status_code ==400:
            return render(request, 'ITGSA/error_fecha.html', {
                        'message': 'Respuesta inválida desde el servidor.'
                        })
        try:
            xml_data = response.text 
            root = ET.fromstring(xml_data)
            datos_pagos = {}
            for mes in root.findall('mes'):
               nombre_mes = mes.get('name')
               bancos = {}
               for banco in mes.findall('banco'):
                codigo_banco = banco.get('codigo')
                valor = float(banco.text)
                bancos[codigo_banco] = valor
                datos_pagos[nombre_mes] = bancos
            meses = list(datos_pagos.keys())
            bancos = set(banco for data in datos_pagos.values() for banco in data)
            datos_chart = {
            banco: [datos_pagos.get(mes, {}).get(banco, 0) for mes in meses] for banco in bancos}
            return render(request, 'ITGSA/resumen_pago.html', {
                'meses': json.dumps(meses),
                'datos_chart': json.dumps(datos_chart),
                'bancos': json.dumps(list(bancos))
                })
        except:
            return render(request, 'ITGSA/error_fecha.html', {
                        'message': 'Respuesta inválida desde el servidor.'
                        })