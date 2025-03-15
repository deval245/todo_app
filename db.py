import psycopg2
def main():
    conn = psycopg2.connect(
        dbname="TodoAppdb",
        user="deval",
        password="1234",
        host="localhost",
        port="5432"
    )

    print("Connection Successful!")
    conn.close()
if __name__=="__main__":
    main()