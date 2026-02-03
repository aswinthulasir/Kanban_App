# TodoKanban - Full-Stack Kanban Board Application

A modern, production-ready TODO application with Kanban board functionality built with FastAPI and vanilla JavaScript. Features real-time collaboration via WebSockets, user authentication, and a responsive dark-themed interface.

## Features

- ✅ **User Authentication** - Secure JWT-based authentication with registration and login
- ✅ **Kanban Boards** - Create multiple boards with customizable columns
- ✅ **Task Management** - Full CRUD operations for tasks with priorities, due dates, and tags
- ✅ **Real-time Collaboration** - WebSocket support for live updates across users
- ✅ **Comments & Attachments** - Add comments and file attachments to tasks
- ✅ **Search & Filter** - Search tasks by title or description
- ✅ **Responsive Design** - Mobile-first design that works on all devices
- ✅ **Dark Theme** - Beautiful dark theme throughout the application
- ✅ **Docker Support** - Easy deployment with Docker and Docker Compose
- ✅ **API Documentation** - Auto-generated Swagger/ReDoc documentation

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM with async support
- **SQLite** - Default database (PostgreSQL ready for production)
- **JWT** - Secure token-based authentication
- **WebSockets** - Real-time updates
- **Pydantic** - Data validation

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **HTML5/CSS3** - Semantic markup and modern CSS
- **WebSocket API** - Real-time communication
- **Fetch API** - Async HTTP requests

## Quick Start

### Option 1: Docker (Recommended)

1. **Clone and navigate to the directory**
   ```bash
   cd todo-kanban-app
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Application: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Alternative API Docs: http://localhost:8000/redoc

### Option 2: Local Development

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and set your own secret keys
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application**
   - Application: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Testing the Application

### 1. Register a New Account
1. Navigate to http://localhost:8000
2. Click "Sign up" or go to http://localhost:8000/register
3. Fill in the registration form:
   - Username: your_username
   - Email: your@email.com
   - Full Name: Your Name (optional)
   - Password: secure_password
4. Click "Create Account"

### 2. Login
1. You'll be redirected to the login page
2. Enter your username and password
3. Click "Sign In"

### 3. Create Your First Board
1. After login, you'll see the dashboard
2. Click "+ Create Board"
3. Enter board details:
   - Board Name: "My Project"
   - Description: "Project management board"
   - Check "Make this board public" if you want others to see it
4. Click "Create Board"

### 4. Add Columns to Your Board
1. Click on your newly created board
2. Click "+ Add Column"
3. Create columns like:
   - "To Do"
   - "In Progress"
   - "Review"
   - "Done"
4. Repeat for each column you need

### 5. Create Tasks
1. In any column, click "+ Add Task"
2. Fill in task details:
   - Title: "Implement authentication"
   - Description: "Add JWT-based authentication"
   - Priority: High
   - Due Date: Select a date
   - Tags: "backend, security"
3. Click "Save Task"

### 6. Manage Tasks
- **View Task**: Click on any task card to see details
- **Edit Task**: Click on a task to open the edit modal
- **Delete Task**: Open task modal and click "Delete"
- **Change Priority**: Edit task and select different priority
- **Add Tags**: Add comma-separated tags when editing

### 7. Test Real-time Features (Optional)
1. Open the board in two different browser windows/tabs
2. Create or move a task in one window
3. Watch it update in real-time in the other window

## API Testing

### Using the Swagger UI
1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. First, use the `/api/v1/auth/register` endpoint to create an account
4. Then use `/api/v1/auth/login` to get an access token
5. Copy the `access_token` from the response
6. Click "Authorize" again and paste the token in the format: `Bearer your_token_here`
7. Now you can test all protected endpoints

### Example API Calls with curl

**Register a user:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword123"
```

**Create a board (replace TOKEN with your access token):**
```bash
curl -X POST "http://localhost:8000/api/v1/boards/" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Board",
    "description": "A test board",
    "is_public": false
  }'
```

