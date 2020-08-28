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
    


def obtenerCasosAcumulados (covid_df):
    # Data Frame que almacenará la columna RESULTADO donde 1 es positivo, 2 es negativo, 3 es pendiente y FECHA_DEF, donde si la fecha es diferente a 9999-99-99 es una defuncion
    casos = ps.concat([covid_df["RESULTADO"], covid_df["FECHA_DEF"]], axis = 1)
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
    return {"Positivos": positivos, "Negativos":negativos, "Pendientes":pendientes, "Defunciones": defunciones}

def obtenerCasosPorDia (covid_df, busqueda_fecha = ""):
    # Lista que guarda las fechas de FECHA_SINTOMA
    fechas = []
    pos_fechas = {}
    # Diccionario que se convertirá en Data Frame
    casosPorDia = {}
    casosPorDia ["FECHA_SINTOMAS"] = []
    casosPorDia ["CASOS_POSITIVOS"] = []
    casosPorDia ["CASOS_NEGATIVOS"] = []
    casosPorDia ["CASOS_PENDIENTES"] = []
    casosPorDia ["DEFUNCIONES"] = []
    total_Casos = len(covid_df)
    #covid_df["FECHA_SINTOMAS"] = ps.to_datetime(covid_df["FECHA_SINTOMAS"])
    #covid_df["FECHA_DEF"] = ps.to_datetime(covid_df["FECHA_DEF"])
    for i in range(total_Casos):
        if covid_df["FECHA_SINTOMAS"][i] not in fechas:
            #print (covid_df["FECHA_SINTOMAS"][i])
            fechas.append(covid_df["FECHA_SINTOMAS"][i])
            casosPorDia ["CASOS_POSITIVOS"].append(0)
            casosPorDia ["CASOS_NEGATIVOS"].append(0)
            casosPorDia ["CASOS_PENDIENTES"].append(0)
            casosPorDia ["DEFUNCIONES"].append(0)
    
    fechas = invertirLista(fechas)
    fechas.sort()
    fechas = invertirLista(fechas)
    casosPorDia ["FECHA_SINTOMAS"] = fechas

    j = 0
    for fecha in fechas:
        pos_fechas[fecha] = j
        j+=1
    
    resbus = {} # Resultado de la busqueda por fecha
    resbus ["CASOS_POSITIVOS"] = []
    resbus ["CASOS_NEGATIVOS"] = []
    resbus ["CASOS_PENDIENTES"] = []
    resbus ["DEFUNCIONES"] = []

    for i in range(total_Casos):
        if (covid_df["RESULTADO"][i] == 1):
            casosPorDia["CASOS_POSITIVOS"][pos_fechas[covid_df["FECHA_SINTOMAS"][i]]] += 1
            if (covid_df["FECHA_SINTOMAS"][i] == busqueda_fecha):
                resbus["CASOS_POSITIVOS"].append(covid_df["ID_REGISTRO"][i])
                resbus["CASOS_NEGATIVOS"].append("0")
                resbus["CASOS_PENDIENTES"].append("0")
                resbus["DEFUNCIONES"].append("0")
        if (covid_df["RESULTADO"][i] == 2):
            casosPorDia["CASOS_NEGATIVOS"][pos_fechas[covid_df["FECHA_SINTOMAS"][i]]] += 1
            if (covid_df["FECHA_SINTOMAS"][i] == busqueda_fecha):
                resbus["CASOS_NEGATIVOS"].append(covid_df["ID_REGISTRO"][i])
                resbus["CASOS_POSITIVOS"].append("0")
                resbus["CASOS_PENDIENTES"].append("0")
                resbus["DEFUNCIONES"].append("0")
        if (covid_df["RESULTADO"][i] == 3):
            casosPorDia["CASOS_PENDIENTES"][pos_fechas[covid_df["FECHA_SINTOMAS"][i]]] += 1
            if (covid_df["FECHA_SINTOMAS"][i] == busqueda_fecha):
                resbus["CASOS_PENDIENTES"].append(covid_df["ID_REGISTRO"][i])
                resbus["CASOS_POSITIVOS"].append("0")
                resbus["CASOS_NEGATIVOS"].append("0")
                resbus["DEFUNCIONES"].append("0")
        if (covid_df["FECHA_DEF"][i] != "9999-99-99" and covid_df["RESULTADO"][i] == 1):
            casosPorDia["DEFUNCIONES"][pos_fechas[covid_df["FECHA_DEF"][i]]] += 1
            if (covid_df["FECHA_DEF"][i] == busqueda_fecha):
                resbus["DEFUNCIONES"].append(covid_df["ID_REGISTRO"][i])
                resbus["CASOS_POSITIVOS"].append("0")
                resbus["CASOS_NEGATIVOS"].append("0")
                resbus["CASOS_PENDIENTES"].append("0")

    return [casosPorDia, resbus]


