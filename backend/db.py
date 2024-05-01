import xml.etree.ElementTree as ET
import os


def verificar_y_crear_archivos():
    directorio = "./backend"
    archivos = [
        os.path.join(directorio, "db.clientes.xml"),
        os.path.join(directorio, "db.transacciones.xml"),
    ]
    for archivo in archivos:
        if not os.path.exists(archivo):
            print(f"\nEl archivo {archivo} no existe, creando...")
            root = ET.Element("Base_Datos")
            tree = ET.ElementTree(root)
            if "clientes" in archivo:
                ET.SubElement(root, "clientes")
                ET.SubElement(root, "bancos")
            elif "transacciones" in archivo:
                ET.SubElement(root, "facturas")
                ET.SubElement(root, "pagos")
            tree.write(archivo)
        else:
            tree = ET.parse(archivo)
            root = tree.getroot()
            updated = False
            if "clientes" in archivo:
                if root.find("clientes") is None:
                    ET.SubElement(root, "clientes")
                    updated = True
                if root.find("bancos") is None:
                    ET.SubElement(root, "bancos")
                    updated = True
            elif "transacciones" in archivo:
                if root.find("facturas") is None:
                    ET.SubElement(root, "facturas")
                    updated = True
                if root.find("pagos") is None:
                    ET.SubElement(root, "pagos")
                    updated = True
            if updated:
                tree.write(archivo)


def limpiar_archivo_clientes(ruta_archivo):
    tree = ET.parse(ruta_archivo)
    root = tree.getroot()

    for clientes in root.findall("clientes"):
        for cliente in list(clientes):
            clientes.remove(cliente)

    for bancos in root.findall("bancos"):
        for banco in list(bancos):
            bancos.remove(banco)

    tree.write(ruta_archivo, encoding="utf-8", xml_declaration=True)


def limpiar_archivo_transacciones(ruta_archivo):
    tree = ET.parse(ruta_archivo)
    root = tree.getroot()

    for facturas in root.findall("facturas"):
        for factura in list(facturas):
            facturas.remove(factura)

    for pagos in root.findall("pagos"):
        for pago in list(pagos):
            pagos.remove(pago)

    tree.write(ruta_archivo, encoding="utf-8", xml_declaration=True)


def agregar_cliente_DB(cliente, ruta_archivo):
    tree = ET.parse(ruta_archivo)
    root = tree.getroot()

    clientes = root.find("clientes")

    cliente_element = ET.SubElement(clientes, "cliente")

    ET.SubElement(cliente_element, "NIT").text = cliente.nit
    ET.SubElement(cliente_element, "nombre").text = cliente.nombre

    tree.write(ruta_archivo, encoding="utf-8", xml_declaration=True)


def agregar_factura_DB(factura, ruta_archivo):
    tree = ET.parse(ruta_archivo)
    root = tree.getroot()

    facturas = root.find("facturas")

    factura_element = ET.SubElement(facturas, "factura")

    ET.SubElement(factura_element, "numeroFactura").text = factura.numeroFactura
    ET.SubElement(factura_element, "NITcliente").text = factura.NITcliente
    ET.SubElement(factura_element, "fecha").text = factura.fecha
    ET.SubElement(factura_element, "valor").text = factura.valor

    tree.write(ruta_archivo, encoding="utf-8", xml_declaration=True)


def agregar_pago_DB(pago, ruta_archivo):
    tree = ET.parse(ruta_archivo)
    root = tree.getroot()

    pagos = root.find("pagos")

    pago_element = ET.SubElement(pagos, "pago")

    ET.SubElement(pago_element, "codigoBanco").text = pago.codigoBanco
    ET.SubElement(pago_element, "fecha").text = pago.fecha
    ET.SubElement(pago_element, "NITcliente").text = pago.NITcliente
    ET.SubElement(pago_element, "valor").text = pago.valor
    ET.SubElement(pago_element, "nombreBanco").text = pago.nombreBanco
    tree.write(ruta_archivo, encoding="utf-8", xml_declaration=True)


def actualizar_cliente_db(ruta_archivo_xml, nit_buscado, nuevo_nombre):
    tree = ET.parse(ruta_archivo_xml)
    raiz = tree.getroot()

    lista_clientes = raiz.find("clientes")

    if lista_clientes is not None:
        for cliente in lista_clientes:
            nit = cliente.find("NIT")
            if nit is not None and nit.text == nit_buscado:
                nombre = cliente.find("nombre")
                if nombre is not None:
                    nombre.text = nuevo_nombre
                    tree.write(ruta_archivo_xml)


def actualizar_banco_db(ruta_archivo_xml, codigo_buscado, nuevo_nombre):
    tree = ET.parse(ruta_archivo_xml)
    raiz = tree.getroot()

    lista_bancos = raiz.find("bancos")

    if lista_bancos is not None:
        for banco in lista_bancos:
            codigo = banco.find("codigo")
            if codigo is not None and codigo.text == codigo_buscado:
                nombre = banco.find("nombre")
                if nombre is not None:
                    nombre.text = nuevo_nombre
                    tree.write(ruta_archivo_xml)


def agregar_banco_DB(banco, ruta_archivo):
    tree = ET.parse(ruta_archivo)
    root = tree.getroot()

    bancos = root.find("bancos")

    bancos_element = ET.SubElement(bancos, "banco")

    ET.SubElement(bancos_element, "codigo").text = banco.codigo
    ET.SubElement(bancos_element, "nombre").text = banco.nombre

    tree.write(ruta_archivo, encoding="utf-8", xml_declaration=True)
