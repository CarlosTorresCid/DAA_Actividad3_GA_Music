import csv
import os
import matplotlib.pyplot as plt

CSV_PATH = os.path.join("logs", "ga_run.csv")

def leer_csv(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append({
                "gen": int(row["gen"]),
                "best_global": float(row["best_global"]),
                "best_gen": float(row["best_gen"]),
                "p_mut": float(row["p_mut"]),
                "sin_mejora_global": int(row["sin_mejora_global"]),
            })
    return rows

def plot_fitness(rows):
    gens = [x["gen"] for x in rows]
    bg = [x["best_global"] for x in rows]
    bg_gen = [x["best_gen"] for x in rows]

    plt.figure()
    plt.plot(gens, bg, label="Mejor global")
    plt.plot(gens, bg_gen, label="Mejor de la generación", alpha=0.7)
    plt.xlabel("Generación")
    plt.ylabel("Fitness")
    plt.title("Evolución del fitness")
    plt.legend()
    out = os.path.join("logs", "fitness.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ Guardado: {out}")

def plot_pmut(rows):
    gens = [x["gen"] for x in rows]
    pm = [x["p_mut"] for x in rows]

    plt.figure()
    plt.plot(gens, pm)
    plt.xlabel("Generación")
    plt.ylabel("p_mut")
    plt.title("Evolución de la probabilidad de mutación")
    out = os.path.join("logs", "p_mut.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ Guardado: {out}")

if __name__ == "__main__":
    rows = leer_csv(CSV_PATH)
    plot_fitness(rows)
    plot_pmut(rows)