**Get all boards:**
```bash
curl -X GET "http://localhost:8000/api/v1/boards/" \
  -H "Authorization: Bearer TOKEN"
```

## Project Structure

```
todo-kanban-app/
├── app/
│   ├── api/              # API routes
│   │   └── v1/          # API version 1
│   ├── core/            # Core functionality (security, config)
│   ├── crud/            # Database CRUD operations
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── websockets/      # WebSocket handlers
│   ├── database.py      # Database configuration
│   └── main.py          # FastAPI app entry point
├── static/              # Static files (CSS, JS)
│   ├── css/
│   └── js/
├── templates/           # HTML templates
├── uploads/             # File uploads directory
├── .env                 # Environment variables
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile           # Docker image definition
└── requirements.txt     # Python dependencies
```

## Environment Variables

Key environment variables (see `.env.example` for all):

```env
# Application
DEBUG=True
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database
DATABASE_URL=sqlite+aiosqlite:///./todoapp.db

# CORS
ALLOWED_ORIGINS=http://localhost:8000
```

## Database Migration to PostgreSQL

To switch from SQLite to PostgreSQL:

1. **Update docker-compose.yml:**
   - Uncomment the PostgreSQL service
   - Uncomment the volumes section

2. **Update .env:**
   ```env
   DATABASE_URL=postgresql+asyncpg://todoapp:password@db:5432/todoapp
   ```

3. **Restart containers:**
   ```bash
   docker-compose down
   docker-compose up --build
   ```

## Development

### Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Run tests:
```bash
pytest
pytest --cov=app tests/
```

### Code formatting:
```bash
black app/
```

### Linting:
```bash
flake8 app/
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token

### Users
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user

### Boards
- `GET /api/v1/boards/` - List all boards
- `POST /api/v1/boards/` - Create board
- `GET /api/v1/boards/{id}` - Get board details
- `PUT /api/v1/boards/{id}` - Update board
- `DELETE /api/v1/boards/{id}` - Delete board

### Columns
- `GET /api/v1/columns/board/{board_id}` - Get board columns
- `POST /api/v1/columns/` - Create column
- `PUT /api/v1/columns/{id}` - Update column
- `DELETE /api/v1/columns/{id}` - Delete column

### Tasks
- `GET /api/v1/tasks/` - List tasks
- `POST /api/v1/tasks/` - Create task
- `GET /api/v1/tasks/{id}` - Get task details
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `GET /api/v1/tasks/search?q=query` - Search tasks

### Comments
- `GET /api/v1/comments/task/{task_id}` - Get task comments
- `POST /api/v1/comments/` - Create comment
- `PUT /api/v1/comments/{id}` - Update comment
- `DELETE /api/v1/comments/{id}` - Delete comment

### WebSocket
- `WS /ws/board/{board_id}` - Real-time board updates

## Troubleshooting

### Port already in use
```bash
# Stop any process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Database issues
```bash
# Remove database and start fresh
rm todoapp.db
# Restart the application
```

### Docker issues
```bash
# Clean up Docker
docker-compose down -v
docker-compose up --build
```

## Security Notes

- Change `SECRET_KEY` and `JWT_SECRET_KEY` in production
- Use strong passwords
- Enable HTTPS in production
- Configure proper CORS origins
- Set `DEBUG=False` in production

## License

MIT License - feel free to use this project for learning or production purposes.

## Support

For issues or questions:
1. Check the API documentation at http://localhost:8000/docs
2. Review the code comments
3. Check the troubleshooting section above

## Roadmap

Future enhancements:
- [ ] Task assignments and notifications
- [ ] Email notifications
- [ ] Task history and activity log
- [ ] Advanced search and filtering
- [ ] Board templates
- [ ] Export boards to PDF/CSV
- [ ] Mobile apps (iOS/Android)
- [ ] Third-party integrations (Slack, GitHub, etc.)
