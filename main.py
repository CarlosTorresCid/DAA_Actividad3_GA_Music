# main.py

import config as cfg
import os
import csv

from musica.midi_importer import MidiImporter
from musica.midi_utils import exportar_genes_a_midi

from ga.poblacion import Poblacion
from ga.operadores import seleccion_torneo, crossover_por_compas, mutar
from ga.individuo import Individuo
from ga.fitness import PesosFitness


# =========================================================
# CLI (interfaz intuitiva)
# =========================================================

def _leer_int_0_100(nombre: str, default: int = 50) -> int:
    """Lee un entero 0..100 por CLI. ENTER = default."""
    while True:
        s = input(f"{nombre} [0..100] (def {default}): ").strip()
        if s == "":
            return default
        try:
            v = int(s)
            if 0 <= v <= 100:
                return v
            print("   ⚠️ Debe estar entre 0 y 100.")
        except ValueError:
            print("   ⚠️ Introduce un número entero (ej: 70).")


def _lerp(a: float, b: float, t: float) -> float:
    """Interpolación lineal: t en [0,1]."""
    return a + (b - a) * t


def pedir_pesos_por_cli() -> tuple[PesosFitness, dict]:
    """
    Interfaz musical (intuitiva) por terminal.
    Devuelve (PesosFitness, preset_dict) para poder guardar el preset.
    """
    print("\n🎛️ AJUSTES MUSICALES (ENTER = valores por defecto)")
    print("   0 = muy bajo / 100 = muy alto\n")

    # Sliders 0..100
    consonancia = _leer_int_0_100("Consonancia (más notas del acorde)", 55)
    suavidad = _leer_int_0_100("Suavidad (menos saltos, más paso a paso)", 55)
    sincopa = _leer_int_0_100("Síncopa (más ritmo fuera de tiempo)", 45)
    repeticion = _leer_int_0_100("Repetición / Hook (más motivo repetido)", 55)
    aire = _leer_int_0_100("Aire / Pausas (más silencios)", 45)

    # 0..1
    t_con = consonancia / 100.0
    t_sua = suavidad / 100.0
    t_sin = sincopa / 100.0
    t_rep = repeticion / 100.0
    t_air = aire / 100.0

    # Rangos recomendados (para no "romper" el fitness)
    w_acorde = _lerp(0.12, 0.38, t_con)
    w_escala = _lerp(0.22, 0.10, t_con)  # inverso: más consonancia => menos "libertad"

    w_mov = _lerp(0.10, 0.32, t_sua)
    w_ritmo = _lerp(0.05, 0.26, t_sin)
    w_hook = _lerp(0.05, 0.28, t_rep)
    rest_obj = _lerp(0.08, 0.35, t_air)

    pesos = PesosFitness(
        w_acorde=w_acorde,
        w_escala=w_escala,
        w_movimiento=w_mov,
        w_ritmo_sincopa=w_ritmo,
        w_repeticion_hook=w_hook,
        rest_ratio_obj=rest_obj,
    )

    preset = {
        "consonancia_0_100": consonancia,
        "suavidad_0_100": suavidad,
        "sincopa_0_100": sincopa,
        "repeticion_hook_0_100": repeticion,
        "aire_pausas_0_100": aire,
        "w_acorde": w_acorde,
        "w_escala": w_escala,
        "w_movimiento": w_mov,
        "w_ritmo_sincopa": w_ritmo,
        "w_repeticion_hook": w_hook,
        "rest_ratio_obj": rest_obj,
    }

    return pesos, preset


# =========================================================
# Anti-estancamiento
# =========================================================

def _reinjection_diversidad(poblacion: Poblacion, porcentaje: float = 0.15, pesos: PesosFitness | None = None) -> None:
    """Reemplaza el peor X% de individuos por nuevos aleatorios."""
    if not (0.0 < porcentaje < 1.0):
        return

    poblacion.ordenar()
    n = len(poblacion.individuos)
    k = max(1, int(n * porcentaje))

    for i in range(n - k, n):
        poblacion.individuos[i] = Individuo().crear_aleatorio()
        poblacion.individuos[i].evaluar(pesos)

    print(f"   🔄 Reinjection: reemplazados {k} individuos (peores).")


def _catastrofe_controlada(poblacion: Poblacion, elite: int = 2, pesos: PesosFitness | None = None) -> None:
    """Reinicia la población manteniendo los 'elite' mejores individuos."""
    poblacion.ordenar()
    elites = [p.copiar() for p in poblacion.individuos[:elite]]

    nuevos = [Individuo().crear_aleatorio() for _ in range(len(poblacion.individuos) - elite)]
    for ind in nuevos:
        ind.evaluar(pesos)

    poblacion.individuos = elites + nuevos
    print("   💥 Catástrofe controlada: reiniciando población (mantengo élite).")


# =========================================================
# GA
# =========================================================

