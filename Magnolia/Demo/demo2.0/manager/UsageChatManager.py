from flask import session, flash
from funct.DataBase import DataBase

class UsageChatManager:
    @staticmethod
    def validate_user_session():
        """Validate user session."""
        if 'user_info' not in session:
            flash('Please log in to view this page.')
            return None
        return session['user_info']

    @staticmethod
    def get_db_config(user_info):
        """Get database configuration from user info."""
        server_name = user_info['server'].replace("\\\\", "\\")
        return {
            'server': server_name,
            'database': user_info['db_name']
        }

    @staticmethod
    def fetch_tables_and_columns(db_config):
        """Fetch tables and their columns from the database."""
        db = DataBase(**db_config)  # Crear una instancia de DataBase
        db.connect()  # Conectar a la base de datos

        try:
            tables_query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'"
            tables = db.execute_query(tables_query)

            tables_columns = {}
            for table in tables:
                columns_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table[0]}'"
                columns = db.execute_query(columns_query)
                tables_columns[table[0]] = [column[0] for column in columns]

        finally:
            db.close()  # Asegurarse de cerrar la conexión a la base de datos

        return tables_columns