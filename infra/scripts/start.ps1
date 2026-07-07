# Starts a previously-stopped instance back up. Gets a new public IP (not
# an Elastic IP) - re-run terraform output/apply.ps1 scripts afterward to
# pick up the new address, and note the security group's IP-restricted
# rules were pinned to whatever IP you were on at the last apply, so a
# fresh apply may be needed if your own IP changed too.
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_refresh-creds.ps1"

Push-Location "$PSScriptRoot\.."
try {
    $instanceId = terraform output -raw instance_id
} finally {
    Pop-Location
}

aws ec2 start-instances --instance-ids $instanceId
