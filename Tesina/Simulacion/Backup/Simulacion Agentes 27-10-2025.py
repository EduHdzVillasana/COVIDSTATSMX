#%%
import numpy as np
import pandas as pd #Usar Polar
import multiprocessing as mp
import time
import warnings
warnings.filterwarnings("ignore")
import os
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
# Obtener fecha actual (YYYY-MM-DD)
fecha = datetime.now().strftime("%Y-%m-%d")
sim = 6
# %%
# Parámetros iniciales
l = 1 #area de cuadrado
n = 700
pi = 0.05 #probab infeccion inicial
dias_recuperacion = 14
pr = 1/dias_recuperacion #Prob recuperacion en tiempo
v = l / 30
S, I, R = 2, 3, 4
graph_size = (5, 5)

initial = [S, I]
p = 0.001 #Población inicial de infectados
iprobs = [1 - p, p]
# %%
# Crear agentes
agentes = pd.DataFrame({
    "x": np.random.uniform(0, l, n),
    "y": np.random.uniform(0, l, n),
    "dx": np.random.uniform(-v, v, n),
    "dy": np.random.uniform(-v, v, n),
    "estado": np.random.choice(initial, size=n, p=iprobs)
})
# Parámetros de simulación
epidemia = []
r = 0.05
tmax = 1000
digitos = int(np.floor(np.log10(tmax))) + 1
# %%
# Funciones auxiliares
def contagio(i, agentes, l, r, pr):
    """Evalúa si el agente i se contagia."""
    if agentes.loc[i, "estado"] in [I,R]:
        return False
    infectados = agentes.index[agentes["estado"] == I].tolist()
    for j in infectados:
        dx = agentes.loc[i, "x"] - agentes.loc[j, "x"]
        dy = agentes.loc[i, "y"] - agentes.loc[j, "y"]
        d = np.sqrt(dx ** 2 + dy ** 2)
        p = (r - d) / r

        #print(p,r,d)

        if np.random.rand() < p and d < r:
            return True
    return False

# %%
def mover_y_actualizar(i, agentes, contagios, l, pr):
    """Actualiza la posición y el estado del agente."""
    a = agentes.iloc[i].copy()
    if contagios[i]:
        a["estado"] = I
    elif a["estado"] == I:
        if np.random.rand() < pr:
            a["estado"] = R
    a["x"] += a["dx"]
    a["y"] += a["dy"]

    # Condiciones periódicas de frontera
    if a["x"] > l: a["x"] -= l
    if a["y"] > l: a["y"] -= l
    if a["x"] < 0: a["x"] += l
    if a["y"] < 0: a["y"] += l

    return a
# %%
def crear_carpeta_fecha(prefijo="simulacion", ruta_base="."):
    """
    Crea una carpeta con la fecha actual en el nombre, por ejemplo:
    simulacion_2025-10-11

    Parámetros:
    -----------
    prefijo : str, opcional
        Texto que irá al inicio del nombre de la carpeta (default="simulacion").
    ruta_base : str, opcional
        Ruta base donde se creará la carpeta (default="." = directorio actual).

    Retorna:
    --------
    str : Ruta completa de la carpeta creada.
    """

    import os
    from datetime import datetime
    # Obtener fecha actual (YYYY-MM-DD)
    fecha = datetime.now().strftime("%Y-%m-%d")

    # Crear nombre de carpeta
    nombre_carpeta = f"{prefijo}_{fecha}"

    # Ruta completa
    ruta_completa = os.path.join(ruta_base, nombre_carpeta)

    # Crear carpeta si no existe
    os.makedirs(ruta_completa, exist_ok=True)

    print(f"✅ Carpeta creada o ya existente: {ruta_completa}")
    return ruta_completa
# %%
def preparar_grafico_inicial(l=1.5, size = (5, 5)):
    fig, ax = plt.subplots(figsize=size)
    ax.set_xlim(0, l)
    ax.set_ylim(0, l)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(loc="lower right", frameon=True)
    return fig, ax

def graficar_agentes(ax, agentes, l=1.5, titulo="", nombre_archivo=None):
    """Versión optimizada: actualiza los datos en lugar de redibujar todo."""
    ax.clear()
    ax.set_xlim(0, l)
    ax.set_ylim(0, l)
    ax.set_title(titulo)

    colores = {2: "blue", 3: "red", 4: "green"}
    for estado, color in colores.items():
        subset = agentes[agentes["estado"] == estado]
        if not subset.empty:
            ax.scatter(subset["x"], subset["y"], color=color, s=15, label=f"{estado}")
    ax.legend(["Susceptible", "Infectado", "Recuperado"], loc="lower right")

    if nombre_archivo:
        plt.savefig(nombre_archivo, dpi=100, bbox_inches="tight")

# %%
from PIL import Image
import glob
import os
import imageio.v2 as imageio

def imagenes_a_gif(carpeta, patron="*.png", nombre_salida="animacion.gif", duracion=0.2):
    """Versión optimizada usando imageio."""
    archivos = sorted(glob.glob(os.path.join(carpeta, patron)))
    if not archivos:
        print("⚠️ No se encontraron imágenes.")
        return

    frames = [imageio.imread(f) for f in archivos]
    gif_path = os.path.join(carpeta, nombre_salida)
    imageio.mimsave(gif_path, frames, duration=duracion)
    print(f"GIF generado: {gif_path}")

