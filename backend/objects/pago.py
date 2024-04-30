class Pago:
    def __init__(self, codigoBanco, fecha, NITcliente, valor):
        self.codigoBanco = codigoBanco
        self.fecha = fecha
        self.NITcliente = NITcliente
        self.valor = valor

    def parseDiccionario(self):
        return {
            'codigoBanco': self.codigoBanco,
            'fecha': self.fecha,
            'NITcliente': self.NITcliente,
            'valor': self.valor,
        }