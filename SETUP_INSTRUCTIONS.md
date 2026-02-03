# TodoKanban - Setup & Testing Instructions

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.11 or higher
- pip (Python package installer)
- Git (optional, for cloning)

For Docker installation (optional):
- Docker Desktop (includes Docker and Docker Compose)

## Installation Methods

You can run this application in three ways:

### Method 1: Quick Start with Script (Recommended for Development)

1. **Navigate to the project directory:**
   ```bash
   cd todo-kanban-app
   ```

2. **Run the startup script:**
   ```bash
   # On Linux/Mac:
   ./run.sh

   # On Windows (use Git Bash or WSL):
   bash run.sh
   ```

3. **Access the application:**
   - Open your browser and go to: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Method 2: Manual Setup

1. **Create and activate virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate on Linux/Mac:
   source venv/bin/activate

   # Activate on Windows (Command Prompt):
   venv\Scripts\activate.bat

   # Activate on Windows (PowerShell):
   venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create necessary directories:**
   ```bash
   mkdir -p uploads data
   ```

4. **Set up environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env if needed (default values work for development)
   ```

5. **Run the application:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application:**
   - Main App: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Method 3: Docker (Recommended for Production)

1. **Start with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Main App: http://localhost:8000
   - API Docs: http://localhost:8000/docs

3. **Stop the application:**
   ```bash
   # Press Ctrl+C, then:
   docker-compose down
   ```

## Step-by-Step Testing Guide

### Phase 1: User Registration & Authentication

1. **Open the application:**
   - Go to http://localhost:8000
   - You'll be redirected to the login page

2. **Create a new account:**
   - Click "Sign up" or navigate to http://localhost:8000/register
   - Fill in the registration form:
     ```
     Username: testuser
     Email: test@example.com
     Full Name: Test User (optional)
     Password: TestPass123!
     Confirm Password: TestPass123!
     ```
   - Click "Create Account"
   - You should see a success message

3. **Login with your account:**
   - You'll be redirected to the login page
   - Enter your credentials:
     ```
     Username: testuser
     Password: TestPass123!
     ```
   - Click "Sign In"
   - You should be redirected to the dashboard

### Phase 2: Board Management

1. **Create your first board:**
   - Click the "+ Create Board" button
   - Fill in the details:
     ```
     Board Name: Project Alpha
     Description: Main project management board
     [ ] Make this board public (leave unchecked for now)
     ```
   - Click "Create Board"
   - The board should appear in your dashboard

2. **Create additional boards:**
   - Create 2-3 more boards to test the dashboard:
     ```
     Board 1: Project Alpha
     Board 2: Personal Tasks
     Board 3: Team Sprint
     ```

3. **Open a board:**
   - Click on "Project Alpha" board
   - You should see an empty Kanban board

### Phase 3: Column Management

1. **Add columns to your board:**
   - Click "+ Add Column" button
   - Create the following columns one by one:

   **Column 1:**
   ```
   Column Name: To Do
   Color: #3b82f6 (blue)
   ```

   **Column 2:**
   ```
   Column Name: In Progress
   Color: #f59e0b (orange)
   ```

   **Column 3:**
   ```
   Column Name: Review
   Color: #8b5cf6 (purple)
   ```

   **Column 4:**
   ```
   Column Name: Done
   Color: #10b981 (green)
   ```

2. **Verify columns:**
   - You should see 4 columns displayed horizontally
   - Each column should have its name and a count (0) badge

### Phase 4: Task Management

1. **Create tasks in "To Do" column:**
   - Click "+ Add Task" in the "To Do" column
   - Create your first task:
     ```
     Title: Set up project structure
     Description: Create initial folders and configuration files
     Priority: High
     Due Date: Select tomorrow's date
     Tags: setup, infrastructure
     ```
   - Click "Save Task"

2. **Create more tasks:**
   Add these tasks to the "To Do" column:

   **Task 2:**
   ```
   Title: Implement user authentication
   Description: Add JWT-based authentication system
   Priority: Urgent
   Tags: backend, security, authentication
   ```

   **Task 3:**
   ```
   Title: Design database schema
   Description: Create ERD and implement models
   Priority: High
   Tags: database, backend
   ```

   **Task 4:**
   ```
   Title: Create API endpoints
   Description: Implement RESTful API endpoints
   Priority: Medium
   Tags: backend, api
   ```

   **Task 5:**
   ```
   Title: Build frontend UI
   Description: Create responsive user interface
   Priority: Medium
   Tags: frontend, ui, design
   ```

3. **Edit a task:**
   - Click on any task card
   - Change the priority to "Low"
   - Add a new tag: "updated"
   - Click "Save Task"
   - Verify the changes are reflected

4. **Move tasks between columns:**
   - Since we haven't implemented drag-and-drop in this version, you can:
   - Click on a task to edit it
   - Note: In a future version, you would change the column_id here
   - For now, just verify you can view and edit tasks

5. **Delete a task:**
   - Click on a task
   - Click the red "Delete" button
   - Confirm the deletion
   - Verify the task is removed from the board

### Phase 5: Testing Real-time Features

1. **Open the same board in two browser windows:**
   - Window 1: Keep your current board open
   - Window 2: Open a new browser window/tab in incognito mode
   - Login with the same credentials
   - Navigate to the same board

2. **Test WebSocket updates:**
   - In Window 1: Create a new task
   - In Window 2: The new task should appear automatically
   - In Window 2: Create a task
   - In Window 1: The task should appear
   - Note: This demonstrates real-time collaboration

### Phase 6: API Testing

1. **Access API Documentation:**
   - Go to http://localhost:8000/docs
   - You'll see the interactive Swagger UI

2. **Test authentication via API:**

   **Register a new user:**
   - Expand `POST /api/v1/auth/register`
   - Click "Try it out"
   - Enter:
     ```json
     {
       "username": "apiuser",
       "email": "api@example.com",
       "password": "ApiPass123!",
       "full_name": "API Test User"
     }
     ```
   - Click "Execute"
   - Check the response (should be 201 Created)

   **Login:**
   - Expand `POST /api/v1/auth/login`
   - Click "Try it out"
   - Enter:
     ```
     username: apiuser
     password: ApiPass123!
     ```
   - Click "Execute"
   - Copy the `access_token` from the response

   **Authorize:**
   - Click the "Authorize" button at the top
   - Paste your token (just the token, not "Bearer")
   - Click "Authorize"
   - Click "Close"

3. **Test board endpoints:**

   **Create a board:**
   - Expand `POST /api/v1/boards/`
   - Click "Try it out"
   - Enter:
     ```json
     {
       "name": "API Test Board",
       "description": "Created via API",
       "is_public": false
     }
     ```
   - Click "Execute"
   - Note the `id` in the response

   **Get all boards:**
   - Expand `GET /api/v1/boards/`
   - Click "Try it out"
   - Click "Execute"
   - You should see your new board in the list

### Phase 7: Search Functionality

1. **Test search:**
   - Go back to your board in the browser
   - Create several tasks with different keywords
   - Use the API search endpoint:
     - Go to http://localhost:8000/docs
     - Expand `GET /api/v1/tasks/search`
     - Click "Try it out"
     - Enter a search query: "authentication"
     - Click "Execute"
     - You should see matching tasks

## Verification Checklist

Use this checklist to ensure everything is working:

- [ ] Application starts without errors
- [ ] Can access the home page (http://localhost:8000)
- [ ] Can register a new user account
- [ ] Can login with created account
- [ ] Dashboard displays after login
- [ ] Can create a new board
- [ ] Multiple boards display correctly
- [ ] Can open a board
- [ ] Can add columns to a board
- [ ] Can create tasks in columns
- [ ] Can edit existing tasks
- [ ] Can delete tasks
- [ ] Task priorities display correctly with colors
- [ ] Task tags display correctly
- [ ] Can logout successfully
- [ ] API documentation is accessible (/docs)
- [ ] Can test API endpoints via Swagger UI
- [ ] Real-time updates work (WebSocket)

## Common Issues and Solutions

### Issue 1: Port 8000 already in use
**Solution:**
```bash
# Find and kill the process using port 8000
# On Linux/Mac:
lsof -ti:8000 | xargs kill -9

