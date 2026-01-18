Param(
    [string]$branch = "feat/local-endpoints",
    [string]$base = "main",
    [string]$title = "Feature: runner integration and hardening",
    [string]$body = "Implements runner integration, Celery worker, webhook signing, Alembic skeleton, Grafana import, and CI improvements."
)

$owner = "seetsele"
$repo = "vrsystems"
$url = "https://github.com/$owner/$repo/pull/new/$branch?base=$base&title=$(uricomponent $title)&body=$(uricomponent $body)"

function uricomponent([string]$s) {
    return [uri]::EscapeDataString($s)
}

Write-Output "gh CLI not found. Open this URL to create the PR in your browser:"
Write-Output $url
Start-Process $url
