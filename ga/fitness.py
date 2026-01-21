# ga/fitness.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import config as cfg

from musica.tonalidad import build_scale_pitch_classes, note_in_scale
from musica.acordes import chord_pitch_classes, note_in_chord


@dataclass(frozen=True)
class PesosFitness:
    # Pesos suaves
    w_acorde: float = 0.22
    w_escala: float = 0.16
    w_movimiento: float = 0.18
    w_ritmo_sincopa: float = 0.14
    w_repeticion_hook: float = 0.16
    w_contorno: float = 0.10
    w_densidad_ideal: float = 0.04
    w_cadencia: float = 0.00

    # Penalizaciones duras (armónico / rango / estructura)
    pen_inicio_compas_no_acorde: float = 7.0
    pen_fuera_rango: float = 3.0
    pen_exceso_ataques: float = 2.0

    # Finales
    pen_ultimo_compas_pobre: float = 12.0
    pen_ultima_nota_ausente: float = 10.0
    pen_ultima_nota_no_acorde: float = 6.0

    # ✅ NUEVO: control de densidad (REST/HOLD/NOTES)
    # objetivo: que la melodía no esté "vacía"
    rest_ratio_obj: float = 0.18      # ~18% rests suele sonar natural (ajustable)
    rest_ratio_tol: float = 0.12      # tolerancia alrededor del objetivo (±12%)
    pen_rest_ratio: float = 18.0      # castigo por alejarse del objetivo

    hold_ratio_max: float = 0.40      # no queremos demasiados HOLD
    pen_hold_ratio: float = 22.0      # castigo fuerte si excede

    # ✅ NUEVO: compases pobres (muy pocos ataques)
    min_ataques_por_compas: int = 2
    pen_compas_pobre: float = 3.0     # por compás pobre (además del final)


def _nota_sonando_en_posicion(genes: List[int], i: int) -> int | None:
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


def _contar_ataques_en_compas(genes: List[int], compas_idx: int) -> int:
    start = compas_idx * cfg.SUBDIVISIONES_POR_COMPAS
    end = start + cfg.SUBDIVISIONES_POR_COMPAS
    return sum(1 for i in range(start, end) if genes[i] >= 0)


def _ataques_por_compas(genes: List[int]) -> List[int]:
    return [_contar_ataques_en_compas(genes, c) for c in range(cfg.COMPASES)]


def _ultima_nota_real(genes: List[int]) -> Optional[int]:
    for i in range(cfg.LONGITUD_MELODIA - 1, -1, -1):
        n = _nota_sonando_en_posicion(genes, i)
        if n is not None:
            return n
    return None


def _triangular_score(x: float, a: float, b: float, c: float) -> float:
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if x < b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)


# ✅ NUEVO
def _contar_tipos(genes: List[int]) -> Tuple[int, int, int]:
    """Devuelve (ataques_notes, rests, holds)."""
    notes = sum(1 for g in genes if g >= 0)
    rests = sum(1 for g in genes if g == cfg.REST)
    holds = sum(1 for g in genes if g == cfg.HOLD)
    return notes, rests, holds


# ✅ NUEVO
def _penalizacion_ratio_rest(rest_ratio: float, obj: float, tol: float) -> float:
    """
    Penaliza si nos alejamos del objetivo de rests.
    - Si estás dentro de [obj - tol, obj + tol] -> 0
    - Si te alejas -> crece linealmente
    """
    lo = max(0.0, obj - tol)
    hi = min(1.0, obj + tol)
    if lo <= rest_ratio <= hi:
        return 0.0
    if rest_ratio < lo:
        return (lo - rest_ratio) / max(lo, 1e-9)
    # rest_ratio > hi
    return (rest_ratio - hi) / max(1.0 - hi, 1e-9)


