# Todo Web Application - Phase 2

A full-stack todo application with user authentication, task management, and modern web technologies.

## Features

- **User Authentication**: Secure login/signup with JWT tokens
- **Task Management**: Create, read, update, delete, and toggle completion status
- **User Isolation**: Each user can only see and manage their own tasks
- **Filtering & Sorting**: Filter tasks by status and sort by creation date or title
- **Pagination**: Efficient loading of large task lists
- **Responsive UI**: Works on desktop and mobile devices

## Tech Stack

- **Frontend**: Next.js 14 with App Router, TypeScript, Tailwind CSS
- **Backend**: FastAPI with Python, SQLModel for ORM
- **Database**: Neon PostgreSQL
- **Authentication**: Better Auth with JWT tokens
- **Styling**: Tailwind CSS

## Prerequisites

- Node.js (v18 or higher)
- Python (v3.9 or higher)
- pip
- Git

## Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd todo-app
   ```

2. **Install backend dependencies**:
   ```bash
   cd apps/server
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**:
   ```bash
   cd ../client
   npm install
   ```

4. **Environment Variables**:

   Create `.env` files in both the server and client directories with the following variables:

   **apps/server/.env**:
   ```env
   DATABASE_URL=your_neon_postgres_connection_string
   BETTER_AUTH_SECRET=your_jwt_secret_key
   ```

   **apps/client/.env.local**:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
   ```

5. **Run the Application**:

   **Option 1: Run locally**

   Terminal 1 (Backend):
   ```bash
   cd apps/server
   uvicorn main:app --reload
   ```

   Terminal 2 (Frontend):
   ```bash
   cd apps/client
   npm run dev
   ```

   **Option 2: Run with Docker**
   ```bash
   docker-compose up --build
   ```

6. **Access the Application**:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### Tasks
- `GET /api/tasks` - Get all user tasks (with optional query params: status, sort, page, limit)
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{id}` - Get a specific task
- `PUT /api/tasks/{id}` - Update a task
- `PATCH /api/tasks/{id}/complete` - Toggle task completion status
- `DELETE /api/tasks/{id}` - Delete a task

## Environment Variables

### Backend (`apps/server/.env`)
- `DATABASE_URL`: PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Secret key for JWT token signing (min 32 characters)

### Frontend (`apps/client/.env.local`)
- `NEXT_PUBLIC_API_URL`: URL of the backend API
- `NEXT_PUBLIC_BETTER_AUTH_URL`: URL of the frontend app for auth redirects

## Project Structure

```
todo-app/
├── apps/
│   ├── client/           # Next.js frontend
│   │   ├── app/          # App Router pages
│   │   ├── components/   # Reusable components
│   │   └── lib/          # Utilities and API client
│   └── server/           # FastAPI backend
│       ├── api/          # API routes
│       ├── auth/         # Authentication logic
│       ├── models/       # Database models
│       └── database/     # Database configuration
├── specs/                # Project specifications and documentation
└── README.md
```

## Development

- **Frontend**: Run `npm run dev` in the `apps/client` directory
- **Backend**: Run `uvicorn main:app --reload` in the `apps/server` directory

## Architecture

This application follows a monorepo structure with:
- Separate frontend (Next.js) and backend (FastAPI) applications
- Shared authentication using JWT tokens
- User isolation at the API level to ensure data privacy
- Type-safe API communication between frontend and backend

## Security

- JWT-based authentication with proper token validation
- User data isolation - users can only access their own tasks
- Input validation and sanitization
- Secure session management with Better Auth"# todo-phase-2-update"
"# todo-app-phase-3-update"

## Phase 4: Local Kubernetes Deployment

This phase adds Kubernetes deployment capability using Docker, Minikube, and Helm charts.

### Prerequisites

- Docker Desktop
- Minikube
- Helm 3
- kubectl

### Setup Instructions

1. **Start Minikube**:
   ```bash
   minikube start
   ```

2. **Build Docker images**:
   ```bash
   # In the project root directory
   eval $(minikube docker-env)

   # Build client image
   docker build -t todo-client:latest ./apps/client/

   # Build server image
   docker build -t todo-server:latest ./apps/server/
   ```

3. **Install Helm charts**:
   ```bash
   # Install server chart first (with required secrets)
   helm install todo-server ./charts/todo-server \
     --set env.OPENAI_API_KEY="your_openai_api_key" \
     --set env.BETTER_AUTH_SECRET="super-secret-jwt-key-for-local-development-min-32-chars"

   # Install client chart
   helm install todo-client ./charts/todo-client
   ```

4. **Access the application**:
   ```bash
   # Get the Minikube IP
   minikube ip

   # Port forward to access the frontend service
   kubectl port-forward svc/todo-client 3000:3000
   ```

   Then access the frontend at http://localhost:3000

### Helm Chart Values

#### todo-server values:
- `env.OPENAI_API_KEY`: OpenAI API key (required)
- `env.BETTER_AUTH_SECRET`: JWT secret (required, min 32 chars)
- `env.DATABASE_URL`: Database connection string (default: SQLite)
- `replicaCount`: Number of server pods (default: 1)
- `service.port`: Service port (default: 8000)

#### todo-client values:
- `env.NEXT_PUBLIC_API_URL`: Backend API URL (default: http://todo-server:8000)
- `env.NEXT_PUBLIC_BETTER_AUTH_URL`: Auth URL (default: http://todo-client:3000)
- `replicaCount`: Number of client pods (default: 1)
- `service.port`: Service port (default: 3000)

### Uninstall

To remove the deployed applications:
```bash
helm uninstall todo-client
helm uninstall todo-server
```
"# todo-app-phase-4" 
