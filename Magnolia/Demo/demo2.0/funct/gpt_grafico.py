import openai
import os
from dotenv import load_dotenv
from funct.DataBase import DataBase
from fuzzywuzzy import process
import re
import traceback

class gpt_grafico:
    def __init__(self, server_name, db_name):
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("No se encontró la clave API. Por favor, revisa tu archivo .env.")
        openai.api_key = api_key

        self.db_instance = DataBase(server_name, db_name)
        self.db_instance.connect()
        self.keywords_dict = {
            "Tablas": self.get_table_names()
        }
        self.messages_history = []  # Initialize the messages history

    def get_table_names(self):
        query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'"
        result = self.db_instance.execute_query(query)
        if result is None:
            return {}
        return {row[0]: row[0] for row in result}

    def get_column_names(self, table_name):
        query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
        result = self.db_instance.execute_query(query)
        if result is None:
            return []
        return [row[0] for row in result]

    def decide_tables_and_columns(self, keywords, threshold=70):
        selected_tables = set()
        selected_columns = set()

        for keyword in keywords:
            table_matches = process.extract(keyword, list(self.keywords_dict["Tablas"].values()), limit=None)
            for table, score in table_matches:
                if score >= threshold:
                    selected_tables.add(table)

            for table in selected_tables:
                columns = self.get_column_names(table)
                for column_keyword in keywords:
                    column_matches = process.extract(column_keyword, columns, limit=None)
                    for column, score in column_matches:
                        if score >= threshold:
                            selected_columns.add((table, column))

        return selected_tables, selected_columns

    def generate_graph_function(self, user_input):
        self.update_history("user", user_input)

        # Aquí, 'keywords' pueden ser extraídos del 'user_input' para decidir las tablas y columnas
        tables, columns = self.decide_tables_and_columns(user_input.split(), threshold=80)
        prompt = (
                    f"Tablas y columnas relevantes para la llamada SQL dentro del gráfico: {tables}, {columns}. "
                    f"Crea una función en Python para generar un gráfico basado en datos de la base de datos. "
                    f"Tipo de gráfico solicitado: {user_input}. "
                    f"Los datos provienen de la base de datos con las siguientes tablas y columnas: {self.keywords_dict['Tablas']}. "
                    f"La función debe ejecutar una consulta SQL, procesar los resultados y generar un gráfico con Plotly. "
                    "REVISA ERRORES EN LA CONSULTA SQL NO USES FUNCIONES COMO LIMIT O TOP DEBIDO A LA VERSIÓN QUE ESTOY UTILIZANDO, PARA EVITAR ERRORES COMO LOS SIGUIENTES:\n"
                    "pyodbc.ProgrammingError: ('42000', '[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Sintaxis incorrecta cerca de 'LIMIT'. (102) (SQLExecDirectW)')\n"
                    "pyodbc.ProgrammingError: ('42000', '[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Uso inválido de la opción NEXT en la declaración FETCH. (153) (SQLExecDirectW)')\n"
                    "('42000', '[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]The text, ntext, and image data types cannot be compared or sorted, except when using IS NULL or LIKE operator)\n"
                    "self.db_instance no olvides que estás usando self para llamar a db_instance, no cambies esto\n"
                    "VERIFICA LA LÓGICA PARA ASEGURAR QUE TODO FUNCIONE COMO DEBERÍA Y SIGUE EL EJEMPLO QUE TE DI COMO PLANTILLA PARA GENERAR TUS GRÁFICOS AL PIE DE LA LETRA\n"
                    "LAS COLUMNAS CON Fecha en su nombre tienen el siguiente formato 'yyyy-mm-dd', por ejemplo, '2023-01-01'\n"
                    "EVITA ERRORES COMO EL SIGUIENTE:\n"
                    "ValueError: La forma de los valores pasados es (50, 1), los índices implican (50, 2)\n"
                    "NO CAMBIES EL FORMATO DE LA GRÁFICA Y DE CÓMO SE LLAMA A LA BASE DE DATOS\n"
                    "UTILIZA SOLAMENTE LAS SIGUIENTES LIBRERÍAS Y EL FORMATO DE MI FUNCIÓN DE EJEMPLO\n"
                    "Incluye un texto descriptivo sobre los resultados del gráfico. Aquí tienes un ejemplo de cómo podría verse la función:\n\n"
                    "TEN CUADO AL MANEJAR result EN LA SIGUIENTE FUNCION, CHECA BIEN COMO SE HACE YA QUE ES UNA TUPLA"
                    "Librerías a utilizar solamente las librerias que te muestro puedes:\n"
                    "import numpy as np\n"
                    "import pandas as pd\n"
                    "import plotly.graph_objs as go\n"
                    "from plotly.subplots import make_subplots\n"
                    "def grafica_violin_genero_edad(self):\n"
                    "    query = \"SELECT Genero, Edad FROM Empleados\"\n"
                    "    self.db_instance.cursor.execute(query)\n"
                    "    result = self.db_instance.cursor.fetchall()\n"
                    "    print(result)\n"
                    "    \n"
                    "    # Preparar los datos\n"
                    "    edades_hombres = [row[1] for row in result if row[0] == 'Masculino']\n"
                    "    edades_mujeres = [row[1] for row in result if row[0] == 'Femenino']\n"
                    "    \n"
                    "    # Crear los gráficos de violín\n"
                    "    trace1 = go.Violin(y=edades_hombres, name='Hombres', box_visible=True, line_color='blue')\n"
                    "    trace2 = go.Violin(y=edades_mujeres, name='Mujeres', box_visible=True, line_color='pink')\n"
                    "    \n"
                    "    # Calcular estadísticas\n"
                    "    media_hombres = np.mean(edades_hombres)\n"
                    "    std_hombres = np.std(edades_hombres)\n"
                    "    media_mujeres = np.mean(edades_mujeres)\n"
                    "    std_mujeres = np.std(edades_mujeres)\n"
                    "    \n"
                    "    # Configuración de la gráfica\n"
                    "    data = [trace1, trace2]\n"
                    "    layout = go.Layout(\n"
                    "        title='Distribución de Edad por Género',\n"
                    "        yaxis=dict(title='Edad'),\n"
                    "        xaxis=dict(title='Género'),\n"
                    "        annotations=[\n"
                    "            dict(\n"
                    "                x=0.1, y=media_hombres, xref='paper', yref='y', showarrow=False, \n"
                    "                text=f'Media: {media_hombres:.1f}, Std: {std_hombres:.1f}', \n"
                    "                font=dict(color='white'), bgcolor='blue'\n"
                    "            ),\n"
                    "            dict(\n"
                    "                x=0.7, y=media_mujeres, xref='paper', yref='y', showarrow=False, \n"
                    "                text=f'Media: {media_mujeres:.1f}, Std: {std_mujeres:.1f}', \n"
                    "                font=dict(color='white'), bgcolor='pink'\n"
                    "            )\n"
                    "        ]\n"
                    "    )\n"
                    "    \n"
                    "    texto = f'''\n"
                    "    Esta gráfica de violín muestra la distribución de edades de los empleados de Magnolia, diferenciando entre géneros masculino y femenino.\n\n"
                    "    Hombres: Edad promedio de aproximadamente {media_hombres:.1f} años con una variabilidad estándar de {std_hombres:.1f} años.\n"
                    "    Mujeres: Edad promedio cercana a {media_mujeres:.1f} años con una desviación estándar de {std_mujeres:.1f} años.\n"
                    "    La forma de cada violín indica las edades más comunes y la dispersión de edades dentro de cada género.\n"
                    "    '''\n"
                    "    \n"
                    "    fig = go.Figure(data=data, layout=layout)\n"
                    "    return fig, texto\n"
                    "    \n"
                    )

        # Asegúrate de que el historial de mensajes esté formateado correctamente
        history_text = "\n".join([f"{message['role']}: {message['content']}" for message in self.messages_history])
        prompt_with_history = prompt

        self.generated_python_code = None
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt_with_history}]
            )
            response_text = response['choices'][0]['message']['content']

            python_code = self.extract_python_code(response_text)
            print(python_code)
            if python_code:
                self.generated_python_code = python_code  # Almacena el código generado
                return python_code
            else:
                return "No se pudo generar el código."
        except Exception as e:
            return f"Error: {e}"
        
    def clean_python_code(self, code):
        # Eliminar palabras "python" o "Python" al principio o al final, excepto en bloques de texto multilínea
        lines = code.splitlines()
        cleaned_lines = []
        skip_line = False
        for line in lines:
            if 'texto = f' in line and line.strip().endswith("'''"):
                skip_line = True
            if skip_line:
                cleaned_lines.append(line)
                if line.strip() == "'''":
                    skip_line = False
                continue
            cleaned_line = line.lstrip("pythonPython").rstrip("pythonPython")
            # Filtrar variables con caracteres no ASCII y eliminar símbolos específicos
            cleaned_line = self._remove_non_ascii_and_specific_symbols(cleaned_line)
            cleaned_line = re.sub(r'[^\x00-\x7F]+', ' ', cleaned_line)
            cleaned_lines.append(cleaned_line)

        return '\n'.join(cleaned_lines)

    def _remove_non_ascii_and_specific_symbols(self, line):
        # Esta función elimina variables con caracteres no ASCII y símbolos específicos
        tokens = line.split()
        cleaned_tokens = []
        for token in tokens:
            if "=" in token and not all(ord(c) < 128 for c in token):
                # Si el token es una asignación de variable y contiene caracteres no ASCII, se omite
                continue
            # Eliminar el símbolo � (U+FFFD)
            token = token.replace('\ufffd', '')
            cleaned_tokens.append(token)
        return ' '.join(cleaned_tokens)

    def extract_python_code(self, response_text):
        # Identificar el comienzo del bloque de código Python
        code_start_marker = "```python"
        code_end_marker = "```"

        code_start = response_text.find(code_start_marker)
        if code_start == -1:
            # Manejar caso en que "python" no esté en minúscula
            code_start_marker = "```Python"
            code_start = response_text.find(code_start_marker)

        if code_start != -1:
            code_start += len(code_start_marker)
            code_end = response_text.find(code_end_marker, code_start)
            if code_end != -1:
                # Extraer el código Python
                python_code = response_text[code_start:code_end].strip()

                # Eliminar las importaciones y retornar solo la función
                return self._extract_function_code(python_code)

        return None

    def _extract_function_code(self, code):
        # Buscar el inicio de la función (primer 'def')
        function_start = code.find('def ')
        if function_start != -1:
            return code[function_start:]
        else:
            return code
        
    def append_to_graficas_py(self, python_code, remove_existing=False):
        graficas_file_path = 'funct/Graficas.py'  # Ruta relativa al archivo

        # Leer el contenido existente
        with open(graficas_file_path, 'r', encoding='utf-8', errors='replace') as file:
            content = file.read()

        # Obtener el nombre de la función
        function_name_line = python_code.split('\n')[0]
        function_name = function_name_line.split(' ')[1].split('(')[0]

        # Verificar si la función ya existe y eliminarla si es necesario
        start = content.find(f'def {function_name}')
        if start != -1:
            end = content.find('\n    def ', start + 1)
            if end == -1:  # Si no hay más funciones después
                end = len(content)
            content = content[:start] + content[end:]

        # Encontrar el final del bloque __init__
        init_end = content.find('\n    def ', content.find('def __init__'))
        init_block_end = content.find('\n    def ', init_end + 1) if init_end != -1 else len(content)
        if init_block_end == -1:
            init_block_end = len(content)

        # Insertar el nuevo código en la posición encontrada
        new_content = content[:init_block_end] + '\n\n    ' + python_code.replace('\n', '\n    ') + content[init_block_end:]

        # Escribir el contenido actualizado en el archivo
        with open(graficas_file_path, 'w', encoding='utf-8', errors='replace') as file:
            file.write(new_content)

        return function_name

        
    def user_input_and_plot(self):
        while True:
            user_input = input("Por favor, ingresa el tipo de gráfico que deseas generar: ")
            self.update_history("user", user_input)

            graph_function_code = self.generate_graph_function(user_input)
            if graph_function_code and graph_function_code != "No se pudo generar el código.":
                function_name = self.append_to_graficas_py(graph_function_code)
                print(f"Función '{function_name}' generada y añadida a Graficas.py.")

                from funct.Graficas import Graficas
                db_config = {
                    'server': 'LAPTOP-IN22ALJ9\\MSSQLSERVER01',
                    'database': 'MagnoliaDB'
                }
                graph_instance = Graficas(**db_config)

                try:
                    if hasattr(graph_instance, function_name):
                        fig, txt = getattr(graph_instance, function_name)()
                        fig.show()
                    else:
                        print(f"No se encontró la función '{function_name}' en la clase Graficas.")
                except Exception as e:
                    error_traceback = traceback.format_exc()  # Aquí se captura el traceback completo
                    print("Se encontró un error al generar la gráfica. Buscando solución...")
                    print(error_traceback)  # Imprime el traceback para diagnóstico
                    corrected_code = self.handle_graph_error(user_input, error_traceback)

                    if corrected_code:
                        self.append_to_graficas_py(graph_function_code, remove_existing=True)
                        new_function_name = self.append_to_graficas_py(corrected_code)
                        try:
                            if hasattr(graph_instance, new_function_name):
                                fig, txt = getattr(graph_instance, new_function_name)()
                                fig.show()
                        except Exception as exc:
                            print(f"Error al intentar ejecutar la función corregida: {exc}")
                break
            else:
                print("No se pudo generar la función de gráfico. ¿Deseas intentarlo de nuevo? (s/n): ")
                if input().lower() != 's':
                    break

    def handle_graph_error(self, user_input, error_message):
        # Crear un prompt detallado con la descripción del error
        print(error_message)
        # Descripción detallada del error
        prompt = (
            f"Hubo un error al intentar generar una gráfica con el input '{user_input}'. "
            "El código que causó este error es:\n\n"
            f"{self.generated_python_code}\n\n"
            f"Error: {error_message}. "
            "RECUERDA QUE LA VARIABLE result DENTRO DE LA FUNCION  ES UNA TUPLA CON LA SIGIENTE FORMA DE EJEMPLO: "
            "TOMA ESTO EN CUENTA AL TRABAJAR CON EL DATAFRAME"
            "Identifica y corrige el problema en el código. "
            "Deja el mismo nombre a la grafica"
            "Considera los siguientes aspectos para prevenir errores comunes:\n"
            "- Validación de los datos antes de su procesamiento.\n"
            "- Corrección de errores de dimensiones en pandas DataFrame.\n"
            "- Asegurarse de que las consultas SQL devuelvan resultados esperados.\n"
            "- Uso correcto de la identación y convenciones de Python.\n"
            "El código corregido deberá ejecutar la consulta SQL, procesar los resultados y generar un gráfico con Plotly sin errores.\n"
            "REVISA ERRORES EN LA CONSULTA SQL NO USES FUNCIONES COMO LIMIT O TOP DEBIDO A LA VERSIÓN QUE ESTOY UTILIZANDO, PARA EVITAR ERRORES COMO LOS SIGUIENTES:\n"
            "pyodbc.ProgrammingError: ('42000', '[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Sintaxis incorrecta cerca de 'LIMIT'. (102) (SQLExecDirectW)')\n"
            "pyodbc.ProgrammingError: ('42000', '[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Uso inválido de la opción NEXT en la declaración FETCH. (153) (SQLExecDirectW)')"
        )

        # Asegúrate de que el historial de mensajes esté formateado correctamente
        history_text = "\n".join([f"{message['role']}: {message['content']}" for message in self.messages_history])
        prompt_with_history = prompt + "\n\nHistorial de mensajes:\n" + history_text

        try:
            # Enviar la consulta a GPT-3 y obtener la respuesta
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt_with_history}]
            )
            response_text = response['choices'][0]['message']['content']

            # Extraer el código Python de la respuesta
            python_code = self.extract_python_code(response_text)

            if python_code:
                print("Nuevo código generado por GPT-3 para resolver el error:\n", python_code)
                return python_code
            else:
                print("No se pudo extraer el código de la respuesta de GPT-3.")
                return None

        except Exception as e:
            print(f"Error al consultar a GPT-3 para la solución del problema: {e}")
            return None

    # Add a method to update the message history
    def update_history(self, role, content):
        self.messages_history.append({"role": role, "content": content})

if __name__ == '__main__':
    db_config = {
        'server_name': 'LAPTOP-IN22ALJ9\\MSSQLSERVER01',
        'db_name': 'MagnoliaDB'
    }
    gpt_graph_instance = gpt_grafico(**db_config)

    while True:
        try:
            gpt_graph_instance.user_input_and_plot()
            break  # Salir del bucle si todo se ejecuta correctamente
        except Exception as e:
            print(f"Se ha producido un error inesperado: {e}")
            # Opcionalmente, puedes decidir si deseas continuar intentando o salir del bucle
            user_choice = input("¿Deseas intentarlo de nuevo? (s/n): ")
            if user_choice.lower() != 's':
                break
