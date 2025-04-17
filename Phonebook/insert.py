import csv
import psycopg2
from config import load_config
from connect import get_connect

# Create table if not exists
def create_table(config):
    conn = get_connect(config)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS PhoneBook (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            phone VARCHAR(50)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Method 1: Upload from CSV
def insert_from_csv(csv_file_path, config):
    conn = get_connect(config)
    cur = conn.cursor()
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            name, phone = row
            cur.execute("INSERT INTO PhoneBook (name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("Data inserted from CSV successfully.")

# Method 2: Insert from Console
def insert_from_console(config):
    conn = get_connect(config)
    cur = conn.cursor()
    while True:
        name = input("Enter name (or type 'exit' to quit): ")
        if name.lower() == 'exit':
            break
        phone = input("Enter phone: ")
        cur.execute("INSERT INTO PhoneBook (name, phone) VALUES (%s, %s)", (name, phone))
        conn.commit()
        print("Record inserted.")
    cur.close()
    conn.close()

# Main
def main():
    config = load_config()
    
    create_table(config)
    print("Choose an option:")
    print("1. Insert from CSV")
    print("2. Insert manually from console")
    choice = input("Enter choice (1 or 2): ")

    if choice == '1':
        path = input("Enter CSV file path: ")
        insert_from_csv(path, config)
    elif choice == '2':
        insert_from_console(config)
    else:
        print("Invalid choice.")

if __name__ == '__main__':
    main()
