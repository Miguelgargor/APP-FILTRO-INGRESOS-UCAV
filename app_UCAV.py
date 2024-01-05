import pandas as pd                         # DataFrames.
from datetime import datetime, timedelta    # Fechas.
import streamlit as st                      # Streamlit.
from io import BytesIO                      # Transformar DF en Excel.

def funcion_filtrar_por_fecha(UCAV_PAGO_INGRESO, Nombre_Hoja, fecha_inicio_indicada, fecha_fin_indicada=None):

    # Prueba a aplicar la función y si da error comprueba los parámetros introducidos:
    try:
        ## 0º) Fecha_FIN por defecto igual a la Fecha_INICIO ó si es menor que la Fecha_INICIO:
        if fecha_inicio_indicada != None and fecha_inicio_indicada !='': # Si está bien la fecha_inicio...
            fecha_inicio= datetime.strptime(fecha_inicio_indicada, '%d/%m/%Y') # Convertir las cadenas de fecha en objetos de fecha.
        else:  # Si es None ó es vacía--> fecha_inicio = fecha_ayer...
            fecha_ayer= datetime.now() - timedelta(days=31)
            fecha_inicio= fecha_ayer.strftime('%d/%m/%Y')
            fecha_inicio= datetime.strptime(fecha_inicio, '%d/%m/%Y')

        if fecha_fin_indicada != None and fecha_fin_indicada !='': # si está bien la fecha_fin...
            fecha_fin= datetime.strptime(fecha_fin_indicada, '%d/%m/%Y')       # Convertir las cadenas de fecha en objetos de fecha.
        else: # Sino...
            fecha_fin= fecha_inicio
        if fecha_fin < fecha_inicio: # Si la fecha_fin es anterior a la fecha_inicio...
            fecha_fin= fecha_inicio
        #---------------------------------------------------------------------------------------------------------------#
        
        ## 1º) LECTURA DE DATOS (EXCEL "UCAV_PAGO_INGRESO"):
        #### Si no se le pasa NINGÚN NOMBRE de la HOJA con la que se quiere trabajar-> Coge la ÚLTIMA HOJA por defecto:
        if Nombre_Hoja is None or Nombre_Hoja=='':
            Nombre_Hoja=pd.ExcelFile(UCAV_PAGO_INGRESO).sheet_names[-1] ## NOMBRE de la ÚLTIMA HOJA del EXCEL ##

        datos= pd.read_excel(UCAV_PAGO_INGRESO, header= 1, sheet_name=Nombre_Hoja)  ## IMPORTANTE: .xlsx  !!!!
        #---------------------------------------------------------------------------------------------------------------#

        ## 2º) QUEDARSE SÓLO CON LAS COLUMNAS NECESARIAS DEL EXCEL "UCAV_PAGO_INGRESO":
        datos_ordenados= datos[['ID Facturación', 'ID', 'Fecha Vto', 'Nombre','Última', '2º Apellido']].copy()
        #---------------------------------------------------------------------------------------------------------------#

        ## 3º) Añadir las columnas vacías necesarias:
        nuevas_columnas= ['FECHA DE PRIMERA MATRÍCULA', 'Nombre Largo', 'Fecha de nacimiento', 'ESTADO', 'SOLICITADO', 'CANTIDAD PENDIENTE', 'DIA DE PAGO', 'CORTE DE PLATAFORMA',
                        'COMENTARIOS', 'INICIOS DE SESIÓN', 'TIEMPO DE CONEXIÓN (HORAS)', 'CONTACTO CON PROFESORES', 'HA HECHO TRABAJOS', 'PRESENTADO A EXÁMENES',
                        'ULTIMA CONEXIÓN', 'TIENE NUMERO DE CUENTA']

        for col in nuevas_columnas:
            datos_ordenados[col]=None
        #---------------------------------------------------------------------------------------------------------------#

        ## 4º) ORDENAR LAS COLUMNAS:
        datos_ordenados= datos_ordenados[['ID Facturación', 'ID', 'FECHA DE PRIMERA MATRÍCULA', 'Nombre Largo', 'Fecha Vto', 'Nombre', 'Última', '2º Apellido','Fecha de nacimiento',
                                'ESTADO', 'SOLICITADO', 'CANTIDAD PENDIENTE', 'DIA DE PAGO', 'CORTE DE PLATAFORMA', 'COMENTARIOS', 'INICIOS DE SESIÓN', 'TIEMPO DE CONEXIÓN (HORAS)',
                                'CONTACTO CON PROFESORES', 'HA HECHO TRABAJOS', 'PRESENTADO A EXÁMENES', 'ULTIMA CONEXIÓN', 'TIENE NUMERO DE CUENTA']]
        #---------------------------------------------------------------------------------------------------------------#

        ## 5º) Cambiar el nombre de la primera columna para que coincida:
        datos_ordenados= datos_ordenados.rename(columns={'ID Facturación': 'TITULACIÓN'})
        #---------------------------------------------------------------------------------------------------------------#

        ## 6º) CAMBIO DEL FORMATO DE LA FECHA DE VENCIMIENTO:
        datos_ordenados['Fecha Vto']= pd.to_datetime(datos_ordenados['Fecha Vto'], format='%d/%m/%Y')
        #---------------------------------------------------------------------------------------------------------------#

        ## 7º) Filtrado del DataFrame para obtener solo las filas dentro del rango de fechas:
        df_filtrado_FECHAS = datos_ordenados[(datos_ordenados['Fecha Vto']>=fecha_inicio) & (datos_ordenados['Fecha Vto'] <= fecha_fin)].copy()
        #---------------------------------------------------------------------------------------------------------------#

        ## 8º) COMPLETAR CON 0 a la izquierda de los ID:
        # Calcular la longitud máxima de ID después de eliminar los valores NaN:
        max_longitud_id= df_filtrado_FECHAS['ID'].dropna().astype(str).str.len().max()

        # Longitud máxima de los ID para rellenar con 0 hasta tener todos los ID la misma longitud:
        if pd.notna(max_longitud_id):
            max_longitud_id = int(max_longitud_id)
        else:
            max_longitud_id = 0  # Si todos los valores son NaN, establece la longitud máxima en 0.
        df_filtrado_FECHAS['ID'] = df_filtrado_FECHAS['ID'].astype(str).str.zfill(max_longitud_id) # Rellena los ID con tantos 0 a la izquierda como sea necesario para tener la misma longitud todos los ID.
        #---------------------------------------------------------------------------------------------------------------#

        ## 9º) Eliminar FILAS DUPLICADAS basándose en todas las columnas:
        df_filtrado_FECHAS.drop_duplicates(inplace=True)
        #---------------------------------------------------------------------------------------------------------------#

        ## 10º) Cambiar el formato de la Fecha Vto. para su visualización a tipo dd/mm/yyyy:
        df_filtrado_FECHAS['Fecha Vto'] = df_filtrado_FECHAS['Fecha Vto'].dt.strftime('%d/%m/%Y')
        #---------------------------------------------------------------------------------------------------------------#
                
        return df_filtrado_FECHAS  # Devuelve los datos filtrados por fecha inicio y fecha final.

    ### EN CASO DE ERROR-> Comprobar los parámetros:
    except Exception as e:
        st.warning("¡COMPRUEBE LOS PARÁMETROS INTRODUCIDOS!:", str(e), icon="⚠️")
