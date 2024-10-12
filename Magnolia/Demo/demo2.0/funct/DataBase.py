import pyodbc

class DataBase:
    def __init__(self, server, database):
        self.server = server
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                                            f'SERVER={self.server};'
                                            f'DATABASE={self.database};'
                                            'Trusted_Connection=yes')

            self.cursor = self.connection.cursor()
            print("Conexión exitosa")
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
            self.cursor = None

    def query(self, sql):
        if self.connection:
            try:
                self.cursor.execute(sql)
                for row in self.cursor:
                    print(row)
            except pyodbc.Error as e:
                print(f"Error ejecutando la consulta: {e}")
        else:
            print("No hay conexión a la base de datos")

    def close(self):
        if self.connection:
            self.connection.close()
            print("Conexión cerrada")

    def execute_query(self, query):
        if not self.connection:
            self.connect()
            if not self.connection:
                return None
        try:
            self.cursor.execute(query)
            if query.strip().lower().startswith("select"):
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return None
        except pyodbc.Error as e:
            print(f"Error executing query: {e}")
            return None

    def execute_query_params(self, query, params=None):
        if not self.connection:
            self.connect()
            if not self.connection:
                return None
        try:
            self.cursor.execute(query, params)
            if query.strip().lower().startswith("select"):
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return None
        except pyodbc.Error as e:
            print(f"Error executing query: {e}")
            return None


def main():
    # Parámetros de conexión a la base de datos
    server = 'LAPTOP-IN22ALJ9\\MSSQLSERVER01'
    database = 'usersdb'

    # Crear una instancia de la clase DataBase
    db = DataBase(server, database)

    # Conectarse a la base de datos
    db.connect()

    # Ejecutar una consulta (ajustar esta consulta a tus necesidades)
    sql = "SELECT * FROM users"  # Reemplaza 'tu_tabla' con el nombre de tu tabla
    db.query(sql)

    # Cerrar la conexión a la base de datos
    db.close()

if __name__ == "__main__":
    main()
