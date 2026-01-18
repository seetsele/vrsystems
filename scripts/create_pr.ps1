param(
    [string]$Branch = 'feature/runner-integration',
    [string]$Base = 'main',
    [string]$Title = 'Feature: runner integration and hardening',
    [string]$Body = 'Implements runner integration, Celery worker, webhook signing, Alembic skeleton, Grafana import, and CI improvements.'
)

if (-not (Get-Command gh -ErrorAction SilentlyContinue)){
    Write-Error "gh CLI not found. Install GitHub CLI or create PR via web UI: https://github.com/<owner>/<repo>/pull/new/$Branch"
    exit 1
}

gh pr create --base $Base --head $Branch --title $Title --body $Body
