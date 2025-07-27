# pointRide - Ride-Sharing Platform

Welcome to the `pointRide` project repository! This document will guide you through setting up your local development environment for the Django-based ride-sharing platform.

## Table of Contents

1.  [Project Overview](#project-overview)
2.  [Prerequisites](#prerequisites)
3.  [Getting Started](#getting-started)
    * [1. Clone the Repository](#1-clone-the-repository)
    * [2. Set Up Pipenv Environment](#2-set-up-pipenv-environment)
    * [3. Run Database Migrations](#3-run-database-migrations)
    * [4. Create a Superuser (Optional)](#4-create-a-superuser-optional)
    * [5. Run the Development Server](#5-run-the-development-server)
4.  [Project Structure Overview](#project-structure-overview)
5.  [Configuration Notes](#configuration-notes)
6.  [Contributing](#contributing)
7.  [Support](#support)

---

## Project Overview

`pointRide` is a ride-sharing platform designed to connect drivers with travellers primarily within Ontario, Canada. It features a multi-step driver registration process, traveller registration, and aims to provide a seamless booking and ride experience.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

* **Python 3.10+**: Django 5.x requires Python 3.10 or newer.
* **Git**: For cloning the repository.
* **pipenv**: Our dependency management tool. Install it globally if you haven't already:
    ```bash
    pip install pipenv
    ```
* **PyCharm (Recommended IDE)**: While any IDE can work, PyCharm offers excellent integration with Django and pipenv.

## Getting Started

Follow these steps to get your local development environment up and running.

### 1. Clone the Repository

First, clone the project from GitHub to your local machine:

```bash
git clone https://github.com/arman-sakif/pointRide.git
cd pointRide
```
*(Replace `<your-repository-url>` with the actual URL of your GitHub repository.)*

### 2. Set Up Pipenv Environment

Navigate into the `pointRide` project directory (where `Pipfile` and `requirements.txt` are located) and install the dependencies using pipenv. This will create a virtual environment and install all necessary packages.

```bash
cd pointRide # Ensure you are in the root directory of the project
pipenv install --dev
```
* `pipenv install`: Installs dependencies from `Pipfile.lock` (or `Pipfile` if `Pipfile.lock` doesn't exist).
* `--dev`: Installs development dependencies as well.

### 3. Run Database Migrations

Once the dependencies are installed, activate the pipenv shell and apply the database migrations:

```bash
pipenv shell
python manage.py migrate
```
* `pipenv shell`: Activates the project's virtual environment. All subsequent commands will run within this environment.
* `python manage.py migrate`: Creates the necessary database tables based on your Django models.

### 4. Create a Superuser (Optional)

If you need to access the Django Admin panel, create a superuser account:

```bash
python manage.py createsuperuser
```
Follow the prompts to set up your username, email, and password.

### 5. Run the Development Server

Finally, start the Django development server:

```bash
python manage.py runserver
```
The server will typically run on `http://127.0.0.1:8000/`. Open this URL in your web browser to see the `pointRide` application.

To exit the pipenv shell, simply type `exit`.

## Project Structure Overview

The project follows a standard Django structure:

```
pointRide/
├── manage.py
├── requirements.txt
├── pointRide/             # Main project configuration
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── accounts/              # User authentication, registration (Driver/Traveller)
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py (to be created)
│   └── templates/accounts/
├── rides/                 # (Future) Ride management, booking
│   └── ...
├── verification/          # (Future) Driver/document verification
│   └── ...
├── static/                # Global static files (CSS, JS, images)
├── media/                 # User-uploaded media (profile pictures, vehicle photos)
└── templates/             # Project-level templates (base.html, home.html)
```

## Configuration Notes

* **`settings.py`**:
    * `DEBUG = True`: Set to `False` for production environments.
    * `ALLOWED_HOSTS`: Remember to configure this for production deployments.
    * `AUTH_USER_MODEL = 'accounts.User'`: Our custom user model.
    * `MEDIA_ROOT` and `MEDIA_URL`: Configured for handling user-uploaded files.
    * `STATIC_URL` and `STATICFILES_DIRS`: Configured for serving static assets.
    * `INSTALLED_APPS`: Ensure all necessary apps (including `accounts`, `crispy_forms`, `crispy_bootstrap5`, etc.) are listed.
