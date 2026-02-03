# Test creating and deleting tasks via API

$BASE_URL = "http://127.0.0.1:8000"

# Login
Write-Host "🔐 Logging in..." -ForegroundColor Cyan
$loginBody = @{
    username = "Admin"
    password = "admin123"
} | ConvertTo-Json

$loginResponse = Invoke-WebRequest -Uri "$BASE_URL/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginBody

$loginData = $loginResponse.Content | ConvertFrom-Json
$token = $loginData.access_token
Write-Host "✅ Logged in successfully" -ForegroundColor Green

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json"
}

# Get boards
Write-Host "📋 Fetching boards..." -ForegroundColor Cyan
$boardsResponse = Invoke-WebRequest -Uri "$BASE_URL/api/v1/boards" `
    -Method GET `
    -Headers $headers

$boards = $boardsResponse.Content | ConvertFrom-Json
$boardId = $boards[0].id
$boardName = $boards[0].name
Write-Host "✅ Found board: $boardName" -ForegroundColor Green

# Get columns
Write-Host "📊 Fetching columns..." -ForegroundColor Cyan
$columnsResponse = Invoke-WebRequest -Uri "$BASE_URL/api/v1/columns?board_id=$boardId" `
    -Method GET `
    -Headers $headers

$columns = $columnsResponse.Content | ConvertFrom-Json
$columnId = $columns[0].id
Write-Host "✅ Found column: $($columns[0].name)" -ForegroundColor Green

# Create task
Write-Host "`n📝 Creating task..." -ForegroundColor Cyan
$taskBody = @{
    title       = "Test Notification Task $(Get-Random)"
    description = "Testing telegram notifications for create/delete"
    board_id    = $boardId
    column_id   = $columnId
    priority    = "HIGH"
    due_date    = "2026-02-10T00:00:00"
} | ConvertTo-Json

$taskResponse = Invoke-WebRequest -Uri "$BASE_URL/api/v1/tasks" `
    -Method POST `
    -Headers $headers `
    -Body $taskBody

$task = $taskResponse.Content | ConvertFrom-Json
$taskId = $task.id
Write-Host "✅ Task created: $($task.title) (ID: $taskId)" -ForegroundColor Green

Write-Host "⏳ Waiting for notification processing..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Delete task
Write-Host "`n🗑️ Deleting task..." -ForegroundColor Cyan
$deleteResponse = Invoke-WebRequest -Uri "$BASE_URL/api/v1/tasks/$taskId" `
    -Method DELETE `
    -Headers $headers

Write-Host "✅ Task deleted successfully" -ForegroundColor Green

Write-Host "⏳ Waiting for notification processing..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

Write-Host "`n✅ Test completed! Check the server terminal for notification logs." -ForegroundColor Green
