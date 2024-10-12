import openai
import os
from dotenv import load_dotenv
from funct.DataBase import DataBase
from fuzzywuzzy import process
import logging

# Configura el logging para depuración
logging.basicConfig(level=logging.DEBUG)

class gpt:
    def __init__(self, server_name, db_name):
        # Carga la clave API desde el archivo .env y configura la clave API de OpenAI
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("No se encontró la clave API. Por favor, revisa tu archivo .env.")
        openai.api_key = api_key

        # Instancia de la clase DataBase y conexión
        self.db_instance = DataBase(server_name, db_name)
        self.db_instance.connect()
        self.keywords_dict = {
            "Tablas": self.get_table_names()
        }
        self.messages_history = [{"role": "system", "content": "Eres un asistente útil."}]
        
    def get_table_names(self):
        query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'"
        result = self.db_instance.execute_query(query)
        if result is None:
            return {}
        return {row[0]: row[0] for row in result}
        
    def update_history(self, role, content):
        self.messages_history.append({"role": role, "content": content})
                
    def get_column_names(self, table_name):
        query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
        result = self.db_instance.execute_query(query)
        if result is None:
            return []
        return [row[0] for row in result]

    def decide_tables_and_columns(self, keywords, threshold=70):
        selected_tables = set()
        selected_columns = set()

        # Identificar tablas relevantes
        for keyword in keywords:
            table_matches = process.extract(keyword, list(self.keywords_dict["Tablas"].values()), limit=None)
            for table, score in table_matches:
                if score >= threshold:
                    selected_tables.add(table)

        # Identificar columnas relevantes de las tablas seleccionadas
        for table in selected_tables:
            columns = self.get_column_names(table)
            for keyword in keywords:
                column_matches = process.extract(keyword, columns, limit=None)
                for column, score in column_matches:
                    if score >= threshold:
                        selected_columns.add((table, column))

        return selected_tables, selected_columns

    def process_user_query(self, user_query):
        # Divide la pregunta del usuario en palabras
        keywords = user_query.split()

        # Busca tablas y columnas con estas palabras clave
        tables, columns = self.decide_tables_and_columns(keywords, threshold=80)
        return tables, columns

    def generate_sql_query(self, user_input):
        logging.debug(f"Generando consulta SQL para la entrada del usuario")
        
        # Update history with user input
        self.update_history("user", user_input)

        tablas, columnas = self.process_user_query(user_input)
        print(tablas)
        print(columnas)
        # Crear el prompt para GPT-4
        prompt = (
            f"Descripcion de la base de datos : tablas {tablas}, columnas = {columnas}."
            f"Tarea principal:Genera una consulta SQL detallada y precisa con las tablas y columnas relevantes de la base de datos anterior, para Microsoft SQL Server que responda a la pregunta específica: '{user_input}'. "
            f"Utiliza únicamente las las tablas y columnas de la descripcion de la base de datos. "
            f"Incluye cualquier JOIN necesario, agrupación o condiciones WHERE que puedan ser relevantes."
            f"Para la limitación de filas, utiliza la sintaxis 'SELECT TOP (n)' de SQL Server en lugar de 'LIMIT' o 'FETCH'. "
            f"Asegúrate de que la consulta sea ejecutable en SQL Server y no utilice sintaxis de otros gestores de base de datos como MySQL o PostgreSQL. "
            f"Evita también las acciones que puedan modificar o borrar datos irreversiblemente."
            f"Si la columnas tiene Fecha en su nombre este es el formato de la fecha, ejemplo: '2023-01-05'"
            f"Si preguntan sobre un Empleado agrega de esa tabla su nombre y apellido. ese tabien es el noobre de las columnas"
            f"EVITA LOS SIGUIENTES ERRORES AL HACER LA QEURY DE SQL:\n"
            f"pyodbc.ProgrammingError: ('42000', '[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Incorrect syntax near 'LIMIT'. (102) (SQLExecDirectW)')\n"
            f"pyodbc.ProgrammingError: ('42000', '[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Invalid usage of the option NEXT in the FETCH statement. (153) (SQLExecDirectW)')"
        )
        
        # Asegúrate de que el historial de mensajes esté formateado correctamente
        history_text = "\n".join([f"{message['role']}: {message['content']}" for message in self.messages_history])
        prompt_with_history = prompt
        logging.debug(f"Prompt con historial: {prompt_with_history}")

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt_with_history}]
            )
            response_text = response['choices'][0]['message']['content']
            logging.debug(f"Respuesta de GPT-4: {response_text}")

            sql_query = self.extract_sql_query(response_text)
            if sql_query:
                logging.debug(f"Consulta SQL generada: {sql_query}")
                return sql_query
            else:
                logging.error("No se encontró una consulta SQL en la respuesta de GPT-4.")
                return None
        except Exception as e:
            logging.error(f"Error al generar la consulta SQL: {e}")
            return None
    def extract_sql_query(self, response_text):
        logging.debug("Extrayendo consulta SQL del texto de respuesta.")

        # Busca con diferentes delimitadores
        sql_query_start = response_text.lower().find("'''")
        end_delimiter = "'''"
        if sql_query_start == -1:
            sql_query_start = response_text.lower().find("```sql")
            end_delimiter = "```"
            if sql_query_start == -1:
                sql_query_start = response_text.lower().find("```SQL".lower())
                if sql_query_start == -1:
                    sql_query_start = response_text.lower().find("```")
                    end_delimiter = "```"

        if sql_query_start != -1:
            sql_query_start += len(end_delimiter)
            sql_query_end = response_text.lower().find(end_delimiter, sql_query_start)

            if sql_query_end != -1:
                # Extrae y limpia la consulta SQL
                sql_query = response_text[sql_query_start:sql_query_end].strip()
                # Elimina la palabra "sql" si está al principio
                if sql_query.lower().startswith("sql"):
                    sql_query = sql_query[3:].strip()
                if sql_query.lower().startswith("SQL"):
                    sql_query = sql_query[3:].strip()
                if sql_query:
                    logging.debug(f"Consulta SQL extraída: {sql_query}")
                    return sql_query

        logging.error("No se pudo extraer la consulta SQL.")
        return None

    def execute_sql_query(self, sql_query):
        if not sql_query:
            return None

        # Eliminar caracteres inválidos como comillas invertidas
        sql_query = sql_query.replace('`', '')

        if sql_query != "NO PUEDO HACER ESTO":
            try:
                result = self.db_instance.execute_query_params(sql_query, ())
                return result
            except Exception as e:
                print(f"Error executing query: {e}")
                print(f"SQL Query: {sql_query}")
                return None
        else:
            return None
            
    def get_response_db_enabled(self, user_input):
        """
        Obtiene una respuesta usando ChatGPT con soporte para consultas de base de datos.
        """
        # Genera la consulta SQL a partir del input del usuario
        sql_query = self.generate_sql_query(user_input)
        db_response = self.execute_sql_query(sql_query)

        # Verifica si se obtuvieron resultados y los formatea
        db_response_text = 'No se obtuvieron resultados' if db_response is None else ', '.join([str(row) for row in db_response])

        # Prepara el mensaje para GPT
        explanation_request = f"Por favor, describe en lenguaje natural y de la mejor manera posible el resultado a la pregunta, HAZ LA RESPUES FORMAL Y ENTENDIBLE, SE PRECISO: '{user_input}'. El resultado de la consulta SQL es: {db_response_text}"

        # Crea un mensaje con el resultado de la consulta SQL y la solicitud de explicación
        self.update_history("assistant", explanation_request)

        # Crea el prompt para enviar a GPT con la explicación de los resultados de la base de datos
        history_text = "\n".join([f"{message['role']}: {message['content']}" for message in self.messages_history])

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": history_text}]
            )
            assistant_response = response['choices'][0]['message']['content']
        except Exception as e:
            assistant_response = str(e)

        self.update_history("assistant", assistant_response)
        return assistant_response


    def get_response_db_disabled(self, user_input):
        """
        Obtiene una respuesta usando ChatGPT sin soporte para consultas de base de datos.
        """
        self.update_history("user", user_input)
        history_text = "\n".join([f"{message['role']}: {message['content']}" for message in self.messages_history])

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": history_text}]
            )
            assistant_response = response['choices'][0]['message']['content']
        except Exception as e:
            assistant_response = str(e)

        self.update_history("assistant", assistant_response)
        return assistant_response
    
    def web_run(self, user_query, db_mode):
        # Añadir consulta del usuario al historial
        self.update_history("user", user_query)

        # Manejar la respuesta de GPT
        if db_mode:
            response = self.get_response_db_enabled(user_query)
        else:
            response = self.get_response_db_disabled(user_query)

        return response
       
if __name__ == '__main__':
    
    db_config = {
        'server_name': 'LAPTOP-IN22ALJ9\\MSSQLSERVER01',
        'db_name': 'MagnoliaDB'
    }
    gpt_instance = gpt(**db_config)

    while True:
        user_query = input("Por favor, ingresa tu pregunta (o escribe 'salir' para terminar): ")
        if user_query.lower() == 'salir':
            print("Saliendo del programa.")
            break

        db_mode = input("¿Quieres utilizar la base de datos para esta consulta? (si/no): ").strip().lower() == 'si'
        
        if db_mode:
            response = gpt_instance.get_response_db_enabled(user_query)
        else:
            response = gpt_instance.get_response_db_disabled(user_query)

        print("GPT:", response)