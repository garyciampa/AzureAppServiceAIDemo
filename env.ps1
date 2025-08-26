# env.ps1 - Load environment variables from .env into the current PowerShell process
# and expose a convenient PowerShell variable named $local_user matching LOCAL_USER
# Usage: dot-source this file in PowerShell: . .\env.ps1

$envFile = Join-Path $PSScriptRoot '.env'
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if (-not [string]::IsNullOrWhiteSpace($line) -and -not $line.TrimStart().StartsWith('#')) {
            $pair = $line -split '=', 2
            if ($pair.Length -eq 2) {
                $name = $pair[0].Trim()
                $value = $pair[1].Trim()

                # Expand PowerShell env variable syntax in the value (e.g., $env:USERNAME)
                $valueToSet = $value
                if ($value -match '^\$env:(.+)$') {
                    $envName = $matches[1]
                    $expanded = [Environment]::GetEnvironmentVariable($envName)
                    if ($null -ne $expanded) {
                        $valueToSet = $expanded
                    }
                }

                # Set as environment variable for this process
                [System.Environment]::SetEnvironmentVariable($name, $valueToSet, 'Process')
                # Also set a PowerShell variable (lowercased) for convenience: e.g., $local_user
                $psVarName = $name.ToLower().Replace('-', '_')
                Set-Variable -Name $psVarName -Value $valueToSet -Scope Global -ErrorAction SilentlyContinue
            }
        }
    }

    if ($env:LOCAL_USER) {
        Set-Variable -Name 'local_user' -Value $env:LOCAL_USER -Scope Global -ErrorAction SilentlyContinue
        Write-Host "Loaded LOCAL_USER from .env into PowerShell as `$local_user and `$env:LOCAL_USER" -ForegroundColor Green
    }
} else {
    Write-Host ".env not found at $envFile. Create .env with LOCAL_USER=<your-username>" -ForegroundColor Yellow
}
