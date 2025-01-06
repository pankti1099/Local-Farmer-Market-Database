import sqlite3

def connect_to_db(db_path):
    """Connect to the SQLite3 database."""
    try:
        connection = sqlite3.connect(db_path)
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def view_vendors(connection):
    """Display all vendors and allow refinement."""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Vendors")
        vendors = cursor.fetchall()
        print("\n--- Vendors ---")
        if vendors:
            print("{:<5} {:<25} {:<35} {:<20}".format("ID", "Name", "Contact Info", "Product Category"))
            print("{:<5} {:<25} {:<35} {:<20}".format("-" * 3, "-" * 25, "-" * 35, "-" * 20))
            for vendor in vendors:
                print("{:<5} {:<25} {:<35} {:<20}".format(vendor[0], vendor[1], vendor[2], vendor[3]))

            # Refinement: Search by Product Category
            refine = input("\nDo you want to refine by product category? (yes/no): ").strip().lower()
            if refine == "yes":
                query_vendors_by_category(connection)
        else:
            print("No vendors found.")
    except sqlite3.Error as e:
        print(f"Error fetching vendors: {e}")


def view_products(connection):
    """Display all products and allow refinement."""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()
        print("\n--- Products ---")
        if products:
            print("{:<5} {:<25} {:<45} {:<20} {:<10}".format("ID", "Name", "Description", "Category", "Price"))
            print("{:<5} {:<25} {:<45} {:<20} {:<10}".format("-" * 3, "-" * 25, "-" * 45, "-" * 20, "-" * 10))
            for product in products:
                print("{:<5} {:<25} {:<45} {:<20} ${:<10.2f}".format(product[0], product[1], product[2], product[3], product[4]))

            refine = input("\nDo you want to refine by vendor? (yes/no): ").strip().lower()
            if refine == "yes":
                vendor_name = input("Enter vendor name to search products: ").strip()
                query_products_by_vendor(connection, vendor_name)  
        else:
            print("No products found.")
    except sqlite3.Error as e:
        print(f"Error fetching products: {e}")



def view_events(connection):
    """Display all market events and allow refinement."""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM MarketEvents")
        events = cursor.fetchall()
        print("\n--- Market Events ---")
        if events:
            print("{:<5} {:<15} {:<10} {:<30}".format("ID", "Date", "Time", "Location"))
            print("{:<5} {:<15} {:<10} {:<30}".format("-" * 3, "-" * 15, "-" * 10, "-" * 30))
            for event in events:
                print("{:<5} {:<15} {:<10} {:<30}".format(event[0], event[1], event[2], event[3]))

            refine_event = input("\nDo you want to refine by event? (yes/no): ").strip().lower()
            if refine_event == "yes":
                event_id = input("Enter the Event ID to view participating vendors: ").strip()
                cursor.execute("""
                    SELECT Vendors.Name, Vendors.ContactInfo 
                    FROM Vendors
                    JOIN VendorMarketParticipation ON Vendors.VendorID = VendorMarketParticipation.VendorID
                    WHERE VendorMarketParticipation.EventID = ?
                """, (event_id,))
                vendors = cursor.fetchall()
                print(f"\nVendors participating in Event ID '{event_id}':")
                if vendors:
                    print("{:<25} {:<35}".format("Vendor Name", "Contact Info"))
                    print("{:<25} {:<35}".format("-" * 25, "-" * 35))
                    for vendor in vendors:
                        print("{:<25} {:<35}".format(vendor[0], vendor[1]))

                    refine_vendor = input("\nDo you want to refine by vendor to view their products? (yes/no): ").strip().lower()
                    if refine_vendor == "yes":
                        vendor_name = input("Enter vendor name to view their products: ").strip()
                        query_products_by_vendor(connection, vendor_name) 
                else:
                    print(f"No vendors found for Event ID '{event_id}'.")
        else:
            print("No events found.")
    except sqlite3.Error as e:
        print(f"Error fetching events: {e}")

def query_products_by_vendor(connection, vendor_name):
    """Query products by vendor name."""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT DISTINCT Products.Name, Products.Description, Products.Price 
            FROM Products
            JOIN ProductVendor ON Products.ProductID = ProductVendor.ProductID
            JOIN Vendors ON ProductVendor.VendorID = Vendors.VendorID
            WHERE Vendors.Name = ?
        """, (vendor_name,))
        products = cursor.fetchall()
        print(f"\nProducts offered by '{vendor_name}':")
        if products:
            print("{:<20} {:<40} {:<10}".format("Name", "Description", "Price"))
            print("{:<20} {:<40} {:<10}".format("-" * 20, "-" * 40, "-" * 10))
            for product in products:
                print("{:<20} {:<40} ${:<10.2f}".format(product[0], product[1], product[2]))
        else:
            print(f"No products found for vendor '{vendor_name}'.")
    except sqlite3.Error as e:
        print(f"Error querying products by vendor: {e}")


def query_vendors_by_category(connection):
    """Query vendors by product category."""
    try:
        category = input("Enter product category to search vendors: ").strip()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Vendors WHERE ProductCategory = ?", (category,))
        vendors = cursor.fetchall()
        print(f"\nVendors in category '{category}':")
        if vendors:
            print("{:<5} {:<20} {:<30} {:<20}".format("ID", "Name", "Contact Info", "Category"))
            for vendor in vendors:
                print("{:<5} {:<20} {:<30} {:<20}".format(vendor[0], vendor[1], vendor[2], vendor[3]))
        else:
            print("No vendors found in this category.")
    except sqlite3.Error as e:
        print(f"Error querying vendors by category: {e}")



def query_events_by_vendor(connection):
    """Query market events involving a specific vendor."""
    try:
        vendor_name = input("Enter vendor name to find their events: ").strip()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT MarketEvents.Date, MarketEvents.Time, MarketEvents.Location 
            FROM MarketEvents
            JOIN VendorMarketParticipation ON MarketEvents.EventID = VendorMarketParticipation.EventID
            JOIN Vendors ON VendorMarketParticipation.VendorID = Vendors.VendorID
            WHERE Vendors.Name = ?
        """, (vendor_name,))
        events = cursor.fetchall()
        print(f"\nEvents for vendor '{vendor_name}':")
        if events:
            print("{:<15} {:<10} {:<30}".format("Date", "Time", "Location"))
            for event in events:
                print("{:<15} {:<10} {:<30}".format(event[0], event[1], event[2]))
        else:
            print("No events found for this vendor.")
    except sqlite3.Error as e:
        print(f"Error querying events by vendor: {e}")


def main():
    db_path = "farmersMarket.db"
    try:
        connection = connect_to_db(db_path)
        if not connection:
            print("Failed to connect to the database. Exiting...")
            return

        print("Welcome to the Local Farmer's Market Database CLI!")
        while True:
            print("\nOptions:")
            print("1. View All Vendors")
            print("2. View All Products")
            print("3. View All Market Events")
            print("4. Exit")
            choice = input("Enter your choice: ").strip()
           
            
            if choice == "1":
                view_vendors(connection)
            elif choice == "2":
                view_products(connection)
            elif choice == "3":
                view_events(connection)
            elif choice == "4":
                print("Exiting... Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

        connection.close()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()