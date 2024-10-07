from pathlib import Path

# Define the base directory of the project, which is important for referencing other directories.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security and debugging settings
# This secret key is critical for Django's cryptographic signing. Keep it safe!
SECRET_KEY = 'your-secret-key'
# Enabling debugging mode for development. Should be set to False in production.
DEBUG = True
# Allowed hosts define which domain names can serve the app. For now, it's set to localhost and all hosts.
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Installed applications
# This list includes both Django's built-in apps and my custom 'tracker' app.
INSTALLED_APPS = [
    'django.contrib.admin',       # Admin interface
    'django.contrib.auth',        # User authentication system
    'django.contrib.contenttypes',# Handles content types
    'django.contrib.sessions',    # Manages user sessions
    'django.contrib.messages',    # Provides messaging framework
    'tracker',                    # My custom expense tracker app
]

# Middleware settings
# Middleware is a chain of components that process requests/responses.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Helps keep the site secure.
    'django.contrib.sessions.middleware.SessionMiddleware',  # Manages sessions across requests.
    'django.middleware.common.CommonMiddleware',      # Provides general utilities.
    'django.middleware.csrf.CsrfViewMiddleware',      # Protects against Cross-Site Request Forgery.
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Handles user authentication.
    'django.contrib.messages.middleware.MessageMiddleware',  # Manages temporary messages between views.
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Protects against clickjacking attacks.
]

# Root URL configuration
# This points to the main URL routing configuration for the project.
ROOT_URLCONF = 'Expense_Tracker_Project.urls'

# Template settings
# Here, I define where Django should look for HTML templates.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # The backend responsible for rendering templates.
        'DIRS': [BASE_DIR / 'tracker' / 'templates'],  # Specify the directory where templates are stored.
        'APP_DIRS': True,  # Automatically looks for templates in each app’s 'templates' folder.
        'OPTIONS': {
            'context_processors': [  # These processors inject useful context variables into templates.
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI application
# This is the entry point for WSGI-compatible web servers to serve the app.
WSGI_APPLICATION = 'Expense_Tracker_Project.wsgi.application'

# Database settings
# Here, I configure the project to use SQLite for storing data. This database is file-based and suitable for development.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # SQLite database engine.
        'NAME': BASE_DIR / 'db.sqlite3',         # The location of the SQLite database file.
    }
}

# Static files settings
# This URL defines the base path for serving static files such as CSS, JavaScript, and images.
STATIC_URL = 'static/'

# Default primary key field type
# New models that do not specify a primary key field will use 'BigAutoField' as the default.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
