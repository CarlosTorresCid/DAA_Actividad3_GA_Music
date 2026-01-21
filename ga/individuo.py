# ga/individuo.py

import random
import config as cfg
from typing import Optional


class Individuo:
    def __init__(self, genes=None):
        self.genes = genes if genes is not None else []
        self.fitness = None

    def evaluar(self, pesos=None):
        from ga.fitness import calcular_fitness
        # Si pesos es None, calcular_fitness usa PesosFitness() por defecto
        self.fitness = calcular_fitness(self.genes, pesos=pesos) if pesos is not None else calcular_fitness(self.genes)
        return self.fitness

    def crear_aleatorio(self):
        self.genes = []
        for _ in range(cfg.LONGITUD_MELODIA):
            r = random.random()
            if r < 0.1:
                self.genes.append(cfg.REST)
            elif r < 0.25:
                self.genes.append(cfg.HOLD)
            else:
                self.genes.append(random.randint(cfg.RANGO_MIN, cfg.RANGO_MAX))
        return self

    def copiar(self):
        copia = Individuo(self.genes.copy())
        copia.fitness = self.fitness
        return copia

    def __repr__(self):
        return f"Individuo(fitness={self.fitness})"
