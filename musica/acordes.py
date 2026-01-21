# musica/acordes.py

from musica.tonalidad import tonic_to_pitch_class

# Fórmulas por intervalos (en semitonos desde la tónica del acorde)
TRIAD_FORMULAS = {
    "maj": [0, 4, 7],   # mayor
    "min": [0, 3, 7],   # menor
}


def parse_chord_symbol(chord: str) -> tuple[str, str]:
    """
    Acepta símbolos simples tipo: 'C', 'G', 'Am', 'Dm', 'F#', 'Bb', 'Em'
    Devuelve (root, quality) donde quality ∈ {'maj', 'min'}
    """
    s = chord.strip()

    if not s:
        raise ValueError("Acorde vacío")

    # Detectar menor por sufijo 'm'
    quality = "maj"
    if s.endswith("m") and not s.endswith("maj"):
        quality = "min"
        s = s[:-1]  # quitar la 'm'

    root = s  # lo que queda es la tónica (puede ser C#, Bb, etc.)
    return root, quality


def chord_pitch_classes(chord: str) -> set[int]:
    """
    Devuelve pitch classes (0..11) del acorde triada (mayor/menor).
    """
    root_str, quality = parse_chord_symbol(chord)
    root_pc = tonic_to_pitch_class(root_str)

    intervals = TRIAD_FORMULAS[quality]
    pcs = {(root_pc + i) % 12 for i in intervals}
    return pcs


def note_in_chord(midi_note: int, chord_pcs: set[int]) -> bool:
    """
    Comprueba si midi_note pertenece al acorde (por pitch class).
    """
    if midi_note < 0:
        return False
    return (midi_note % 12) in chord_pcs
