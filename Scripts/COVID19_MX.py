# Program used to analyse and create plots of sars-cov-2 cases in Mexico and tweet them.

import pandas as pd 
import os
import datetime as dt
import matplotlib.pyplot as plt
import time
import sys

sys.path.insert(0,'../../../TweetCOVIDSTATSMX')
from My_Tweet import My_Tweet

# Class to store covid cases by state data
# Entity = State or City (future)
class Entity:
    name = ""
    ht = "" #Hash Tag use in twitter
    positiveC = 0
    negativeC = 0
    suspectedC = 0
    deceased = 0
    dpm = 0.0 # deaths per millon

# Function used to sumarize a CLASIFICACION_FINAL value
def getResult (cl):
    positive = [1,2,3]
    negative = [7]
    #suspicious = 6

    if (cl in positive):
        return 1
    elif (cl in negative):
        return 2
    else:
        return 3


# Function used to add a result column in the main data frame summarizing the "CLASIFICACION_FINAL" column
def addResult (data_frame):
    result = []
    for cl in data_frame["CLASIFICACION_FINAL"]:
        result.append(getResult(cl))
    data_frame["RESULTADO"] = result


# Function to get the main data frame from a url (due to file size it is obtained locally temporarily)
# Get today´s or yesterday´s file
def getDataFrame ():
    #url = "https://raw.githubusercontent.com/EduHdzVillasana/COVIDSTATSMX/master/Datos%20Abiertos"
    url = "../../../COVIDSTATSMX/Datos Abiertos"
    # Geting the file´s name YYMMDDCOVID19MEXICO.csv
    td = dt.date.today()
    date = str(td)
    sufix = "COVID19MEXICO.csv"

    year = str(td.year - 2000)

    if td.month >= 10:
        month = str(td.month)
    else:
        month = "0" + str(td.month)
    
    if td.day >= 10:
        day = str(td.day)
    else:
        day = "0" + str(td.day)
    
    prefix = year + month + day

    try:
        covid_df = pd.read_csv(url + "/" + prefix + sufix, encoding = 'latin1')
        print("DataSet Cargado")
    except:
        td = td - dt.timedelta(days = 1)
        date = str(td)
        year = str(td.year - 2000)

        if td.month >= 10:
            month = str(td.month)
        else:
            month = "0" + str(td.month)
        
        if td.day >= 10:
            day = str(td.day)
        else:
            day = "0" + str(td.day)
        
        prefix = year + month + day

        try:
            covid_df = pd.read_csv(url + "/" + prefix + sufix, encoding = 'latin1')
            print("DataSet Cargado")
        except:
            covid_df = None
            date = "0"
            print("No se encontro el archivo")
    return covid_df, date

# Save a dataframe with name, path and file type
def saveDataFrame (path = "C:", name = "DATAFRAME.xls", type = "xls", dataFrame = None):
    if dataFrame is not None:
        if type == "csv":
            dataFrame.to_csv(os.path.join(path,name))
        elif type == "xls":
            dataFrame.to_excel(os.path.join(path,name))
        elif type == "json":
            dataFrame.to_json(os.path.join(path,name))
    else:
        raise Exception('DataFrame is None')

# Print the cumulative cases
def printCumulativeCases (cCases):
    # mortality rate
    mRate = cCases["Defunciones"] / cCases["Positivos"] * 100
    # positivity index
    pIndex = cCases["Positivos"] / (cCases["Negativos"] + cCases["Positivos"]) * 100

    print ("  Total de casos estudiados: " + str(cCases["Total"])+ "\n\n" +
            "  Casos Positivos a SARS-CoV-2: " + str(cCases["Positivos"])+ "\n\n" +
            "  Casos No Positivos a SARS-CoV-2: " + str(cCases["Negativos"])+ "\n\n" +
            "  Casos Con Resultado Pendiente: " + str(cCases["Pendientes"]) + "\n\n" +
            "  Defunciones Positivas a SARS-CoV-2: " + str(cCases["Defunciones"]) + "\n\n" +
            "  Tasa de Letalidad: %.3f%s\n\n  Tasa de Positividad : %.3f%s\n" % (mRate,"%",pIndex,"%"))

# Save on a dict the comulative cases
def getComulativeCases (covid_df):
    cases = covid_df[["RESULTADO","FECHA_DEF"]]
    positiveC = len(cases[cases["RESULTADO"] == 1])
    negativeC = len(cases[cases["RESULTADO"] == 2])
    suspectedC = len(cases[cases["RESULTADO"] == 3])
    deceased = len(cases[(cases["RESULTADO"] == 1) & (cases["FECHA_DEF"] != "9999-99-99")])
    dictCC = {
        "Positivos": positiveC,
        "Negativos": negativeC,
        "Pendientes": suspectedC,
        "Defunciones": deceased,
        "Total": len(cases)
    }
    return dictCC

