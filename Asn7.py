import pyodbc
import uuid
from datetime import datetime

current_user = None

def connect_to_db():
    try:
        conn = pyodbc.connect('driver={ODBC Driver 18 for SQL Server}; server=cypress.csil.sfu.ca; uid=s_ksrahman;pwd=gdyg4m3hyEYjLnLh; Encrypt=yes;TrustServerCertificate=yes')
        return conn
    except pyodbc.Error as e:
        print("Error connecting to the database:", e)
        return None

def login_user(conn):
    global current_user  # Refer to the global session variable

    try:
        cursor = conn.cursor()
        
        # Prompt user for ID
        user_id = input("Enter your user ID: ").strip()
        
        # Query to validate user ID
        query = "SELECT * FROM dbo.User_yelp WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        if user:
            # Set the global variable to indicate the user is logged in
            current_user = {'user_id' : user[0], 'user_name' : user[1]}
            print(f"Login successful! Welcome, {current_user['user_name']}")
        else:
            print("Invalid User ID. Please try again.")
    except pyodbc.Error as e:
        print("Error during login:", e)

# Check if the user is logged in before performing an action
def ensure_logged_in():
    if current_user is None:
        print("You must log in first.")
        return False
    return True

# Logout function (optional)
def logout():
    global current_user
    current_user = None
    print("You have logged out.")


def search_business(conn):
    global current_user
    if not ensure_logged_in():
        return
    cursor = conn.cursor()

    # Prompt the user for search filters (min stars, city, name)
    min_stars = input("Enter minimum number of stars (or press Enter to skip): ")
    city = input("Enter city (or press Enter to skip): ")
    name = input("Enter business name (or part of it, case insensitive, or press Enter to skip): ")

    # Construct the SQL query with filters
    query = "SELECT business_id, name, address, city, stars FROM dbo.Business WHERE 1=1"
    params = []

    if min_stars:
        query += " AND stars >= ?"
        params.append(float(min_stars))
    if city:
        query += " AND city LIKE ?"
        params.append(f"%{city}%")
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")

    # Execute the query
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()

    if not results:
        print("No businesses found matching the criteria.")
        return

    # Function to print results with stars or "No stars"
    def print_results(sorted_results):
        # Increase space before 'Business ID' to add padding on the left
        print(f" {'':<1}{'Business ID':<22} {'Name':<60} {'Address':<55} {'City':<20} {'Stars':<3}")
        print("="*180)  # Optional: Adds a line separator for better readability

        for row in sorted_results:
            business_id = row[0] if row[0] is not None else "N/A"
            name = row[1] if row[1] is not None else "Unknown"
            address = row[2] if row[2] is not None else "No Address"
            city = row[3] if row[3] is not None else "Unknown"
            stars = row[4] if row[4] is not None else "No stars"

            # Add a little space to the left of business_id
            print(f" {'':<1}{business_id:<22} {name:<60} {address:<55} {city:<20} {stars:<3}")


    # Sort results based on user input
    while True:
        print("\nChoose sorting option:")
        print("1. Sort by Name")
        print("2. Sort by City")
        print("3. Sort by Stars")
        print("4. Stop and exit")


        choice = input("Enter your choice: ")

        if choice == '1':
            sorted_results = sorted(results, key=lambda x: x[1].lower())  # Sort b4y name (case insensitive)
            print_results(sorted_results)

        elif choice == '2':
            sorted_results = sorted(results, key=lambda x: x[3].lower())  # Sort by city (case insensitive)
            print_results(sorted_results)

        elif choice == '3':
            sorted_results = sorted(results, key=lambda x: x[4] if x[4] is not None else float('-inf'))  # Sort by stars, ascending
            print_results(sorted_results)


        elif choice == '4':
            print("Exiting...")
            return

        else:
            print("Invalid choice. Please try again.")
