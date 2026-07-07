# Copies source code to the running instance over SSH (scp) - not git.
# Skips anything that doesn't exist locally yet, so this works even before
# all pipeline modules exist. Never touches .venv/.git/infra on either end.
$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot\..\infra"
try {
    $ip = terraform output -raw public_ip
} finally {
    Pop-Location
}

$repoRoot = "$PSScriptRoot\.."
$items = @("asr", "translation", "tts", "pipeline", "main.py", "pyproject.toml", ".python-version")

foreach ($item in $items) {
    $localPath = Join-Path $repoRoot $item
    if (Test-Path $localPath) {
        Write-Output "Syncing $item..."
        scp -r -o StrictHostKeyChecking=accept-new -i ~/.ssh/id_ed25519 $localPath "ubuntu@${ip}:/home/ubuntu/tara/"
    }
}