# Get a list with dates YYYY-MM-DD
def getDateList (today_s):
    i = dt.date(2020,1,1) # Covid cases register starts on Junuary First 2020
    today_l = today_s.split('-')
    td = dt.date(int(today_l[0]),int(today_l[1]),int(today_l[2]))
    p_date = str(i.year)+"-"+"0"+str(i.month)+"-"+"0"+str(i.day)
    dates = [p_date]

    while i != td:
        i += dt.timedelta(days = 1)
        if (i.month < 10):
            month = "0"+str(i.month)
        else:
            month = str(i.month)
        
        if (i.day < 10):
            day = "0"+str(i.day)
        else:
            day = str(i.day)

        p_date = str(i.year) + "-" + month + "-" + day
        dates.append(p_date)
    return dates


# Filter the data and get a dict with the cases registraded by day
# There is an option where the state and county can be specified
def getCasesByDay (covid_df, dates, state = 0, countys = []):
    casesBD = {} # it will be changed to data frame

    casesBD ["FECHA"] = []
    casesBD ["CASOS_POSITIVOS"] = []
    casesBD ["CASOS_NEGATIVOS"] = []
    casesBD ["CASOS_SOSPECHOSOS"] = []
    casesBD ["DEFUNCIONES"] = []
    casesBD ["FECHA"] = dates
    #totalCases = len(covid_df)

    # The data is filtered and positive cases, negative cases, suspicius cases and confirmed deaths for each day are count
    # For positive, negative and suspicious cases the column "FECHA" represents the day when the symptoms started,
    # while for deaths, it represent the date of death
    # It should not be forgotten that only cold numbers are shown here, but each one of the deaths represents a life lost.

    for date in casesBD["FECHA"]:
        casesO = covid_df[["FECHA_SINTOMAS", "RESULTADO","FECHA_DEF"]][((covid_df["ENTIDAD_RES"] == state)
        |( state == 0)) 
        & ((covid_df["MUNICIPIO_RES"].isin (countys)) 
        | (len(countys) == 0))]

        cases = casesO[casesO["FECHA_SINTOMAS"] == date]
        positiveC = cases[cases["RESULTADO"] == 1]
        negativeC = cases[cases["RESULTADO"] == 2]
        suspectedC = cases[cases["RESULTADO"] == 3]

        deceasedC = casesO[(casesO["FECHA_DEF"] == date)
        & (casesO["RESULTADO"] == 1)]

        casesBD["CASOS_POSITIVOS"].append(len(positiveC))
        casesBD["CASOS_NEGATIVOS"].append(len(negativeC))
        casesBD["CASOS_SOSPECHOSOS"].append(len(suspectedC))
        casesBD["DEFUNCIONES"].append(len(deceasedC))
    return casesBD

# Function to create and save graph´s images
def createGraph (name, casesBD_df, date):
    plt.figure(figsize = (20,10))
    plt.plot(casesBD_df["FECHA"],casesBD_df["CASOS_POSITIVOS"],"r")
    plt.plot(casesBD_df["FECHA"],casesBD_df["DEFUNCIONES"],"b")
    plt.plot(casesBD_df["FECHA"],casesBD_df["CASOS_SOSPECHOSOS"],"g")
    plt.title("GRAFICA " + name +" "+ date + "\nCASOS POSITIVOS (ROJO)\nDEFUNCIONES (AZUL)\nCASOS SOSPECHOSOS (VERDE)")
    plt.savefig("../Graficas/" + date + "/"+ name +" " + date + ".png")


