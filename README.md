# COVIDSTATSMX
El objetivo de este proyecto es realizar un análisis de la epidemia de sars-cov-2 en México, se inició en abril del 2020 para practicar el manejo de dataframes y la implementación de modelos de machine learning.


Los datos usados en este proyecto fueron obtenidos del repositorio de datos abiertos de la [Secretaría de Salud](https://datos.gob.mx/busca/dataset/informacion-referente-a-casos-covid-19-en-mexico)

## Descripción de los campos.
* `FECHA_ACTUALIZACION`: Indica la fecha en que se actualizó la información de cada caso.
* `ID_REGISTRO`: Numero de identificador del caso.
* `ORIGEN`: Indica si el caso fue detectado por el sistema de unidades de salud monitoras de enfermedades respiratorias (USMER).
* `SECTOR`: Indica el tipo de institución del Sistema Nacional de Salud que brindó la atención al paciente.
* `ENTIDAD_UM`: Identifica la entidad de la unidad médica que le brindó la atención.
* `SEXO`: Sexo del caso.
* `ENTIDAD_NAC`: Identifica la entidad de nacimiento del paciente.
* `ENTIDAD_RES`: Identifica la entidad de recidencia del paciente.
* `MUNICIPIO_RES`: Identifica el municipio de recidencia del paciente.
* `TIPO_PACIENTE`: Indica si la atención fue ambulatoria o se hospitalizó.
* `FECHA_INGRESO`: Fecha en la que el paciente recibió la atención.
* `FECHA_SINTOMAS`: Fecha del inicio de sintomas del paciente.
* `FECHA_DEF`: Fecha de defunción del paciente, si no aplica será 9999-99-99.
* `INTUBADO`: Indica si el paciente requirió intubación.
* `NEUMONIA`: Indica si al paciente se le diagnosticó con neumonía.
* `EDAD`: Edad del paciente.
* `NACIONALIDAD`: Nacionalidad del paciente.
* `EMBARAZO`: Indica si la paciente está embarazada.
* `HABLA_LENGUA_INDIG`: Indica si el paciente habla lengua indígena.
* `DIABETES`: Indica si el paciente ha sido diagnosticado con diabetes.
* `EPOC`: Indica si el paciente ha sido diagnosticado con EPOC.
* `ASMA`: Indica si el paciente ha sido diagnosticado con asma.
* `INMUSUPR`: Indica si el paciente presenta inmunosupresión.
* `HIPERTENCION`: Indica si el paciente ha sido diagnosticado con hipertención.
* `OTRAS_COM`: Indica si el paciente tiene diagnóstico de otras enfermedades.
* `CARDIOVASCULAR`: Indica si el paciente tiene un diagnóstico de enfermedades cardiovasculares.
* `OBESIDAD`: Indica si el paciente tiene un diagnóstico de obesidad.
* `RENAL_CRONICA`: Indica si el paciente ha sido diagnosticado con insuficiencia renal crónica.
* `TABAQUISMO`: Indica si el paciente tiene el hábito del tabaquismo.
* `OTRO_CASO`: Indica si el paciente esta relacionado con otro caso confirmado.
* `TOMA_MUESTRA`: Indica si al paciente se le tomó muestra.
* `RESULTADO_LAB`: Indica el resultado de laboratorio.
* `CLASIFICACION_FINAL`: Indica la clasificación del paciente.
* `MIGRANTE`: Indica si el paciente es migrante.
* `PAIS_NACIONALIDAD`: Indica la nacionalidad del paciente.
* `PAIS_ORIGEN`: Indica el pais del que partió rumbo a México.
* `UCI`: Indica si el paciente requirió ingresar a una Unidad de Cuidados Intensivos.
