import os

def run_file(file_name):
    try:
        # Run the specified Python file using os.system
        os.system(f"python {file_name}")
    except KeyboardInterrupt:
        # Handle keyboard interrupt (Ctrl+C) and print a message
        print("\nProcess interrupted. Returning to the main menu.")

def main():
    while True:
        print("\nChoose a file to run:")
        print("1. Products (products.py)")
        print("2. Cashier (cashier.py)")
        print("3. Consultant (consultant.py)")
        print("4. Accountant (accountant.py)")
        print("5. Quit")

        choice = input("Enter the number of your choice: ")

        if choice == '1':
            run_file("products.py")
        elif choice == '2':
            run_file("cashier.py")
        elif choice == '3':
            run_file("consultant.py")
        elif choice == '4':
            run_file("accountant.py")
        elif choice == '5':
            print("Quitting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a valid number.")

if __name__ == "__main__":
    main()
