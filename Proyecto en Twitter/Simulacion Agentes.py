#%%
import numpy as np
import pandas as pd
import multiprocessing as mp
import time
import warnings
warnings.filterwarnings("ignore")
import os
from datetime import datetime
# Obtener fecha actual (YYYY-MM-DD)
fecha = datetime.now().strftime("%Y-%m-%d")
# %%
# Parámetros iniciales
l = 1.5 #area de cuadrado
n = 50
pi = 0.05 #probab infeccion inicial
pr = 0.02 #Prob recuperacion en tiempo
v = l / 30
S, I, R = 2, 3, 4

initial = [S, I]
p = 0.2
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
sim = 1
# Parámetros de simulación
epidemia = []
r = 0.1
tmax = 10000
digitos = int(np.floor(np.log10(tmax))) + 1
# %%
# Funciones auxiliares
def contagio(i, agentes, l, r, pr):
    """Evalúa si el agente i se contagia."""
    if agentes.loc[i, "estado"] == I:
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
import matplotlib.pyplot as plt

def graficar_agentes(agentes, l=1.5, titulo="Distribución de agentes", guardar=False, nombre_archivo="agentes.png"):
    """
    Grafica los agentes según su estado epidemiológico:
    - 2: Susceptible (azul)
    - 3: Infectado (rojo)
    - 4: Recuperado (verde)
    
    Parámetros:
    -----------
    agentes : pd.DataFrame
        DataFrame con columnas ['x', 'y', 'estado']
    l : float, opcional
        Tamaño del área cuadrada donde se mueven los agentes (default=1.5)
    titulo : str, opcional
        Título del gráfico
    guardar : bool, opcional
        Si True, guarda la imagen en archivo
    nombre_archivo : str, opcional
        Nombre del archivo de salida (si guardar=True)
    """
    
    # Crear figura
    plt.figure(figsize=(6, 6))
    plt.title(titulo)
    plt.xlabel("x")
    plt.ylabel("y")

    # Filtrar por estado
    susceptibles = agentes[agentes["estado"] == 2]
    infectados   = agentes[agentes["estado"] == 3]
    recuperados  = agentes[agentes["estado"] == 4]

    # Graficar
    plt.scatter(susceptibles["x"], susceptibles["y"], color="blue", label="Susceptible", s=30)
    plt.scatter(infectados["x"], infectados["y"], color="red", label="Infectado", s=30)
    plt.scatter(recuperados["x"], recuperados["y"], color="green", label="Recuperado", s=30)

    # Limites y leyenda
    plt.xlim(0, l)
    plt.ylim(0, l)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.3)

    # Guardar o mostrar
    if guardar:
        plt.savefig(nombre_archivo, dpi=150)
        plt.close()
    else:
        plt.show()

# %%
from PIL import Image
import glob
import os

def imagenes_a_gif(carpeta, patron="*.png", nombre_salida="animacion.gif", duracion=200, loop=0):
    """
    Crea un GIF animado a partir de un conjunto de imágenes en una carpeta.

    Parámetros:
    -----------
    carpeta : str
        Ruta de la carpeta donde están las imágenes.
    patron : str, opcional
        Patrón de búsqueda (por ejemplo "*.png" o "frame_*.jpg").
    nombre_salida : str, opcional
        Nombre del archivo GIF resultante (default="animacion.gif").
    duracion : int, opcional
        Duración de cada frame en milisegundos (default=200 = 0.2s).
    loop : int, opcional
        Número de veces que se repetirá la animación. 
        0 = infinito (default).

    Retorna:
    --------
    None (guarda el archivo .gif en la carpeta especificada)
    """
    # Obtener lista de imágenes
    ruta = os.path.join(carpeta, patron)
    archivos = sorted(glob.glob(ruta))

    if len(archivos) == 0:
        print("⚠️ No se encontraron imágenes con ese patrón.")
        return

    # Cargar todas las imágenes
    frames = [Image.open(img) for img in archivos]

    # Guardar como GIF
    gif_path = os.path.join(carpeta, nombre_salida)
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=duracion,
        loop=loop
    )

    print(f"GIF generado correctamente: {gif_path}")

# %%
def generar_gif(agentes_epidemia):

    
    for i in agentes_epidemia["Iteracion"].values:
        it = agentes.loc[agentes["Iteracion"] == i]

        graficar_agentes(it, l, titulo=f"simulacion {sim}-it {i}-{fecha}", guardar=True, nombre_archivo = f"agentes_{i}.png")
    
    carpeta = crear_carpeta_fecha(prefijo=f"simulacion_{sim}")

    imagenes_a_gif(carpeta, nombre_salida=f"simulacion_{sim}.gif")

# %%
# Simulación
data1 = pd.DataFrame(columns=["tiempo", "n"])
tinicial = time.time()

nt = [50, 10, 20, 30]
"""
with mp.Pool(mp.cpu_count() - 1) as pool:
    for k in range(5):
        for tiempo in range(1, tmax + 1):
            infectados = len(agentes[agentes["estado"] == I])
            epidemia.append(infectados)
            if infectados == 0:
                break

            # Calcular contagios en paralelo
            contagios = pool.starmap(
                contagio, [(i, agentes, l, r, pr) for i in range(n)]
            )

            # Actualizar agentes en paralelo
            nuevos_agentes = pool.starmap(
                mover_y_actualizar, [(i, agentes, contagios, l, pr) for i in range(n)]
            )

            agentes = pd.DataFrame(nuevos_agentes)

            tfinal = time.time()
            data1 = pd.concat(
                [data1, pd.DataFrame([[tfinal - tinicial, n]], columns=["tiempo", "n"])],
                ignore_index=True
            )
"""
infectados_epidemia = pd.DataFrame()

for tiempo in range(1, tmax + 1):
    infectados = len(agentes[agentes["estado"] == I])
    epidemia.append(infectados)
    if infectados == 0:
        break

    # Calcular contagios en paralelo
    contagios = [contagio(i, agentes, l, r, pr) for i in range(n)]

    # Actualizar agentes en paralelo
    nuevos_agentes = [mover_y_actualizar(i, agentes, contagios, l, pr) for i in range(n)]

    agentes = pd.DataFrame(nuevos_agentes)
    agentes["Iteracion"] = tiempo

    infectados_epidemia = pd.concat([infectados_epidemia, agentes])

    tfinal = time.time()
    data1 = pd.concat(
        [data1, pd.DataFrame([[tiempo,tfinal - tinicial, n, infectados]], columns=["iteracion","tiempo", "n", "infectados"])],
        ignore_index=True
    )

# Al final, epidemia contiene la evolución de infectados
# data1 contiene tiempos de ejecución por iteración
print("Simulación finalizada")
print("Evolución de infectados:", epidemia)
print(data1.head())
data1.to_excel("Datos Simulacion.xlsx", index = False)
infectados_epidemia.to_csv("Detalle agentes.csv", index = False)
# %%
