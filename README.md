# Expense Tracker Project

This is a web-based expense tracker built with Django. It allows users to add, view, and categorize expenses. This project was created for CSCI-3340-03.

## Features:
- Add new expenses with a category, amount, and date
- View a list of all expenses
- Optional notes for detailed descriptions
- Easy to extend and customize

## Installation Instructions:
1. Clone the repository:
    ```bash
    git clone https://github.com/johnjohn2410/Expense_Tracker_Project.git
    ```
2. Navigate to the project directory and set up a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Apply migrations and start the server:
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

## Usage:
- Visit `http://127.0.0.1:8000/` to start using the expense tracker.

## License:
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
