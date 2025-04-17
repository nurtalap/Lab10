import psycopg2
from config import load_config
from connect import get_connect

def query_phonebook(config):
    conn = get_connect(config)
    cur = conn.cursor()

    while True:
        print("\n--- FILTERS FOR SEARCH ---")
        print("1. Find by name")
        print("2. Find by phone")
        print("3. All rows")
        print("4. Find by name part")
        print("5. Exit")
        choice = input("Choose action (1-5): ")

        if choice == '1':
            name = input("Enter name: ")
            cur.execute("SELECT * FROM phonebook WHERE name = %s", (name,))
            rows = cur.fetchall()

        elif choice == '2':
            phone = input("Enter phone: ")
            cur.execute("SELECT * FROM phonebook WHERE phone = %s", (phone,))
            rows = cur.fetchall()

        elif choice == '3':
            cur.execute("SELECT * FROM phonebook")
            rows = cur.fetchall()

        elif choice == '4':
            partial = input("Enter name part: ")
            cur.execute("SELECT * FROM phonebook WHERE name ILIKE %s", (f"%{partial}%",))
            rows = cur.fetchall()

        elif choice == '5':
            break

        else:
            print("Incorrect action.")
            continue

        if rows:
            print("\nResults:")
            for row in rows:
                print(f"ID: {row[0]} | Name: {row[1]} | Phone: {row[2]}")
        else:
            print("Empty.")

    cur.close()
    conn.close()

if __name__ == '__main__':
    config = load_config()
    query_phonebook(config)
