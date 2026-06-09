$ErrorActionPreference = "Continue"

$RepoRoot = "C:\Proj\lite-Mono"
$TrainPid = 6928
$RunName = "phase2_boundary_loss_b12_30ep_w005"
$RunDir = Join-Path $RepoRoot "citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/runs/$RunName"
$Weights29 = Join-Path $RunDir "models/weights_29"
$PostprocessScript = Join-Path $RepoRoot "citrus_project/milestones/04_lightweight_vegetation_improvement/Marvel/postprocess_phase2_boundary_b12_30ep_w005.ps1"
$WatcherLog = Join-Path $RunDir "watcher_postprocess.log"

function Write-WatcherLog {
  param([string]$Message)
  $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  Add-Content -LiteralPath $WatcherLog -Value "[$stamp] $Message"
}

Set-Location $RepoRoot
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

Write-WatcherLog "Watcher started for PID $TrainPid."

$proc = Get-Process -Id $TrainPid -ErrorAction SilentlyContinue
if ($null -ne $proc) {
  Write-WatcherLog "Training process is still running; waiting for it to exit."
  Wait-Process -Id $TrainPid
  Write-WatcherLog "Training process exited."
} else {
  Write-WatcherLog "Training process was already absent when watcher started."
}

if (Test-Path -LiteralPath $Weights29) {
  Write-WatcherLog "Found final checkpoint at $Weights29. Starting postprocess."
  & "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -File $PostprocessScript 2>&1 |
    Tee-Object -FilePath (Join-Path $RunDir "postprocess_console.log")
  Write-WatcherLog "Postprocess command finished with exit code $LASTEXITCODE."
} else {
  Write-WatcherLog "Final checkpoint weights_29 not found. Postprocess was not started."
}
