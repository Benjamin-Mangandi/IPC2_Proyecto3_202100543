from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import xml.etree.ElementTree as ET
import requests
from django.views.decorators.csrf import csrf_exempt
from xml.dom.minidom import parseString


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
            cliente = response.json()
            return render(request, 'ITGSA/estado_cuenta.html', {'cliente': cliente})
        else:
            return HttpResponse("Cliente no encontrado", status=404)
    else:
        return render(request, 'ITGSA/clientes.html')

@csrf_exempt
def guardar_configuracion(request):
    if request.method == 'POST':
        archivo = request.FILES['Archivo_configuracion']
         # Enviar la solicitud al backend con el contenido del archivo
        flask_endpoint = 'http://localhost:8880/configuracion/guardarConfiguracion'
        response = requests.post(flask_endpoint, data=archivo.read(), headers={'Content-Type': 'text/xml'})
        parseado_string = parseString(response.content)
        xml_formateado = parseado_string.toprettyxml(indent= "        ")
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
        xml_formateado = parseado_string.toprettyxml(indent= "        ")
        return render(request,'ITGSA/transaccion.html',{
            "respuesta_xml": xml_formateado
        } )
    else:
        # Método no permitido
        return JsonResponse({'error': 'Método no permitido', 'status': 405})