#############################################################################################################################

## A) CONFIGURACIÓN GENERAL DE LA PÁGINA WEB:
st.set_page_config(page_title="App Filtrado Alumnos Ingreso",                                                             # Nombre en el Navegador.
                   page_icon="https://raw.githubusercontent.com/Miguelgargor/IMAGENES_APPs/main/logoUcav_navegador.png",  # Icono del Navegador.
                   layout="wide",                                                                                         # Mostrarlo en toda la pantalla.
                   initial_sidebar_state="expanded")                                                                      # Mostrar la barra lateral inicialmente.
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

## B) BARRA LATERAL: (Indicar los parámetros de la Función):
with st.sidebar:                              # Barra Lateral.
    st.title(':red_circle: :red[FILTROS]')    # Título.
    st.header('ARCHIVO:')                     # Encabezado.
    #.................................................................#
    with st.expander(':blue[**Cargar archivo excel**] :open_file_folder:'):   # BOTÓN QUE SE ABRE.
        UCAV_PAGO_INGRESO = st.file_uploader(label="Elegir el Excel **UCAV_PAGO_INGRESO**", type=["xlsx", "xls"]) # SUBIR UN ARCHIVO.
    st.divider()   # LÍNEA HORIZONTAL.
    #.................................................................#
    st.header('FILTRO POR FECHAS:')
    fecha_menosunmes_menosundia= (datetime.now() - timedelta(days=31)).strftime('%d/%m/%Y')
    fecha_menosunmes_menos5dias= (datetime.now() - timedelta(days=35)).strftime('%d/%m/%Y')
    fecha_inicio_indicada, fecha_fin_indicada= st.columns(2)
    with fecha_inicio_indicada:
        fecha_inicio_indicada = st.text_input(':blue[**Fecha Desde**] (Ejemplo: {})'.format(fecha_menosunmes_menos5dias), fecha_menosunmes_menosundia) # ENTRADA DE TEXTO.

    with fecha_fin_indicada:
        fecha_fin_indicada = st.text_input(':blue[**Fecha Hasta**] (Ejemplo: {})'.format(fecha_menosunmes_menos5dias), fecha_menosunmes_menosundia)    # ENTRADA DE TEXTO.
    st.divider()   # LÍNEA HORIZONTAL.
    #.................................................................#
    st.header('HOJA:')
    with st.expander(':blue[Hoja del Excel a filtrar]'):   # BOTÓN QUE SE ABRE.
        Nombre_Hoja = st.text_input("Dejar en blanco para usar la última hoja del Excel.") # ENTRADA DE TEXTO.
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