def calcular_fitness(genes: List[int], pesos: PesosFitness = PesosFitness()) -> float:
    if len(genes) != cfg.LONGITUD_MELODIA:
        raise ValueError(f"Longitud de genes inválida: {len(genes)} != {cfg.LONGITUD_MELODIA}")

    escala_pcs = build_scale_pitch_classes(cfg.TONICA, cfg.MODO)
    acordes_pcs = [chord_pitch_classes(ch) for ch in cfg.ACORDES]

    penalizaciones_duras = 0.0

    # A1: Inicio de compás debe apoyar el acorde
    for compas in range(cfg.COMPASES):
        start = compas * cfg.SUBDIVISIONES_POR_COMPAS
        nota = _nota_sonando_en_posicion(genes, start)
        if nota is None or not note_in_chord(nota, acordes_pcs[compas]):
            penalizaciones_duras += pesos.pen_inicio_compas_no_acorde

    # A2: Rango vocal
    for g in genes:
        if g >= 0 and (g < cfg.RANGO_MIN or g > cfg.RANGO_MAX):
            penalizaciones_duras += pesos.pen_fuera_rango

    # A3: Exceso de ataques por compás
    LIM_ATAQUES = 6
    for compas in range(cfg.COMPASES):
        ataques = _contar_ataques_en_compas(genes, compas)
        exceso = max(0, ataques - LIM_ATAQUES)
        penalizaciones_duras += exceso * pesos.pen_exceso_ataques

    # ✅ A3b: Compases pobres (evita melodías vacías)
    ataques_por = _ataques_por_compas(genes)
    compases_pobres = sum(1 for a in ataques_por if a < pesos.min_ataques_por_compas)
    penalizaciones_duras += compases_pobres * pesos.pen_compas_pobre

    # A4: Final no vacío y cierre estable
    ataques_ultimo = ataques_por[-1]
    if ataques_ultimo < 2:
        penalizaciones_duras += pesos.pen_ultimo_compas_pobre

    ultima = _ultima_nota_real(genes)
    if ultima is None:
        penalizaciones_duras += pesos.pen_ultima_nota_ausente
    else:
        if not note_in_chord(ultima, acordes_pcs[-1]):
            penalizaciones_duras += pesos.pen_ultima_nota_no_acorde

    # ✅ A5: Penalización por ratios REST/HOLD
    notes, rests, holds = _contar_tipos(genes)
    total = len(genes)

    rest_ratio = rests / total
    hold_ratio = holds / total

    # REST: queremos cerca del objetivo (ni 0 rests ni demasiados)
    penalizaciones_duras += pesos.pen_rest_ratio * _penalizacion_ratio_rest(
        rest_ratio=rest_ratio,
        obj=pesos.rest_ratio_obj,
        tol=pesos.rest_ratio_tol,
    )

    # HOLD: si nos pasamos de un máximo, castigamos fuerte
    if hold_ratio > pesos.hold_ratio_max:
        penalizaciones_duras += pesos.pen_hold_ratio * ((hold_ratio - pesos.hold_ratio_max) / (1.0 - pesos.hold_ratio_max))

    # B) Puntuación suave
    score_acorde = 0.0
    score_escala = 0.0
    eventos = 0

    for i in range(cfg.LONGITUD_MELODIA):
        nota = _nota_sonando_en_posicion(genes, i)
        if nota is None:
            continue

        compas = i // cfg.SUBDIVISIONES_POR_COMPAS
        en_acorde = note_in_chord(nota, acordes_pcs[compas])
        en_escala = note_in_scale(nota, escala_pcs)

        if en_acorde:
            score_acorde += 1.0
            score_escala += 1.0
        elif en_escala:
            score_acorde += 0.25
            score_escala += 0.65
        else:
            score_acorde += 0.0
            score_escala -= 0.5

        eventos += 1

    if eventos == 0:
        score_acorde_norm = 0.0
        score_escala_norm = 0.0
    else:
        score_acorde_norm = max(0.0, min(1.0, score_acorde / eventos))
        score_escala_norm = max(0.0, min(1.0, (score_escala / eventos + 0.5) / 1.5))

    # B3 Movimiento melódico
    score_mov = 0.0
    pares = 0
    grandes_seguidos = 0
    prev = None

    for i in range(cfg.LONGITUD_MELODIA):
        nota = _nota_sonando_en_posicion(genes, i)
        if nota is None:
            continue
        if prev is None:
            prev = nota
            continue

        intervalo = abs(nota - prev)

        if intervalo <= 4:
            score_mov += 1.0
            grandes_seguidos = 0
        elif intervalo <= 7:
            score_mov += 0.6
            grandes_seguidos = 0
        elif intervalo <= 9:
            score_mov += 0.15
            grandes_seguidos = 1
        else:
            score_mov -= 0.35
            grandes_seguidos += 1

        if grandes_seguidos >= 2:
            score_mov -= 1.0

        prev = nota
        pares += 1

    score_mov_norm = 0.0 if pares == 0 else max(0.0, min(1.0, (score_mov / pares + 1.0) / 2.0))

    # B4 Ritmo / síncopa
    ataques_on = 0
    ataques_off = 0
    total_ataques = 0

    for i in range(cfg.LONGITUD_MELODIA):
        if genes[i] >= 0:
            pos = i % cfg.SUBDIVISIONES_POR_COMPAS
            if pos in (0, 2, 4, 6):
                ataques_on += 1
            else:
                ataques_off += 1
            total_ataques += 1

    if total_ataques == 0:
        score_ritmo_norm = 0.0
    else:
        ratio_off = ataques_off / total_ataques
        if ratio_off < 0.10:
            score_ritmo_norm = 0.2
        elif ratio_off <= 0.45:
            score_ritmo_norm = 1.0
        elif ratio_off <= 0.70:
            score_ritmo_norm = 0.6
        else:
            score_ritmo_norm = 0.2

    # B5 Hook
    compases = []
    for c in range(cfg.COMPASES):
        start = c * cfg.SUBDIVISIONES_POR_COMPAS
        compases.append(tuple(genes[start:start + cfg.SUBDIVISIONES_POR_COMPAS]))

    iguales = 0
    for i in range(cfg.COMPASES):
        for j in range(i + 1, cfg.COMPASES):
            if compases[i] == compases[j]:
                iguales += 1

    if iguales == 0:
        score_hook_norm = 0.2
    elif 1 <= iguales <= 5:
        score_hook_norm = 1.0
    elif 6 <= iguales <= 10:
        score_hook_norm = 0.7
    else:
        score_hook_norm = 0.2

    # B6 Contorno
    notas_reales = [g for g in genes if g >= 0]
    if len(notas_reales) < 2:
        score_contorno_norm = 0.0
    else:
        nmin = min(notas_reales)
        nmax = max(notas_reales)
        rango = nmax - nmin

        score_rango = _triangular_score(rango, a=4, b=9, c=14)

        idx_max = next(i for i, g in enumerate(genes) if g == nmax)
        compas_max = idx_max // cfg.SUBDIVISIONES_POR_COMPAS

        if compas_max <= 2:
            score_climax = 0.2
        elif compas_max <= 4:
            score_climax = 0.6
        else:
            score_climax = 1.0

        score_contorno_norm = 0.6 * score_rango + 0.4 * score_climax

    # B7 Densidad ideal (ataques por compás)
    dens_scores = []
    ataques_por = _ataques_por_compas(genes)
    for a in ataques_por:
        dens_scores.append(_triangular_score(a, a=1.5, b=4.0, c=6.5))
    score_dens_norm = sum(dens_scores) / len(dens_scores)

    score_suave = (
        pesos.w_acorde * score_acorde_norm +
        pesos.w_escala * score_escala_norm +
        pesos.w_movimiento * score_mov_norm +
        pesos.w_ritmo_sincopa * score_ritmo_norm +
        pesos.w_repeticion_hook * score_hook_norm +
        pesos.w_contorno * score_contorno_norm +
        pesos.w_densidad_ideal * score_dens_norm
    )

    return 100.0 - penalizaciones_duras + 100.0 * score_suave
