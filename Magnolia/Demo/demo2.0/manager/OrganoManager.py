# organo_manager.py
import json
from flask import flash, redirect, url_for, render_template, request
import pandas as pd
import plotly
from funct.DataBase import DataBase
from funct.Graficas import Graficas
from funct.per import per
# Asegúrate de importar cualquier otra dependencia que necesites, como la clase DataBase o Graficas

class OrganoManager:
    def validate_user(self, session):
        if 'user_info' not in session:
            flash('Please log in to view this page.')
            return redirect(url_for('login'))
        return session['user_info']
    
    def get_db_config(self, user_info):
        server_name = user_info['server'].replace("\\\\", "\\")
        return {
            'server': server_name,
            'database': user_info['db_name']
        }
    def load_section_info(self, user_info):
        secciones_dic_str = user_info.get('secciones_dic', '{}')
        try:
            return json.loads(secciones_dic_str)
        except json.JSONDecodeError:
            flash("Error decoding secciones_dic.")
            return render_template('error.html', error="Invalid secciones_dic format")
        
    def execute_queries(self, db_config, secciones_dic, seccion):
        db = DataBase(**db_config)
        db.connect()

        datos = []
        columnas = []
        df = pd.DataFrame()
        if seccion in secciones_dic:
                tablas = secciones_dic[seccion]['Tablas']
                tablas_format = ', '.join([f"'{t}'" for t in tablas])

                if len(tablas) > 1 and secciones_dic[seccion]['Join']:
                    query_datos = f"SELECT * FROM {tablas[0]} JOIN {tablas[1]} {secciones_dic[seccion]['Join']}"
                else:
                    tipo = request.args.get('type', tablas[0])
                    query_datos = f"SELECT * FROM {tipo}"

                datos = db.execute_query(query_datos)
                # Recuperar la tabla actual desde los argumentos de la solicitud o usar la primera tabla de la sección
                tipo_actual = request.args.get('type', secciones_dic[seccion]['Tablas'][0])
                # Consulta para obtener las columnas de la tabla actual
                query_columnas = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{tipo_actual}'"

                columnas = db.execute_query(query_columnas)
                if columnas is None:
                    flash('Error al recuperar las columnas de la base de datos.')
                    return redirect(url_for('inicio'))

                columnas = [col[0] for col in columnas]
                
                # Convertir los datos a un DataFrame de Pandas
                if datos:  # Comprueba si hay datos antes de intentar crear el DataFrame
                    datos_modificados = [list(fila) for fila in datos]
                    df = pd.DataFrame(datos_modificados)
                else:
                    flash('No hay datos disponibles para esta sección.')
        db.close()
        return datos, columnas, df        
    
    def generate_graphs(self, secciones_dic, seccion, db_config):
        graph = Graficas(**db_config)  # Instanciar Graficas aquí
        graficas_html = []

        if 'Graficas' in secciones_dic[seccion]:
            for nombre_funcion_str in secciones_dic[seccion]['Graficas']:
                # Divide la cadena para obtener el nombre de la función
                nombre_funcion = nombre_funcion_str.split('.')[-1]

                if hasattr(graph, nombre_funcion):
                    funcion_grafica = getattr(graph, nombre_funcion)
                    fig, text = funcion_grafica()  # Ejecuta la función
                    grafica_html = plotly.io.to_html(fig, full_html=False)
                    graficas_html.append((grafica_html, text))
                else:
                    flash(f"Función gráfica '{nombre_funcion}' no encontrada.")       

        return graficas_html
    
    @staticmethod
    def performance_analysis(df, columns):
        analysis = per.perform_data_analysis(df, columns)
        return analysis