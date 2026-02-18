# Test script for Todo API
# Run this script to test the API endpoints

$API_URL = "http://localhost:8000"

# Test 1: Health check
Write-Host "`n=== Testing Health Check ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "$API_URL/health" -Method Get

# Test 2: Register a new user
Write-Host "`n=== Registering New User ===" -ForegroundColor Cyan
try {
    $registerBody = @{
        email = "test@example.com"
        password = "test123456"
    } | ConvertTo-Json

    $registerResponse = Invoke-RestMethod -Uri "$API_URL/api/auth/register" -Method Post -Body $registerBody -ContentType "application/json"
    Write-Host "Registration successful!" -ForegroundColor Green
    Write-Host "Token: $($registerResponse.token)"
    Write-Host "User: $($registerResponse.user.email)"
    
    # Save token for next test
    $token = $registerResponse.token
} catch {
    Write-Host "Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    # Try to login instead
    Write-Host "Trying to login..." -ForegroundColor Yellow
    try {
        $loginBody = @{
            email = "test@example.com"
            password = "test123456"
        } | ConvertTo-Json

        $loginResponse = Invoke-RestMethod -Uri "$API_URL/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
        Write-Host "Login successful!" -ForegroundColor Green
        Write-Host "Token: $($loginResponse.token)"
        $token = $loginResponse.token
    } catch {
        Write-Host "Login failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Test 3: Create a task
Write-Host "`n=== Creating a Task ===" -ForegroundColor Cyan
try {
    $taskBody = @{
        title = "Test Task from PowerShell"
        description = "This is a test task created via PowerShell script"
    } | ConvertTo-Json

    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }

    $taskResponse = Invoke-RestMethod -Uri "$API_URL/api/tasks/" -Method Post -Body $taskBody -Headers $headers
    Write-Host "Task created successfully!" -ForegroundColor Green
    Write-Host "Task ID: $($taskResponse.id)"
    Write-Host "Task Title: $($taskResponse.title)"
} catch {
    Write-Host "Task creation failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

# Test 4: Get all tasks
Write-Host "`n=== Getting All Tasks ===" -ForegroundColor Cyan
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }

    $tasks = Invoke-RestMethod -Uri "$API_URL/api/tasks/" -Method Get -Headers $headers
    Write-Host "Found $($tasks.Count) task(s)" -ForegroundColor Green
    foreach ($task in $tasks) {
        Write-Host "  - [$($task.id)] $($task.title) (Completed: $($task.completed))" -ForegroundColor Gray
    }
} catch {
    Write-Host "Failed to get tasks: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Tests Complete ===" -ForegroundColor Cyan
