from manager.LoginManager import LoginManager
from manager.HomeManager import HomeManager
from manager.ChatManager import ChatManager
from manager.UsageChatManager import UsageChatManager
from manager.OrganoManager import OrganoManager 

from flask import Flask, request, render_template, flash, redirect, url_for, session, jsonify
import json


app = Flask(__name__)
app.secret_key = 'your_real_secret_key_here'


db_config = {
    'server': 'LAPTOP-IN22ALJ9\\MSSQLSERVER01',
    'database': 'usersdb'
}

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    login_manager = LoginManager(db_config)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if login_manager.authenticate_user(username, password):
            return redirect(url_for('home'))
        else:
            flash('Incorrect username or password.')

    return render_template('login.html')

@app.route('/home')
def home():
    user_info = HomeManager.load_user_session()
    if user_info is None:
        return redirect(url_for('login'))

    home_manager = HomeManager(user_info)
    db = home_manager.get_db_connection()
    if db is None:
        return render_template('error.html', error="Database connection error")

    nombres_secciones, secciones_dic = home_manager.process_user_sections()
    if nombres_secciones is None or secciones_dic is None:
        return render_template('error.html', error="Invalid secciones_dic format")

    # Add any additional logic you need here

    db.close()
    return render_template('home.html', user_info=user_info,
                           nombres_secciones=nombres_secciones,
                           secciones_dic=secciones_dic)

@app.route('/logout')
def logout():
    # Clear the user session
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user_info' not in session:
        return redirect(url_for('login'))

    user_info = session['user_info']
    gpt_instance = ChatManager.initialize_gpt_instance(user_info)

    if request.method == 'POST':
        return ChatManager.process_post_request(gpt_instance)

    # Optional: Handle GET request
    # return process_get_request()

    return "Invalid request method", 400

@app.route('/usage_chat')
def usage_chat():
    user_info = UsageChatManager.validate_user_session()
    if user_info is None:
        return redirect(url_for('login'))

    db_config_1 = UsageChatManager.get_db_config(user_info)
    
    try:
        secciones_dic = json.loads(user_info['secciones_dic'])
    except json.JSONDecodeError:
        flash("Error decoding secciones_dic.")
        return render_template('error.html', error="Invalid secciones_dic format")

    nombres_secciones = list(secciones_dic.keys())
    
    tables_columns = UsageChatManager.fetch_tables_and_columns(db_config_1)

    return render_template('usage_chat.html', user_info=user_info, tables_columns=tables_columns,
                           secciones_dic=secciones_dic, nombres_secciones=nombres_secciones)


@app.route('/organo/<seccion>')
def organo(seccion):
    organo_manager = OrganoManager()  # Create an instance of OrganoManager

    user_info = organo_manager.validate_user(session)  # Use the instance to call methods
    if not user_info:
        return  # Redirect is handled in validate_user

    db_config_2 = organo_manager.get_db_config(user_info)
    secciones_dic = organo_manager.load_section_info(user_info)
    if secciones_dic is None:
        return  # Error template already rendered

    datos, columnas, df = organo_manager.execute_queries(db_config_2, secciones_dic, seccion)
    graficas_html = organo_manager.generate_graphs(secciones_dic, seccion, db_config_2)
    
    analysis_results = organo_manager.performance_analysis(df, columnas)

    df_empty = df.empty
    if not df_empty:
        df.to_excel(f'static/{seccion}_data.xlsx')

    nombres_secciones = list(secciones_dic.keys())

    return render_template('organo.html', 
                           datos=datos, 
                           columnas=columnas, 
                           seccion_actual=seccion,
                           tablas_seccion=secciones_dic[seccion]['Tablas'],
                           graficas=graficas_html, 
                           df_empty=df_empty, 
                           nombres_secciones=nombres_secciones, 
                           secciones_dic=secciones_dic,
                           analysis_results=analysis_results)



from funct.gpt_grafico import gpt_grafico
import plotly

@app.route('/graficas_gpt', methods=['GET', 'POST'])
def graficas_gpt():
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('login'))

    # Valores predeterminados para graph_html y description
    graph_html, description = None, None

                    
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        
        server_name = user_info['server'].replace("\\\\", "\\")
        
        # Lógica para procesar la entrada del usuario y generar el gráfico y el texto
        try:
            gpt_graph_instance = gpt_grafico(server_name, user_info['db_name'])
            graph_function_code = gpt_graph_instance.generate_graph_function(user_input)
            function_name = gpt_graph_instance.append_to_graficas_py(graph_function_code)
            print(function_name)
            # Ejecutar la función generada y obtener la gráfica y el texto
            from funct.Graficas import Graficas
            graph_instance = Graficas(server_name, user_info['db_name'])
            if hasattr(graph_instance, function_name):
                funcion_grafica = getattr(graph_instance, function_name)
                fig, text = funcion_grafica()  # Ejecuta la función
                fig.show()
                graph_html = plotly.io.to_html(fig, full_html=False)  # Ensure this matches the variable passed to the template
            else:
                graph_html, description = None, "No se pudo generar la gráfica."

        except Exception as e:
            graph_html, description = None, f"Error: {e}"
    # Justo antes de return en tu función graficas_gpt
    print("Debug - Graph HTML:", graph_html)  # Imprime el HTML de la gráfica para depuración

    return render_template('graficas_gpt.html', user_info=user_info, graph_html=graph_html, description=description)

 
if __name__ == '__main__':
    app.run(debug=True)