import psycopg2
import cx_Oracle
import os
from dotenv import load_dotenv
from sql import consulta_ceadex

load_dotenv()

# PostgreSQL connection parameters
pg_username = os.getenv('')[:7]
pg_password = os.getenv('')
pg_host = os.getenv('')
pg_port = os.getenv('')
pg_database = os.getenv('')

# Oracle connection parameters
ora_username = os.getenv('')
ora_password = os.getenv('')
ora_host = os.getenv('')
ora_port = os.getenv('')
ora_service_name = os.getenv('')
ora_table = os.getenv('')

# Connect to PostgreSQL
pg_conn = psycopg2.connect(user=pg_username, password=pg_password,host=pg_host,port=pg_port,database=pg_database)

# Connect to Oracle
ora_conn = cx_Oracle.connect(
    ora_username,
    ora_password,
    cx_Oracle.makedsn(ora_host, ora_port, service_name=ora_service_name)
)

# Force encoding - Created after error: UnicodeEncodeError: 'ascii' codec can't encode character '\xe1' in position 29: ordinal not in range(128)
pg_conn.set_client_encoding('UTF8')
os.environ["NLS_LANG"] = ".UTF8"

# Create cursors
pg_cursor = pg_conn.cursor()
ora_cursor = ora_conn.cursor()

# Fetch the total number of rows
# pg_cursor.execute('SELECT COUNT(*) FROM your_pg_table')
# total_rows = pg_cursor.fetchone()[0]

# Select rows in batches of 10,000
# for offset_value in range(0, total_rows, 10000):
    # Select rows from PostgreSQL
print("Iniciando consulta no banco PostgreSQL")
pg_cursor.execute(consulta_ceadex)
rows = pg_cursor.fetchall()

# Prepare the SQL statement for Oracle
columns = ', '.join(desc[0] for desc in pg_cursor.description)
placeholders = ', '.join(':' + desc[0] for desc in pg_cursor.description)
ora_sql = f'INSERT INTO {ora_table} ({columns}) VALUES ({placeholders})'.encode('UTF8')

# Insert rows into Oracle
print("Iniciando inserção de dados no banco Oracle")
ora_cursor.execute(f'TRUNCATE TABLE STG_SELFSERVICE.{ora_table} DROP STORAGE')

# for row in rows:
#   ora_cursor.execute(ora_sql, row)  

ora_cursor.executemany(ora_sql, rows)
ora_conn.commit()

# Close cursors and connections
pg_cursor.close()
pg_conn.close()
ora_cursor.close()
ora_conn.close()
print("Extração executada com sucesso")