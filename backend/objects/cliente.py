class Cliente:
    def __init__(self, nombre, nit):
        self.nombre = nombre
        self.nit = nit
        self.saldo = 0
        self.transacciones = []
        self.pagos = []

    def parseDiccionario(self):
        return {
            'nit': self.nit,
            'nombre': self.nombre,
            'saldo': self.saldo,
            'transacciones': [transaccion.parseDiccionario() for transaccion in self.transacciones],
            'pagos': [pago.parseDiccionario() for pago in self.pagos]
        }