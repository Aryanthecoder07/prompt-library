import streamlit as st
import sqlite3
import json
import os

# 1. PAGE CONFIGURATION
st.set_page_config(layout="wide", page_title="RTC Prompt Library", page_icon="⚡")

# --- CONFIGURATION ---
DB_FILE = "prompts.db"
ADMIN_PASSWORD = "admin123"  # <--- SET YOUR PASSWORD HERE

# --- DATABASE MANAGEMENT FUNCTIONS ---
def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Prompts Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            desc TEXT,
            prompt TEXT,
            trending BOOLEAN DEFAULT 0
        )
    ''')
    
    # Categories Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Initialize default categories if table is empty
    c.execute("SELECT count(*) FROM categories")
    if c.fetchone()[0] == 0:
        default_cats = ["Communication", "Development", "Productivity", "Data", 
                        "Design", "Learning", "Content", "HR", "Business", 
                        "Sales", "Social Media", "Marketing", "Personal", 
                        "Creative Writing", "Writing", "Uncategorized"]
        for cat in default_cats:
            c.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))
            
    conn.commit()
    conn.close()

def migrate_json_if_needed():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT count(*) FROM prompts")
    count = c.fetchone()[0]
    
    if count == 0 and os.path.exists('prompts.json'):
        with open('prompts.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for p in data:
                # Ensure category exists in the new categories table
                c.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (p['category'],))
                
                c.execute('''
                    INSERT INTO prompts (title, category, desc, prompt, trending)
                    VALUES (?, ?, ?, ?, ?)
                ''', (p['title'], p['category'], p['desc'], p['prompt'], p['trending']))
        conn.commit()
        st.toast(f"✅ Migrated {len(data)} prompts from JSON to SQLite!")
    conn.close()

# --- DATA OPERATIONS: PROMPTS ---
def get_all_prompts():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM prompts ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_prompt_to_db(title, category, desc, prompt_text, trending):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO prompts (title, category, desc, prompt, trending) VALUES (?, ?, ?, ?, ?)",
              (title, category, desc, prompt_text, trending))
    conn.commit()
    conn.close()

def update_prompt_in_db(id, title, category, desc, prompt_text, trending):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE prompts 
        SET title=?, category=?, desc=?, prompt=?, trending=? 
        WHERE id=?
    ''', (title, category, desc, prompt_text, trending, id))
    conn.commit()
    conn.close()

