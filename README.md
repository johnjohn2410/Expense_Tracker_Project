💸 Expense Tracker Project 💸
This is a web-based expense tracker built with Django. It allows users to add, view, and categorize expenses in a user-friendly interface.

🎯 Features:
➕ Add New Expenses with a category, amount, and date.
📜 View All Expenses in an organized list.
📝 Optional Notes for detailed descriptions of each expense.
💼 Easy to Extend and customize for your specific needs.
📈 Set and update Monthly Budgets to track spending.
📊 Add Income entries to manage your finances effectively.
📁 Export data to CSV files.

🛠️ Installation Instructions for JetBrains PyCharm and VSCODE

1. **Clone the Repository**:
   First, clone the repository to your local machine:
   ```bash
   git clone https://github.com/johnjohn2410/Expense_Tracker_Project.git
   cd Expense_Tracker_Project
   ```

2. **Open PyCharm or VS Code**:
   - **PyCharm**: Launch PyCharm, and select Open from the welcome screen. Navigate to the folder where you cloned the project and click Open.
   - **VS Code**: Launch VS Code and open the cloned project folder.

3. **Set Up a Python Virtual Environment**:
   - Open the terminal in your preferred IDE.
   - Create a virtual environment by running the following command:
     ```bash
     python -m venv venv
     ```

4. **Activate the Virtual Environment**:
   - **On Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **On macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

5. **Install Dependencies**:
   - In the terminal, install the required dependencies by running:
     ```bash
     pip install -r requirements.txt
     ```

6. **Apply Migrations and Start the Server**:
   - Run the following commands to set up the database and start the Django development server:
     ```bash
     python manage.py migrate
     python manage.py runserver
     ```
   - Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser to use the project.

💻 **Usage**:
After following the steps above for your preferred IDE, you can visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to start using the Expense Tracker.

➕ Add expenses, 📜 view your expense list, 🗂️ categorize your expenses, set monthly budgets, add income, and export your expenses to a CSV file.

📝 **License**:
This project is licensed under the MIT License – see the LICENSE file for details.

🛠️ **Explanation**:
The JetBrains PyCharm section explains how to set up the project using a virtual environment, install dependencies, and run the Django server. The Visual Studio Code section includes similar steps but adds details for configuring the Python interpreter in VS Code.