# On Windows:
netstat -ano | findstr :8000
# Note the PID and then:
taskkill /PID <PID> /F
```

### Issue 2: Module not found errors
**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 3: Database errors
**Solution:**
```bash
# Remove existing database and restart
rm todoapp.db
# Or if using Docker:
docker-compose down -v
docker-compose up --build
```

### Issue 4: Can't see the login page
**Solution:**
- Make sure all HTML templates are in the `templates/` folder
- Check that static files are in the `static/` folder
- Restart the server

### Issue 5: WebSocket connection fails
**Solution:**
- Check browser console for errors
- Ensure WebSocket is not blocked by firewall
- Try accessing via localhost instead of 127.0.0.1 or vice versa

## Next Steps After Testing

Once you've verified everything works:

1. **Customize the application:**
   - Modify the dark theme colors in `static/css/variables.css`
   - Add your own logo
   - Customize the welcome message

2. **Add more features:**
   - Implement drag-and-drop for tasks
   - Add user profile pages
   - Implement task assignments
   - Add email notifications

3. **Prepare for production:**
   - Change all secret keys in `.env`
   - Set `DEBUG=False`
   - Configure PostgreSQL
   - Set up a reverse proxy (Nginx)
   - Enable HTTPS
   - Configure proper CORS origins

4. **Deploy:**
   - Use Docker Compose for deployment
   - Consider using services like:
     - DigitalOcean
     - AWS
     - Heroku
     - Render

## Getting Help

If you encounter any issues:

1. Check the main README.md file
2. Review the API documentation at /docs
3. Check the console logs in your browser (F12)
4. Check the server logs in your terminal
5. Review the error messages carefully

## Success Indicators

You know the application is working correctly when:

1. ✅ You can register and login
2. ✅ You can create and view boards
3. ✅ You can add columns to boards
4. ✅ You can create and manage tasks
5. ✅ Tasks display with correct priorities and colors
6. ✅ Real-time updates work across browser windows
7. ✅ API endpoints respond correctly in Swagger UI
8. ✅ The application looks good on mobile devices

Congratulations! You now have a fully functional Kanban board application! 🎉
