from flask import flash, session
from funct.DataBase import DataBase  # Assuming this class handles all database operations
from funct.Hash import Hash  # Assuming this class has appropriate methods for password handling

class LoginManager:
    def __init__(self, db_config):
        self.db_config = db_config

    def connect_to_database(self):
        try:
            db = DataBase(**self.db_config)
            db.connect()
            return db
        except Exception as e:
            flash(f'Database connection error: {e}')
            return None

    def get_user_data(self, username):
        db = self.connect_to_database()
        if db:
            try:
                query = "SELECT user_password, nombre, apellido, correo, server, db_name FROM users WHERE username = ?"
                user_data = db.execute_query_params(query, (username,))
                return user_data
            finally:
                db.close()
        return None

    def get_user_sections(self, username):
        db = self.connect_to_database()
        if db:
            try:
                query = "SELECT secciones_dic FROM users WHERE username = ?"
                secciones_data = db.execute_query_params(query, (username,))
                return secciones_data
            finally:
                db.close()
        return None

    def authenticate_user(self, username, password):
        user_data = self.get_user_data(username)
        if user_data and Hash.verify_password(password, user_data[0][0]):
            secciones_data = self.get_user_sections(username)
            session['user_info'] = {
                'first_name': user_data[0][1],
                'last_name': user_data[0][2],
                'email': user_data[0][3],
                'server': user_data[0][4],
                'db_name': user_data[0][5],
                'secciones_dic': secciones_data[0][0] if secciones_data else '{}'
            }
            return True
        return False
