# 💸 Expense Tracker Project 💸

This is a *web-based expense tracker* built with Django. It allows users to add, view, and categorize expenses in a user-friendly interface.

---

## 🎯 Features:
- ➕ **Add New Expenses** with a category, amount, and date.
- 📜 **View All Expenses** in an organized list.
- 📝 **Optional Notes** for detailed descriptions of each expense.
- 💼 **Easy to Extend** and customize for your specific needs.
- Export data to CSV files or through excel.

---

## 🛠️ Installation Instructions for JetBrains PyCharm and VSCODE
1. Open PyCharm:
Launch PyCharm, and select Open from the welcome screen.
Navigate to the folder where you cloned the project and click Open.and click Open.

2. Set Up a Python Virtual Environment:
Open the terminal in VS Code (View > Terminal).
Create a virtual environment by running the following command:
bash
Copy code
"python -m venv venv"

4. Activate the Virtual Environment:

On Windows:
bash
venv\Scripts\activate

On macOS/Linux:
bash
source venv/bin/activate

5. Install Python Extensions:
VS Code may prompt you to install the Python extension. If not:
Go to the Extensions tab (Ctrl+Shift+X), search for Python, and install it.
Ensure the virtual environment is selected as your interpreter:
Open the command palette (Ctrl+Shift+P) and search for Python: Select Interpreter.
Choose the interpreter inside the venv folder.

6. Install Dependencies:
In the terminal, install the required dependencies:
bash
Copy code
pip install -r requirements.txt

7. Apply Migrations and Start the Server:
Run the following commands to set up the database and start the Django development server:
bash
Copy code
python manage.py migrate
python manage.py runserver
Open http://127.0.0.1:8000/ in your browser to use the project.

💻 Usage:
After following the steps above for your preferred IDE, you can visit http://127.0.0.1:8000/ to start using the Expense Tracker.

➕ Add expenses, 📜 view your expense list, and 🗂️ categorize your expenses.

📝 License:
This project is licensed under the MIT License – see the LICENSE file for details.

🛠️ Explanation:
The JetBrains PyCharm section explains how to set up the project using a virtual environment, install dependencies, and run the Django server.
The Visual Studio Code section includes similar steps but adds details for configuring the Python interpreter in VS Code.


### 📥 Cloning the Repository
First, clone the repository to your local machine:

```bash
git clone https://github.com/johnjohn2410/Expense_Tracker_Project.git
cd Expense_Tracker_Project
