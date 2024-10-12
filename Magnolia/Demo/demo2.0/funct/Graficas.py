import numpy as np
import networkx as nx
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from funct.DataBase import DataBase
from collections import defaultdict
import plotly.express as px

class Graficas:
    # -*- coding: utf-8 -*-
    def __init__(self, server, database):
            self.server = server
            self.database = database
            self.db_instance = DataBase(server, database)
            self.db_instance.connect()
              
    def grafica_violin_genero_edad(self):
        query = "SELECT Genero, Edad FROM Empleados"
        self.db_instance.cursor.execute(query)
        result = self.db_instance.cursor.fetchall()
        print(result)
        # Preparar los datos
        edades_hombres = [row[1] for row in result if row[0] == 'Masculino']
        edades_mujeres = [row[1] for row in result if row[0] == 'Femenino']

        # Crear los gr�ficos de viol�n
        trace1 = go.Violin(y=edades_hombres, name='Hombres', box_visible=True, line_color='blue')
        trace2 = go.Violin(y=edades_mujeres, name='Mujeres', box_visible=True, line_color='pink')

        # Calcular estad�sticas
        media_hombres = np.mean(edades_hombres)
        std_hombres = np.std(edades_hombres)
        media_mujeres = np.mean(edades_mujeres)
        std_mujeres = np.std(edades_mujeres)

        # Configuraci�n de la gr�fica
        data = [trace1, trace2]
        layout = go.Layout(
            title='Distribuci�n de Edad por G�nero',
            yaxis=dict(title='Edad'),
            xaxis=dict(title='G�nero'),
            annotations=[
                dict(
                    x=0.1, y=media_hombres, xref='paper', yref='y', showarrow=False, 
                    text=f"Media: {media_hombres:.1f}, Std: {std_hombres:.1f}", 
                    font=dict(color='white'), bgcolor='blue'
                ),
                dict(
                    x=0.7, y=media_mujeres, xref='paper', yref='y', showarrow=False, 
                    text=f"Media: {media_mujeres:.1f}, Std: {std_mujeres:.1f}", 
                    font=dict(color='white'), bgcolor='pink'
                )
            ]
        )
        
        texto = f'''
        Esta gr�fica de viol�n muestra la distribuci�n de edades de los empleados de Magnolia, diferenciando entre g�neros masculino y femenino.\n

        Hombres: Edad promedio de aproximadamente {media_hombres:.1f} a�os con una variabilidad est�ndar de {std_hombres:.1f} a�os.\n
        Mujeres: Edad promedio cercana a {media_mujeres:.1f} a�os con una desviaci�n est�ndar de {std_mujeres:.1f} a�os.\n
        La forma de cada viol�n indica las edades m�s comunes y la dispersi�n de edades dentro de cada g�nero.
        '''

        fig = go.Figure(data=data, layout=layout)
        return fig, texto    









 

    def grafica_violin_salarios(self):
        # Ejecutamos la consulta para obtener los salarios base de los puestos
        query = "SELECT SalarioBase FROM Puestos"
        self.db_instance.cursor.execute(query)
        result = self.db_instance.cursor.fetchall()
        
        # Extraemos los salarios de los resultados
        salarios = [row[0] for row in result]

        # Crear el gr�fico de viol�n
        trace_salarios = go.Violin(y=salarios, name='Salarios', box_visible=True, line_color='purple')

        # Calcular estad�sticas
        media_salarios = np.mean(salarios)
        std_salarios = np.std(salarios)

        # Configuraci�n de la gr�fica
        layout = go.Layout(
            title='Distribuci�n de Salarios Totales',
            yaxis=dict(title='Salario'),
            xaxis=dict(title=''),
            showlegend=False,
            annotations=[
                dict(
                    x=0.1, y=media_salarios, xref='paper', yref='y', showarrow=False, 
                    text=f"Media: {round((int(media_salarios)*0.001),2):.1f} k, Std: {round((int(std_salarios)*0.001)):.1f} k", 
                    font=dict(color='white'), bgcolor='purple'
                )
            ]
        )
                
        texto = texto = f'''
        Esta gr�fica de viol�n representa la distribuci�n de los salarios base de los puestos en la empresa. Proporciona una visi�n general de c�mo est�n distribuidos los salarios, desde los m�s bajos hasta los m�s altos, dentro de la organizaci�n.

        La l�nea de color p�rpura indica la densidad de los diferentes niveles salariales. La parte m�s ancha del viol�n muestra el rango donde se concentran la mayor�a de los salarios, mientras que las partes m�s estrechas representan los salarios menos comunes.

        Datos clave:
        - Salario Medio: Aproximadamente {round((int(media_salarios)*0.001),2):.1f} mil (k).
        - Desviaci�n Est�ndar: Aproximadamente {round((int(std_salarios)*0.001)):.1f} mil (k). Esto indica la variaci�n en los salarios entre los diferentes puestos.
        '''

        
        fig = go.Figure(data=[trace_salarios], layout=layout)
        return fig, texto


    def grafica_red_encargados(self):
        # Consulta SQL actualizada para obtener nombre y apellido
        query = """
        SELECT e.IdEmpleado, e.IdEncargado, e.nombre, e.apellido
        FROM Empleados e
        WHERE e.IdEncargado IS NOT NULL AND e.IdEncargado != 0
        """
        self.db_instance.cursor.execute(query)
        result = self.db_instance.cursor.fetchall()
        
        # Dividir los resultados en dos listas: una para 'x' (IdEmpleado) y otra para 'y' (IdEncargado)
        x = [tupla[0] for tupla in result]  # Primer elemento de cada tupla
        y = [tupla[1] for tupla in result]  # Segundo elemento de cada tupla
        
        # Crear listas de nombres, apellidos y diccionario para mapeo
        nombre = [tupla[2] for tupla in result]
        apellido = [tupla[3] for tupla in result]
        nombre_completo = [f"{n} {a}" for n, a in zip(nombre, apellido)]
        mapeo_nombres = dict(zip(x, nombre_completo))

        # Crear el grafo desde el DataFrame
        data = pd.DataFrame({'IdEmpleado': x, 'IdEncargado': y})
        # Crear el grafo desde el DataFrame
        G = nx.from_pandas_edgelist(data, 'IdEncargado', 'IdEmpleado')

        # Posiciones de los nodos
        pos = nx.spring_layout(G)

        eig_cen = nx.eigenvector_centrality(G)

        temp = {}

        for w in sorted(eig_cen, key=eig_cen.get, reverse=True):
            temp[w] = eig_cen[w]

        color = []
        for node in G:
            if  (node == list(temp.keys())[0] or node == list(temp.keys())[1] or node == list(temp.keys())[2] or node==list(temp.keys())[3]):
                color.append('red')
            else:
                color.append('black') 
                    
        # Datos para los nodos y bordes
        edge_x = []
        edge_y = []
        node_x = []
        node_y = []
        node_text = []
        hover_text = []  # Texto que aparecer� al pasar el mouse sobre el nodo
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            hover_text.append(mapeo_nombres.get(node, "Desconocido"))  # Texto para hover

            # Crear trazas de bordes y nodos
            edge_trace = go.Scatter(
                x=edge_x, 
                y=edge_y, 
                line=dict(width=0.5, color='#888'), 
                mode='lines',
                showlegend=False  # Ocultar esta leyenda
            )

            node_trace = go.Scatter(
                x=node_x, 
                y=node_y, 
                mode='markers',  # Solo marcadores, sin texto
                hoverinfo='text',  # Mostrar texto al pasar el mouse
                text=hover_text,  # Texto de hover
                marker=dict(
                    showscale=False, 
                    size=10, 
                    color=color,  # Aqu� se asignan los colores a los nodos
                    line_width=2
                ),
                showlegend=False  # Ocultar esta leyenda
            )
        # Configuraci�n del gr�fico
        fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
            title='Red de Encargados de Empleados', 
            showlegend=True,  # Habilitar leyenda
            hovermode='closest', 
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), 
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            legend=dict(
                itemsizing='constant',
                x=1,  # Posici�n X de la leyenda
                y=1,  # Posici�n Y de la leyenda
                bgcolor='rgba(255,255,255,0.5)'  # Color de fondo de la leyenda
            )
        ))

        # A�adir leyenda manualmente para nodos de alta centralidad
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color='red'),
            legendgroup='group',
            showlegend=True,
            name='Nodos mas influyentes de la red'
        ))

                
        texto = f'''
        Esta gr�fica muestra la red de relaciones entre empleados y sus encargados en la empresa Magnolia. Cada nodo representa a un empleado, y las l�neas conectan a cada empleado con su respectivo encargado.

        La red es una herramienta �til para visualizar la estructura jer�rquica y las relaciones de reporte dentro de la organizaci�n. Los nodos de color rojo representan a los empleados m�s influyentes en la red, basados en su centralidad de autovector (eigenvector centrality). Estos empleados pueden ser clave en la difusi�n de informaci�n o en la toma de decisiones dentro de la empresa.

        Nodos m�s influyentes:
        '''

        # A�adir los nombres de los nodos m�s influyentes
        for i, node in enumerate(list(temp.keys())[:4]):
            texto += f"- {mapeo_nombres.get(node, 'Desconocido')} (ID: {node})\n"

        texto += f'''
        El color rojo resaltan la importancia de estos empleados en la red. Este an�lisis puede ayudar a identificar l�deres potenciales y puntos clave en la estructura organizativa.
        '''

        return fig, texto


    def grafica_stock_productos(self):
        query = "SELECT NombreProducto, Stock FROM Productos ORDER BY Stock DESC"
        self.db_instance.cursor.execute(query)
        result = self.db_instance.cursor.fetchall()

        # Ordenar los productos por stock de mayor a menor
        nombres = [row[0] for row in result]
        stocks = [row[1] for row in result]

        # Crear un degradado de colores de azul a rojo (puedes elegir otros colores)
        colores = ['rgba(255, {} , {}, {})'.format(int(r), int(g), 255) for r, g in zip(np.linspace(255, 0, len(stocks)), np.linspace(0, 255, len(stocks)))]

        data = go.Bar(x=nombres, y=stocks, marker=dict(color=colores))
        layout = go.Layout(title='Stock de Productos',
                        xaxis=dict(title='Producto'),
                        yaxis=dict(title='Stock'),
                        xaxis_tickangle=-45)  # Inclinar las etiquetas para mejor visualizaci�n
        fig = go.Figure(data=[data], layout=layout)
        
        texto = f'''
        Esta gr�fica muestra el stock actual de los productos en la empresa Magnolia, clasificados en orden descendente. La altura de cada barra representa la cantidad de stock disponible para cada producto.

        Los colores de las barras representan un degradado de azul a rojo, donde el azul indica mayor disponibilidad y el rojo, menor disponibilidad. Esta representaci�n visual ayuda a identificar r�pidamente los productos con stock cr�tico o en exceso.

        Productos destacados:
        - Mayor stock: '{nombres[0]}' con {stocks[0]} unidades.
        - Menor stock: '{nombres[-1]}' con {stocks[-1]} unidades.
        '''

        return fig, texto


    # Asumiendo que db_instance ya est� conectado

    def grafica_compras_por_mes(self):
        query = """
        SELECT
        FORMAT(FechaCompra, 'yyyy-MM') as MesCompra,
        SUM(PrecioTotal) as TotalCompra
        FROM Compras
        GROUP BY FORMAT(FechaCompra, 'yyyy-MM')
        ORDER BY FORMAT(FechaCompra, 'yyyy-MM')
        """
        self.db_instance.cursor.execute(query)
        result = self.db_instance.cursor.fetchall()

        # Acceder a los datos por �ndice
        fechas = [row[0] for row in result]
        total_compras = [row[1] for row in result]

        return fechas, total_compras

    def grafica_ventas_por_mes(self):
        query = """
        SELECT
        FORMAT(FechaVenta, 'yyyy-MM') as MesVenta,
        SUM(Total) as TotalVenta
        FROM Ventas
        GROUP BY FORMAT(FechaVenta, 'yyyy-MM')
        ORDER BY FORMAT(FechaVenta, 'yyyy-MM')
        """
        self.db_instance.cursor.execute(query)
        result = self.db_instance.cursor.fetchall()

        # Acceder a los datos por �ndice
        fechas = [row[0] for row in result]
        total_ventas = [row[1] for row in result]

        return fechas, total_ventas

    def grafica_compras_y_ventas_por_mes(self):
        fechas_compras, total_compras = self.grafica_compras_por_mes()
        fechas_ventas, total_ventas = self.grafica_ventas_por_mes()

        # Crear subplots para tener dos l�neas en el mismo gr�fico
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # A�adir trazas de compras y ventas
        fig.add_trace(go.Scatter(x=fechas_compras, y=total_compras, mode='lines+markers', name='Compras Totales', marker=dict(color='red')), secondary_y=False)
        fig.add_trace(go.Scatter(x=fechas_ventas, y=total_ventas, mode='lines+markers', name='Ventas Totales', marker=dict(color='blue')), secondary_y=True)
        
        # Configuraci�n del layout de la gr�fica
        fig.update_layout(
            title='Compras y Ventas por Mes',
            xaxis_title='Mes',
            yaxis_title='Total de Compras',
            yaxis2_title='Total de Ventas',
            legend=dict(x=0.01, y=0.99)
        )
        
        # Establecer el mismo rango de fechas para ambos ejes y
        fig.update_yaxes(range=[0, max(max(total_compras), max(total_ventas))], secondary_y=False)
        fig.update_yaxes(range=[0, max(max(total_compras), max(total_ventas))], secondary_y=True)

        # Calcular m�ximo y m�nimo para compras y ventas
        max_compra = max(total_compras)
        mes_max_compra = fechas_compras[total_compras.index(max_compra)]
        min_compra = min(total_compras)
        mes_min_compra = fechas_compras[total_compras.index(min_compra)]

        max_venta = max(total_ventas)
        mes_max_venta = fechas_ventas[total_ventas.index(max_venta)]
        min_venta = min(total_ventas)
        mes_min_venta = fechas_ventas[total_ventas.index(min_venta)]

        # Texto descriptivo
        texto = f'''
        Esta gr�fica dual muestra la evoluci�n mensual de las compras y ventas de Magnolia, permitiendo una comparaci�n directa entre ambos flujos financieros. 

        La l�nea roja indica el total de compras, alcanzando su pico m�ximo de {max_compra} en {mes_max_compra} y su punto m�s bajo de {min_compra} en {mes_min_compra}. Por otro lado, la l�nea azul representa el total de ventas, con su valor m�ximo de {max_venta} en {mes_max_venta} y el m�nimo de {min_venta} en {mes_min_venta}.
        '''

        return fig, texto


    def grafica_ventas_compras_ganancia_total(self):
        # Obtener ventas totales por producto
        query_ventas = """
        SELECT p.NombreProducto, SUM(v.Total) 
        FROM Ventas v 
        JOIN Productos p ON v.IdProducto = p.IdProducto 
        GROUP BY v.IdProducto, p.NombreProducto
        """
        self.db_instance.cursor.execute(query_ventas)
        ventas_result = self.db_instance.cursor.fetchall()
        productos, ventas_totales = zip(*ventas_result)

        # Obtener compras totales por producto
        query_compras = """
        SELECT p.NombreProducto, SUM(c.PrecioTotal) 
        FROM Compras c 
        JOIN Productos p ON c.IdProducto = p.IdProducto 
        GROUP BY c.IdProducto, p.NombreProducto
        """
        self.db_instance.cursor.execute(query_compras)
        compras_result = self.db_instance.cursor.fetchall()

        # Mapear compras a los productos
        compras_totales = [next((c[1] for c in compras_result if c[0] == p), 0) for p in productos]

        # Calcular la ganancia total
        ganancia_total = sum(ventas_totales) - sum(compras_totales)


        # Calcular la diferencia (gap) entre ventas y compras para cada producto
        diferencias = [abs(ventas - compras) for ventas, compras in zip(ventas_totales, compras_totales)]
        
        # Posiciones para las barras de diferencia y colores seg�n la condici�n
        posiciones_diferencia = []
        colores_diferencia = []

        for ventas, compras in zip(ventas_totales, compras_totales):
            posiciones_diferencia.append(min(ventas, compras))
            # Verde si ventas >= compras, de lo contrario amarillo
            colores_diferencia.append('green' if ventas >= compras else 'yellow')

        # Crear la gr�fica de barras
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Agregar ventas y compras
        fig.add_trace(go.Bar(x=productos, y=ventas_totales, name='Ventas Totales'), secondary_y=False)
        fig.add_trace(go.Bar(x=productos, y=compras_totales, name='Compras Totales'), secondary_y=False)

        # Agregar las diferencias como una nueva serie de barras con base en el valor m�s peque�o
        fig.add_trace(go.Bar(x=productos, y=diferencias, base=posiciones_diferencia, marker_color=colores_diferencia, name='Diferencia -'))

        # Trucos para la leyenda: a�adir trazas "dummy" para la leyenda de diferencias negativas y positivas
        fig.add_trace(go.Bar(x=[None], y=[None], orientation='h', marker_color='green', name='Diferencia +'))

        # Agregar anotaci�n para la ganancia total
        color_ganancia = 'green' if ganancia_total >= 0 else 'yellow'
        fig.add_annotation(
            x=0.05, y=0.95, xref="paper", yref="paper",
            text=f"Ganancia Total: {ganancia_total}",
            showarrow=False,
            font=dict(size=14),
            bgcolor=color_ganancia,
            bordercolor="black",
            borderwidth=2
        )

        # Configuraci�n del layout de la gr�fica
        fig.update_layout(
            title='Ventas y Compras Totales por Producto',
            xaxis_title='Producto',
            yaxis_title='Total en Moneda',
            legend=dict(x=0.99, y=0.01, bgcolor="rgba(255,255,255,0.5)")
        )

        # Texto descriptivo
        texto = f'''
        La gr�fica muestra una comparaci�n entre las ventas y compras totales por producto en Magnolia, destacando las diferencias y la ganancia total. Cada producto se representa mediante barras que indican las ventas y compras acumuladas. 

        Las barras verdes y amarillas representan las diferencias: verde cuando las ventas superan a las compras y amarillo en caso contrario. Esta visualizaci�n ayuda a identificar qu� productos est�n generando m�s ingresos en comparaci�n con su costo de adquisici�n.

        Puntos destacados:
        - Ganancia Total: La ganancia total se calcula como la suma de todas las ventas menos la suma de todas las compras, resultando en {ganancia_total}.
        '''

        return fig, texto

    def grafica_boxplot_compras_y_ventas_diarias_por_mes(self):
        # Consulta para obtener los totales diarios de compras por mes
        query_compras = """
        SELECT
        FORMAT(FechaCompra, 'yyyy-MM') as Mes,
        FORMAT(FechaCompra, 'dd') as Dia,
        PrecioTotal
        FROM Compras
        ORDER BY Mes, Dia
        """
        self.db_instance.cursor.execute(query_compras)
        compras_result = self.db_instance.cursor.fetchall()

        # Consulta para obtener los totales diarios de ventas por mes
        query_ventas = """
        SELECT
        FORMAT(FechaVenta, 'yyyy-MM') as Mes,
        FORMAT(FechaVenta, 'dd') as Dia,
        Total
        FROM Ventas
        ORDER BY Mes, Dia
        """
        self.db_instance.cursor.execute(query_ventas)
        ventas_result = self.db_instance.cursor.fetchall()

        # Organizar los datos en un diccionario donde la clave es el mes y los valores son las listas de totales diarios
        compras_por_mes = defaultdict(list)
        ventas_por_mes = defaultdict(list)

        for mes, dia, total in compras_result:
            compras_por_mes[mes].append(total)

        for mes, dia, total in ventas_result:
            ventas_por_mes[mes].append(total)

        # Crear la figura para los boxplots
        fig = go.Figure()

        # Obtener la lista combinada de meses con datos de compras o ventas
        meses_con_datos = sorted(set(compras_por_mes.keys()).union(ventas_por_mes.keys()))
    
        # Par�metros para el estilo de los boxplots (grosor de las l�neas)
        line_style = dict(width=2)  # Ajustar el grosor de las l�neas

        # Listas para almacenar los valores y las etiquetas de mes
        compras_values = []
        compras_labels = []
        ventas_values = []
        ventas_labels = []

        # Rellenar las listas con los valores y las etiquetas de mes
        for mes in meses_con_datos:
            if mes in compras_por_mes:
                compras_values.extend(compras_por_mes[mes])
                compras_labels.extend([mes] * len(compras_por_mes[mes]))
            
            if mes in ventas_por_mes:
                ventas_values.extend(ventas_por_mes[mes])
                ventas_labels.extend([mes] * len(ventas_por_mes[mes]))

        # Agregar los boxplots de compras y ventas
        fig.add_trace(go.Box(
            y=compras_values,
            x=compras_labels,
            name='Compras',
            marker_color='red',
            boxmean='sd',
            line=line_style
        ))

        fig.add_trace(go.Box(
            y=ventas_values,
            x=ventas_labels,
            name='Ventas',
            marker_color='blue',
            boxmean='sd',
            line=line_style
        ))

        # Configurar el layout de la figura
        fig.update_layout(
            title='Distribuci�n Diaria de Compras y Ventas por Mes',
            yaxis_title='Total en Pesos ($)',
            boxmode='group'
        )


        # Determinar el mes con la mayor media de compras y ventas
        mes_mayor_media_compra = max(compras_por_mes, key=lambda k: np.mean(compras_por_mes[k]))
        media_max_compras = np.mean(compras_por_mes[mes_mayor_media_compra])

        mes_mayor_media_venta = max(ventas_por_mes, key=lambda k: np.mean(ventas_por_mes[k]))
        media_max_ventas = np.mean(ventas_por_mes[mes_mayor_media_venta])

        # Texto descriptivo
        texto = f'''
        La gr�fica 'Distribuci�n Diaria de Compras y Ventas por Mes' presenta una comparaci�n mensual de las distribuciones diarias de compras y ventas en Magnolia. Cada 'boxplot' muestra la variabilidad, tendencia central y desviaciones de las transacciones diarias por mes.

        Aspectos destacados:
        - Mes con Mayor Media de Compras: {mes_mayor_media_compra} con una media de compras de ${media_max_compras:,.2f}.
        - Mes con Mayor Media de Ventas: {mes_mayor_media_venta} con una media de ventas de ${media_max_ventas:,.2f}.
        '''

        return fig, texto

    def graficar_frecuencia_transacciones_por_mes(self):
        
    # Consulta para obtener los totales diarios de compras por mes
        query_compras = """
        SELECT
        FORMAT(FechaCompra, 'yyyy-MM') as Mes,
        FORMAT(FechaCompra, 'dd') as Dia,
        PrecioTotal
        FROM Compras
        ORDER BY Mes, Dia
        """
        self.db_instance.cursor.execute(query_compras)
        compras_result = self.db_instance.cursor.fetchall()

        # Consulta para obtener los totales diarios de ventas por mes
        query_ventas = """
        SELECT
        FORMAT(FechaVenta, 'yyyy-MM') as Mes,
        FORMAT(FechaVenta, 'dd') as Dia,
        Total
        FROM Ventas
        ORDER BY Mes, Dia
        """
        self.db_instance.cursor.execute(query_ventas)
        ventas_result = self.db_instance.cursor.fetchall()

        # Organizar los datos en un diccionario donde la clave es el mes y los valores son las listas de totales diarios
        compras_por_mes = defaultdict(list)
        ventas_por_mes = defaultdict(list)

        for mes, dia, total in compras_result:
            compras_por_mes[mes].append(total)

        for mes, dia, total in ventas_result:
            ventas_por_mes[mes].append(total)


        frecuencia_compras_por_mes = {mes: len(totales) for mes, totales in compras_por_mes.items()}
        frecuencia_ventas_por_mes = {mes: len(totales) for mes, totales in ventas_por_mes.items()}
        

        # Combinar los meses de compras y ventas
        meses = sorted(set(frecuencia_compras_por_mes.keys()).union(frecuencia_ventas_por_mes.keys()))

        # Listas para almacenar las frecuencias de compras y ventas
        frecuencias_compras = []
        frecuencias_ventas = []

        # Rellenar las listas con las frecuencias de compras y ventas
        for mes in meses:
            frecuencias_compras.append(frecuencia_compras_por_mes.get(mes, 0))
            frecuencias_ventas.append(frecuencia_ventas_por_mes.get(mes, 0))

        # Crear la figura para el gr�fico de barras
        fig = go.Figure()

        # Agregar las barras de compras al gr�fico
        fig.add_trace(go.Bar(
            x=meses,
            y=frecuencias_compras,
            name='Compras',
            marker_color='green'
        ))

        # Agregar las barras de ventas al gr�fico
        fig.add_trace(go.Bar(
            x=meses,
            y=frecuencias_ventas,
            name='Ventas',
            marker_color='purple'
        ))

        # Configurar el layout de la figura
        fig.update_layout(
            barmode='group',  # Modo de agrupaci�n de barras
            title='Frecuencia de Transacciones de Compras y Ventas por Mes',
            xaxis_title='Mes',
            yaxis_title='N�mero de Transacciones'
        )

        # Determinar el mes con mayor y menor frecuencia de compras
        mes_mayor_frecuencia_compra = max(frecuencia_compras_por_mes, key=frecuencia_compras_por_mes.get)
        mayor_frecuencia_compras = frecuencia_compras_por_mes[mes_mayor_frecuencia_compra]
        mes_menor_frecuencia_compra = min(frecuencia_compras_por_mes, key=frecuencia_compras_por_mes.get)
        menor_frecuencia_compras = frecuencia_compras_por_mes[mes_menor_frecuencia_compra]

        # Determinar el mes con mayor y menor frecuencia de ventas
        mes_mayor_frecuencia_venta = max(frecuencia_ventas_por_mes, key=frecuencia_ventas_por_mes.get)
        mayor_frecuencia_ventas = frecuencia_ventas_por_mes[mes_mayor_frecuencia_venta]
        mes_menor_frecuencia_venta = min(frecuencia_ventas_por_mes, key=frecuencia_ventas_por_mes.get)
        menor_frecuencia_ventas = frecuencia_ventas_por_mes[mes_menor_frecuencia_venta]

        # Texto descriptivo
        texto = f'''
        La gr�fica 'Frecuencia de Transacciones de Compras y Ventas por Mes' de Magnolia ilustra el n�mero de transacciones comerciales realizadas cada mes. Se diferencian las compras y ventas con barras de color verde y morado respectivamente.

        Aspectos destacados:
        - Mes con Mayor Frecuencia de Compras: {mes_mayor_frecuencia_compra} con {mayor_frecuencia_compras} transacciones.
        - Mes con Menor Frecuencia de Compras: {mes_menor_frecuencia_compra} con {menor_frecuencia_compras} transacciones.
        - Mes con Mayor Frecuencia de Ventas: {mes_mayor_frecuencia_venta} con {mayor_frecuencia_ventas} transacciones.
        - Mes con Menor Frecuencia de Ventas: {mes_menor_frecuencia_venta} con {menor_frecuencia_ventas} transacciones.
        '''

        return fig, texto

    def graficar_frecuencia_compras_ventas(self):
        # Obtener la frecuencia de ventas por producto
        query_ventas = """
        SELECT p.NombreProducto, COUNT(v.IdVenta) 
        FROM Ventas v 
        JOIN Productos p ON v.IdProducto = p.IdProducto 
        GROUP BY v.IdProducto, p.NombreProducto
        """
        self.db_instance.cursor.execute(query_ventas)
        ventas_result = self.db_instance.cursor.fetchall()
        productos, frecuencia_ventas = zip(*ventas_result)

        # Obtener la frecuencia de compras por producto
        query_compras = """
        SELECT p.NombreProducto, COUNT(c.IdCompras) -- Corregido aqu�, era IdCompra y se cambi� a IdCompras
        FROM Compras c 
        JOIN Productos p ON c.IdProducto = p.IdProducto 
        GROUP BY c.IdProducto, p.NombreProducto
        """
        self.db_instance.cursor.execute(query_compras)
        compras_result = self.db_instance.cursor.fetchall()
        
        # Mapear la frecuencia de compras a los productos
        frecuencia_compras = [next((c[1] for c in compras_result if c[0] == p), 0) for p in productos]

        # Crear la gr�fica de barras
        fig = go.Figure()

        # Agregar la frecuencia de ventas
        fig.add_trace(go.Bar(
            x=productos,
            y=frecuencia_ventas,
            name='Frecuencia Ventas',
            marker_color='lightblue'  # Color azul claro para ventas
        ))

        # Agregar la frecuencia de compras
        fig.add_trace(go.Bar(
            x=productos,
            y=frecuencia_compras,
            name='Frecuencia Compras',
            marker_color='pink'  # Color rosa para compras
        ))

        # Configuraci�n del layout de la gr�fica
        fig.update_layout(
            title='Frecuencia de Compras y Ventas por Producto',
            xaxis_title='Producto',
            yaxis_title='Frecuencia',
            barmode='group'
        )
        texto = '''
        La gr�fica ilustra la frecuencia de compras y ventas de cada producto en Magnolia, ofreciendo una comparaci�n visual entre ambas actividades. Con barras en tonos de azul claro para las ventas y rosa para las compras, se puede apreciar r�pidamente la popularidad y demanda de los productos.

        Aspectos destacados:
        - Frecuencia de Transacciones: Cada par de barras muestra cu�ntas veces se ha comprado y vendido un producto, destacando los productos m�s populares o con mayor rotaci�n.
        - Comparaci�n Producto por Producto: La disposici�n permite comparar directamente las frecuencias de compra y venta de cada producto, revelando desequilibrios o simetr�as.
        - Identificaci�n de Tendencias: Se pueden identificar productos con alta demanda pero baja adquisici�n (o viceversa), lo que puede indicar necesidades de ajustes en la gesti�n del inventario o en la estrategia de ventas.
        '''

        return fig, texto

    def grafica_total_compras_por_cliente(self):
        # Obtener el total de compras por cliente
        query_total_compras = """
        SELECT 
        c.Nombre, 
        SUM(v.Total) as TotalCompras
        FROM Ventas v
        JOIN Clientes c ON v.IdCliente = c.IdCliente
        GROUP BY c.Nombre
        ORDER BY TotalCompras DESC
        """
        self.db_instance.cursor.execute(query_total_compras)
        compras_result = self.db_instance.cursor.fetchall()

        # Preparar datos para la gr�fica
        clientes, total_compras = zip(*compras_result)

        # Crear la gr�fica de barras
        fig = go.Figure()

        # Agregar las barras con un mapa de calor para los colores
        fig.add_trace(go.Bar(
            x=clientes,
            y=total_compras,
            marker=dict(color=total_compras, coloraxis="coloraxis")
        ))

        # Configuraci�n del layout de la gr�fica
        fig.update_layout(
            title='Total de Compras por Cliente',
            xaxis_title='Cliente',
            yaxis_title='Total Compras',
            coloraxis=dict(colorscale='Bluered_r'),  # Escala de colores del mapa de calor (reversa)
            template='plotly_white'  # Tema claro
        )
        # Texto descriptivo
        texto = f'''
        La gr�fica 'Total de Compras por Cliente' de Magnolia presenta un an�lisis detallado del volumen de compras realizado por cada cliente, clasificado en orden descendente. La visualizaci�n utiliza barras coloreadas, con tonalidades que var�an seg�n el monto total de compras, para ofrecer una representaci�n clara de la contribuci�n de cada cliente al negocio.

        Los datos m�s sobresalientes incluyen:
        - Cliente Mayor Gasto: '{clientes[0]}' con un total de compras de ${total_compras[0]}.
        - Rango de Gastos: Desde ${min(total_compras)} hasta ${max(total_compras)}, reflejando la diversidad en los patrones de gasto de los clientes.
        '''

        return fig, texto


    #3. Distribuci�n del M�todo de Pago Utilizado por los Clientes
    def grafica_metodo_pago_distribucion(self):
        # Obtener distribuci�n del m�todo de pago
        query_metodo_pago = """
        SELECT 
        MetodoPago, 
        COUNT(IdVenta) as Frecuencia
        FROM Ventas
        GROUP BY MetodoPago
        """
        self.db_instance.cursor.execute(query_metodo_pago)
        metodo_pago_result = self.db_instance.cursor.fetchall()

        # Preparar datos para la gr�fica
        metodos_pago, frecuencias = zip(*metodo_pago_result)

        # Crear la gr�fica de pastel
        fig = go.Figure()

        # Agregar el gr�fico de pastel
        fig.add_trace(go.Pie(
            labels=metodos_pago,
            values=frecuencias,
            pull=[0.1 if max(frecuencias) == f else 0 for f in frecuencias]  # Resaltar el m�todo m�s utilizado
        ))

        # Configuraci�n del layout de la gr�fica
        fig.update_layout(
            title='Distribuci�n del M�todo de Pago',
            template='plotly_white'  # Para un tema claro
        )
        # Texto descriptivo
        texto = f'''
        La gr�fica 'Distribuci�n del M�todo de Pago' de Magnolia ilustra la preferencia de los m�todos de pago entre los clientes. Mediante un gr�fico de pastel, se muestra la frecuencia de cada m�todo, permitiendo identificar cu�les son los m�s populares y utilizados en las transacciones de ventas.

        Datos sobresalientes:
        - M�todo de Pago Principal: '{metodos_pago[frecuencias.index(max(frecuencias))]}', representando el {max(frecuencias) / sum(frecuencias) * 100:.2f}% del total de transacciones.
        - Distribuci�n de M�todos: Permite ver la proporci�n de cada m�todo de pago en relaci�n con el total de ventas.
        '''

        return fig, texto


    def grafica_total_compras_por_proveedor(self):
        query = """
        SELECT 
        p.IdProveedor, 
        SUM(c.PrecioTotal) as TotalCompras
        FROM Compras c
        JOIN Proveedor p ON c.IdProveedor = p.IdProveedor
        GROUP BY p.IdProveedor
        ORDER BY TotalCompras DESC
        """
        self.db_instance.cursor.execute(query)
        resultado = self.db_instance.cursor.fetchall()

        proveedores, total_compras = zip(*resultado)

        fig = go.Figure([go.Bar(x=proveedores, y=total_compras)])
        fig.update_layout(title='Total de Compras por Proveedor', xaxis_title='Proveedor', yaxis_title='Total Compras')

        # Texto descriptivo
        texto = f'''
        La gr�fica 'Total de Compras por Proveedor' ofrece una visi�n clara de las transacciones econ�micas de Magnolia con sus proveedores, representadas en barras que indican el total de compras a cada uno.

        Puntos destacados:
        - Proveedor con Mayor Compra: El proveedor con ID '{proveedores[total_compras.index(max(total_compras))]}', encabeza la lista con un total de compras de ${max(total_compras):,.2f}.
        - Proveedor con Menor Compra: Por otro lado, el proveedor con ID '{proveedores[total_compras.index(min(total_compras))]}', tiene el menor volumen de compras, con un total de ${min(total_compras):,.2f}.
        - An�lisis de Diversificaci�n: La gr�fica muestra c�mo Magnolia distribuye sus compras entre varios proveedores, lo que puede indicar un enfoque diversificado en la gesti�n de la cadena de suministro.
        '''

        return fig, texto

    def grafica_distribucion_tipos_proveedores(self):
        query = """
        SELECT 
        TipoDeProvedor, 
        COUNT(*) as Cantidad
        FROM Proveedor
        GROUP BY TipoDeProvedor
        """
        self.db_instance.cursor.execute(query)
        resultado = self.db_instance.cursor.fetchall()

        tipos, cantidad = zip(*resultado)

        fig = go.Figure([go.Pie(labels=tipos, values=cantidad)])
        fig.update_layout(title='Distribuci�n de Tipos de Proveedores')

        # Determinar el tipo de proveedor con mayor y menor representaci�n
        tipo_mayor_representacion = max(zip(tipos, cantidad), key=lambda x: x[1])
        tipo_menor_representacion = min(zip(tipos, cantidad), key=lambda x: x[1])

        # Texto descriptivo
        texto = f'''
        La gr�fica 'Distribuci�n de Tipos de Proveedores' muestra la diversidad de proveedores con los que Magnolia trabaja, categorizados por su tipo. Cada segmento del gr�fico circular representa un tipo de proveedor diferente y su proporci�n en la base total de proveedores de la empresa.

        Aspectos destacados:
        - Mayor Representaci�n: El tipo de proveedor '{tipo_mayor_representacion[0]}' es el m�s representado, con {tipo_mayor_representacion[1]} proveedores.
        - Menor Representaci�n: El tipo de proveedor '{tipo_menor_representacion[0]}' tiene la menor representaci�n, con solo {tipo_menor_representacion[1]} proveedores.
        '''

        return fig, texto

    def grafica_salarios_por_puesto(self):
        query = """
        SELECT Puesto, SalarioBase
        FROM Puestos
        ORDER BY SalarioBase
        """
        self.db_instance.cursor.execute(query)
        resultado = self.db_instance.cursor.fetchall()

        puestos, salarios = zip(*resultado)

        # Crear una escala de colores (azul, verde, p�rpura)
        colores = ['rgba({}, {}, {}, 1)'.format(r, g, b) for r, g, b in zip(np.linspace(0, 0, len(salarios)), np.linspace(255, 0, len(salarios)), np.linspace(255, 255, len(salarios)))]

        fig = go.Figure(data=[go.Bar(x=puestos, y=salarios, marker_color=colores)])
        fig.update_layout(title='Salarios Base por Puesto', xaxis_title='Puesto', yaxis_title='Salario Base')
        # Identificar el puesto con el salario base m�s alto y el m�s bajo
        puesto_salario_maximo = max(zip(puestos, salarios), key=lambda x: x[1])
        puesto_salario_minimo = min(zip(puestos, salarios), key=lambda x: x[1])

        # Texto descriptivo
        texto = f'''
        La gr�fica 'Salarios Base por Puesto' de Magnolia ilustra los salarios base asignados a diferentes puestos en la organizaci�n. Cada barra representa un puesto espec�fico y la altura de la barra indica el nivel de salario base asociado a ese puesto.

        Aspectos destacados:
        - Mayor Salario Base: El puesto '{puesto_salario_maximo[0]}' tiene el salario base m�s alto en la empresa, con un monto de ${puesto_salario_maximo[1]:.2f}.
        - Menor Salario Base: Por otro lado, el puesto '{puesto_salario_minimo[0]}' cuenta con el salario base m�s bajo, situ�ndose en ${puesto_salario_minimo[1]:.2f}.
        '''

        return fig, texto


    def grafica_boxplot_salarios_por_departamento(self):
        query = """
        SELECT d.Departamento, p.SalarioBase
        FROM Puestos p
        JOIN Departamentos d ON p.IdDepartamento = d.IdDepartamento
        """
        self.db_instance.cursor.execute(query)
        resultado = self.db_instance.cursor.fetchall()

        departamentos, salarios = zip(*resultado)

        df = pd.DataFrame({'Departamento': departamentos, 'SalarioBase': salarios})
        fig = go.Figure()

        for departamento in df['Departamento'].unique():
            dept_salarios = df[df['Departamento'] == departamento]['SalarioBase']
            fig.add_trace(go.Box(y=dept_salarios, name=departamento))

        fig.update_layout(title='Distribuci�n de Salarios por Departamento', yaxis_title='Salario Base', xaxis_title='Departamento')
        # Asegurar que los salarios sean num�ricos
        df['SalarioBase'] = pd.to_numeric(df['SalarioBase'], errors='coerce')

        # Calcular el salario promedio por departamento
        salario_promedio_por_departamento = df.groupby('Departamento')['SalarioBase'].mean()

        # Identificar el departamento con el salario base m�s alto y m�s bajo en promedio
        depto_salario_maximo = salario_promedio_por_departamento.idxmax()
        salario_maximo_promedio = salario_promedio_por_departamento.max()
        depto_salario_minimo = salario_promedio_por_departamento.idxmin()
        salario_minimo_promedio = salario_promedio_por_departamento.min()

        # Crear la figura para los boxplots
        fig = go.Figure()

        for departamento in df['Departamento'].unique():
            dept_salarios = df[df['Departamento'] == departamento]['SalarioBase']
            fig.add_trace(go.Box(y=dept_salarios, name=departamento))

        # Configuraci�n del layout de la gr�fica
        fig.update_layout(
            title='Distribuci�n de Salarios por Departamento',
            yaxis_title='Salario Base',
            xaxis_title='Departamento'
        )

        # Texto descriptivo
        texto = f'''
        La gr�fica 'Distribuci�n de Salarios por Departamento' muestra la variabilidad y la distribuci�n de los salarios base dentro de cada departamento de Magnolia. Los 'boxplots' individuales representan diferentes departamentos, proporcionando un an�lisis visual de la dispersi�n salarial y la tendencia central.

        Aspectos destacados:
        - Departamento con Mayor Salario Promedio: '{depto_salario_maximo}' destaca con un salario promedio m�s alto de aproximadamente ${salario_maximo_promedio:.2f}.
        - Departamento con Menor Salario Promedio: En contraste, '{depto_salario_minimo}' tiene el salario promedio m�s bajo, alrededor de ${salario_minimo_promedio:.2f}.
        '''

        return fig, texto

             
if __name__ == '__main__':
    db_config = {
        'server': 'LAPTOP-IN22ALJ9\\MSSQLSERVER01',
        'database': 'MagnoliaDB'
    }
    
    graph = Graficas(**db_config)
    
    fig, texto = graph.grafica_top3_empleados()
    fig.show()
