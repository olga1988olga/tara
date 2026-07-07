# Stops the instance (compute billing pauses) without destroying it -
# the EBS volume, IP allocation logic, and all installed software persist.
# Public IP will change on next start (not an Elastic IP).
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_refresh-creds.ps1"

Push-Location "$PSScriptRoot\.."
try {
    $instanceId = terraform output -raw instance_id
} finally {
    Pop-Location
}

aws ec2 stop-instances --instance-ids $instanceId
