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
            color: #ffffff;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
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
            color: #ffffff;
            margin-bottom: 40px;
            font-size: 36px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        /* Center the text input labels */
        .stTextInput > label {
            text-align: center;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 10px;
            color: #ffffff;
        }
        </style>
        <div class="title-center">DIET Dehradun 📚Library Catalog</div>
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

def get_total_books():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM books")
    total = c.fetchone()[0]
    conn.close()
    return total

def main_app(username):
    st.markdown(
        """
        <style>
        /* Main container styling */
        .main {
            background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
            padding: 20px;
            border-radius: 15px;
        }
        
        /* Title styling */
        .catalog-title {
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            margin-top: 40px;
            margin-bottom: 20px;
            color: #ffffff;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Total books counter */
        .total-books {
            text-align: center;
            font-size: 24px;
            color: #ffffff;
            margin-bottom: 40px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            backdrop-filter: blur(5px);
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background: linear-gradient(135deg, #2c3e50 0%, #1a1a1a 100%);
            padding: 20px;
            border-radius: 15px;
        }
        
        .sidebar-title {
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 20px;
            text-align: center;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        
        /* Modernize Streamlit radio buttons for categories - no circles, rounded rectangles, smooth color transition */
        .stRadio [role="radiogroup"] {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .stRadio [role="radiogroup"] > label {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 220px;
            min-height: 44px;
            border-radius: 22px;
            background: #23242a;
            color: #fff;
            font-size: 1.1em;
            font-weight: 600;
            letter-spacing: 1px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            position: relative;
            transition: background 0.4s, box-shadow 0.3s, transform 0.2s;
            cursor: pointer;
            text-align: center;
            padding: 0 32px 0 24px;
            margin: 0 auto;
        }
        .stRadio [role="radiogroup"] > label:hover,
        .stRadio [role="radiogroup"] > label[data-selected="true"] {
            background: #ff6a88;
            color: #fff;
            box-shadow: 0 6px 24px rgba(255, 204, 112, 0.18);
            transform: translateY(-2px) scale(1.03);
        }
        /* Hide the radio input and its visual circle */
        .stRadio [role="radiogroup"] input[type="radio"] {
            display: none !important;
        }
        /* Do NOT hide label > div, so category names remain visible */
        .stRadio [role="radiogroup"] > label span, .stRadio [role="radiogroup"] > label div {
            flex: 1;
            text-align: center;
            font-size: 1.1em;
            font-weight: 600;
            letter-spacing: 1px;
            z-index: 2;
        }
        .stRadio [role="radiogroup"] > label::after {
            content: "→";
            position: absolute;
            right: 18px;
            font-size: 1.3em;
            opacity: 0.7;
            transition: opacity 0.2s;
        }
        .stRadio [role="radiogroup"] > label[data-selected="true"]::after,
        .stRadio [role="radiogroup"] > label:hover::after {
            opacity: 1;
        }
        
        /* Logout button styling */
        .stButton > button[kind="logout"] {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            border-radius: 15px;
            height: 50px;
            font-size: 18px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 20px;
            width: 100%;
            transition: all 0.3s ease;
        }
        
        .stButton > button[kind="logout"]:hover {
            background: linear-gradient(135deg, #c0392b, #e74c3c);
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 8px 15px rgba(231, 76, 60, 0.3);
        }
        
        /* Search box styling */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 10px;
            color: white;
            padding: 10px;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
        }
        
        /* Dataframe styling */
        .stDataFrame {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 10px;
        }
        
        /* Form styling */
        .stForm {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 20px;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
        }
        
        /* Info and warning messages */
        .stInfo, .stWarning, .stSuccess, .stError {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 10px;
        }
        .category-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 220px;
            min-height: 44px;
            border-radius: 22px;
            background: #23242a;
            color: #fff;
            font-size: 1.1em;
            font-weight: 600;
            letter-spacing: 1px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            position: relative;
            transition: background 0.4s, box-shadow 0.3s, transform 0.2s;
            cursor: pointer;
            text-align: center;
            padding: 0 32px 0 24px;
            margin: 0 auto 12px auto;
            border: none;
        }
        .category-btn.selected {
            background: #ff6a88 !important;
            color: #fff !important;
            box-shadow: 0 6px 24px rgba(255, 204, 112, 0.18);
            transform: translateY(-2px) scale(1.03);
        }
        .category-btn:hover {
            background: #ff6a88;
            color: #fff;
        }
        </style>
        <div class="catalog-title">DIET Dehradun 📖Library Catalog</div>
        """
        , unsafe_allow_html=True)

    total_books = get_total_books()
    st.markdown(f'<div class="total-books">Total Books: {total_books}</div>', unsafe_allow_html=True)

    categories = get_categories()
    if not categories:
        st.warning("No categories available. Please add books.")
        return

    # Sidebar for category selection and logout
    with st.sidebar:
        st.markdown('<div class="sidebar-title">📚 Categories</div>', unsafe_allow_html=True)
        
        # Vertical button menu for categories
        if 'selected_cat' not in st.session_state or st.session_state.selected_cat not in categories:
            st.session_state.selected_cat = categories[0]
        for cat in categories:
            btn_label = f"{cat}  →"
            if st.button(btn_label, key=f"cat_{cat}", use_container_width=True, help=cat):
                st.session_state.selected_cat = cat
        # Custom JS/CSS to highlight the selected button
        st.markdown(f"""
        <style>
        [data-testid="stButton"] button.category-btn {{
            background: #23242a;
            color: #fff;
        }}
        [data-testid="stButton"] button.category-btn.selected {{
            background: #ff6a88 !important;
            color: #fff !important;
        }}
        </style>
        <script>
        const btns = window.parent.document.querySelectorAll('[data-testid="stButton"] button.category-btn');
        btns.forEach(btn => {{
            if(btn.innerText.trim() === "{st.session_state.selected_cat}  →") {{
                btn.classList.add('selected');
            }} else {{
                btn.classList.remove('selected');
            }}
        }});
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", key="logout"):
            logout()

    selected_cat = st.session_state.selected_cat

    # Main content area
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
        
        # Category management section
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
    else:
        # guest view only
        st.info("Read-only access. Please login as admin to modify the catalog.")

def main():
    st.set_page_config(page_title="Library Catalog", layout="centered")
    init_db()

    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login()
    else:
        main_app(st.session_state.get('username', 'guest'))

if __name__ == "__main__":
    main()
