import sys

STOCK_FILE = "stock.txt"

def load_stock():
    stock = {}
    try:
        with open(STOCK_FILE, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    name, count = line.split(',')
                    stock[name.lower()] = int(count)
    except FileNotFoundError:
        print("Error: stock.txt not present.")
    except ValueError:
        print("Error: Corrupted file format in stock.txt.")
    return stock

def save_stock(stock):
    try:
        with open(STOCK_FILE, 'w') as file:
            for name, count in stock.items():
                file.write(f"{name},{count}\n")
        print("Stock saved successfully.")
    except Exception as e:
        print(f"Error saving file: {e}")

def show_stock(stock):
    print("\nCurrent Stock:")
    for idx, (name, count) in enumerate(stock.items(), start=1):
        print(f"{idx}. {name}: {count}")
    print()

def get_stock_key(stock, prompt_msg):
    user_input = input(prompt_msg).strip().lower()
    if user_input.isdigit():
        idx = int(user_input)
        if 1 <= idx <= len(stock):
            return list(stock.keys())[idx - 1]
        else:
            print("Invalid ID entered.")
            return None
    return user_input

def add_stock(stock):
    show_stock(stock)
    key = get_stock_key(stock, 'Enter stock name/id to change, or new name to add: ')
    if not key: return
    try:
        amount = int(input(f"Enter how much to add to '{key}': "))
        if amount < 0:
            print("Invalid input: value cannot be negative.")
            return
        stock[key] = stock.get(key, 0) + amount
        print("Stock updated.")
    except ValueError:
        print("Invalid input: enter a number.")

def remove_stock(stock):
    show_stock(stock)
    key = get_stock_key(stock, 'Enter stock name/id to change: ')
    if not key: return
    if key not in stock:
        print("Invalid: Must already be in stock.")
        return
    try:
        amount = int(input(f"Enter how much to remove from '{key}': "))
        if amount < 0:
            print("Invalid input: value cannot be negative.")
            return
        if stock[key] - amount < 0:
            print("Invalid input: Stock cannot drop below 0.")
            return
        stock[key] -= amount
        print("Stock updated.")
    except ValueError:
        print("Invalid input: enter a number.")

def main():
    stock = load_stock()
    while True:
        print("\n--- Menu ---")
        print("enter 1 to add stock")
        print("enter 2 to remove stock")
        print("enter 3 to show stock's contents")
        print("enter 4 to exit the program")
        
        choice = input("Choice: ").strip()
        if choice == '1': add_stock(stock)
        elif choice == '2': remove_stock(stock)
        elif choice == '3': show_stock(stock)
        elif choice == '4':
            save_stock(stock)
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()