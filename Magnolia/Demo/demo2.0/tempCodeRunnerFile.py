
from flask import render_template, request, session, redirect, url_for, flash, jsonify
from funct.DataBase import DataBase
from funct.gpt_grafico import gpt_grafico
import plotly.io

selections = {}
@app.route('/get_columns', methods=['POST'])
def get_columns():
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('login'))

    selected_tables = request.json['tables']
    server_name = user_info['server'].replace("\\\\", "\\")
    new_db_config = {'server': server_name, 'database': user_info['db_name']}
    db = DataBase(**new_db_config)
    db.connect()

    columns = {}
    for table in selected_tables:
        table = table.translate({ord('('): None})
        table = table.translate({ord(','): None})
        table = table.translate({ord(')'): None})
        print(table)
        query = f"SELECT column_name FROM information_schema.columns WHERE table_name = {table}"
        try:
            query_results = db.execute_query(query)
            columns[table] = [row[0] for row in query_results]
        except Exception as e:
            print(f"Error executing query for table '{table}': {e}")
            columns[table] = []

    db.close()
    return jsonify(columns)

@app.route('/get_selections', methods=['GET'])
def get_selections():
    return jsonify(selections)

@app.route('/graficas_gpt', methods=['GET', 'POST'])
def graficas_gpt():
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('login'))

    db_config = {'server': user_info['server'].replace("\\\\", "\\"), 'database': user_info['db_name']}
    graph_html, description, tables = None, None, None

    if request.method == 'POST':
        if 'user_input' in request.form:
            # Procesar la entrada del usuario para generación de gráficos
            user_input = request.form.get('user_input')
            try:
                gpt_graph_instance = gpt_grafico(user_info['server'], user_info['db_name'])
                graph_function_code = gpt_graph_instance.generate_graph_function(user_input)
                function_name = gpt_graph_instance.append_to_graficas_py(graph_function_code)

                from funct.Graficas import Graficas
                graph_instance = Graficas(**db_config)
                if hasattr(graph_instance, function_name):
                    fig, description = getattr(graph_instance, function_name)()
                    graph_html = plotly.io.to_html(fig, full_html=False)
                else:
                    graph_html, description = None, "No se pudo generar la gráfica."

            except Exception as e:
                graph_html, description = None, f"Error: {e}"

        elif 'selection' in request.form:
            # Procesar la selección de tablas y columnas
            selection = request.form.getlist('selection')
            formatted_selection = format_selection(selection)
            for table, columns in formatted_selection.items():
                if table in selections:
                    for column in columns:
                        if column not in selections[table]:
                            selections[table].append(column)
                else:
                    selections[table] = columns
            flash('Selection has been updated.')

    # Cargar información de las tablas para la selección
    db = DataBase(**db_config)
    db.connect()
    tables = db.execute_query("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'")
    db.close()

    return render_template('graficas_gpt.html', user_info=user_info, graph_html=graph_html, description=description, tables=tables, selections=selections)

def format_selection(selection):
    formatted = {}
    for item in selection:
        if '.' in item:
            table, column = item.split('.')
            if table not in formatted:
                formatted[table] = []
            formatted[table].append(column)
    return formatted