# The server runs persistently on the instance as a systemd service (starts
# on boot, restarts on crash) - this script just opens the SSH tunnel to
# reach it. Leave this running while testing in a browser at
# http://localhost:8000 - Ctrl+C to stop (only closes the tunnel, server
# keeps running).
$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot\..\infra"
try {
    $ip = terraform output -raw public_ip
} finally {
    Pop-Location
}

ssh -N -L 8000:localhost:8000 -o StrictHostKeyChecking=accept-new -i ~/.ssh/id_ed25519 "ubuntu@$ip"
