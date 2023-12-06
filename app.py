import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
from streamlit_folium import folium_static
import folium

class VisualizadorDatos:
    def __init__(self, archivo):
        self.data = pd.read_csv(archivo, delimiter=";")
        self.data_ubigeos = pd.read_csv('TB_UBIGEOS.csv')
        self.data_ingresos = pd.read_csv('ingresos.csv', delimiter=";", encoding='latin-1')
        self.data_ACP = pd.read_csv('archivo_ACP.csv', delimiter=";", encoding='latin-1')
        self.columnas_departamento = ['DEPARTAMENTO1']
        self.columnas_provincia = ['DEPARTAMENTO1', 'PROVINCIA1']
        self.columnas_distrito = ['DEPARTAMENTO1', 'PROVINCIA1', 'DISTRITO1']
        self.columnas_anp_cate = ['ANP_CATE']
        self.columnas_acp_ubpo = ['ACP_UBPO']

    def filtrar_y_eliminar_nulos(self, data_frame):
        return data_frame.dropna()

    def convertir_a_str(self, data_frame):
        return data_frame.applymap(str)

    def concatenar_columnas(self, data_frame, columnas):
        data_frame['Location'] = data_frame.apply(lambda row: '; '.join(row), axis=1)
        return data_frame

    def contar_ocurrencias(self, data_frame):
        conteo = data_frame['Location'].value_counts().reset_index()
        conteo.columns = ['Ubicacion', 'Count']
        return conteo

    def generar_grafica(self, conteo, titulo):
        figura = px.bar(conteo, x='Ubicacion', y='Count', title=titulo)
        return figura

    def mostrar_grafica(self, figura):
        st.plotly_chart(figura)
    
    def generar_mapa_ubigeos(self, gdf):
        m = folium.Map(location=[-9.1900, -75.0152], zoom_start=5, control_scale=True)

        # Define un diccionario que asigne colores a cada categoría única en ANP_CATE
        color_mapping = {
            'Reserva Nacional': {'color': 'blue', 'imagen_url': 'https://blog.redbus.pe/wp-content/uploads/2020/07/000483356W.jpg'},
            'Parque Nacional': {'color': 'green', 'imagen_url': 'https://www.machupicchuterra.com/wp-content/uploads/parque-gueppi-sekime-full-media.jpg'},
            'Reserva Comunal': {'color': 'red', 'imagen_url': 'https://imgs.mongabay.com/wp-content/uploads/sites/25/2018/04/17151228/RC-AMARAKAERI-IN%CC%83IGO-MANEIRO_058.jpg'},
            'Santuario Nacional': {'color': 'beige', 'imagen_url': 'https://blog.redbus.pe/wp-content/uploads/2020/06/Calipuy.jpg'},
            'Bosque de Protección': {'color': 'orange', 'imagen_url': 'https://elcomercio.pe/resizer/3X4JnzzvB2ohTvodpgv4NwDw8Dg=/580x330/smart/filters:format(jpeg):quality(75)/cloudfront-us-east-1.images.arcpublishing.com/elcomercio/WQ4OOR2LQZDVVNIFY377GNC2IA.jpeg'},
            'Refugio de Vida Silvestre': {'color': 'darkgreen', 'imagen_url': 'https://www.aboutespanol.com/thmb/UYohUziWoKGbS7G9-YqCcYLwxDI=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/laquipampa-597b8d455f9b58928bd9418e.jpg'},
            'Santuario Histórico': {'color': 'purple', 'imagen_url': 'https://usil-blog.s3.amazonaws.com/PROD/blog/image/dia-santuario-historico-machu-picchu.jpg'},
            'Coto de Caza': {'color': 'darkblue', 'imagen_url': 'https://aider.com.pe/wp-content/uploads/2023/07/venado-1-768x576.jpg'},
            'Reserva Paisajistica': {'color': 'darkred', 'imagen_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Espejos_de_agua_Reserva_Paisajistica_Nor_Yauyos_Cochas.jpg/1200px-Espejos_de_agua_Reserva_Paisajistica_Nor_Yauyos_Cochas.jpg'},
        }

        for idx, row in gdf.iterrows():
            categoria_anp = row['ANP_CATE']
            categoria_info = color_mapping.get(categoria_anp, {'color': 'gray', 'imagen_url': 'URL_DEFAULT'})
            color = categoria_info['color']
            imagen_url = categoria_info['imagen_url']

            # Construye el contenido del popup con la imagen correspondiente
            popup_content = f"<p>{row['distrito']}</p><img style='width: 100px; height:100px; object-fit: cover;' src='{imagen_url}' alt='imagen'>"

            # Usa 'Marker' en lugar de 'folium.Marker' y especifica el color directamente
            folium.Marker(
                location=[row['latitud'], row['longitud']],
                popup=folium.Popup(html=popup_content, max_width=300),
                icon=folium.Icon(color=color)
            ).add_to(m)

        # Construye la cadena HTML con información de todos los colores y categorías
        recuadro_html = """
        <div style="position: absolute; z-index: 100; bottom: -310px; right: 20px; background-color: white; color: black; padding: 10px; border: 1px solid black;">
            {categorias_html}
        </div>
        """

        categorias_html = ""
        for categoria, categoria_info in color_mapping.items():
            categoria_html = f'<p style="margin: 0; font-size:12px"><span style="width: 15px; height: 15px; display: inline-block; background-color: {categoria_info["color"]};"></span> {categoria}</p>'
            categorias_html += categoria_html

        html_code = recuadro_html.format(categorias_html=categorias_html)
        st.markdown(html_code, unsafe_allow_html=True)

        return m

    def mostrar_grafica_seleccionada(self, figuras, nombres_figuras):
        opcion_seleccionada = st.selectbox("Selecciona la gráfica a mostrar", nombres_figuras)
        indice_seleccionado = nombres_figuras.index(opcion_seleccionada)
        self.mostrar_grafica(figuras[indice_seleccionado])
    
    def contar_ocurrencias_acp_tipro(self, data_frame, acp_tipro_seleccionado):
        # Filtrar el DataFrame según la selección de ACP_TIPRO
        if acp_tipro_seleccionado:
            data_frame = data_frame[self.data_ACP['ACP_TIPRO'] == acp_tipro_seleccionado]

        # Contar las ocurrencias de cada ubicación
        conteo = data_frame['Location'].value_counts().reset_index()
        conteo.columns = ['Ubicacion', 'Count']
        return conteo
    
    def mostrar_grafica_acp(self, data_acp_ubpo, categorias_acp_tipro):
        acp_tipro_seleccionado = st.selectbox("Selecciona la categoría de ACP_TIPRO", categorias_acp_tipro, index=0)
    
        # Contar las ocurrencias de ACP_UBPO considerando la selección de ACP_TIPRO
        conteo_acp_ubpo_acp_tipro = self.contar_ocurrencias_acp_tipro(data_acp_ubpo, acp_tipro_seleccionado)
        
        # Generar gráfica de barras para ACP_UBPO considerando ACP_TIPRO
        fig_acp_ubpo_acp_tipro = self.generar_grafica(conteo_acp_ubpo_acp_tipro, f"Conteo por ACP_UBPO ({acp_tipro_seleccionado})")
        
        # Mostrar la gráfica de ACP_UBPO considerando ACP_TIPRO en la aplicación Streamlit
        self.mostrar_grafica(fig_acp_ubpo_acp_tipro)
    
    def grafica_ingresos(self, data):
        # Filtrar y eliminar valores nulos
        data_filtrada = self.filtrar_y_eliminar_nulos(data[['TIPO_DOC_VTA', 'UNIDAD_DEPENDENCIA']])

        # Contar las ocurrencias de cada combinación de 'TIPO_DOC_VTA' y 'UNIDAD_DEPENDENCIA'
        conteo_ingresos = data_filtrada.groupby(['TIPO_DOC_VTA', 'UNIDAD_DEPENDENCIA']).size().reset_index(name='Count')

        # Generar la gráfica de barras apiladas
        figura_ingresos = px.bar(conteo_ingresos, x='UNIDAD_DEPENDENCIA', y='Count', color='TIPO_DOC_VTA',
                                title='Conteo de Facturas y Boletas por Unidad de Dependencia',
                                labels={'UNIDAD_DEPENDENCIA': 'Unidad de Dependencia', 'Count': 'Conteo'})
        
        # Mostrar la gráfica
        return figura_ingresos
    
    def grafica_pastel_ingresos(self, data):
        # Filtrar y eliminar valores nulos
        data_filtrada = self.filtrar_y_eliminar_nulos(data[['ANP', 'IMPORTE_TOTAL', 'FECHA_DOC_VTA']])

        # Convertir la columna FECHA_DOC_VTA a tipo datetime para extraer el año
        data_filtrada['FECHA_DOC_VTA'] = pd.to_datetime(data_filtrada['FECHA_DOC_VTA'], format='%Y%m%d')
        data_filtrada['Año'] = data_filtrada['FECHA_DOC_VTA'].dt.year

        # Obtener la lista única de años en los datos
        años_disponibles = data_filtrada['Año'].unique()

        # Permitir al usuario seleccionar el año
        año_seleccionado = st.selectbox("Selecciona un año:", años_disponibles)

        # Filtrar por el año seleccionado
        data_anio_seleccionado = data_filtrada[data_filtrada['Año'] == año_seleccionado]

        # Agrupar por ANP y calcular el total de importe
        resumen_anio_seleccionado = data_anio_seleccionado.groupby('ANP')['IMPORTE_TOTAL'].sum().reset_index()

        # Generar la gráfica de pastel
        title = f'Distribución del Importe Total por Región (ANP) en el Año: {año_seleccionado}'
        figura_pastel = px.pie(resumen_anio_seleccionado, values='IMPORTE_TOTAL', names='ANP', title=title)

        # Mostrar la gráfica
        return figura_pastel

    def grafica_lineal_anual(self, data):
        # Filtrar y eliminar valores nulos
        data_filtrada = self.filtrar_y_eliminar_nulos(data[['FECHA_DOC_VTA', 'ANP', 'IMPORTE_TOTAL']])

        # Convertir la columna FECHA_DOC_VTA a tipo datetime para extraer el año
        data_filtrada['FECHA_DOC_VTA'] = pd.to_datetime(data_filtrada['FECHA_DOC_VTA'], format='%Y%m%d')
        data_filtrada['Año'] = data_filtrada['FECHA_DOC_VTA'].dt.year

        # Obtener la lista única de años en los datos
        años_disponibles = data_filtrada['Año'].unique()

        # Agrupar por año y región (ANP) y calcular el total de ingresos
        resumen_anual = data_filtrada.groupby(['Año', 'ANP'])['IMPORTE_TOTAL'].sum().reset_index()

        # Generar la gráfica lineal
        figura_ingresos_anuales = px.line(resumen_anual, x='Año', y='IMPORTE_TOTAL', color='ANP',
                                        title='Ingresos a lo largo de los Años por Región (ANP)',
                                        labels={'Año': 'Año', 'IMPORTE_TOTAL': 'Monto Total'})

        # Mostrar la gráfica
        return figura_ingresos_anuales


    def mostrar_grafica_ingresos(self, figuras, nombre_ingresos):
        opcion_seleccionada = st.selectbox("Selecciona la gráfica a mostrar", nombre_ingresos)
        indice_seleccionado = nombre_ingresos.index(opcion_seleccionada)
        self.mostrar_grafica(figuras[indice_seleccionado])


