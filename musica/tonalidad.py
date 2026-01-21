# musica/tonalidad.py

NOTE_TO_PC = {
    "C": 0, "C#": 1, "Db": 1,
    "D": 2, "D#": 3, "Eb": 3,
    "E": 4,
    "F": 5, "F#": 6, "Gb": 6,
    "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10,
    "B": 11
}

MAJOR_STEPS = [2, 2, 1, 2, 2, 2, 1]  # tonos/semitonos entre grados
MINOR_NATURAL_STEPS = [2, 1, 2, 2, 1, 2, 2]  # menor natural


def tonic_to_pitch_class(tonica: str) -> int:
    """
    Convierte 'C', 'F#', 'Bb' a su pitch class (0..11).
    """
    t = tonica.strip()
    if t not in NOTE_TO_PC:
        raise ValueError(f"Tónica no soportada: {tonica}")
    return NOTE_TO_PC[t]


def build_scale_pitch_classes(tonica: str, modo: str) -> set[int]:
    """
    Devuelve el conjunto de pitch classes (0..11) de la escala mayor o menor natural.
    """
    modo_norm = modo.strip().lower()
    if modo_norm not in ("mayor", "menor"):
        raise ValueError("Modo debe ser 'mayor' o 'menor'")

    steps = MAJOR_STEPS if modo_norm == "mayor" else MINOR_NATURAL_STEPS
    root = tonic_to_pitch_class(tonica)

    pcs = [root]
    acc = root
    for s in steps[:-1]:  # 6 pasos para generar 7 notas
        acc = (acc + s) % 12
        pcs.append(acc)

    return set(pcs)


def note_in_scale(midi_note: int, scale_pcs: set[int]) -> bool:
    """
    Comprueba si midi_note pertenece a la escala (por pitch class).
    """
    if midi_note < 0:
        return False
    return (midi_note % 12) in scale_pcs
