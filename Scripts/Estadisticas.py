"""
    Autor: Eduardo Alán Hernández Villasana
    Estudiante de Licenciatura en Ciencias Computacionales en
    la Universidad Autonoma de Nuevo León - Facultad de Ciencias Fisico Matemáticas
"""
import pandas as ps
import os
import datetime as dt
import matplotlib.pyplot as plt

def invertirLista (cadenas):
    cadenas_nueva = []
    for cadena in cadenas:
        elementos = cadena.split('/')
        cadenas_nueva.append (elementos[1] +"/"+ elementos[0] +"/"+ elementos[2])
    return cadenas_nueva


def obtenerDataFrame (fecha = "hoy"):
    url = "https://raw.githubusercontent.com/EduHdzVillasana/COVIDSTATSMX/master/Datos%20Abiertos"
    x = dt.date.today()
    fecha = str(x)
    sufijo = "COVID19MEXICO.csv"
    # 200617COVID19MEXICO.csv
    año = str(x.year - 2000)
    if x.month >= 10:
        mes = str(x.month)
    else:
        mes = "0" + str(x.month)
    
    if x.day >= 10:
        dia = str(x.day)
    else:
        dia = "0" + str(x.day)

    prefijo = año + mes + dia
    try:
        covid_df = ps.read_csv(url + "/" + prefijo + sufijo)
        print ("DataSet obtenido de: \n" + url + "/" + prefijo + sufijo)
    except:
        x = x - dt.timedelta(days = 1)
        fecha = str(x)
        año = str(x.year - 2000)
        if x.month >= 10:
            mes = str(x.month)
        else:
            mes = "0" + str(x.month)
        
        if x.day >= 10:
            dia = str(x.day)
        else:
            dia = "0" + str(x.day)

        prefijo = año + mes + dia
        try:
            covid_df = ps.read_csv(url + "/" + prefijo + sufijo)
            print ("DataSet obtenido de: \n" + url + "/" + prefijo + sufijo)
        except:
            covid_df = None
            fecha = "0"
    #print (dt.datetime.now() - x) Para medir el tiempo que se tarda en leer el dataset
    return covid_df, fecha

def guardarDataFrame (path = "C:", nombre = "DATAFRAME", tipo = ".xls", dataFrame = None):
    if tipo == ".csv":
        dataFrame.to_csv(os.path.join(path, nombre))
    elif tipo == ".xls":
        dataFrame.to_excel(os.path.join(path, nombre))
    elif tipo == ".json":
        dataFrame.to_json(os.path.join(path, nombre))

def imprimirAcumulados (casosA):
    # variable que guarda el indice de letalidad en porcentaje
    inice_L = casosA["Defunciones"] / casosA["Positivos"] * 100
    # Variable que guarda el indice de positividad nacional
    indice_P = casosA["Positivos"] / (casosA["Negativos"] + casosA["Positivos"]) * 100
    print ("  Total de casos estudiados: " + str(casosA["Total"])+ "\n\n" +
            "  Casos Positivos a SARS-CoV-2: " + str(casosA["Positivos"])+ "\n\n" +
            "  Casos No Positivos a SARS-CoV-2: " + str(casosA["Negativos"])+ "\n\n" +
            "  Casos Con Resultado Pendiente: " + str(casosA["Pendientes"]) + "\n\n" +
            "  Defunciones Positicas a SARS-CoV-2: " + str(casosA["Defunciones"]) + "\n\n" +
            "  Tasa de Letalidad: %.3f%s\n\n  Tasa de Positividad : %.3f%s\n" % (inice_L,"%",indice_P,"%"))

def obtenerCasosAcumulados (covid_df):
    # Data Frame que almacenará la columna RESULTADO donde 1 es positivo, 2 es negativo, 3 es pendiente y FECHA_DEF, donde si la fecha es diferente a 9999-99-99 es una defuncion
    #casos = ps.concat([covid_df["RESULTADO"], covid_df["FECHA_DEF"]], axis = 1)
    
    casos = covid_df[["RESULTADO", "FECHA_DEF"]]
    # Contador de los casos positivos
    positivos = 0 
    # Contador de los casos negativos
    negativos = 0
    # Contador de los casos pendientes
    pendientes = 0
    # Contador de defunciones por covid-19
    defunciones = 0
    #print (casos.head())
    for i in range (len(casos)):
        if casos["RESULTADO"][i] == 1:
            positivos += 1
            if casos ["FECHA_DEF"][i] != "9999-99-99":
                defunciones +=1
        elif casos["RESULTADO"][i] == 2:
            negativos += 1
        elif casos["RESULTADO"][i] == 3:
            pendientes +=1
    return {"Positivos": positivos, "Negativos":negativos, "Pendientes":pendientes, "Defunciones": defunciones, "Total": len(casos)}