def main():
    # Título de la aplicación Streamlit
    st.markdown("# Áreas Naturales Protegidas (ANP) de Administración Nacional Definitiva ")

    # Crear una instancia de la clase VisualizadorDatos y cargar el archivo CSV
    visualizador = VisualizadorDatos("archivo.csv")

    # Filtrar y eliminar valores nulos para cada nivel geográfico (departamento, provincia, distrito)
    data_anp_cate = visualizador.filtrar_y_eliminar_nulos(visualizador.data[visualizador.columnas_anp_cate])
    data_departamento = visualizador.filtrar_y_eliminar_nulos(visualizador.data[visualizador.columnas_departamento])
    data_provincia = visualizador.filtrar_y_eliminar_nulos(visualizador.data[visualizador.columnas_provincia])
    data_distrito = visualizador.filtrar_y_eliminar_nulos(visualizador.data[visualizador.columnas_distrito])
    data_acp_ubpo = visualizador.filtrar_y_eliminar_nulos(visualizador.data_ACP[visualizador.columnas_acp_ubpo])

    # Convertir las columnas a tipo str si no lo son
    data_anp_cate = visualizador.convertir_a_str(data_anp_cate)
    data_departamento = visualizador.convertir_a_str(data_departamento)
    data_provincia = visualizador.convertir_a_str(data_provincia)
    data_distrito = visualizador.convertir_a_str(data_distrito)
    data_acp_ubpo = visualizador.convertir_a_str(data_acp_ubpo)

    # Concatenar las columnas para formar la columna 'Location' para cada nivel geográfico
    data_anp_cate = visualizador.concatenar_columnas(data_anp_cate, visualizador.columnas_anp_cate)
    data_departamento = visualizador.concatenar_columnas(data_departamento, visualizador.columnas_departamento)
    data_provincia = visualizador.concatenar_columnas(data_provincia, visualizador.columnas_provincia)
    data_distrito = visualizador.concatenar_columnas(data_distrito, visualizador.columnas_distrito)
    data_acp_ubpo = visualizador.concatenar_columnas(data_acp_ubpo, visualizador.columnas_acp_ubpo)

    # Contar las ocurrencias de cada ubicación para cada nivel geográfico
    conteo_anp_cate = visualizador.contar_ocurrencias(data_anp_cate)
    conteo_departamento = visualizador.contar_ocurrencias(data_departamento)
    conteo_provincia = visualizador.contar_ocurrencias(data_provincia)
    conteo_distrito = visualizador.contar_ocurrencias(data_distrito)

    # Generar gráficas de barras para cada nivel geográfico
    fig_anp_cate = visualizador.generar_grafica(conteo_anp_cate, "Conteo por ANP CATE")
    fig_departamento = visualizador.generar_grafica(conteo_departamento, "Conteo por Departamento")
    fig_provincia = visualizador.generar_grafica(conteo_provincia, "Conteo por Provincia")
    fig_distrito = visualizador.generar_grafica(conteo_distrito, "Conteo por Distrito")
    
    # Unir los datos de coordenadas con los datos de Ubigeos utilizando el código UBIGEO1
    merged_data = pd.merge(visualizador.data, visualizador.data_ubigeos, how="left", left_on="UBIGEO1", right_on="ubigeo_inei")

    # Filtrar solo las filas que tienen datos de Ubigeo y coordenadas
    filtered_data = merged_data.dropna(subset=['latitud', 'longitud'])
    
    # Crear un GeoDataFrame con la información de Ubigeos
    geometry = gpd.points_from_xy(filtered_data['longitud'], filtered_data['latitud'])
    gdf = gpd.GeoDataFrame(filtered_data, geometry=geometry)

    # Generar el mapa de Ubigeos
    mapa_ubigeos = visualizador.generar_mapa_ubigeos(gdf)
    
    # Mostrar el mapa de Ubigeos en la aplicación Streamlit
    st.markdown("## Áreas Naturales Protegidas (ANP) ")
    folium_static(mapa_ubigeos)

    # Almacena las figuras y nombres de las figuras en listas
    st.markdown("## Áreas de Conservación Regional (ACR).")
    figuras = [fig_anp_cate, fig_departamento, fig_provincia, fig_distrito]
    nombres_figuras = ["Conteo por ANP CATE", "Conteo por Departamento", "Conteo por Provincia", "Conteo por Distrito"]

    # Mostrar la gráfica seleccionada en la aplicación Streamlit
    visualizador.mostrar_grafica_seleccionada(figuras, nombres_figuras)
    
    st.markdown("## Áreas de Conservación Privada (ACP).")
    categorias_acp_tipro = visualizador.data_ACP['ACP_TIPRO'].unique()
    visualizador.mostrar_grafica_acp(data_acp_ubpo, categorias_acp_tipro)
 
    # Mostrar gráfica de ingresos
    st.markdown("## Ingresos")
    fig_ingreso = visualizador.grafica_ingresos(visualizador.data_ingresos)
    fig_pastel = visualizador.grafica_pastel_ingresos(visualizador.data_ingresos)
    fig_lineal = visualizador.grafica_lineal_anual(visualizador.data_ingresos)
    figuras_ingresos = [fig_ingreso, fig_pastel, fig_lineal]
    nombre_ingresos = ["Boleta-Factura", "Monto Total", "Ingresos (2021-2022-2023)"]
    visualizador.mostrar_grafica_ingresos(figuras_ingresos, nombre_ingresos)

if __name__ == "__main__":
    main()
