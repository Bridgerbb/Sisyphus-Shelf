# 📚 Sisyphus's Shelf (The Pile)

A full-stack, multi-user web application built with Django designed to help users track, manage, and visualize their ever-growing backlog of media.

🚀 [Live Demo] http://44.255.117.28/

## ✨ Key Features
* **Multi-User Authentication:** Secure user registration and login system with isolated user databases.
* **Dynamic Metadata Lookup:** Integrated with TMDB, Google Books, and IGDB APIs to auto-fill covers, creators, and descriptions.
* **Interactive Dashboard:** Utilizes Chart.js for data visualization and a custom "Shelf Weight" statistics suite.
* **Priority Queue:** A custom drag-and-drop interface (SortableJS) for reordering high-priority items.
* **Sisyphus's Choice (Randomizer):** An "I'm Feeling Lucky" feature that picks a random item from the user's backlog to solve choice paralysis.
* **Containerized Deployment:** Fully Dockerized architecture, deployed on AWS EC2.

## 🛠️ Technology Stack
* **Backend:** Python, Django 5.1
* **Database:** SQLite
* **Frontend:** JavaScript (ES6+), Bootstrap 5, Chart.js, SortableJS
* **Deployment:** Docker, AWS EC2, Nginx/WhiteNoise

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