def ejecutar_ga(pesos: PesosFitness | None = None) -> tuple[list[int], float]:
    """
    GA con:
    - mutación adaptativa
    - reinyección periódica
    - catástrofe controlada
    - logging a CSV
    - fitness parametrizable por CLI
    """
    generaciones = 180

    poblacion = Poblacion.crear_inicial(cfg.TAMANO_POBLACION)
    poblacion.evaluar(pesos)

    mejor_global = poblacion.mejor().copiar()

    base_mut = cfg.PROB_MUTACION
    prob_mut = base_mut

    paciencia = 12
    sin_mejora_boost = 0
    sin_mejora_global = 0

    reinject_cada = 15
    reinject_pct = 0.15

    catastrofe_umbral = paciencia * 2   # 24
    catastrofe_elite = cfg.ELITISMO

    os.makedirs("logs", exist_ok=True)
    historial = []

    for gen in range(1, generaciones + 1):
        nueva = []

        # 1) elitismo
        poblacion.ordenar()
        elites = poblacion.individuos[:cfg.ELITISMO]
        nueva.extend([e.copiar() for e in elites])

        # 2) reproducción
        while len(nueva) < cfg.TAMANO_POBLACION:
            p1 = seleccion_torneo(poblacion, k=cfg.K_TORNEO)
            p2 = seleccion_torneo(poblacion, k=cfg.K_TORNEO)

            h1, h2 = crossover_por_compas(p1, p2)

            h1 = mutar(h1, prob_gen=prob_mut)
            h2 = mutar(h2, prob_gen=prob_mut)

            h1.evaluar(pesos)
            nueva.append(h1)

            if len(nueva) < cfg.TAMANO_POBLACION:
                h2.evaluar(pesos)
                nueva.append(h2)

        poblacion = Poblacion(nueva)

        # 3) reinjection periódica
        if reinject_cada > 0 and gen % reinject_cada == 0:
            _reinjection_diversidad(poblacion, porcentaje=reinject_pct, pesos=pesos)

        # 4) actualizar mejor global
        EPS = 1e-4
        mejor_gen = poblacion.mejor()

        if mejor_gen.fitness > mejor_global.fitness + EPS:
            mejor_global = mejor_gen.copiar()
            sin_mejora_boost = 0
            sin_mejora_global = 0
            prob_mut = max(base_mut, prob_mut * 0.90)
        else:
            sin_mejora_boost += 1
            sin_mejora_global += 1

            if sin_mejora_global in (10, 15, 20, 23, 24, 25):
                print(f"   🧊 sin_mejora_global={sin_mejora_global} (umbral={catastrofe_umbral})")

            if sin_mejora_boost >= paciencia:
                prob_mut = min(0.35, prob_mut * 1.60)
                sin_mejora_boost = 0

            if sin_mejora_global >= catastrofe_umbral:
                _catastrofe_controlada(poblacion, elite=catastrofe_elite, pesos=pesos)
                sin_mejora_global = 0
                sin_mejora_boost = 0
                prob_mut = base_mut

        # Logging por generación
        historial.append({
            "gen": gen,
            "best_global": float(mejor_global.fitness),
            "best_gen": float(mejor_gen.fitness),
            "p_mut": float(prob_mut),
            "sin_mejora_global": int(sin_mejora_global),
        })

        print(f"Gen {gen:03d} | Mejor fitness: {mejor_global.fitness:.3f} | p_mut: {prob_mut:.3f}")

    # Guardar CSV
    if historial:
        csv_path = os.path.join("logs", "ga_run.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=historial[0].keys())
            w.writeheader()
            w.writerows(historial)
        print(f"\n📄 Log guardado: {csv_path}")

    return mejor_global.genes, float(mejor_global.fitness)


# =========================================================
# MAIN
# =========================================================

def main():
    print("=== MIDI -> CONFIG -> GA ===")

    # 1) Cargar MIDI de entrada
    info = MidiImporter.cargar("entrada.mid", compases_esperados=cfg.COMPASES)

    # 2) Aplicar al config
    cfg.aplicar_midi_input(
        bpm=info.bpm,
        tonica=info.tonica,
        modo=info.modo,
        acordes=info.acordes,
    )

    print("\n--- Config aplicada desde MIDI ---")
    print(f"TEMPO: {cfg.TEMPO}")
    print(f"TONICA: {cfg.TONICA}")
    print(f"MODO: {cfg.MODO}")
    print(f"ACORDES: {cfg.ACORDES}")

    # 3) Pedir preset musical (CLI)
    pesos, preset = pedir_pesos_por_cli()

    # Guardar preset para reproducibilidad
    os.makedirs("logs", exist_ok=True)
    with open("logs/preset.txt", "w", encoding="utf-8") as f:
        for k, v in preset.items():
            f.write(f"{k}: {v}\n")
    print("📄 Guardado: logs/preset.txt")

    # 4) Ejecutar GA con esos pesos
    genes, fit = ejecutar_ga(pesos)

    print("\n=== MEJOR RESULTADO ===")
    print(f"Fitness: {fit}")
    print(f"Genes: {genes}")

    # Guardar genes a TXT
    with open("logs/mejor_genes.txt", "w", encoding="utf-8") as f:
        f.write(",".join(map(str, genes)) + "\n")
    print("📄 Guardado: logs/mejor_genes.txt")

    # Exportar MIDI
    exportar_genes_a_midi(
        genes=genes,
        salida_path="resultado.mid",
        bpm=cfg.TEMPO,
        compas="4/4",
    )

    notes = sum(1 for g in genes if g >= 0)
    rests = sum(1 for g in genes if g == cfg.REST)
    holds = sum(1 for g in genes if g == cfg.HOLD)
    print(f"NOTES={notes} REST={rests} HOLD={holds} | rest%={rests / len(genes):.2f} hold%={holds / len(genes):.2f}")

    print("\n✅ Exportado: resultado.mid")


if __name__ == "__main__":
    main()