# %%
def generar_gif(infectados_epidemia, l, sim, fecha, size):

    carpeta = crear_carpeta_fecha(prefijo=f"simulacion_{sim}")
    fig, ax = preparar_grafico_inicial(l, size = size)
    frames = []

    iteraciones = sorted(infectados_epidemia["Iteracion"].unique())

    for i in iteraciones:
        it = infectados_epidemia[infectados_epidemia["Iteracion"] == i]
        titulo = f"Sim {sim} - it {i} - {fecha}"
        graficar_agentes(ax, it, l, titulo)

        # Guardar frame directamente en memoria
        fig.canvas.draw()
        frame = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        frames.append(frame)

    gif_path = os.path.join(carpeta, f"simulacion_{sim}.gif")
    imageio.mimsave(gif_path, frames, duration=0.2)
    plt.close(fig)
    print(f"GIF generado directamente: {gif_path}")
# %%
def createGraphInfected (name, casesBD_df, date, inf_col = "infectados", guardar = False):
    import matplotlib.pyplot as plt
    import seaborn as sns
    fig = plt.figure(figsize=(20,10))
    ax = fig.add_subplot()
    sns.lineplot(x = casesBD_df["iteracion"], y = casesBD_df[inf_col], label = "Infectados", color = "r", ax = ax)
    ax.set_title(f"GRAFICA {name} {date}")
    ax.set_ylabel("CASOS")
    if guardar:
        plt.savefig(f"simulacion_{sim}.png")
    else:
        plt.show()
# %%
# Simulación
data1 = pd.DataFrame(columns=["iteracion", "tiempo", "n", "infectados", "nuevos_infectados"])
tinicial = time.time()

nt = [50, 10, 20, 30]
infectados_epidemia = pd.DataFrame()
for tiempo in range(1, tmax + 1):
    # Convertir a arrays para acelerar cálculos
    X = agentes["x"].to_numpy()
    Y = agentes["y"].to_numpy()
    estado = agentes["estado"].to_numpy()

    infectados = (estado == I)
    susceptibles = (estado == S)
    n_infectados = infectados.sum()

    epidemia.append(n_infectados)
    if n_infectados == 0:
        break

    # --- Contagio vectorizado ---
    X_s = X[susceptibles]
    Y_s = Y[susceptibles]
    X_i = X[infectados]
    Y_i = Y[infectados]

    if len(X_i) > 0 and len(X_s) > 0:
        dx = X_s[:, None] - X_i[None, :]
        dy = Y_s[:, None] - Y_i[None, :]
        d = np.sqrt(dx**2 + dy**2)
        p = np.clip((r - d) / r, 0, 1)

        # Contagio si está dentro del radio y pasa la probabilidad
        contagiados_mask = (np.random.rand(*p.shape) < p) & (d < r)
        nuevos_contagios = np.any(contagiados_mask, axis=1)

        contagios = np.zeros_like(estado, dtype=bool)
        contagios[np.where(susceptibles)[0][nuevos_contagios]] = True
    else:
        contagios = np.zeros_like(estado, dtype=bool)
        nuevos_contagios = np.array([])

    n_nuevos_contagios = contagios.sum()

    # --- Actualizar estados y posiciones ---
    estado[contagios] = I  # nuevos infectados
    recuperados = (estado == I) & (np.random.rand(len(estado)) < pr)
    estado[recuperados] = R

    # Mover agentes con fronteras periódicas
    agentes["x"] = (X + agentes["dx"]) % l
    agentes["y"] = (Y + agentes["dy"]) % l
    agentes["estado"] = estado
    agentes["Iteracion"] = tiempo

    # Guardar en el histórico completo
    infectados_epidemia = pd.concat([infectados_epidemia, agentes.copy()], ignore_index=True)

    # Guardar estadísticas por iteración
    tfinal = time.time()
    data1 = pd.concat(
        [
            data1,
            pd.DataFrame(
                [[tiempo, tfinal - tinicial, len(estado), n_infectados, n_nuevos_contagios]],
                columns=["iteracion", "tiempo", "n", "infectados", "nuevos_infectados"]
            ),
        ],
        ignore_index=True,
    )
"""
for tiempo in range(1, tmax + 1):
    infectados = len(agentes[agentes["estado"] == I])
    epidemia.append(infectados)
    if infectados == 0:
        break

    # Calcular contagios en paralelo
    contagios = [contagio(i, agentes, l, r, pr) for i in range(n)]
    #contagios = pool.starmap(contagio,[(i, agentes, l, r, pr) for i in range(n)])
    nuevos_contagios = sum(contagios)

    # Actualizar agentes en paralelo
    nuevos_agentes = [mover_y_actualizar(i, agentes, contagios, l, pr) for i in range(n)]
    #nuevos_agentes = pool.starmap(mover_y_actualizar,[(i, agentes, contagios, l, pr) for i in range(n)])

    agentes = pd.DataFrame(nuevos_agentes)
    agentes["Iteracion"] = tiempo

    infectados_epidemia = pd.concat([infectados_epidemia, agentes])

    tfinal = time.time()
    data1 = pd.concat(
        [data1, pd.DataFrame([[tiempo,tfinal - tinicial, n, infectados, nuevos_contagios]], columns=["iteracion","tiempo", "n", "infectados","nuevos_infectados"])],
        ignore_index=True
    )
"""

# Al final, epidemia contiene la evolución de infectados
# data1 contiene tiempos de ejecución por iteración
print("Simulación finalizada")
#print(data1.head())
data1.to_excel("Datos Simulacion.xlsx", index = False)
infectados_epidemia.to_csv("Detalle agentes.csv", index = False)
# %%
tfinal2 = time.time()
print(f"Tiempo: {tfinal2-tinicial}")
generar_gif(infectados_epidemia,l,sim,fecha, size = graph_size)
# %%
createGraphInfected(f"Simulacion {sim}", data1, date = fecha, guardar=True)