def delete_prompt_from_db(prompt_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM prompts WHERE id=?", (prompt_id,))
    conn.commit()
    conn.close()

# --- DATA OPERATIONS: CATEGORIES ---
def get_all_categories():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM categories ORDER BY name ASC")
    rows = c.fetchall()
    conn.close()
    return [row['name'] for row in rows]

def add_category(name):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def rename_category(old_name, new_name):
    conn = get_connection()
    c = conn.cursor()
    try:
        # Update category name in categories table
        c.execute("UPDATE categories SET name=? WHERE name=?", (new_name, old_name))
        # Update all prompts that had the old category name 
        c.execute("UPDATE prompts SET category=? WHERE category=?", (new_name, old_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_category(name, delete_prompts=False):
    conn = get_connection()
    c = conn.cursor()
    
    # Delete the category from categories table
    c.execute("DELETE FROM categories WHERE name=?", (name,))
    
    if delete_prompts:
        # Delete all prompts in this category
        c.execute("DELETE FROM prompts WHERE category=?", (name,))
    else:
        # Move prompts to 'Uncategorized'
        # Ensure Uncategorized exists
        c.execute("INSERT OR IGNORE INTO categories (name) VALUES ('Uncategorized')")
        c.execute("UPDATE prompts SET category='Uncategorized' WHERE category=?", (name,))
        
    conn.commit()
    conn.close()

# --- INITIALIZATION ---
init_db()
migrate_json_if_needed()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("⚡ RTC Library")
    page_selection = st.radio("Navigation", ["🔍 Browse Prompts", "⚙️ Admin Panel"])
    
    # Initialize session state for login
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # Logout Button
    if st.session_state.authenticated:
        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

    st.divider()

# ==========================================
# PAGE 1: BROWSE PROMPTS
# ==========================================
if page_selection == "🔍 Browse Prompts":
    st.title("⚡ RTC Prompt Library")
    
    prompts_data = get_all_prompts()
    search_query = st.text_input("🔍 Search...", placeholder="e.g. Python, Email, HR")
    st.divider()

    if search_query:
        st.subheader(f"Results for '{search_query}'")
        display_prompts = [
            p for p in prompts_data 
            if search_query.lower() in p['title'].lower() 
            or search_query.lower() in p['desc'].lower()
        ]
    else:
        st.subheader("🔥 Trending Prompts")
        display_prompts = [p for p in prompts_data if p['trending']]

    if display_prompts:
        num_columns = 3
        for i in range(0, len(display_prompts), num_columns):
            cols = st.columns(num_columns)
            batch = display_prompts[i : i + num_columns]
            for j, prompt_item in enumerate(batch):
                with cols[j]:
                    with st.container(border=True):
                        st.caption(f"📂 {prompt_item['category']}")
                        st.subheader(prompt_item['title'])
                        st.markdown(f"_{prompt_item['desc']}_")
                        st.divider() 
                        st.markdown("#### Prompt") 
                        st.code(prompt_item['prompt'], language="text", wrap_lines=True)
    else:
        st.info("No prompts found.")

# ==========================================
# PAGE 2: ADMIN PANEL
# ==========================================
elif page_selection == "⚙️ Admin Panel":
    
    if not st.session_state.authenticated:
        st.header("🔒 Admin Login")
        password_input = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if password_input == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect Password")
    else:
        st.title("⚙️ Admin Dashboard")
        
        # Tabs including new Category Manager
        tab1, tab2, tab3 = st.tabs(["➕ Add New Prompt", "✏️ Manage Prompts", "📂 Manage Categories"])
        
        # Helper to refresh categories dynamically
        current_categories = get_all_categories()

        # --- TAB 1: ADD NEW PROMPT ---
        with tab1:
            st.subheader("Create New Prompt")
            with st.form("add_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                new_title = col1.text_input("Title")
                new_cat = col2.selectbox("Category", current_categories)
                new_desc = st.text_input("Short Description")
                new_prompt = st.text_area("Prompt Content", height=150)
                new_trending = st.checkbox("Mark as Trending?")
                
                if st.form_submit_button("Save Prompt"):
                    add_prompt_to_db(new_title, new_cat, new_desc, new_prompt, new_trending)
                    st.success(f"Prompt '{new_title}' added!")
                    st.rerun()

        # --- TAB 2: EDIT / DELETE PROMPTS ---
        with tab2:
            st.subheader("Edit or Delete Prompts")
            all_prompts = get_all_prompts()
            
            if not all_prompts:
                st.info("No prompts available.")
            else:
                prompt_titles = [f"{p['id']}: {p['title']}" for p in all_prompts]
                selected_prompt_str = st.selectbox("Select Prompt", prompt_titles)
                selected_id = int(selected_prompt_str.split(":")[0])
                selected_data = next(p for p in all_prompts if p['id'] == selected_id)
                
                with st.form("edit_form"):
                    e_title = st.text_input("Title", value=selected_data['title'])
                    
                    try:
                        cat_index = current_categories.index(selected_data['category'])
                    except ValueError:
                        cat_index = 0
                        
                    e_cat = st.selectbox("Category", current_categories, index=cat_index)
                    e_desc = st.text_input("Description", value=selected_data['desc'])
                    e_prompt = st.text_area("Prompt", value=selected_data['prompt'], height=200)
                    e_trending = st.checkbox("Trending", value=bool(selected_data['trending']))
                    
                    if st.form_submit_button("💾 Update Prompt"):
                        update_prompt_in_db(selected_id, e_title, e_cat, e_desc, e_prompt, e_trending)
                        st.success("Prompt updated!")
                        st.rerun()

                st.markdown("### Danger Zone")
                if st.button(f"🗑️ Delete '{selected_data['title']}'", type="primary"):
                    delete_prompt_from_db(selected_id)
                    st.error("Prompt deleted.")
                    st.rerun()

        # --- TAB 3: MANAGE CATEGORIES (NEW FEATURE) ---
        with tab3:
            st.subheader("📂 Category Management")
            
            # 1. Create New
            with st.expander("🆕 Create New Category", expanded=True):
                new_cat_name = st.text_input("New Category Name")
                if st.button("Create Category"):
                    if new_cat_name:
                        if add_category(new_cat_name):
                            st.success(f"Category '{new_cat_name}' created!")
                            st.rerun()
                        else:
                            st.error("Category already exists.")
                    else:
                        st.warning("Please enter a name.")

            st.divider()

            # 2. Rename
            with st.expander("✏️ Rename Category"):
                col_r1, col_r2 = st.columns(2)
                cat_to_rename = col_r1.selectbox("Select Category to Rename", current_categories)
                new_name_input = col_r2.text_input("New Name")
                
                if st.button("Rename"):
                    if new_name_input and cat_to_rename:
                        if rename_category(cat_to_rename, new_name_input):
                            st.success(f"Renamed '{cat_to_rename}' to '{new_name_input}'")
                            st.rerun()
                        else:
                            st.error("Failed to rename. Name might already exist.")
                    else:
                        st.warning("Please fill all fields.")

            st.divider()

            # 3. Delete
            with st.expander("🗑️ Delete Category"):
                cat_to_delete = st.selectbox("Select Category to Delete", current_categories)
                
                st.warning(f"You are about to delete '{cat_to_delete}'.")
                
                col_d1, col_d2 = st.columns(2)
                
                # Delete logic explained in UI
                # Option 1: Delete everything
                if col_d1.button("🔥 Delete Category & ALL its Prompts"):
                    delete_category(cat_to_delete, delete_prompts=True)
                    st.success(f"Deleted '{cat_to_delete}' and all associated prompts.")
                    st.rerun()
                    
                # Option 2: Move prompts to uncategorized
                if col_d2.button("📦 Delete Category (Move Prompts to Uncategorized)"):
                    delete_category(cat_to_delete, delete_prompts=False)
                    st.success(f"Deleted '{cat_to_delete}'. Prompts moved to 'Uncategorized'.")
                    st.rerun()