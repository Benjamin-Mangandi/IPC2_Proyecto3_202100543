class Cliente:
    def __init__(self, nombre, nit):
        self.nombre = nombre
        self.nit = nit
        self.saldo = 0
        self.transacciones = []
        self.pagos = []