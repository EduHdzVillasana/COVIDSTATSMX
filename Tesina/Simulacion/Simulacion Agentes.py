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
sim = 11
# %%
# Parámetros iniciales
l = 4 #area de cuadrado
n = 12000
pi = 0.05 #probab infeccion inicial
dias_recuperacion = 14
pr = dias_recuperacion #Prob recuperacion en tiempo
v = l / 30
S, I, R = 2, 3, 4
size_dot = 0.2
graph_size = (5, 5)
R0 = 1.5
p_contacto = 0.2 #probabilidad promedio de contagio dentro del radio (0 < p_contacto <= 1)
sigma = 2 #Desviacion estandar en dias de duracion de infeccion
initial = [S, I]
p = 0.001 #Población inicial de infectados
iprobs = [1 - p, p]
# %%
# Crear agentes
agentes = pd.DataFrame({
    "agente_id": np.arange(n) + 1,
    "x": np.random.uniform(0, l, n),
    "y": np.random.uniform(0, l, n),
    "dx": np.random.uniform(-v, v, n),
    "dy": np.random.uniform(-v, v, n),
    "estado": np.random.choice(initial, size=n, p=iprobs),
    "dias_infectado_restante": np.zeros(n, dtype=int)
})

# Parámetros de simulación
epidemia = []
r = 0.05
tmax = 1000
digitos = int(np.floor(np.log10(tmax))) + 1
# %%
# Funciones auxiliares
def estimar_radio(R0, n, l, pr, p_contacto=0.5):
    """
    Calcula el radio de contagio (r) esperado dado un R0 deseado.
    R0 : número básico de reproducción
    n  : número de agentes
    l  : tamaño del área cuadrada
    pr : probabilidad de recuperación por paso
    p_contacto : probabilidad promedio de contagio dentro del radio (0 < p_contacto <= 1)
    """
    rho = n / (l ** 2)                # densidad de agentes
    T_inf = pr                    # duración promedio de la infección
    r = np.sqrt(R0 / (np.pi * rho * p_contacto * T_inf))
    return r
# %%
def duracion_infeccion_normal(mu=7, sigma=2, size=1, min_val=1, max_val=20):
    """
    Genera duraciones (enteros positivos) con distribución normal truncada
    usando solo NumPy.

    Parámetros:
    -----------
    mu : float -> media
    sigma : float -> desviación estándar
    size : int -> cantidad de muestras
    min_val, max_val : límites inferiores y superiores para truncar
    """
    duraciones = np.random.normal(loc=mu, scale=sigma, size=size)
    duraciones = np.clip(duraciones, min_val, max_val)  # recorta extremos
    return duraciones.astype(int)
# %%
def contagio(X,Y, estado, l, r, pr):
    infectados = (estado == I)
    susceptibles = (estado == S)

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
    return contagios
# %%
def mover_y_actualizar(estado, agentes, contagios, l, pr, tiempo, sigma=2):
    agentes_nuevos = agentes.copy()

    # Actualizando dias de infeccion en agentes infectados
    agentes_nuevos.loc[estado == I, "dias_infectado_restantes"] -= 1

    #Calculando Recuperados
    recuperados = (estado == I) & (agentes_nuevos["dias_infectado_restantes"] <= 0)
    estado[recuperados] = R

    # Nuevos Infectados
    agentes_nuevos.loc[contagios, "dias_infectado_restantes"] = duracion_infeccion_normal(
        mu= pr, sigma=sigma, size=contagios.sum()
    )
    estado[contagios] = I

    # Mover agentes con fronteras periódicas
    agentes_nuevos["x"] = (X + agentes["dx"]) % l
    agentes_nuevos["y"] = (Y + agentes["dy"]) % l
    agentes_nuevos["estado"] = estado
    agentes_nuevos["Iteracion"] = tiempo

    return agentes_nuevos
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
            ax.scatter(subset["x"], subset["y"], color=color, s=size_dot, label=f"{estado}")
    ax.legend(["Susceptible", "Infectado", "Recuperado"], 
                loc="lower right",
                scatterpoints=1,     # cuántos puntos por etiqueta
                markerscale=2.5,     # escala del tamaño respecto al gráfico
                frameon=True)

    if nombre_archivo:
        plt.savefig(nombre_archivo, dpi=100, bbox_inches="tight")

# %%
from PIL import Image
import glob
import os
import imageio.v2 as imageio

def imagenes_a_gif(carpeta, patron="*.png", nombre_salida="animacion.gif", duracion=0.5):
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
def createGraphInfected (name, casesBD_df, date, inf_col = "nuevos_infectados", guardar = False):
    import matplotlib.pyplot as plt
    import seaborn as sns
    fig = plt.figure(figsize=(20,10))
    ax = fig.add_subplot()
    sns.lineplot(x = casesBD_df["iteracion"], y = casesBD_df[inf_col], label = "Nuevos Casos", color = "r", ax = ax)
    ax.set_title(f"GRAFICA {name} {date}")
    ax.set_ylabel("CASOS")
    if guardar:
        plt.savefig(os.path.join(carpeta,f"simulacion_{sim}.png"))
    else:
        plt.show()
# %%
# Simulación
data1 = pd.DataFrame(columns=["iteracion", "tiempo", "n", "infectados", "nuevos_infectados"])
tinicial = time.time()

r = estimar_radio(R0, n,l,pr,p_contacto)

nt = [50, 10, 20, 30]
infectados_epidemia = pd.DataFrame()

agentes.loc[agentes["estado"] == I, "dias_infectado_restantes"] = duracion_infeccion_normal(
    mu= pr, sigma=sigma, size=agentes[agentes["estado"] == I].shape[0]
)

for tiempo in range(1, tmax + 1):
    # Guardar en el histórico completo
    infectados_epidemia = pd.concat([infectados_epidemia, agentes.copy()], ignore_index=True)

    # Convertir a arrays para acelerar cálculos
    X = agentes["x"].to_numpy()
    Y = agentes["y"].to_numpy()
    estado = agentes["estado"].to_numpy()

    infectados = (estado == I)
    n_infectados = infectados.sum()

    epidemia.append(n_infectados)
    if n_infectados == 0:
        break

    # Calcular contagios con numpy
    contagios = contagio(X,Y,estado,l,r,pr)
    n_nuevos_contagios = contagios.sum()

    # --- Actualizar estados y posiciones ---
    agentes = mover_y_actualizar(estado, agentes, contagios, l, pr, tiempo)

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
# %%

# Al final, epidemia contiene la evolución de infectados
# data1 contiene tiempos de ejecución por iteración
print("Simulación finalizada")
print(f"r: {r}")
#print(data1.head())
carpeta = crear_carpeta_fecha(prefijo=f"simulacion_{sim}")
data1.to_excel(os.path.join(carpeta, "Datos Simulacion.xlsx"), index = False)
infectados_epidemia.to_csv(os.path.join(carpeta, "Detalle agentes.csv"), index = False)
# %%
tfinal2 = time.time()
print(f"Tiempo: {tfinal2-tinicial}")
generar_gif(infectados_epidemia,l,sim,fecha, size = graph_size)
# %%
createGraphInfected(f"Simulacion {sim}", data1, date = fecha, guardar=True)