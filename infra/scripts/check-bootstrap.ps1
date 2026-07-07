# Non-interactive sanity check: waits for cloud-init to finish, then
# confirms Node.js, Claude Code, and the TARA repo are present.
$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot\.."
try {
    $ip = terraform output -raw public_ip
} finally {
    Pop-Location
}

$remoteScript = @'
echo CONNECTED
cloud-init status --wait
echo --- node ---
which node && node --version
echo --- claude ---
which claude && claude --version
echo --- repo ---
ls -la /home/ubuntu/tara
'@

ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 -i ~/.ssh/id_ed25519 "ubuntu@$ip" $remoteScript
