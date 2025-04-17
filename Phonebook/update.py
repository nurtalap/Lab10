import psycopg2
from connect import get_connect
from config import load_config

def update_phonebook(config):
    conn = get_connect(config)
    cur = conn.cursor()

    while True:
        print("\n--- UPDATE MENU ---")
        print("1. Change name")
        print("2. Change phone")
        print("3. Exit")
        choice = input("Choose action (1-3): ")

        if choice == '1':
            old_name = input("Enter current name: ")
            new_name = input("Enter new name: ")
            cur.execute("UPDATE phonebook SET name = %s WHERE name = %s", (new_name, old_name))
            print(f"Name updated: {old_name} → {new_name}")

        elif choice == '2':
            user_name = input("Enter name to update phone: ")
            new_phone = input("Enter new phone: ")
            cur.execute("UPDATE phonebook SET phone = %s WHERE name = %s", (new_phone, user_name))
            print(f"Phone updated for {user_name}: {new_phone}")

        elif choice == '3':
            break

        else:
            print("Incorrect action.")

        conn.commit()

    cur.close()
    conn.close()

if __name__ == "__main__":
    config = load_config()
    update_phonebook(config)
