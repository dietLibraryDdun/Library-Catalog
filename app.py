import streamlit as st
import sqlite3
import pandas as pd

DB_FILE = "library.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create categories table
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # Create books table
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            number TEXT NOT NULL,
            author TEXT,
            category TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def get_categories():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name FROM categories")
    cats = [row[0] for row in c.fetchall()]
    conn.close()
    return sorted(cats)

def get_books_by_category(category):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM books WHERE category = ?", conn, params=(category,))
    conn.close()
    return df

def add_book(name, number, author, category):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO books (name, number, author, category) VALUES (?, ?, ?, ?)",
              (name, number, author, category))
    conn.commit()
    conn.close()

def delete_book(book_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

def add_category(category_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def delete_category(category_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM categories WHERE name = ?", (category_name,))
    c.execute("DELETE FROM books WHERE category = ?", (category_name,))
    conn.commit()
    conn.close()

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.view_mode = None
    st.rerun()

def login():
    # (Style and layout omitted for brevity - same as original)
    # Create two columns for the buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("View Catalog", key="view_catalog", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.username = 'guest'
            st.session_state.view_mode = 'guest'
            st.rerun()
    with col2:
        if st.button("Admin Login", key="admin_login", use_container_width=True):
            st.session_state.view_mode = 'admin_login'
            st.rerun()
    if st.session_state.get('view_mode') == 'admin_login':
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", key="login"):
            if username == "diet" and password == "dietlb1983":
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.view_mode = 'admin'
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials.")

def main_app(username):
    st.header(" DIET Dehradun <br>📖Library Catalog")

    categories = get_categories()
    if not categories:
        st.warning("No categories available. Please add categories.")
        return

    selected_cat = st.selectbox("Select Category", options=categories)
    df_cat = get_books_by_category(selected_cat)

    search_term = st.text_input("🔍 Search Book")
    if search_term:
        df_cat = df_cat[df_cat['name'].str.contains(search_term, case=False)]

    if not df_cat.empty:
        st.dataframe(df_cat[['name', 'author']], use_container_width=True)
    else:
        st.info("No books found.")

    if st.session_state.view_mode == 'admin':
        col1, col2 = st.columns(2)

        with col1:
            with st.expander("➕ Add a New Book", expanded=True):
                with st.form("add_book_form"):
                    new_name = st.text_input("Book Name")
                    new_number = st.text_input("Book Number")
                    new_author = st.text_input("Author (optional)")
                    submitted = st.form_submit_button("Add Book")
                    if submitted:
                        if not new_name.strip() or not new_number.strip():
                            st.error("Book Name and Number cannot be empty.")
                        else:
                            add_book(new_name.strip(), new_number.strip(), new_author.strip(), selected_cat)
                            st.success(f"Added '{new_name}' to '{selected_cat}'.")
                            st.rerun()

        with col2:
            with st.expander("🗑️ Delete a Book", expanded=True):
                if df_cat.empty:
                    st.info("No books to delete.")
                else:
                    delete_options = [(row['id'], f"{row['name']} by {row['author'] or 'Unknown'}") for idx, row in df_cat.iterrows()]
                    book_to_delete = st.selectbox("Select book to delete", options=delete_options, format_func=lambda x: x[1])
                    if st.button("Delete Book"):
                        delete_book(book_to_delete[0])
                        st.success(f"Deleted '{book_to_delete[1]}'.")
                        st.rerun()

        with st.expander("📂 Manage Categories", expanded=False):
            st.subheader("➕ Add a New Category")
            new_category = st.text_input("Enter New Category Name")
            if st.button("Add Category"):
                if new_category.strip():
                    add_category(new_category.strip())
                    st.success(f"Category '{new_category}' added.")
                    st.rerun()
                else:
                    st.error("Category name cannot be empty.")

            st.subheader("🗑️ Delete a Category")
            if categories:
                cat_to_delete = st.selectbox("Select Category to Delete", options=categories)
                if st.button("Delete Category"):
                    delete_category(cat_to_delete)
                    st.success(f"Category '{cat_to_delete}' deleted along with its books.")
                    st.rerun()
            else:
                st.info("No categories available.")

        st.markdown("---")
        if st.button("Logout"):
            logout()
    else:
        st.info("Read-only access. Please login as admin to modify the catalog.")
        if st.button("Logout"):
            logout()

def main():
    st.set_page_config(page_title="Library Catalog", layout="centered")
    init_db()

    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login()
    else:
        main_app(st.session_state.get('username', 'guest'))

if __name__ == "__main__":
    main()
