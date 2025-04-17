import psycopg2
from config import load_config
from connect import get_connect

def delete_from_phonebook(config):
    conn = get_connect(config)
    cur = conn.cursor()

    while True:
        print("\n--- DELETE FROM PHONEBOOK ---")
        print("1. Delete by name")
        print("2. Delete by phone")
        print("3. Exit")
        choice = input("Choose action (1-3): ")

        if choice == '1':
            name = input("Enter name to delete: ")
            cur.execute("DELETE FROM phonebook WHERE name = %s", (name,))
            print(f"Deleted rows: {cur.rowcount}")

        elif choice == '2':
            phone = input("Enter phone to delete: ")
            cur.execute("DELETE FROM phonebook WHERE phone = %s", (phone,))
            print(f"Deleted rows: {cur.rowcount}")

        elif choice == '3':
            break

        else:
            print("Incorrect action.")
            continue

        conn.commit()

    cur.close()
    conn.close()

if __name__ == '__main__':
    config = load_config()
    delete_from_phonebook(config)
