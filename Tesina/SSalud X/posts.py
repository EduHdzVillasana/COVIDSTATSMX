import os
import pdfplumber
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed


# 📂 Rutas
carpeta_base = r"Comunicados"   # donde están las carpetas 2020, 2021, 2022
carpeta_salida = r"Resultados" # carpeta donde guardarás los PDFs encontrados


# Crear carpeta de salida si no existe
os.makedirs(carpeta_salida, exist_ok=True)

# 🔍 Palabras a buscar
palabras = ["semaforo", "semáforo"]

def revisar_pdf(ruta_pdf):
    """Abre un PDF y revisa si contiene alguna de las palabras"""
    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            texto = ""
            for pagina in pdf.pages:
                texto += pagina.extract_text() or ""
            texto_lower = texto.lower()
            if any(pal in texto_lower for pal in palabras):
                return ruta_pdf
    except Exception as e:
        return f"ERROR {ruta_pdf}: {e}"
    return None

def copiar_pdf(ruta_pdf):
    """Copia el PDF encontrado a la carpeta de salida"""
    archivo = os.path.basename(ruta_pdf)
    destino = os.path.join(carpeta_salida, archivo)
    # Evitar sobrescribir duplicados
    if os.path.exists(destino):
        base, ext = os.path.splitext(archivo)
        i = 1
        while os.path.exists(os.path.join(carpeta_salida, f"{base}_{i}{ext}")):
            i += 1
        destino = os.path.join(carpeta_salida, f"{base}_{i}{ext}")
    shutil.copy2(ruta_pdf, destino)
    return destino

if __name__ == "__main__":
    # 📂 Obtener lista de PDFs
    todos_pdfs = []
    for root, _, files in os.walk(carpeta_base):
        for f in files:
            if f.lower().endswith(".pdf"):
                todos_pdfs.append(os.path.join(root, f))

    print(f"Total de PDFs encontrados: {len(todos_pdfs)}")

    encontrados = []

    # 🚀 Procesamiento en paralelo
    with ProcessPoolExecutor(max_workers=4) as executor:  # ajusta max_workers según núcleos
        futures = {executor.submit(revisar_pdf, pdf): pdf for pdf in todos_pdfs}
        for future in as_completed(futures):
            resultado = future.result()
            if resultado and not str(resultado).startswith("ERROR"):
                destino = copiar_pdf(resultado)
                encontrados.append((resultado, destino))
                print(f"✅ Copiado: {resultado} → {destino}")
            elif resultado and str(resultado).startswith("ERROR"):
                print(resultado)

    print("\n📊 Resumen")
    print(f"Total archivos encontrados: {len(encontrados)}")