$ErrorActionPreference = "Stop"

Write-Host "--- AWS Lambda Deployment Script ---" -ForegroundColor Cyan

# Check for AWS CLI
if (-not (Get-Command "aws" -ErrorAction SilentlyContinue)) {
    Write-Error "AWS CLI is not installed or not in PATH."
    exit 1
}

# Check for Docker
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed or not in PATH."
    exit 1
}

# Get AWS Account ID
try {
    $callerIdentity = aws sts get-caller-identity --output json | ConvertFrom-Json
    $accountId = $callerIdentity.Account
    Write-Host "Detected AWS Account ID: $accountId" -ForegroundColor Green
} catch {
    Write-Error "Failed to get AWS Account ID. Please run 'aws configure' first."
    exit 1
}

$region = "ap-south-1" # Default to Mumbai as requested (IST constraints)
$repoName = "market-monitor"
$imageUri = "$accountId.dkr.ecr.$region.amazonaws.com/$repoName"

# 1. Login to ECR
Write-Host "`n1. Logging in to ECR..." -ForegroundColor Yellow
aws ecr get-login-password --region $region | docker login --username AWS --password-stdin "$accountId.dkr.ecr.$region.amazonaws.com"

# 2. Create Repository (if not exists)
Write-Host "`n2. Checking/Creating ECR Repository..." -ForegroundColor Yellow
try {
    aws ecr describe-repositories --repository-names $repoName --region $region > $null 2>&1
    Write-Host "Repository '$repoName' already exists."
} catch {
    Write-Host "Creating repository '$repoName'..."
    aws ecr create-repository --repository-name $repoName --region $region
}

# 3. Build Docker Image
Write-Host "`n3. Building Docker Image..." -ForegroundColor Yellow
docker build -t $repoName .

# 4. Tag Image
Write-Host "`n4. Tagging Image..." -ForegroundColor Yellow
docker tag "$repoName`:latest" "$imageUri`:latest"

# 5. Push Image
Write-Host "`n5. Pushing Image to ECR..." -ForegroundColor Yellow
docker push "$imageUri`:latest"

Write-Host "`n-------------------------------------------------------" -ForegroundColor Green
Write-Host "Deployment to ECR Complete!" -ForegroundColor Green
Write-Host "Image URI: $imageUri`:latest" -ForegroundColor Cyan
Write-Host "`nNext Steps:"
Write-Host "1. Go to AWS Lambda Console -> Create Function -> Container Image"
Write-Host "2. Select the Image URI above."
Write-Host "3. Set Environment Variables (DATABASE_URL, TELEGRAM_BOT_TOKEN, etc.)"
Write-Host "-------------------------------------------------------"
