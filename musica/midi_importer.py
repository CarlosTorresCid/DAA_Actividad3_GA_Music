# musica/midi_importer.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict

from music21 import converter, tempo, meter, chord, stream


@dataclass
class MidiInputInfo:
    bpm: Optional[int]
    compas: str
    tonica: Optional[str]
    modo: Optional[str]              # "mayor" / "menor"
    acordes: List[str]               # 1 acorde por compás
    num_compases_detectados: int


class MidiImporter:
    """
    Servicio de importación MIDI:
    - Extrae tempo, compás, tonalidad (estimada) y acordes (inferidos).
    """

    @staticmethod
    def _primera_instancia(iterable, cls):
        for x in iterable:
            if isinstance(x, cls):
                return x
        return None

    @staticmethod
    def cargar(
        midi_path: str,
        compases_esperados: int = 8,
    ) -> MidiInputInfo:
        score = converter.parse(midi_path)

        # ---- Tempo ----
        bpm = None
        mm = MidiImporter._primera_instancia(
            score.recurse().getElementsByClass(tempo.MetronomeMark),
            tempo.MetronomeMark
        )
        if mm is not None and mm.number is not None:
            bpm = int(mm.number)

        # ---- Compás ----
        ts = MidiImporter._primera_instancia(
            score.recurse().getElementsByClass(meter.TimeSignature),
            meter.TimeSignature
        )
        compas = ts.ratioString if ts is not None else "4/4"

        # ---- Tonalidad (estimada) ----
        tonica, modo = None, None
        try:
            k = score.analyze("key")
            tonica = k.tonic.name
            modo = "mayor" if k.mode == "major" else "menor"
        except Exception:
            pass

        # ---- Acordes por compás (inferidos) ----
        # chordify agrupa verticalmente las notas
        ch = score.chordify()

        # FIX: chordify() a veces devuelve Part en lugar de Score
        base = ch.parts[0] if hasattr(ch, "parts") else ch

        # Intentamos obtener compases ya segmentados
        compases = list(base.getElementsByClass(stream.Measure))

        # Si no hay compases, forzamos segmentación en compases
        if len(compases) == 0:
            base = base.makeMeasures()
            compases = list(base.getElementsByClass(stream.Measure))

        num_compases = len(compases)
        if num_compases < compases_esperados:
            raise ValueError(
                f"El MIDI tiene {num_compases} compases detectados, "
                f"pero se esperaban al menos {compases_esperados}."
            )

        compases = compases[:compases_esperados]

        acordes: List[str] = []
        for m in compases:
            dur_por_simbolo: Dict[str, float] = {}

            for c in m.recurse().getElementsByClass(chord.Chord):
                root = c.root().name
                quality = c.quality

                if quality == "major":
                    sym = root
                elif quality == "minor":
                    sym = root + "m"
                else:
                    # simplificación: lo tratamos como mayor
                    sym = root

                dur_por_simbolo[sym] = dur_por_simbolo.get(sym, 0.0) + float(c.duration.quarterLength)

            if not dur_por_simbolo:
                # fallback si el MIDI no tiene información armónica suficiente
                acordes.append("C")
            else:
                acordes.append(max(dur_por_simbolo.items(), key=lambda kv: kv[1])[0])

        return MidiInputInfo(
            bpm=bpm,
            compas=compas,
            tonica=tonica,
            modo=modo,
            acordes=acordes,
            num_compases_detectados=num_compases
        )
