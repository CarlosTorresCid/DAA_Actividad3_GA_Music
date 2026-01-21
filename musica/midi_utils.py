# musica/midi_utils.py

from __future__ import annotations

from typing import List, Optional

import config as cfg

try:
    from music21 import stream, note, tempo, meter
except ImportError as e:
    raise ImportError(
        "Falta instalar music21. Ejecuta: pip install music21"
    ) from e


def exportar_genes_a_midi(
    genes: List[int],
    salida_path: str = "resultado.mid",
    bpm: Optional[int] = None,
    compas: str = "4/4"
) -> str:
    """
    Convierte genes (NOTE midi / REST / HOLD) a un MIDI.
    - Cada posición representa una corchea (1/2 negra) si SUBDIVISIONES_POR_COMPAS=8 en 4/4.
    - NOTE crea una nota nueva.
    - HOLD prolonga la nota anterior.
    - REST crea silencio.

    Devuelve el path de salida.
    """
    if bpm is None:
        bpm = cfg.TEMPO

    s = stream.Stream()
    s.append(tempo.MetronomeMark(number=bpm))
    s.append(meter.TimeSignature(compas))

    # Duración de cada subdivisión en "quarterLength"
    # En 4/4: negra = 1.0, corchea = 0.5
    dur_sub = 4.0 / cfg.SUBDIVISIONES_POR_COMPAS  # 4 negras por compás

    actual_pitch: Optional[int] = None
    actual_dur = 0.0

    def flush_actual():
        nonlocal actual_pitch, actual_dur
        if actual_pitch is not None and actual_dur > 0:
            n = note.Note()
            n.pitch.midi = actual_pitch
            n.quarterLength = actual_dur
            s.append(n)
        actual_pitch = None
        actual_dur = 0.0

    for g in genes:
        if g == cfg.REST:
            flush_actual()
            r = note.Rest()
            r.quarterLength = dur_sub
            s.append(r)

        elif g == cfg.HOLD:
            if actual_pitch is None:
                r = note.Rest()
                r.quarterLength = dur_sub
                s.append(r)
            else:
                actual_dur += dur_sub

        else:
            flush_actual()
            actual_pitch = g
            actual_dur = dur_sub

    flush_actual()

    s.write("midi", fp=salida_path)
    return salida_path
