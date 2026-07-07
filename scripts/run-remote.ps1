# Uploads a local audio file, runs the pipeline against it on the instance,
# and copies the resulting output wav back locally for a sanity-check listen.
param(
    [Parameter(Mandatory = $true)][string]$AudioFile
)
$ErrorActionPreference = "Stop"

if (-not (Test-Path $AudioFile)) {
    throw "Audio file not found: $AudioFile"
}

Push-Location "$PSScriptRoot\..\infra"
try {
    $ip = terraform output -raw public_ip
} finally {
    Pop-Location
}

$remoteInput = "sample_input" + [System.IO.Path]::GetExtension($AudioFile)
$sshOpts = @("-o", "StrictHostKeyChecking=accept-new", "-i", "$HOME/.ssh/id_ed25519")

scp @sshOpts $AudioFile "ubuntu@${ip}:/home/ubuntu/tara/$remoteInput"

# -t forces a pty and PYTHONUNBUFFERED avoids output being fully buffered
# until the process exits, so progress actually streams instead of going
# silent for minutes.
$remoteCmd = "export PATH=`$HOME/.local/bin:`$PATH && cd ~/tara && uv sync && PYTHONUNBUFFERED=1 uv run python -u -m pipeline.app $remoteInput sample_output.wav"
ssh -t @sshOpts "ubuntu@$ip" $remoteCmd

scp @sshOpts "ubuntu@${ip}:/home/ubuntu/tara/sample_output.wav" "$PSScriptRoot\..\sample_output.wav"
Write-Output "Output saved locally to sample_output.wav"