covid_df, updateDate = getDataFrame()
if (covid_df is not None):
    dates = getDateList(updateDate)
    os.makedirs("../Graficas/" + updateDate, exist_ok=True)
    os.makedirs("../Casos_Por_Dia/" + updateDate, exist_ok=True)
    cbd = "../Casos_Por_Dia/" + updateDate # Cases by day folder path
    addResult(covid_df)

    # National View
    cCases =  getComulativeCases(covid_df)
    printCumulativeCases (cCases)
    time.sleep(5)
    
    national = Entity()
    national.positiveC = cCases["Positivos"]
    national.negativeC = cCases["Negativos"]
    national.suspectedC = cCases["Pendientes"]
    national.deceased = cCases["Defunciones"]
    national.dpm = national.deceased/127091642*1000000
    national.ht = "#México"
    national.name = "NACIONAL"

    # Get national cases by day
    casesBD_dict = getCasesByDay(covid_df, dates)
    casesBD_df = pd.DataFrame(casesBD_dict)
    saveDataFrame(path = cbd,
    name = updateDate +"-NACIONAL.xls",
    type = "xls",
    dataFrame = casesBD_df)

    createGraph("NACIONAL", casesBD_df, updateDate)
    print("Grafica Nacional Guardada")

    # Get Cases by day for each state
    population = pd.read_csv("../Poblacion/Poblacion.csv")
    #states = {"ESTADO":[],"HASHTAG":[],"CASOS_POSITIVOS":[],"CASOS_NEGATIVOS":[],"DEFUNCIONES":[],"SOSPECHOSOS":[],"TASA_POSITIVIDAD":[],"TASA_MORTALIDAD":[],"MUERTES_POR_MILLON":[],"HABITANTES":[]}
    ht = ["#Aguascalientes","#BajaCalifornia","#BajaCaliforniaSur","#Campeche","#Chiapas","#Chihuahua","#CDMX","#Coahuila","#Colima"
    ,"#Durango","#Edoméx","#Guanajuato","#Guerrero","#Hidalgo","#Jalisco","#Michoacán","#Morelos","#Nayarit","#NuevoLeón","#Oaxaca"
    ,"#Puebla","#Querétaro","#QuintanaRoo","#SanLuisPotosi","#Sinaloa","#Sonora","#Tabasco","#Tamaulipas","#Tlaxcala","#Veracruz"
    ,"#Yucatán","#Zacatecas"]
    statesDict = {}
    i = 0
    today = updateDate.split("-")
    day = today[2]
    month = today[1]
    year = today[0]
    for idState in population["CLAVE"]:
        # Name of state
        STATE = population[population["CLAVE"] == idState]["ESTADO"].tolist()[0]

        statesDict[STATE] = pd.DataFrame(getCasesByDay(covid_df, dates, state = idState))
    
        saveDataFrame(path = cbd,
        name = updateDate +"-"+STATE+".xls",
        type = "xls",
        dataFrame = statesDict[STATE])

        createGraph(STATE,statesDict[STATE],updateDate)
        plt.close()
        print (STATE + " LISTO")

        # Number Positive, Negative, Suspicious and Deceased cases
        """
        positiveC = len (covid_df[(covid_df["ENTIDAD_RES"] == idState)
        & (covid_df["RESULTADO"] == 1)])

        negativeC = len (covid_df[(covid_df["ENTIDAD_RES"] == idState)
        & (covid_df["RESULTADO"] == 2)])

        deceased = len (covid_df[(covid_df["ENTIDAD_RES"] == idState)
        & (covid_df["RESULTADO"] == 1)
        & (covid_df["FECHA_DEF"] != "9999-99-99")])

        suspiciousC = len (covid_df[(covid_df["ENTIDAD_RES"] == idState)
        & (covid_df["RESULTADO"] == 3)])"""

        positiveC = sum(statesDict[STATE]["CASOS_POSITIVOS"])
        negativeC = sum(statesDict[STATE]["CASOS_NEGATIVOS"])
        deceased = sum(statesDict[STATE]["DEFUNCIONES"])
        suspiciousC = sum(statesDict[STATE]["CASOS_SOSPECHOSOS"])

        # Positive Index
        positiveIndex = positiveC / (negativeC + positiveC)

        # Mortality Rate
        mRate = deceased/positiveC

        # Deaths per Million
        popTotal = int(population[population["CLAVE"] == idState]["POBLACION"].tolist()[0])
        dpm = deceased/popTotal * 1000000

        # Info is incerted in a dict (not actualy used)
        """
        states["ESTADO"].append(STATE)
        states["CASOS_POSITIVOS"].append(positiveC) 
        states["CASOS_NEGATIVOS"].append(negativeC)
        states["DEFUNCIONES"].append(deceased)
        states["SOSPECHOSOS"].append(suspiciousC)
        states["TASA_POSITIVIDAD"].append(positiveIndex)
        states["TASA_MORTALIDAD"].append(mRate)
        states["MUERTES_POR_MILLON"].append(dpm)
        states["HABITANTES"].append(popTotal)
        states["HASHTAG"].append(ht[i])
        """

        statesInfo = Entity
        statesInfo.positiveC = positiveC
        statesInfo.negativeC = negativeC
        statesInfo.deceased = deceased
        statesInfo.suspectedC = suspiciousC
        statesInfo.ht = ht[i]
        statesInfo.name = STATE
        statesInfo.dpm = dpm

        info = "#COVID19 en "+statesInfo.ht+" #México al "+day+"/"+month+"/"+year+"\nCasos Positivos: "+str(statesInfo.positiveC)
        info +="\nCasos Sospechosos: "+str(statesInfo.suspectedC)+"\nCasos Negativos: "+str(statesInfo.negativeC)
        info +="\nFallecidos: "+str(statesInfo.deceased)
        imagepath = updateDate+"/"+statesInfo.name+" "+updateDate+".png"
        My_Tweet.post(info,imagepath)

        i+=1

    info = "#COVID19 en "+national.ht+" al "+day+"/"+month+"/"+year+"\nCasos Positivos: "+str(national.positiveC)
    info +="\nCasos Sospechosos: "+str(national.suspectedC)+"\nCasos Negativos: "+str(national.negativeC)
    info +="\nFallecidos: "+str(national.deceased)

    imagepath = updateDate+"/"+national.name+" "+updateDate+".png"
    My_Tweet.post(info,imagepath)
    #states_df = pd.DataFrame(states)
    #print (states_df)
    #saveDataFrame(dataFrame = states_df)
