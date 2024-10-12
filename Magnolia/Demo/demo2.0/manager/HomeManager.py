import json
from flask import session, flash
from funct.DataBase import DataBase  # Make sure this is accessible in the folder

class HomeManager:
    def __init__(self, user_info):
        self.user_info = user_info

    @staticmethod
    def load_user_session():
        """Load user session data."""
        if 'user_info' not in session:
            flash('Please log in to view this page.')
            return None
        return session['user_info']

    def get_db_connection(self):
        """Establish a database connection."""
        server_name = self.user_info['server'].replace("\\\\", "\\")
        new_db_config = {
            'server': server_name,
            'database': self.user_info['db_name']
        }
        try:
            db = DataBase(**new_db_config)
            db.connect()
            return db
        except Exception as e:
            flash(f"Error connecting to the database: {e}")
            return None

    def process_user_sections(self):
        """Process user sections."""
        secciones_dic_str = self.user_info['secciones_dic']
        try:
            secciones_dic = json.loads(secciones_dic_str)
            nombres_secciones = list(secciones_dic.keys())
            return nombres_secciones, secciones_dic
        except json.JSONDecodeError:
            flash("Error decoding secciones_dic.")
            return None, None