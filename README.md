# 📚 Sisyphus's Shelf (The Pile)

A full-stack, multi-user web application built with Django designed to help users track, manage, and visualize their ever-growing backlog of video games, books, and movies.

## ✨ Key Features
* **Multi-User Authentication:** Secure user registration and login system. Users have isolated databases and can only view/edit their own media items.
* **Interactive Dashboard:** Utilizes Chart.js to provide dynamic visual data graphs of backlog status and automatically queries the user's top "High Priority" items.
* **Live Search & Filtering:** Dynamically filter the database by Title, Creator, or Custom Genre tags without reloading the page.
* **Polished UI/UX:** Built with Bootstrap, featuring custom Toast Notifications for all CRUD operations (Create, Read, Update, Delete) and interactive JavaScript modal confirmations.
* **Containerized Deployment:** Fully Dockerized architecture, deployed live on an AWS EC2 Ubuntu instance.

## 🛠️ Technology Stack
* **Backend:** Python, Django 6.0
* **Database:** SQLite (Development & Production)
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js
* **Deployment:** Docker, Docker Compose, AWS EC2
* **Version Control:** Git & GitHub

## 🚀 Running the Project Locally

### Prerequisites
* Python 3.10+
* Git

### Installation Steps
1. Clone the repository:
   ```bash
   git clone [https://github.com/Bridgerbb/Sisyphus-Shelf.git](https://github.com/Bridgerbb/Sisyphus-Shelf.git)
   cd Sisyphus-Shelf
Create and activate a virtual environment:

Bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install dependencies:

Bash
pip install -r requirements.txt
Apply database migrations:

Bash
python manage.py migrate
Run the development server:

Bash
python manage.py runserver
Open your browser and navigate to http://127.0.0.1:8000/

🐳 Running with Docker
Ensure Docker Desktop is running.

Build and start the containers:

Bash
docker compose up -d --build
Run database migrations inside the container:

Bash
docker compose exec web python manage.py migrate
🧪 Testing
This project includes automated testing for database models, user authentication, and view security. To run the test suite locally:

Bash
python manage.py test