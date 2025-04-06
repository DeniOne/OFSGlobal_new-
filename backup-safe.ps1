# Create timestamp for backup name
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

# Define backup directories
$backupDir = "backups"
$tempDir = "temp_$timestamp"
$configDir = "$tempDir\_configs_and_db"

# Create required directories
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
New-Item -ItemType Directory -Force -Path $configDir | Out-Null

Write-Host "Copying important files..."

# Copy configs and databases
Get-ChildItem -Path "." -Recurse -File | Where-Object {
    $_.Extension -in ".db",".env",".ini",".json",".conf"
} | ForEach-Object {
    try {
        $destPath = Join-Path $configDir $_.Name
        Copy-Item $_.FullName -Destination $destPath -Force -ErrorAction SilentlyContinue
        Write-Host "Copied file: $($_.Name)"
    } catch {
        Write-Host "Failed to copy: $($_.Name)"
    }
}

Write-Host "Copying project files..."

# Copy all other project files
Get-ChildItem -Path "." -Exclude @("node_modules",".git","venv","backups",$tempDir) | ForEach-Object {
    try {
        Copy-Item $_.FullName -Destination $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    } catch {
        Write-Host "Failed to copy: $($_.FullName)"
    }
}

# Create ZIP archive
$backupFile = Join-Path $backupDir "backup_$timestamp.zip"
Compress-Archive -Path $tempDir\* -DestinationPath $backupFile -Force

# Cleanup temp directory
Remove-Item -Path $tempDir -Recurse -Force

Write-Host "Backup successfully created: $backupFile" 