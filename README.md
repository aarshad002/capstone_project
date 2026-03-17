# TaskFlow - Capstone Project

## Project Overview
TaskFlow is a Django-based task management web application developed as a capstone project.  
It helps teams organize projects, assign tasks, track task progress, and collaborate through comments.

The system supports role-based access control with two main user roles:

- **Manager**
- **Employee**

Managers can create projects, create tasks, assign tasks, and manage work across projects.  
Employees can view their assigned tasks, update task statuses, and add comments.

---

## Features

### Authentication
- User registration
- User login
- User logout
- Custom user model with role support

### Role-Based Access
- **Manager**
  - Create projects
  - Delete projects
  - Create tasks
  - Edit tasks
  - Delete tasks
  - Assign tasks to employees
  - View managed project tasks
  - Comment on tasks

- **Employee**
  - View assigned tasks
  - Update task status
  - Comment on tasks
  - Cannot create or delete projects/tasks

### Project Management
- Project list page
- Project detail page
- Create project
- Delete project

### Task Management
- Create task
- Edit task
- Delete task
- Assign task to a user
- Update task status
- Task detail page

### Comment System
- Add comments to tasks
- Show comment author
- Show comment timestamp

### Dashboard
- Summary of task counts:
  - Pending
  - In Progress
  - Completed
- Manager dashboard:
  - Managed projects
  - Personal tasks
- Employee dashboard:
  - Assigned tasks only

### Security
- Login protection using Django authentication
- Role-based permission checks
- CSRF protection in forms

---

## User Roles

### Manager
Managers can manage projects and tasks across the system.

### Employee
Employees can only interact with their own assigned tasks and comments.

---

## Tech Stack

- **Backend:** Django
- **Language:** Python
- **Database:** SQLite
- **Frontend:** HTML, CSS, Django Templates
- **Authentication:** Django built-in authentication system
- **Version Control:** Git / GitHub

---

## Installation and Setup

### 1. Clone the repository
```bash
git clone https://github.com/aarshad002/capstone_project.git
cd TaskFlow
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

### 3. Activate the virtual environment
```bash
conda 
```
### 4. Intall dependencies
```bash
pip install -r requirements.txt
```
### 5. Apply migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser(for admin access)
```bash
python manage.py createsuperuser
```
### 7. Run the server
```bash
python manage.py runserver
```
Then open : http://127.0.0.1:8000/

## Project Structure

```bash
TaskFlow/
│
├── accounts/      # Custom user model and authentication-related logic
├── projects/      # Project models, views, forms, and URLs
├── tasks/         # Task models, views, forms, and URLs
├── templates/     # Global templates
├── static/        # CSS files
├── config/        # Project settings and root URLs
└── manage.py
