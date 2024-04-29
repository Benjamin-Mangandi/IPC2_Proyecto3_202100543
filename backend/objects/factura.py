class Factura:
    def __init__(self, numeroFactura, NITcliente, fecha, valor):
        self.numeroFactura = numeroFactura
        self.NITcliente = NITcliente
        self.fecha = fecha
        self.valor = valor
        self.abono = "NO APLICA"
        self.codigoBanco = "NO APLICA"
    
    def parseDiccionario(self):
        return {
            'numeroFactura': self.numeroFactura,
            'NITcliente': self.NITcliente,
            'fecha': self.fecha,
            'valor': self.valor,
            'abono': self.abono,
            'codigoBanco': self.codigoBanco,
        }