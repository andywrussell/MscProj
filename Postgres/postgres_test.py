import psycopg2

connection = psycopg2.connect(user="postgres",
                              password="4ndr3wP0ST",
                              host="127.0.0.1",
                              port="5432",
                              database="twitter_test")

cursor = connection.cursor()
# Print PostgreSQL Connection properties
print(connection.get_dsn_parameters(), "\n")

# Print PostgreSQL version
cursor.execute("SELECT version();")
record = cursor.fetchone()
print("You are connected to - ", record, "\n")