def imprimirAcumulados (casosA):
    # variable que guarda el indice de letalidad en porcentaje
    inice_L = casosA["Defunciones"] / casosA["Positivos"] * 100
    # Variable que guarda el indice de positividad nacional
    indice_P = casosA["Positivos"] / (casosA["Negativos"] + casosA["Positivos"]) * 100
    print ("  Total de casos estudiados: " + str(total)+ "\n\n" +
            "  Casos Positivos a SARS-CoV-2: " + str(casosA["Positivos"])+ "\n\n" +
            "  Casos No Positivos a SARS-CoV-2: " + str(casosA["Negativos"])+ "\n\n" +
            "  Casos Con Resultado Pendiente: " + str(casosA["Pendientes"]) + "\n\n" +
            "  Defunciones Positicas a SARS-CoV-2: " + str(casosA["Defunciones"]) + "\n\n" +
            "  Tasa de Letalidad: %.3f%s\n\n  Tasa de Positividad : %.3f%s\n" % (inice_L,"%",indice_P,"%"))
    
def obtenerDataFrame (fecha = "hoy"):
    url = "https://raw.githubusercontent.com/EduHdzVillasana/COVIDSTATSMX/master/Datos%20Abiertos"
    x = dt.date.today()
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
    except:
        x = x - dt.timedelta(days = 1)
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
        except:
            covid_df = None
    #print (dt.datetime.now() - x) Para medir el tiempo que se tarda en leer el dataset
    return {"DF": covid_df, "DT": x}

def guardarDataFrame (path = "C:", nombre = "DATAFRAME", tipo = ".xls", dataFrame = None):
    if tipo == ".csv":
        dataFrame.to_csv(os.path.join(path, nombre))
    elif tipo == ".xls":
        dataFrame.to_excel(os.path.join(path, nombre))
    elif tipo == ".json":
        dataFrame.to_json(os.path.join(path, nombre))

