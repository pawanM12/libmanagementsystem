import sqlite3
from datetime import datetime

# Function to initialize the database and create tables if they don't exist
def initialize_database():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Create books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            quantity INTEGER NOT NULL,
            available INTEGER NOT NULL
        )
    ''')

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')

    # Create borrowings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrowings (
            borrow_id INTEGER PRIMARY KEY,
            book_id INTEGER,
            user_id INTEGER,
            borrow_date TEXT,
            due_date TEXT,
            return_date TEXT,
            FOREIGN KEY(book_id) REFERENCES books(book_id),
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()

# LibrarySystem class
class LibrarySystem:
    def __init__(self):
        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def return_book(self, user_id, book_id, return_date):
        """Simplified return book function with overdue handling."""
        # Step 1: Get book details
        self.cursor.execute('SELECT * FROM books WHERE book_id = ?', (book_id,))
        book = self.cursor.fetchone()

        if not book:
            print("Book not found.")
            return
        
        title, author, isbn, quantity, available = book[1], book[2], book[3], book[4], book[5]

        # Step 2: Check if the user has borrowed the book
        self.cursor.execute('''
            SELECT * FROM borrowings WHERE user_id = ? AND book_id = ? AND return_date IS NULL
        ''', (user_id, book_id))
        borrow_record = self.cursor.fetchone()

        if not borrow_record:
            print("No active borrow record found.")
            return
        
        borrow_date, due_date = borrow_record[3], borrow_record[4]
        
        # Step 3: Check if the book is overdue
        overdue_fine = 0
        if return_date > due_date:
            overdue_days = (datetime.strptime(return_date, "%Y-%m-%d") - datetime.strptime(due_date, "%Y-%m-%d")).days
            overdue_fine = overdue_days * 1  # 1 unit per day overdue

        # Step 4: Update book availability and return date
        self.cursor.execute('''
            UPDATE books SET available = available + 1 WHERE book_id = ?
        ''', (book_id,))
        
        # Update the borrowings table to mark the book as returned
        self.cursor.execute('''
            UPDATE borrowings SET return_date = ? WHERE borrow_id = ?
        ''', (return_date, borrow_record[0]))
        
        # Commit changes to the database
        self.conn.commit()

        # Print results
        if overdue_fine > 0:
            print(f"Book returned late. {overdue_fine} fine applied.")
        else:
            print("Book returned successfully, no fine.")

    def get_user_info(self, user_id):
        """Get user info like borrowings and fines."""
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = self.cursor.fetchone()
        if user:
            print(f"User: {user[1]} (Email: {user[2]})")
        else:
            print("User not found.")

# Initialize database and create tables
initialize_database()

# Example usage:
if __name__ == "__main__":
    library = LibrarySystem()

    # Add some books and users manually for testing
    library.cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', ("Alice", "alice@email.com"))
    library.cursor.execute('INSERT INTO books (title, author, isbn, quantity, available) VALUES (?, ?, ?, ?, ?)', 
                           ("Book A", "Author X", "1234567890", 5, 5))

    # Commit to save changes
    library.conn.commit()

    # Borrow a book (this would normally be handled in a separate function)
    library.cursor.execute('INSERT INTO borrowings (book_id, user_id, borrow_date, due_date) VALUES (?, ?, ?, ?)', 
                           (1, 1, '2024-12-01', '2024-12-10'))

    # Commit to save changes
    library.conn.commit()

    # Return book on time
    library.return_book(1, 1, '2024-12-09')

    # Get user info after returning the book
    library.get_user_info(1)

    # Return book late (to trigger fine)
    library.return_book(1, 1, '2024-12-12')

    # Get user info again
    library.get_user_info(1)

    # Close the connection
    library.close()
