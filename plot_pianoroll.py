import os
import numpy as np
import matplotlib.pyplot as plt
import config as cfg

GENES_PATH = os.path.join("logs", "mejor_genes.txt")

def cargar_genes(path):
    with open(path, "r", encoding="utf-8") as f:
        line = f.readline().strip()
    return [int(x) for x in line.split(",")]

def genes_a_eventos(genes):
    # Convierte REST/HOLD en una nota "activa" por tick (o None)
    active = None
    notas = []
    for g in genes:
        if g == cfg.REST:
            active = None
            notas.append(None)
        elif g == cfg.HOLD:
            notas.append(active)
        else:
            active = g
            notas.append(active)
    return notas

def plot_pianoroll(genes):
    notas = genes_a_eventos(genes)

    # matriz [pitch, time]
    pitches = [n for n in notas if n is not None]
    if not pitches:
        print("No hay notas para dibujar.")
        return

    pmin, pmax = min(pitches), max(pitches)
    T = len(notas)
    H = (pmax - pmin + 1)

    mat = np.zeros((H, T), dtype=int)
    for t, n in enumerate(notas):
        if n is not None:
            mat[pmax - n, t] = 1  # invertido para que el pitch alto quede arriba

    plt.figure()
    plt.imshow(mat, aspect="auto", interpolation="nearest")
    plt.xlabel("Tiempo (subdivisiones)")
    plt.ylabel("Pitch (relativo)")
    plt.title("Piano roll (mejor melodía)")
    out = os.path.join("logs", "pianoroll.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ Guardado: {out}")

if __name__ == "__main__":
    genes = cargar_genes(GENES_PATH)
    plot_pianoroll(genes)
