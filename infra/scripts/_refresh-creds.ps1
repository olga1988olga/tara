# Dot-sourced by the other scripts in this folder - exports fresh short-lived
# credentials from the current `aws login` session into env vars for
# Terraform to pick up. Re-run `aws login` yourself first if this fails
# (the underlying browser session lasts up to 12h).
$creds = aws configure export-credentials --profile default --format process | ConvertFrom-Json
$env:AWS_ACCESS_KEY_ID = $creds.AccessKeyId
$env:AWS_SECRET_ACCESS_KEY = $creds.SecretAccessKey
$env:AWS_SESSION_TOKEN = $creds.SessionToken
