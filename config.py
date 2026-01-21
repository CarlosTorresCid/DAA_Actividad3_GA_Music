# =========================
# CONFIGURACIÓN MUSICAL
# =========================

# Estructura temporal
COMPASES = 8
SUBDIVISIONES_POR_COMPAS = 8
LONGITUD_MELODIA = COMPASES * SUBDIVISIONES_POR_COMPAS  # 64

# Compás y tempo
COMPAS = "4/4"
TEMPO = 120  # BPM

# Tonalidad
TONICA = "C"
MODO = "mayor"

# Progresión de acordes
ACORDES = [
    "C", "G", "Am", "F",
    "C", "G", "F", "C"
]

# Rango vocal (MIDI)
RANGO_MIN = 60  # C4
RANGO_MAX = 72  # C5

# =========================
# REPRESENTACIÓN
# =========================

REST = -1
HOLD = -2

# =========================
# PARÁMETROS GA
# =========================

TAMANO_POBLACION = 40
GENERACIONES = 120
PROB_MUTACION = 0.08
K_TORNEO = 3
ELITISMO = 2


from typing import Optional, List


def aplicar_midi_input(
    bpm: Optional[int],
    tonica: Optional[str],
    modo: Optional[str],
    acordes: Optional[List[str]],
):
    """
    Aplica información del MIDI a la configuración en tiempo de ejecución.
    """
    global TEMPO, TONICA, MODO, ACORDES

    if bpm is not None:
        TEMPO = int(bpm)

    if tonica is not None:
        TONICA = tonica

    if modo is not None:
        m = modo.strip().lower()
        if m in ("mayor", "menor"):
            MODO = m

    if acordes:
        if len(acordes) >= COMPASES:
            ACORDES = list(acordes[:COMPASES])
        else:
            ACORDES = list(acordes)
            while len(ACORDES) < COMPASES:
                ACORDES.append(ACORDES[-1])
