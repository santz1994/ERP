# GitHub Environments and Secrets Setup Script
param([string]$Owner = "santz1994", [string]$Repo = "ERP")

# Check GitHub CLI
$ghPath = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghPath) {
    Write-Host "ERROR: GitHub CLI not found" -ForegroundColor Red
    exit 1
}

Write-Host "OK: GitHub CLI is installed" -ForegroundColor Green

# Verify authentication
try {
    & gh auth status 2>&1 | Out-Null
    Write-Host "OK: GitHub CLI authenticated" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Not authenticated" -ForegroundColor Red
    exit 1
}

# Create environments
Write-Host "Creating environments..." -ForegroundColor Cyan
& gh api repos/$Owner/$Repo/environments/staging --method PUT 2>&1 | Out-Null
Write-Host "OK: Staging environment created" -ForegroundColor Green

& gh api repos/$Owner/$Repo/environments/production --method PUT 2>&1 | Out-Null
Write-Host "OK: Production environment created" -ForegroundColor Green

# Collect secrets
Write-Host ""
Write-Host "====== STAGING CONFIGURATION ======" -ForegroundColor Cyan
$stagingHost = Read-Host "STAGING_HOST (IP or hostname)"
$stagingUser = Read-Host "STAGING_USER (SSH username)"
$stagingSshKeyPath = Read-Host "STAGING_SSH_KEY (path to private key file)"

if (-not (Test-Path $stagingSshKeyPath)) {
    Write-Host "ERROR: File not found: $stagingSshKeyPath" -ForegroundColor Red
    exit 1
}

$stagingSshKey = Get-Content $stagingSshKeyPath -Raw

Write-Host ""
Write-Host "====== PRODUCTION CONFIGURATION ======" -ForegroundColor Cyan
$prodHost = Read-Host "PROD_HOST (IP or hostname)"
$prodUser = Read-Host "PROD_USER (SSH username)"
$prodSshKeyPath = Read-Host "PROD_SSH_KEY (path to private key file)"

if (-not (Test-Path $prodSshKeyPath)) {
    Write-Host "ERROR: File not found: $prodSshKeyPath" -ForegroundColor Red
    exit 1
}

$prodSshKey = Get-Content $prodSshKeyPath -Raw

Write-Host ""
Write-Host "====== SLACK (OPTIONAL) ======" -ForegroundColor Cyan
$slackWebhook = Read-Host "SLACK_WEBHOOK URL (press Enter to skip)"

# Create secrets
Write-Host ""
Write-Host "Creating secrets..." -ForegroundColor Cyan

$stagingHost | & gh secret set STAGING_HOST --repo "$Owner/$Repo"
Write-Host "OK: STAGING_HOST" -ForegroundColor Green

$stagingUser | & gh secret set STAGING_USER --repo "$Owner/$Repo"
Write-Host "OK: STAGING_USER" -ForegroundColor Green

$stagingSshKey | & gh secret set STAGING_SSH_KEY --repo "$Owner/$Repo"
Write-Host "OK: STAGING_SSH_KEY" -ForegroundColor Green

$prodHost | & gh secret set PROD_HOST --repo "$Owner/$Repo"
Write-Host "OK: PROD_HOST" -ForegroundColor Green

$prodUser | & gh secret set PROD_USER --repo "$Owner/$Repo"
Write-Host "OK: PROD_USER" -ForegroundColor Green

$prodSshKey | & gh secret set PROD_SSH_KEY --repo "$Owner/$Repo"
Write-Host "OK: PROD_SSH_KEY" -ForegroundColor Green

if (-not [string]::IsNullOrWhiteSpace($slackWebhook)) {
    $slackWebhook | & gh secret set SLACK_WEBHOOK --repo "$Owner/$Repo"
    Write-Host "OK: SLACK_WEBHOOK" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "====== SETUP COMPLETE ======" -ForegroundColor Green
Write-Host "Environments: staging, production" -ForegroundColor Green
Write-Host "Secrets configured successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next: https://github.com/$Owner/$Repo/settings/secrets/actions" -ForegroundColor Cyan