def obtenerCasosPorDiaEstado (covid_df, codigo_Estado, lista_de_Municipios,busqueda_fecha = ""):
    # Lista que guarda las fechas de FECHA_SINTOMA
    fechas = []
    pos_fechas = {}
    # Diccionario que se convertirá en Data Frame
    casosPorDia = {}
    casosPorDia ["FECHA_SINTOMAS"] = []
    casosPorDia ["CASOS_POSITIVOS"] = []
    casosPorDia ["CASOS_NEGATIVOS"] = []
    casosPorDia ["CASOS_PENDIENTES"] = []
    casosPorDia ["DEFUNCIONES"] = []
    total_Casos = len(covid_df)
    #covid_df["FECHA_SINTOMAS"] = ps.to_datetime(covid_df["FECHA_SINTOMAS"])
    #covid_df["FECHA_DEF"] = ps.to_datetime(covid_df["FECHA_DEF"])
    for i in range(total_Casos):
        if covid_df["FECHA_SINTOMAS"][i] not in fechas:
            #print (covid_df["FECHA_SINTOMAS"][i])
            fechas.append(covid_df["FECHA_SINTOMAS"][i])
            casosPorDia ["CASOS_POSITIVOS"].append(0)
            casosPorDia ["CASOS_NEGATIVOS"].append(0)
            casosPorDia ["CASOS_PENDIENTES"].append(0)
            casosPorDia ["DEFUNCIONES"].append(0)
    
    fechas = invertirLista(fechas)
    fechas.sort()
    fechas = invertirLista(fechas)
    casosPorDia ["FECHA_SINTOMAS"] = fechas

    j = 0
    for fecha in fechas:
        pos_fechas[fecha] = j
        j+=1
    
    resbus = {} # Resultado de la busqueda por fecha
    resbus ["CASOS_POSITIVOS"] = []
    resbus ["CASOS_NEGATIVOS"] = []
    resbus ["CASOS_PENDIENTES"] = []
    resbus ["DEFUNCIONES"] = []

    for i in range(total_Casos):
        if (covid_df["RESULTADO"][i] == 1 and covid_df["ENTIDAD_RES"][i] == codigo_Estado and covid_df["MUNICIPIO_RES"][i] in lista_de_Municipios):
            casosPorDia["CASOS_POSITIVOS"][pos_fechas[covid_df["FECHA_SINTOMAS"][i]]] += 1
            if (covid_df["FECHA_SINTOMAS"][i] == busqueda_fecha):
                resbus["CASOS_POSITIVOS"].append(covid_df["ID_REGISTRO"][i])
                resbus["CASOS_NEGATIVOS"].append("0")
                resbus["CASOS_PENDIENTES"].append("0")
                resbus["DEFUNCIONES"].append("0")
        if (covid_df["RESULTADO"][i] == 2 and covid_df["ENTIDAD_RES"][i] == codigo_Estado and covid_df["MUNICIPIO_RES"][i] in lista_de_Municipios):
            casosPorDia["CASOS_NEGATIVOS"][pos_fechas[covid_df["FECHA_SINTOMAS"][i]]] += 1
            if (covid_df["FECHA_SINTOMAS"][i] == busqueda_fecha):
                resbus["CASOS_NEGATIVOS"].append(covid_df["ID_REGISTRO"][i])
                resbus["CASOS_POSITIVOS"].append("0")
                resbus["CASOS_PENDIENTES"].append("0")
                resbus["DEFUNCIONES"].append("0")
        if (covid_df["RESULTADO"][i] == 3 and covid_df["ENTIDAD_RES"][i] == codigo_Estado and covid_df["MUNICIPIO_RES"][i] in lista_de_Municipios):
            casosPorDia["CASOS_PENDIENTES"][pos_fechas[covid_df["FECHA_SINTOMAS"][i]]] += 1
            if (covid_df["FECHA_SINTOMAS"][i] == busqueda_fecha):
                resbus["CASOS_PENDIENTES"].append(covid_df["ID_REGISTRO"][i])
                resbus["CASOS_POSITIVOS"].append("0")
                resbus["CASOS_NEGATIVOS"].append("0")
                resbus["DEFUNCIONES"].append("0")
        if (covid_df["FECHA_DEF"][i] != "9999-99-99" and covid_df["RESULTADO"][i] == 1 and covid_df["ENTIDAD_RES"][i] == codigo_Estado and covid_df["MUNICIPIO_RES"][i] in lista_de_Municipios):
            casosPorDia["DEFUNCIONES"][pos_fechas[covid_df["FECHA_DEF"][i]]] += 1
            if (covid_df["FECHA_DEF"][i] == busqueda_fecha):
                resbus["DEFUNCIONES"].append(covid_df["ID_REGISTRO"][i])
                resbus["CASOS_POSITIVOS"].append("0")
                resbus["CASOS_NEGATIVOS"].append("0")
                resbus["CASOS_PENDIENTES"].append("0")

    return [casosPorDia, resbus]


# Lista de Id de municipios
zonaMetroMty = [39,26,6,46,21,48,31,18,19,9,49,43]
NuevoLeon = 19

diccionario = obtenerDataFrame()
covid_df = diccionario["DF"]
fecha_dataset = diccionario["DT"]
print("Cargado Información de " + str(fecha_dataset))
# Vaiable que guarda el total de casos estudiados
total = len(covid_df)
# Variable que guarda los datos de casos acumulados
casosA = obtenerCasosAcumulados(covid_df) 
imprimirAcumulados(casosA)
"""
lcpd = obtenerCasosPorDiaEstado(covid_df, NuevoLeon, zonaMetroMty)
zmMty = lcpd[0]
zmMty_df = ps.DataFrame(zmMty)
fullpath = "C:/Users/alana/Documents/COVIDSTATS/CASOSPORDIA"
nombre = str(fecha_dataset) + "ZONAMETROMONTERREYCPD.xls"
guardarDataFrame(fullpath, nombre, ".xls", zmMty_df)"""

lcpd = obtenerCasosPorDia(covid_df, "13/01/2020")
casosPorDia_dict = lcpd[0]
busqueda = lcpd[1]
casosPorDia_df = ps.DataFrame(casosPorDia_dict)
busqueda_df = ps.DataFrame(busqueda)
fullpath = "C:/Users/alana/Documents/COVIDSTATS/CASOSPORDIA"
nombre = str(fecha_dataset) + "COVIDCPD.xls"
print ("inicio_Plot")
casosPorDia_df.plot(kind = "line", y = "CASOS_POSITIVOS", x = "FECHA_SINTOMAS")
plt.show()
print ("Finalizo_Plot")
guardarDataFrame(fullpath, nombre, ".xls", casosPorDia_df)
#guardarDataFrame("C:/Users/alana/Documents/COVIDSTATS/BUSQUEDAS","PRIMERCASO.xls",".xls", busqueda_df)

