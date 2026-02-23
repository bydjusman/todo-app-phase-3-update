# Test Backend API
Write-Host "Testing Backend API..." -ForegroundColor Cyan
Write-Host ""

$API_URL = "http://localhost:8000"

# Test 1: Health Check
Write-Host "1. Testing Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_URL/health" -Method Get
    Write-Host "[OK] Health check passed: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Health check failed: $_" -ForegroundColor Red
    Write-Host "Make sure backend is running on port 8000" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Register User
Write-Host "2. Testing User Registration..." -ForegroundColor Yellow
$registerData = @{
    email = "test@example.com"
    password = "test123456"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/auth/register" -Method Post -Body $registerData -ContentType "application/json"
    Write-Host "[OK] User registered successfully" -ForegroundColor Green
    $token = $response.token
    Write-Host "Token: $($token.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "[INFO] User already exists, trying login..." -ForegroundColor Yellow
        
        # Test 3: Login User
        Write-Host ""
        Write-Host "3. Testing User Login..." -ForegroundColor Yellow
        try {
            $response = Invoke-RestMethod -Uri "$API_URL/api/auth/login" -Method Post -Body $registerData -ContentType "application/json"
            Write-Host "[OK] User logged in successfully" -ForegroundColor Green
            $token = $response.token
            Write-Host "Token: $($token.Substring(0, 20))..." -ForegroundColor Gray
        } catch {
            Write-Host "[ERROR] Login failed: $_" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[ERROR] Registration failed: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Test 4: Create Task
Write-Host "4. Testing Task Creation..." -ForegroundColor Yellow
$taskData = @{
    title = "Test Task"
    description = "This is a test task"
    completed = $false
} | ConvertTo-Json

try {
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    # Use trailing slash to avoid redirect losing Authorization header
    $response = Invoke-RestMethod -Uri "$API_URL/api/tasks/" -Method Post -Body $taskData -Headers $headers
    Write-Host "[OK] Task created successfully" -ForegroundColor Green
    Write-Host "Task ID: $($response.id)" -ForegroundColor Gray
    $taskId = $response.id
} catch {
    Write-Host "[ERROR] Task creation failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 5: Get Tasks
Write-Host "5. Testing Get Tasks..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    # Use trailing slash to avoid redirect losing Authorization header
    $response = Invoke-RestMethod -Uri "$API_URL/api/tasks/" -Method Get -Headers $headers
    Write-Host "[OK] Tasks retrieved successfully" -ForegroundColor Green
    Write-Host "Total tasks: $($response.Count)" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] Get tasks failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "All tests passed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend is working correctly!" -ForegroundColor Cyan
Write-Host "You can now use the frontend at http://localhost:3000" -ForegroundColor Cyan
