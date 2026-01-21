# ga/operadores.py

import random
import config as cfg
from ga.individuo import Individuo

from musica.tonalidad import build_scale_pitch_classes
from musica.acordes import chord_pitch_classes


def seleccion_torneo(poblacion, k=3):
    candidatos = random.sample(poblacion.individuos, k)
    return max(candidatos, key=lambda x: x.fitness)


def crossover_por_compas(p1: Individuo, p2: Individuo) -> tuple[Individuo, Individuo]:
    punto_compas = random.randint(1, (cfg.LONGITUD_MELODIA // cfg.SUBDIVISIONES_POR_COMPAS) - 1)
    corte = punto_compas * cfg.SUBDIVISIONES_POR_COMPAS

    g1 = p1.genes[:corte] + p2.genes[corte:]
    g2 = p2.genes[:corte] + p1.genes[corte:]

    return Individuo(g1), Individuo(g2)


def _nota_sonando(genes: list[int], i: int) -> int | None:
    """
    Devuelve la nota real que suena en i:
    - REST -> None
    - NOTE >=0 -> nota
    - HOLD -> busca hacia atrás la última NOTE (si encuentra REST antes, None)
    """
    g = genes[i]
    if g == cfg.REST:
        return None
    if g == cfg.HOLD:
        j = i - 1
        while j >= 0:
            if genes[j] >= 0:
                return genes[j]
            if genes[j] == cfg.REST:
                return None
            j -= 1
        return None
    return g


def _pc_a_notas_en_rango(pcs: set[int], rango_min: int, rango_max: int) -> list[int]:
    """
    Convierte pitch classes a notas MIDI dentro del rango.
    """
    out = []
    for n in range(rango_min, rango_max + 1):
        if (n % 12) in pcs:
            out.append(n)
    return out


def _elegir_nota_musical(genes: list[int], i: int) -> int:
    """
    Elige una nota "musical":
    1) prioriza acorde del compás
    2) luego escala
    3) favorece movimiento pequeño respecto a la nota anterior
    """
    compas = i // cfg.SUBDIVISIONES_POR_COMPAS

    # pitch classes de escala y acorde del compás
    escala_pcs = set(build_scale_pitch_classes(cfg.TONICA, cfg.MODO))
    acorde_pcs = set(chord_pitch_classes(cfg.ACORDES[compas]))

    candidatos_acorde = _pc_a_notas_en_rango(acorde_pcs, cfg.RANGO_MIN, cfg.RANGO_MAX)
    candidatos_escala = _pc_a_notas_en_rango(escala_pcs, cfg.RANGO_MIN, cfg.RANGO_MAX)

    # nota anterior (para favorecer pasos pequeños)
    prev = None
    if i > 0:
        prev = _nota_sonando(genes, i - 1)

    def elegir_cercana(cands: list[int]) -> int:
        if not cands:
            return random.randint(cfg.RANGO_MIN, cfg.RANGO_MAX)

        if prev is None:
            return random.choice(cands)

        # ponderación por cercanía: intervalos pequeños pesan más
        # peso = 1 / (1 + distancia)
        pesos = []
        for n in cands:
            d = abs(n - prev)
            pesos.append(1.0 / (1.0 + d))

        # selección por ruleta
        total = sum(pesos)
        r = random.random() * total
        acc = 0.0
        for n, w in zip(cands, pesos):
            acc += w
            if acc >= r:
                return n
        return cands[-1]

    # 70% acorde, 30% escala (cuando mutamos a nota)
    if candidatos_acorde and random.random() < 0.70:
        return elegir_cercana(candidatos_acorde)

    if candidatos_escala:
        return elegir_cercana(candidatos_escala)

    return random.randint(cfg.RANGO_MIN, cfg.RANGO_MAX)


def mutar(ind: Individuo, prob_gen=None) -> Individuo:
    """
    Mutación musical:
    - mantiene REST/HOLD con probabilidades
    - si toca nota: elige nota preferentemente del acorde/escala y cercana a la anterior
    """
    if prob_gen is None:
        prob_gen = cfg.PROB_MUTACION

    genes = ind.genes.copy()

    for i in range(len(genes)):
        if random.random() < prob_gen:
            r = random.random()

            # Mantén tus ratios, pero ahora la "nota" es musical
            if r < 0.15:
                genes[i] = cfg.REST
            elif r < 0.30:
                genes[i] = cfg.HOLD
            else:
                genes[i] = _elegir_nota_musical(genes, i)

    return Individuo(genes)