# Function to print user search results in a consistent format
def print_users(users):
    # Headers for user data
    headers = ['User ID', 'Name', 'Review Count', 'Useful', 'Funny', 'Cool', 'Average Stars', 'Yelping Since']
    
    # Column widths for printing neatly
    column_widths = [22, 35, 15, 10, 10, 10, 15, 20]
    
    # Print header
    print(f"{headers[0]:<{column_widths[0]}} {headers[1]:<{column_widths[1]}} {headers[2]:<{column_widths[2]}} "
          f"{headers[3]:<{column_widths[3]}} {headers[4]:<{column_widths[4]}} {headers[5]:<{column_widths[5]}} "
          f"{headers[6]:<{column_widths[6]}} {headers[7]:<{column_widths[7]}}")
    print("="*180)  # Line separator

    # Print each user row
    for user in users:
        # Format the 'yelping_since' date as 'YYYY-MM-DD' or any other preferred format
        yelping_since = user[7].strftime('%Y-%m-%d') if isinstance(user[7], datetime) else user[7]
        
        # Ensure no None values and print the row
        print(f"{user[0]:<{column_widths[0]}} {user[1]:<{column_widths[1]}} {user[2]:<{column_widths[2]}} "
              f"{user[3]:<{column_widths[3]}} {user[4]:<{column_widths[4]}} {user[5]:<{column_widths[5]}} "
              f"{user[6]:<{column_widths[6]}} {yelping_since:<{column_widths[7]}}")
        
        
def search_users(conn):

    global current_user
    if not ensure_logged_in():
        return

    cursor = conn.cursor()

    # Prompt the user for search filters (name, minimum review count, minimum average stars)
    name = input("Enter name (or part of it, case insensitive, or press Enter to skip): ")
    min_review_count = input("Enter minimum review count (or press Enter to skip): ")
    min_avg_stars = input("Enter minimum average stars (or press Enter to skip): ")

    # Construct the SQL query with filters
    query = "SELECT user_id, name, review_count, useful, funny, cool, average_stars, yelping_since FROM dbo.User_yelp WHERE 1=1"
    params = []

    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    if min_review_count:
        query += " AND review_count >= ?"
        params.append(int(min_review_count))
    if min_avg_stars:
        query += " AND average_stars >= ?"
        params.append(float(min_avg_stars))

    # Execute the query
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()

    if not results:
        print("No users found matching the criteria.")
        return

    # Sort results by name (case insensitive)
    sorted_results = sorted(results, key=lambda x: x[1].lower())

    # Call the print_users function to display the results
    print_users(sorted_results)

def makeFriend(conn):
    global current_user  # Access the currently logged-in user
    
    if not ensure_logged_in():
        return  # Ensure the user is logged in before proceeding

    cursor = conn.cursor()
    
    # Prompt the logged-in user to input the ID of the user they want to befriend
    friend_id = input("Enter the user ID of the person you want to add as a friend: ").strip()
    
    if not friend_id or friend_id == current_user['user_id']:
        print("Invalid user ID. You cannot add yourself as a friend.")
        return

    try:
        # Check if the user ID exists in the database
        query = "SELECT user_id, name FROM dbo.User_yelp WHERE user_id = ?"
        cursor.execute(query, (friend_id,))
        friend = cursor.fetchone()
        
        if not friend:
            print("The user ID you entered does not exist. Please try again.")
            return
        
        # Check if the friendship already exists
        check_query = "SELECT * FROM dbo.Friendship WHERE user_id = ? AND friend = ?"
        cursor.execute(check_query, (current_user['user_id'], friend_id))
        existing_friendship = cursor.fetchone()

        if existing_friendship:
            print(f"You are already friends with {friend[1]} ({friend_id}).")
            return

        # Insert the new friendship into the database
        insert_query = "INSERT INTO dbo.Friendship (user_id, friend) VALUES (?, ?)"
        cursor.execute(insert_query, (current_user['user_id'], friend_id))
        conn.commit()
        print(f"Successfully added {friend[1]} ({friend_id}) as your friend!")
    
    except pyodbc.Error as e:
        print("An error occurred while adding the friend:", e)
        conn.rollback()

