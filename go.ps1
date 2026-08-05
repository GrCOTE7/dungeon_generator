Set-Location -Path "$PSScriptRoot"

# Vérifie silencieusement l'alignement des versions; message orange uniquement en cas d'écart.
& "$PSScriptRoot\scripts\check_version_sync.ps1"

$mode = if ($args.Count -gt 0) { "$($args[0])".ToLowerInvariant() } else { "" }

uv sync --extra desktop
uv run flet -V

if ($mode -eq "w") {
    Write-Host "Lancement de l'application Flet - MODE WEB"
    uv run --active python -m flet.cli run ./main.py -r --web
}
else {
    Write-Host "Lancement de l'application Flet - MODE APP"
    uv run --active python -m flet.cli run ./main.py -r
}
