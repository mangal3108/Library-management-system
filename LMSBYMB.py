import tkinter as tk
from tkinter import messagebox, Menu, ttk
import sqlite3
import hashlib
from PIL import Image, ImageTk

# Database setup
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS books
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             title TEXT,
             author TEXT,
             year INTEGER,
             isbn INTEGER)''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             username TEXT UNIQUE,
             password TEXT,
             role TEXT)''')
conn.commit()

# Functions for library management
def add_book(title, author, year, isbn):
    cursor.execute("INSERT INTO books (title, author, year, isbn) VALUES (?, ?, ?, ?)",
                   (title, author, year, isbn))
    conn.commit()

def view_books():
    cursor.execute("SELECT * FROM books")
    return cursor.fetchall()

def delete_book(book_id):
    cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()

def search_books(title="", author="", year="", isbn=""):
    cursor.execute("SELECT * FROM books WHERE title=? OR author=? OR year=? OR isbn=?",
                   (title, author, year, isbn))
    return cursor.fetchall()

def update_book(book_id, title, author, year, isbn):
    cursor.execute("UPDATE books SET title=?, author=?, year=?, isbn=? WHERE id=?",
                   (title, author, year, isbn, book_id))
    conn.commit()

def register_user(username, password, role):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, hashed_password, role))
        conn.commit()
        messagebox.showinfo("Success", "User registered successfully")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists")

def authenticate_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT role FROM users WHERE username=? AND password=?",
                   (username, hashed_password))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

# GUI Functions
def clear_entries():
    title_entry.delete(0, tk.END)
    author_entry.delete(0, tk.END)
    year_entry.delete(0, tk.END)
    isbn_entry.delete(0, tk.END)

def add_book_command():
    add_book(title_entry.get(), author_entry.get(), year_entry.get(), isbn_entry.get())
    list_books()
    clear_entries()

def list_books():
    books_list.delete(*books_list.get_children())
    for row in view_books():
        books_list.insert("", "end", values=row)

def delete_book_command():
    selected_book = books_list.selection()
    if selected_book:
        book_id = books_list.item(selected_book)['values'][0]
        delete_book(book_id)
        list_books()

def search_book_command():
    books_list.delete(*books_list.get_children())
    for row in search_books(title_entry.get(), author_entry.get(), year_entry.get(), isbn_entry.get()):
        books_list.insert("", "end", values=row)

def set_resolution(width, height):
    global root
    scale_factor = width / 800  # base width for scaling
    root.geometry(f"{width}x{height}")

    # Adjust font sizes and element sizes based on resolution
    default_font_size = int(10 * scale_factor)
    title_label.config(font=("Arial", default_font_size))
    author_label.config(font=("Arial", default_font_size))
    year_label.config(font=("Arial", default_font_size))
    isbn_label.config(font=("Arial", default_font_size))
    title_entry.config(font=("Arial", default_font_size))
    author_entry.config(font=("Arial", default_font_size))
    year_entry.config(font=("Arial", default_font_size))
    isbn_entry.config(font=("Arial", default_font_size))
    for button in action_buttons:
        button.config(font=("Arial", default_font_size))

    # Adjust column widths in treeview
    col_width = int(100 * scale_factor)
    for col in books_list["columns"]:
        books_list.column(col, width=col_width)

def show_help():
    messagebox.showinfo("Help", "Library Management System Help:\n\n"
                                "1. Add Book: Enter book details and click 'Add Book'.\n"
                                "2. Search Book: Enter search criteria and click 'Search Book'.\n"
                                "3. Delete Book: Select a book from the list and click 'Delete Book'.\n"
                                "4. View All Books: Click 'View All Books' to see all books.\n"
                                "5. Update Book: Select a book, modify details, and click 'Update Book'."
                                "THANKS For Using . Made By Mangal Bhadouriya")

def login():
    username = username_entry.get()
    password = password_entry.get()
    role = authenticate_user(username, password)
    if role:
        switch_frame(main_app_frame)
        main_app(role)
    else:
        messagebox.showerror("Error", "Invalid username or password")

def register():
    switch_frame(registration_frame)

def submit_registration():
    register_user(reg_username_entry.get(), reg_password_entry.get(), role_var.get())
    switch_frame(login_frame)

def switch_frame(frame):
    frame.tkraise()

def main_app(role):
    global root, title_entry, author_entry, year_entry, isbn_entry, books_list, title_label, author_label, year_label, isbn_label, action_buttons

    # Labels and entries for book details
    title_label = ttk.Label(main_app_frame, text="Title")
    title_label.grid(row=0, column=0)
    title_entry = ttk.Entry(main_app_frame)
    title_entry.grid(row=0, column=1)

    author_label = ttk.Label(main_app_frame, text="Author")
    author_label.grid(row=0, column=2)
    author_entry = ttk.Entry(main_app_frame)
    author_entry.grid(row=0, column=3)

    year_label = ttk.Label(main_app_frame, text="Year")
    year_label.grid(row=1, column=0)
    year_entry = ttk.Entry(main_app_frame)
    year_entry.grid(row=1, column=1)

    isbn_label = ttk.Label(main_app_frame, text="ISBN")
    isbn_label.grid(row=1, column=2)
    isbn_entry = ttk.Entry(main_app_frame)
    isbn_entry.grid(row=1, column=3)

    # Buttons for actions
    action_buttons = []
    if role == 'librarian':
        action_buttons.append(ttk.Button(main_app_frame, text="Add Book", command=add_book_command))
        action_buttons[-1].grid(row=2, column=0)
        action_buttons.append(ttk.Button(main_app_frame, text="Search Book", command=search_book_command))
        action_buttons[-1].grid(row=2, column=1)
        action_buttons.append(ttk.Button(main_app_frame, text="Delete Book", command=delete_book_command))
        action_buttons[-1].grid(row=2, column=2)
        action_buttons.append(ttk.Button(main_app_frame, text="Update Book", command=update_book_command))
        action_buttons[-1].grid(row=2, column=3)

    action_buttons.append(ttk.Button(main_app_frame, text="View All Books", command=list_books))
    action_buttons[-1].grid(row=3, column=1)

    # Listbox to display books
    columns = ("ID", "Title", "Author", "Year", "ISBN")
    books_list = ttk.Treeview(main_app_frame, columns=columns, show="headings")
    for col in columns:
        books_list.heading(col, text=col)
    books_list.grid(row=4, column=0, columnspan=4, sticky="nsew")

    main_app_frame.grid_rowconfigure(4, weight=1)
    main_app_frame.grid_columnconfigure(3, weight=1)

    # Initial list of books
    list_books()

def update_book_command():
    selected_book = books_list.selection()
    if selected_book:
        book_id = books_list.item(selected_book)['values'][0]
        update_book(book_id, title_entry.get(), author_entry.get(), year_entry.get(), isbn_entry.get())
        list_books()
        clear_entries()

# Splash screen function
def splash_screen():
    splash = tk.Tk()
    splash.title("Library Management System")

    # Load and display image
    image = Image.open("preview.jpg")
    photo = ImageTk.PhotoImage(image)
    splash_label = tk.Label(splash, image=photo)
    splash_label.image = photo  # keep a reference
    splash_label.pack()

    # Center the splash screen on the screen
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    splash_width, splash_height = image.size
    x = (screen_width // 2) - (splash_width // 2)
    y = (screen_height // 2) - (splash_height // 2)
    splash.geometry(f"{splash_width}x{splash_height}+{x}+{y}")

    # Set the splash screen to disappear after 3 seconds
    splash.after(3000, splash.destroy)
    splash.mainloop()

# Show splash screen
splash_screen()

# Main window setup
root = tk.Tk()
root.title("Library Management System By Mangal Bhadouriya")

# Menu for changing screen resolution and help
menu = Menu(root)
root.config(menu=menu)

settings_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="Settings", menu=settings_menu)

resolution_menu = Menu(settings_menu, tearoff=0)
settings_menu.add_cascade(label="Resolution", menu=resolution_menu)
resolution_menu.add_command(label="800x600", command=lambda: set_resolution(800, 600))
resolution_menu.add_command(label="1024x768", command=lambda: set_resolution(1024, 768))
resolution_menu.add_command(label="1280x720", command=lambda: set_resolution(1280, 720))
resolution_menu.add_command(label="1920x1080", command=lambda: set_resolution(1920, 1080))

menu.add_command(label="Help", command=show_help)

# Frames for different sections
login_frame = ttk.Frame(root)
registration_frame = ttk.Frame(root)
main_app_frame = ttk.Frame(root)

for frame in (login_frame, registration_frame, main_app_frame):
    frame.grid(row=0, column=0, sticky="nsew")

# Login Frame
ttk.Label(login_frame, text="Username").grid(row=0, column=0)
username_entry = ttk.Entry(login_frame)
username_entry.grid(row=0, column=1)

ttk.Label(login_frame, text="Password").grid(row=1, column=0)
password_entry = ttk.Entry(login_frame, show="*")
password_entry.grid(row=1, column=1)

ttk.Button(login_frame, text="Login", command=login).grid(row=2, columnspan=2)
ttk.Button(login_frame, text="Register", command=register).grid(row=3, columnspan=2)

# Registration Frame
ttk.Label(registration_frame, text="Username").grid(row=0, column=0)
reg_username_entry = ttk.Entry(registration_frame)
reg_username_entry.grid(row=0, column=1)

ttk.Label(registration_frame, text="Password").grid(row=1, column=0)
reg_password_entry = ttk.Entry(registration_frame, show="*")
reg_password_entry.grid(row=1, column=1)

ttk.Label(registration_frame, text="Role").grid(row=2, column=0)
role_var = tk.StringVar(value="student")
ttk.Radiobutton(registration_frame, text="Student", variable=role_var, value="student").grid(row=2, column=1)
ttk.Radiobutton(registration_frame, text="Librarian", variable=role_var, value="librarian").grid(row=2, column=2)

ttk.Button(registration_frame, text="Register", command=submit_registration).grid(row=3, columnspan=3)
ttk.Button(registration_frame, text="Back to Login", command=lambda: switch_frame(login_frame)).grid(row=4, columnspan=3)

# Start with login frame
switch_frame(login_frame)

# Run the Tkinter event loop for the main window
root.mainloop()

# Close the database connection when done
conn.close()


