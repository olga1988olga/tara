# Pass flags space-separated, e.g. -var-file cpu.tfvars - NOT -var-file=cpu.tfvars.
# PowerShell mis-splits the "=" form when forwarding args to a native exe,
# which surfaces as a confusing "Too many command line arguments" from terraform.
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_refresh-creds.ps1"

Push-Location "$PSScriptRoot\.."
try {
    terraform plan @args
} finally {
    Pop-Location
}
