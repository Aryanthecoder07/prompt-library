# ⚡ RTC Prompt Library

A self-hosted, database-driven prompt management system built with Streamlit and SQLite. This application allows teams to store, organize, and standardize their best AI prompts for consistent results.

## ✨ Features

* **🔍 Search & Filter:** Instantly find prompts by title, description, or category.
* **📂 Dynamic Categories:** Fully customizable organization. Create new categories, rename existing ones, and manage deletions.
* **🔥 Trending Section:** Highlight frequently used prompts for quick access.
* **⚙️ Admin Panel:** A secure, password-protected interface for administrators.
    * **CRUD Operations:** Add, Edit, and Delete prompts easily.
    * **Category Management:** Rename categories (auto-updates prompts) or delete categories (with options to delete prompts or move them to 'Uncategorized').
* **💾 Auto-Migration:** Automatically imports existing `prompts.json` data into the SQLite database on the first run.

## 🔮 Coming Soon

* **🤖 AI-Based Personalization:** Smart recommendations that suggest prompts based on your usage history and role.
* **✨ Prompt Refiner:** Integrated AI tool to automatically polish and improve your draft prompts.
* **👥 User Accounts:** Individual user logins to save personal favorites and private collections.
* **📊 Analytics Dashboard:** visual insights into which prompts are being used the most.

## 🚀 Getting Started

### Prerequisites

* Python 3.8 or higher
* `pip` (Python package installer)

### Installation

1.  **Clone or Download** this repository to your local machine.
2.  **Install dependencies:**
    ```bash
    pip install streamlit
    ```
    *(Note: `sqlite3` and `json` are included with Python by default)*

### Running the App

1.  Open your terminal or command prompt.
2.  Navigate to the project directory.
3.  Run the application:
    ```bash
    streamlit run main.py
    ```
4.  The app will launch automatically in your web browser at `http://localhost:8501`.

## 🛠️ Configuration

### 🔑 Admin Password
The default password for the Admin Panel is `admin123`.
To change this, open `main.py` and edit line 11:
```python
ADMIN_PASSWORD = "YOUR_SECURE_PASSWORD"
