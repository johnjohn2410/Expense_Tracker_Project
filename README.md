💸 **Expense Tracker Project** 💸

This is a web-based expense tracker built with Django. It allows users to add, view, and categorize expenses in a user-friendly interface.

---

## 🎯 Features

- **➕ Add New Expenses**: Easily add expenses with a category, amount, and date.
- **📜 View All Expenses**: See all your expenses in an organized list.
- **📝 Optional Notes**: Add detailed descriptions for each expense.
- **💼 Easy Customization**: Extend and customize the application for your specific needs.
- **📈 Monthly Budget Management**: Set and update monthly budgets to track spending.
- **📊 Income Management**: Add income entries to manage your finances effectively.
- **📁 Export Data**: Export expenses to CSV files for easy backup or analysis.

---

## 🛠️ Installation Instructions for PyCharm and VS Code

### 1. Clone the Repository
First, clone the repository to your local machine:
```bash
git clone https://github.com/johnjohn2410/Expense_Tracker_Project.git
cd Expense_Tracker_Project
```

### 2. Open in Your Preferred IDE
- **PyCharm**: Launch PyCharm, and select **Open** from the welcome screen. Navigate to the folder where you cloned the project and click **Open**.
- **VS Code**: Launch VS Code and open the cloned project folder.

### 3. Set Up a Python Virtual Environment
- Open the terminal in your preferred IDE.
- Create a virtual environment by running the following command:
  ```bash
  python -m venv venv
  ```

### 4. Activate the Virtual Environment
- **On Windows**:
  ```bash
  venv\Scripts\activate
  ```
- **On macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### 5. Install Dependencies
Install the required dependencies by running:
```bash
pip install -r requirements.txt
```

### 6. Apply Migrations and Start the Server
Set up the database and start the Django development server:
```bash
python manage.py
