# Setup Script for Law Platform Backend

Write-Host "🚀 Setting up Law Platform Backend..." -ForegroundColor Cyan

# Check if Python is installed
Write-Host "`n1️⃣ Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+ first." -ForegroundColor Red
    exit 1
}

# Check if PostgreSQL is running
Write-Host "`n2️⃣ Checking PostgreSQL..." -ForegroundColor Yellow
Write-Host "⚠️  Make sure PostgreSQL is installed and running." -ForegroundColor Yellow
Write-Host "   Database: law_platform" -ForegroundColor Gray
Write-Host "   User: postgres" -ForegroundColor Gray
Write-Host "   Password: (check your .env file)" -ForegroundColor Gray

# Create virtual environment if it doesn't exist
if (-Not (Test-Path "venv")) {
    Write-Host "`n3️⃣ Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "`n3️⃣ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`n4️⃣ Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  If you see an execution policy error, run:" -ForegroundColor Yellow
    Write-Host "   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Gray
    exit 1
}
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host "`n5️⃣ Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Generate Prisma Client
Write-Host "`n6️⃣ Generating Prisma Client..." -ForegroundColor Yellow
prisma generate
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Prisma Client generated" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to generate Prisma Client" -ForegroundColor Red
    exit 1
}

# Push database schema
Write-Host "`n7️⃣ Creating database tables..." -ForegroundColor Yellow
Write-Host "⚠️  This will create tables in your database." -ForegroundColor Yellow
$confirm = Read-Host "Continue? (y/n)"
if ($confirm -eq "y" -or $confirm -eq "Y") {
    prisma db push
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database tables created" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create database tables" -ForegroundColor Red
        Write-Host "   Make sure PostgreSQL is running and DATABASE_URL in .env is correct" -ForegroundColor Gray
    }
} else {
    Write-Host "⏭️  Skipped database creation" -ForegroundColor Yellow
}

# Done
Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`n🚀 To start the server, run:" -ForegroundColor Cyan
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "`n📚 API Documentation will be available at:" -ForegroundColor Cyan
Write-Host "   http://localhost:8000/docs" -ForegroundColor White