def obtenerCasosPorDia (covid_df, estado = 0, municipios = []):
    # Lista que guarda las fechas de FECHA
    fechas = []
    # Diccionario que guarda la posicion de las fechas
    pos_fechas = {}
    # Diccionario que se convertirá en Data Frame
    casosPorDia = {}
    # Se crean las listas que almacenarán los datos
    casosPorDia ["FECHA"] = []
    casosPorDia ["CASOS_POSITIVOS"] = []
    casosPorDia ["CASOS_NEGATIVOS"] = []
    casosPorDia ["CASOS_SOSPECHOSOS"] = []
    casosPorDia ["DEFUNCIONES"] = []
    total_Casos = len(covid_df)
    # Se crea la lista de las fechas
    for i in range(total_Casos):
        if covid_df["FECHA_SINTOMAS"][i] not in fechas:
            #print (covid_df["FECHA_SINTOMAS"][i])
            fechas.append(covid_df["FECHA_SINTOMAS"][i])
    
    # Se ordenan las fechas, debido al formato (dd/mm/aaaa) se tiene que invertir a (mm/dd/aaaa) para ordenarlo y después se devuelven a 
    # su posicion original
    fechas = invertirLista(fechas)
    fechas.sort()
    fechas = invertirLista(fechas)
    casosPorDia ["FECHA"] = fechas
    # Se filtran los datos y se cuentan los casos positivos, negativos, sospechosos, y defunciones confirmadas por cada fecha
    # Para los casos positivos, negativos y sospechosos la columna "FECHA" representa su fecha de inicio de sintomas, 
    # mientras que para las defunciones, la columna "FECHA" representa la fecha de defunción.
    # No se debe olvidar que aqui solamente se muestran numeros frios, pero cada una de las defunciones representa una vida perdida.
    
    for fecha in casosPorDia["FECHA"]:
        casos_P = covid_df[(covid_df["FECHA_SINTOMAS"] == fecha) & (covid_df["RESULTADO"] == 1) & ((covid_df["ENTIDAD_RES"] == estado) |( estado == 0)) & ((covid_df["MUNICIPIO_RES"] in municipios) | (len(municipios) == 0))]
        casos_N = covid_df[(covid_df["FECHA_SINTOMAS"] == fecha) & (covid_df["RESULTADO"] == 2) & ((covid_df["ENTIDAD_RES"] == estado) |( estado == 0)) & ((covid_df["MUNICIPIO_RES"] in municipios) | (len(municipios) == 0))]
        casos_S = covid_df[(covid_df["FECHA_SINTOMAS"] == fecha) & (covid_df["RESULTADO"] == 3) & ((covid_df["ENTIDAD_RES"] == estado) |( estado == 0)) & ((covid_df["MUNICIPIO_RES"] in municipios) | (len(municipios) == 0))]
        Def = covid_df[(covid_df["FECHA_DEF"] == fecha) & (covid_df["RESULTADO"] == 1)  & ((covid_df["ENTIDAD_RES"] == estado) |( estado == 0)) & ((covid_df["MUNICIPIO_RES"] in municipios) | (len(municipios) == 0))]

        casosPorDia ["CASOS_POSITIVOS"].append(len(casos_P))
        casosPorDia ["CASOS_NEGATIVOS"].append(len(casos_N))
        casosPorDia ["CASOS_SOSPECHOSOS"].append(len(casos_S))
        casosPorDia ["DEFUNCIONES"].append(len(Def))
    return casosPorDia
zonaMetroMty = [39,26,6,46,21,48,31,18,19,9,49,43]
NuevoLeon = 19
covid_df, fecha_actualizacion = obtenerDataFrame()
if (fecha_actualizacion == "0"):
    print ("No se encontró el Data Set")
else:
    print ("\n Fecha de datos: " + str(fecha_actualizacion) + "\n")
    casosAcumulados = obtenerCasosAcumulados(covid_df)
    imprimirAcumulados(casosAcumulados)
    casosPorDia_dict = obtenerCasosPorDia(covid_df, NuevoLeon, zonaMetroMty)
    casosPorDia_df = ps.DataFrame(casosPorDia_dict)
    print(casosPorDia_df.head())

    

