# Connects interactively to the current instance using Terraform's own
# output, so you never have to copy/paste the IP by hand.
$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot\.."
try {
    $ip = terraform output -raw public_ip
} finally {
    Pop-Location
}

ssh -i ~/.ssh/id_ed25519 "ubuntu@$ip"