## C) CUERPO DE LA PÁGINA WEB:
col1, col2, col3 = st.columns([40, 0.5, 59.95])   # COLUMNAS CON DISTINTOS ANCHOS. (En %).

## C.1.) IMAGEN CON HIPERVÍNCULO: (En la Columna 1):
with col1:                       # URL HIPERVÍNCULO #      # Se abrirá en una nueva pestaña #    # URL IMAGEN #                                                                     # ANCHO #
    col1 = st.markdown('<a href="https://www.ucavila.es/" target="_blank"><img src="https://raw.githubusercontent.com/Miguelgargor/IMAGENES_APPs/main/UCAV_logo.png" alt="UCAV Logo" width="300"></a>',
                       unsafe_allow_html=True) # Permitir usar HTML #

with col3:
    col3= st.header('FILTRADO DE DATOS PAGO POR INGRESOS')

    #--------------------------------------------------------------------------------------#
st.write(''); st.write('') # LÍNEAS en BLANCO.
# Escritura.
st.write('Esta app web te permitirá filtrar los datos de los alumnos que tienen sus pagos por transferencia bancaria,', 
         'con el fin de modificarlos el formato necesario para compatibilizarlo con el archivo Excel del Drive.')
st.write('Primero elige los filtros necesarios en la barra lateral. Después, sólamente tienes que pulsar en "**FILTRAR**".')
st.write(''); st.write('') # LÍNEAS en BLANCO.
    #--------------------------------------------------------------------------------------#

## C.2.) BOTÓN de EJECUCIÓN:
if st.button(":blue[**FILTRAR**]"):    # De color AZUL (:blue[]) y en NEGRITA(** **).
    if UCAV_PAGO_INGRESO is not None:
        try:
            with st.spinner('Cargando...'):      ### CARGANDO... ###
                # Llamar a la función:
                df_resultado = funcion_filtrar_por_fecha(UCAV_PAGO_INGRESO, Nombre_Hoja, fecha_inicio_indicada, fecha_fin_indicada)

                def formatear_fecha(fecha): ## COMPLETAR LAS FECHAS CON LOS 0 NECESARIOS--> ej.: 01/09/2023.
                    partes= fecha.split('/') # Divide la fecha en sus partes.
                    # Añade ceros a la izquierda si es necesario:
                    dia= partes[0].zfill(2)
                    mes= partes[1].zfill(2)
                    año= partes[2]
                    # Formatea la fecha como 'dd-mm-yyyy':
                    fecha_formateada = f'{dia}-{mes}-{año}'
                    return fecha_formateada
                #··································································#

