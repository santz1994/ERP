# GitHub Actions Workflow Setup Guide

## Overview
This guide explains how to set up the required GitHub repository settings for the CI/CD workflows to function properly.

## Issues Fixed
✅ **qa-testing-pipeline.yml** - Fixed `env` context variable usage in service definitions
✅ **deploy.yml** - Fixed Slack action input parameter names

## Required Repository Configuration

### 1. GitHub Environments
You must create two environments in your repository settings:

**Location:** Repository Settings → Environments

#### Staging Environment
- **Name:** `staging`
- **URL (Optional):** `https://staging.qutykarunia.com`
- **Deployment branches:** `develop`

#### Production Environment
- **Name:** `production`
- **URL:** `https://erp.qutykarunia.com`
- **Deployment branches:** `main`
- **Required reviewers (Recommended):** Add team members who should approve production deployments

### 2. Repository Secrets
Add the following secrets to your repository:

**Location:** Repository Settings → Secrets and variables → Actions

#### Staging Secrets
```
STAGING_HOST           # Staging server hostname/IP
STAGING_USER           # SSH user for staging server
STAGING_SSH_KEY        # SSH private key for staging server
```

#### Production Secrets
```
PROD_HOST              # Production server hostname/IP
PROD_USER              # SSH user for production server
PROD_SSH_KEY           # SSH private key for production server
```

#### Notification Secrets
```
SLACK_WEBHOOK          # Slack webhook URL for notifications
GITHUB_TOKEN           # (Auto-provided by GitHub Actions)
```

### 3. Setup Steps

1. **Create Environments:**
   - Go to Repository Settings
   - Click "Environments" in the left sidebar
   - Click "New environment"
   - Create `staging` and `production` environments

2. **Add Secrets:**
   - Go to Repository Settings
   - Click "Secrets and variables" → "Actions"
   - Click "New repository secret"
   - Add all required secrets listed above

3. **Configure SSH Access:**
   - Generate SSH keys for your staging and production servers
   - Add public keys to `~/.ssh/authorized_keys` on both servers
   - Store private keys as `STAGING_SSH_KEY` and `PROD_SSH_KEY` secrets

4. **Setup Slack Integration (Optional):**
   - Create a Slack App or use existing one
   - Generate an Incoming Webhook URL
   - Add as `SLACK_WEBHOOK` secret

## Workflow Triggers

### Deploy Pipeline (deploy.yml)
- **Staging:** Automatic on push to `develop` branch
- **Production:** Automatic on push to `main` branch
- **Manual:** Use GitHub Actions "Run workflow" button

### QA Testing Pipeline (qa-testing-pipeline.yml)
- **On every push** to `main` or `develop`
- **On every pull request** to `main` or `develop`
- **Daily schedule:** 2 AM UTC
- **Manual trigger:** Available via workflow dispatch

## Workflow Phases

### Deploy Workflow
1. **Phase 1: Test** - Run unit tests, coverage, and security scans
2. **Phase 2: Build** - Build Docker images
3. **Phase 3: Security Scan** - Trivy vulnerability scanning
4. **Phase 4: Deploy to Staging** - Deploy to staging environment (if develop branch)
5. **Phase 5: Deploy to Production** - Deploy to production (if main branch)
6. **Phase 6: Post-Deploy Tests** - Smoke tests and performance checks

### QA Testing Workflow
- **Python Tests** - Unit tests, integration tests, boundary value analysis
- **API Tests** - Contract testing, endpoint verification
- **E2E Tests** - Frontend testing with Playwright
- **Performance Tests** - Load testing with Locust

## Troubleshooting

### Environment Not Found Error
```
Value 'staging' is not valid
```
**Solution:** Create the environment in GitHub Settings → Environments

### Secret Not Found Error
```
Context access might be invalid: STAGING_HOST
```
**Solution:** Add the secret in GitHub Settings → Secrets and variables

### SSH Connection Failed
**Solutions:**
1. Verify SSH key is correct
2. Check server IP/hostname
3. Verify SSH user has correct permissions
4. Test SSH connection manually: `ssh -i key.pem user@host`

### Slack Notifications Not Working
**Solutions:**
1. Verify `SLACK_WEBHOOK` secret is set correctly
2. Check webhook URL format: `https://hooks.slack.com/services/...`
3. Verify Slack app has permission to post messages

## Best Practices

1. **Use branch protection rules** for `main` and `develop`
2. **Require status checks** to pass before merge
3. **Require reviews** before merging to `main`
4. **Monitor workflow runs** in Actions tab
5. **Keep secrets secure** - never commit them
6. **Test in staging first** before production deployment
7. **Review deployment logs** for any issues

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Slack API Documentation](https://api.slack.com/)