def reviewBusiness(conn):
    global current_user  # Access the currently logged-in user
    
    if not ensure_logged_in():
        return  # Ensure the user is logged in before proceeding

    cursor = conn.cursor()
    business_id = input("Enter the business ID you want to review: ").strip()
    cursor.execute("SELECT business_id, stars, review_count FROM dbo.Business WHERE business_id = ?", business_id)
    business = cursor.fetchone()
    if not business:
        print(f"No business found with ID {business_id}.")
        return
    
    # Step 3: Get the star rating from the user
    while True:
        try:
            stars = int(input("Enter your star rating (1 to 5): ").strip())
            if 1 <= stars <= 5:
                break
            else:
                print("Invalid input! Please enter a star rating between 1 and 5.")
        except ValueError:
            print("Invalid input! Please enter a valid integer between 1 and 5.")

    review_id = str(uuid.uuid4()).replace("-", "")[:22]

    try:
        # Step 4: Insert the review into the Review table
        cursor.execute("""
            INSERT INTO dbo.Review (review_id, user_id, business_id, stars)
            VALUES (?, ?, ?, ?)
        """, review_id, current_user['user_id'], business_id, stars)

        # Commit the transaction if the insert is successful
        conn.commit()
        print(f"Your review for business {business_id} has been submitted.")
    except pyodbc.Error as e:
        # Catch SQL errors, particularly from the trigger
        error_message = e.args[1]  # Get the error message
        print(f"Error: {error_message}")
        return

    cursor.execute("""
        SELECT review_id, user_id, stars, date
        FROM dbo.Review
        WHERE business_id = ? AND user_id = ?
        ORDER BY date DESC
    """, business_id, current_user['user_id'])
    reviews = cursor.fetchall()
    review_count = business[2]  # review_count from the business table
    num_stars = business[1]  # current average stars for the business

    # step 5: handle business' stars
    # Old review exists
    if reviews:
        total_stars_old = review_count * num_stars
        latest_stars = reviews[0][2]
        total_stars_new = (total_stars_old - latest_stars) + stars
        num_stars_new = total_stars_new / (review_count)
        cursor.execute("""
            UPDATE dbo.Business
            SET stars = ?
            WHERE business_id = ?
        """, num_stars_new, business_id)
        print(f"Updated business {business_id}'s average stars to {num_stars_new:.1f}.")
    # New review
    else:
        new_review_count = review_count - 1
        total_stars_old = new_review_count * num_stars
        total_stars_new = total_stars_old + stars
        num_stars_new = total_stars_new / (review_count)
        cursor.execute("""
            UPDATE dbo.Business
            SET stars = ?
            WHERE business_id = ?
        """, num_stars_new, business_id)
        print(f"Updated business {business_id}'s average stars to {num_stars_new:.1f}.")

    conn.commit()


# Main function
def main():
    global current_user
    conn = connect_to_db()
    
    if conn:
        # Login loop
        while not current_user:
            login_user(conn)
        
        # After successful login, proceed to other functionalities
        while True:
            print("\nChoose an operation:")
            print("1. Search Business")
            print("2. Search Users")
            print("3. Make a friend")
            print("4. Review a business")
            print("5. Log out")
            print("6. Close Application")
            choice = input("Enter your choice: ")
            
            if choice == '1':
                search_business(conn)
            elif choice == '2':
                search_users(conn)
            elif choice == '3':
                    while True:
                        search_first = input("Do you wish to search for the user before making a friend? (yes/no): ").strip().lower()
                        if search_first == 'yes':
                            search_users(conn)  
                            makeFriend(conn)   
                            break
                        elif search_first == 'no':
                            makeFriend(conn)   
                            break
                        else:
                            print("Invalid input. Please enter 'yes' or 'no'.")
            elif choice == '4':
                    while True:
                        search_first = input("Do you wish to search for the business before leaving a review? (yes/no): ").strip().lower()
                        if search_first == 'yes':
                            search_business(conn)  
                            reviewBusiness(conn)   
                            break
                        elif search_first == 'no':
                            reviewBusiness(conn)     
                            break
                        else:
                            print("Invalid input. Please enter 'yes' or 'no'.")
            elif choice == '5':
                logout()
                login_user(conn)
            elif choice == '6':
                logout() 
                break
            else:
                print("Invalid choice. Please try again.")
        
        # Close the connection when done
        conn.close()

if __name__ == "__main__":
    main()