##C.3.) GUARDAR EL RESULTADO:
                if len(df_resultado)>= 1:                                       # Si NO es una tabla vacía... GUÁRDALA...
                    st.success(" ¡Datos filtrados correctamente!", icon="✅")  # MENSAJE de ÉXITO.
                    df_resultado.reset_index(drop=True, inplace=True)           # RESETEAR el ÍNDICE (y eliminar el anterior).
                    df_resultado.index= df_resultado.index+1                    # Empezar el ÍNDICE desde el 1.
                    st.dataframe(df_resultado)                                  # MOSTRAR el DF RESULTADO.
                    buffer= BytesIO()                                           # ¡¡¡Para CONVERTIR el DF -> En EXCEL!!!
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df_resultado.to_excel(writer, sheet_name='DATOS_FILTRADOS', index=False)  

                    if fecha_fin_indicada != None and fecha_fin_indicada !='' and fecha_fin_indicada > fecha_inicio_indicada: # Si está bien la fecha_fin...
                        fecha_inicio_guardar = formatear_fecha(fecha_inicio_indicada)   # fecha_inicio_indicada.replace('/', '-')  # Cambio de / por - para que se pueda guardar el archivo.
                        fecha_fin_guardar = formatear_fecha(fecha_fin_indicada)         # fecha_fin_indicada.replace('/', '-').
                        if fecha_inicio_guardar==fecha_fin_guardar:                     # Si es solo un día, que se guarde sólo con la primera fecha_inicio.
                            ### BOTÓN de DOWNLOAD!!   
                            st.download_button(label=':green[**Descargar Resultados**] :inbox_tray:',                                    # NOMBRE del BOTÓN. (Verde y Negrita + Emoji).
                                                data= buffer,                                                                            # DATOS.
                                                file_name= 'UCAV_PAGO_INGRESO_DATOS_FILTRADOS_DEL_{}.xlsx'.format(fecha_inicio_guardar)) # NOMBRE ARCHIVO que se GUARDA.
                        #..................................................................................................................................................................#
                        else:                                                           # Si es más de un día, que se guarde con el intervalo de tiempo.
                            ### BOTÓN de DOWNLOAD!!   
                            st.download_button(label=':green[**Descargar Resultados**] :inbox_tray:',                                    # NOMBRE del BOTÓN. (Verde y Negrita + Emoji).
                                                data= buffer,                                                                            # DATOS.
                                                file_name= 'UCAV_PAGO_INGRESO_DATOS_FILTRADOS_DESDE_{}_HASTA_{}.xlsx'.format(fecha_inicio_guardar, fecha_fin_guardar)) # NOMBRE ARCHIVO que se GUARDA.
                        #..................................................................................................................................................................#
                    else:
                        fecha_inicio_guardar = formatear_fecha(fecha_inicio_indicada) # fecha_inicio_indicada.replace('/', '-')  # Cambio de / por - para que se pueda guardar el archivo.
                        ### BOTÓN de DOWNLOAD!!      
                        st.download_button(label=':green[**Descargar Resultados**] :inbox_tray:',                                    # NOMBRE del BOTÓN. (Verde y Negrita + Emoji).
                                            data= buffer,                                                                            # DATOS.
                                            file_name= 'UCAV_PAGO_INGRESO_DATOS_FILTRADOS_DEL_{}.xlsx'.format(fecha_inicio_guardar))  # NOMBRE ARCHIVO que se GUARDA.
                else:
                    st.write('')                                                 # Línea en Blanco.
                    st.write(':red[***¡NO HAY REGISTROS PARA ESTAS FECHAS!***]') # SI len(df)=0.
                    st.write('Prueba con otras fechas.')                         # Texto.

        except Exception as e:             # Si al intentar ejecutar la FUNCIÓN hay un ERROR...
            st.error(f"Error MIGUEL: {str(e)}")
    else:
        st.warning(' ¡Cargue un archivo de datos "UCAV_PAGO_INGRESO_DATOS" válido!', icon="⚠️") # Muestra como WARNING si NO has insertado el ARCHIVO CORRECTO de DATOS.
####################################################################################################################################################################
