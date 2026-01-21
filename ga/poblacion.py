# ga/poblacion.py

from ga.individuo import Individuo


class Poblacion:
    def __init__(self, individuos=None):
        self.individuos = individuos if individuos is not None else []

    @staticmethod
    def crear_inicial(tamano: int) -> "Poblacion":
        inds = [Individuo().crear_aleatorio() for _ in range(tamano)]
        return Poblacion(inds)

    def evaluar(self, pesos=None):
        for ind in self.individuos:
            ind.evaluar(pesos)

    def mejor(self) -> Individuo:
        return max(self.individuos, key=lambda x: x.fitness)

    def ordenar(self):
        self.individuos.sort(key=lambda x: x.fitness, reverse=True)
