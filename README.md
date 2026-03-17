# AssignHub - Assignment Management System

AssignHub is a modern, full-stack web application designed to help students manage their courses and assignments efficiently. It features a robust **Django** backend and a clean, responsive Vue.js frontend.

## 🚀 Features

### **Core Functionality**
- **User Authentication**: Secure registration and login using JWT (JSON Web Tokens).
- **Course Management**: Organize your studies by creating, updating, and deleting courses.
- **Task Management**: Track your assignments with titles, deadlines, and statuses (`todo`, `doing`, `done`).
- **Dashboard Overview**: A centralized view showing your course count, upcoming deadlines, and completed tasks.

### **Smart Tracking**
- **Countdown Timers**: Real-time countdown for each task (e.g., `3d 5h left`).
- **Urgent Task Labeling**: Tasks due within 7 days are automatically highlighted.
- **Overdue Detection**: Past-due tasks are clearly marked as `OVERDUE`.
- **Email Reminders**: Automated daily background tasks that scan for assignments due within the next 24 hours and send email notifications to users.

## 🛠️ Tech Stack

### **Backend**
- **Language**: Python 3.9+
- **Framework**: [Django](https://www.djangoproject.com/) & [Django REST Framework](https://www.django-rest-framework.org/)
- **Database**: SQLite (Default)
- **Authentication**: [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- **Task Scheduler**: [APScheduler](https://apscheduler.readthedocs.io/) (via Management Command)

### **Frontend**
- **Framework**: [Vue.js 3](https://vuejs.org/) (Composition API)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Icons**: [Lucide Icons](https://lucide.dev/)
- **HTTP Client**: [Axios](https://axios-http.com/)

## 📂 Project Structure

```text
AssignmentManagementSystem/
├── config/                 # Django Project Configuration
├── api/                    # Django App (Models, Views, Serializers)
│   ├── management/         # Management commands (reminders)
│   ├── migrations/         # Database migrations
│   ├── models.py           # Database models
│   ├── serializers.py      # DRF Serializers
│   └── views.py            # API Views
├── frontend/               # Frontend source code
│   └── index.html          # Single Page Application (SPA)
├── requirements.txt        # Python dependencies
├── manage.py               # Django CLI
├── db.sqlite3              # SQLite database file
└── .env                    # Environment variables
```

## ⚡ Getting Started

### **1. Prerequisites**
- Python 3.9 or higher installed on your system.

### **2. Setup Virtual Environment**
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Configure Environment Variables**
Copy the example environment file to create your own configuration:
```bash
cp .env.example .env
# On Windows: copy .env.example .env
```
Edit the `.env` file with your settings:
```env
JWT_SECRET=your_secret_key_here
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
```

### **5. Initialize Database**
```bash
python manage.py migrate
```

### **6. Run the Application**
```bash
python manage.py runserver 0.0.0.0:3000
```
The server will start at **http://localhost:3000**.

### **7. Start Email Reminders (Optional)**
To enable background email reminders, run this command in a separate terminal:
```bash
python manage.py run_reminders
```

## 🧪 Testing
A Python test script is provided to verify all API functionalities:
```bash
python test-py-api.py
```

## 📄 License
This project is licensed under the MIT License.
