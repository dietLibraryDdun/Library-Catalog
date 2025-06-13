import streamlit as st
import sqlite3
import pandas as pd

DB_FILE = "library.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
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
    c.execute("SELECT DISTINCT category FROM books")
    cats = [row[0] for row in c.fetchall()]
    conn.close()
    return cats

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
    c.execute("INSERT INTO books (name, number, author, category) VALUES (?, ?, ?, ?)",
              ("New Book", "000", None, category_name))
    conn.commit()
    conn.close()

def delete_category(category_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # First delete all books in this category
    c.execute("DELETE FROM books WHERE category = ?", (category_name,))
    conn.commit()
    conn.close()

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.view_mode = None
    st.rerun()

def login():
    # Center and style the title and buttons
    st.markdown(
        """
        <style>
        .title-center {
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            margin-top: 40px;
            margin-bottom: 60px;
            color: #2c3e50;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .center-container {
            display: flex;
            justify-content: center;
            gap: 50px;
            margin-bottom: 40px;
        }
        /* Custom button styling */
        .stButton > button {
            width: 100%;
            height: 80px;
            border-radius: 20px;
            font-size: 28px;
            font-weight: 700;
            transition: all 0.3s ease;
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
            border: none;
            margin: 15px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        /* View Catalog button - Green */
        .stButton > button[kind="view_catalog"] {
            background: linear-gradient(135deg, #2ecc71, #27ae60);
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }
        .stButton > button[kind="view_catalog"]:hover {
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 12px 20px rgba(46, 204, 113, 0.3);
        }
        /* Admin Login button - Red */
        .stButton > button[kind="admin_login"] {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }
        .stButton > button[kind="admin_login"]:hover {
            background: linear-gradient(135deg, #c0392b, #e74c3c);
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 12px 20px rgba(231, 76, 60, 0.3);
        }
        /* Admin login form minimalist styling */
        .stTextInput > div > div > input {
            border: none;
            border-radius: 7px;
            padding: 10px 8px;
            font-size: 18px;
            text-align: center;
            box-sizing: border-box;
            background: none;
            box-shadow: none;
            transition: border-color 0.2s;
        }
        .stTextInput > div > div > input:focus {
            border: none;
            box-shadow: none;
        }
        /* Login button in admin form */
        .stButton > button[kind="login"] {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            border-radius: 15px;
            height: 60px;
            font-size: 22px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stButton > button[kind="login"]:hover {
            background: linear-gradient(135deg, #c0392b, #e74c3c);
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 8px 15px rgba(231, 76, 60, 0.3);
        }
        /* Admin login title */
        .admin-login-title {
            text-align: center;
            color: #ff0000;
            margin-bottom: 40px;
            font-size: 36px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        /* Center the text input labels */
        .stTextInput > label {
            text-align: center;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 10px;
        }
        </style>
        <div class="title-center">📚 Library Catalog</div>
        """
        , unsafe_allow_html=True)

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

    # Admin login form if chosen
    if st.session_state.get('view_mode') == 'admin_login':
        st.markdown("""
            <style>
            .admin-login-title {
                text-align: center;
                color: #ff0000;
                margin-bottom: 40px;
                font-size: 36px;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }
            </style>
            <h2 class="admin-login-title">🔐 Admin Login</h2>
        """, unsafe_allow_html=True)
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
    st.markdown(
        """
        <style>
        .catalog-title {
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            margin-top: 40px;
            margin-bottom: 40px;
            color: #2c3e50;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        </style>
        <div class="catalog-title">📖 Library Catalog</div>
        """
        , unsafe_allow_html=True)

    categories = get_categories()
    if not categories:
        st.warning("No categories available. Please add books.")
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
                    new_number = st.text_input("Book Number (can be alphanumeric)")
                    new_author = st.text_input("Author/Publication (optional)")
                    submitted = st.form_submit_button("Add Book")

                    if submitted:
                        if not new_name.strip() or not new_number.strip():
                            st.error("Book Name and Number cannot be empty.")
                        else:
                            add_book(new_name.strip(), new_number.strip(), new_author.strip() or None, selected_cat)
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

        st.markdown("---")
        
        # Category management section moved here
        with st.expander("📁 Manage Categories", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                with st.form("add_category_form"):
                    new_category = st.text_input("New Category Name")
                    submitted = st.form_submit_button("Add Category")
                    if submitted:
                        if not new_category.strip():
                            st.error("Category name cannot be empty.")
                        else:
                            add_category(new_category.strip())
                            st.success(f"Added category '{new_category}'.")
                            st.rerun()
            
            with col2:
                if categories:
                    category_to_delete = st.selectbox("Select category to delete", options=categories)
                    if st.button("Delete Category"):
                        if st.warning(f"Are you sure you want to delete '{category_to_delete}'? This will also delete all books in this category."):
                            delete_category(category_to_delete)
                            st.success(f"Deleted category '{category_to_delete}' and all its books.")
                            st.rerun()

        if st.button("Logout"):
            logout()
    else:
        # guest view only
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
