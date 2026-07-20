param(
    [string]$Ref = $env:FEIBI_JIUBI_REF,
    [string]$SourceRoot = ""
)

$ErrorActionPreference = "Stop"
$Repository = "KanadeK/feibi-jiubi-codex-pet"
$PetId = "feibi-jiubi"

if ([string]::IsNullOrWhiteSpace($Ref)) {
    $Ref = "main"
}

$codexRoot = if ([string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
    Join-Path $env:USERPROFILE ".codex"
} else {
    $env:CODEX_HOME
}

$petsRoot = Join-Path $codexRoot "pets"
$target = Join-Path $petsRoot $PetId
$backupRoot = Join-Path $codexRoot "pet-backups"
$stage = Join-Path ([System.IO.Path]::GetTempPath()) ("feibi-jiubi-" + [guid]::NewGuid().ToString("N"))
$backupPath = $null

function Assert-Checksum {
    param(
        [string]$FilePath,
        [string]$RelativePath,
        [string[]]$ChecksumLines
    )

    $escaped = [regex]::Escape($RelativePath)
    $line = $ChecksumLines | Where-Object { $_ -match "^[a-fA-F0-9]{64}\s+$escaped$" } | Select-Object -First 1
    if ($null -eq $line) {
        throw "Missing checksum for $RelativePath"
    }

    $expected = ($line -split "\s+")[0].ToLowerInvariant()
    $actual = (Get-FileHash -LiteralPath $FilePath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $expected) {
        throw "Checksum mismatch for $RelativePath"
    }
}

try {
    New-Item -ItemType Directory -Force -Path $stage | Out-Null
    $stagePetJson = Join-Path $stage "pet.json"
    $stageSpritesheet = Join-Path $stage "spritesheet.webp"
    $stageChecksums = Join-Path $stage "checksums.txt"

    if ([string]::IsNullOrWhiteSpace($SourceRoot)) {
        $rawRoot = "https://raw.githubusercontent.com/$Repository/$Ref"
        Invoke-WebRequest -UseBasicParsing "$rawRoot/pet/pet.json" -OutFile $stagePetJson
        Invoke-WebRequest -UseBasicParsing "$rawRoot/pet/spritesheet.webp" -OutFile $stageSpritesheet
        Invoke-WebRequest -UseBasicParsing "$rawRoot/checksums.txt" -OutFile $stageChecksums
    } else {
        $resolvedSource = (Resolve-Path -LiteralPath $SourceRoot).Path
        Copy-Item -LiteralPath (Join-Path $resolvedSource "pet/pet.json") -Destination $stagePetJson
        Copy-Item -LiteralPath (Join-Path $resolvedSource "pet/spritesheet.webp") -Destination $stageSpritesheet
        Copy-Item -LiteralPath (Join-Path $resolvedSource "checksums.txt") -Destination $stageChecksums
    }

    $checksumLines = Get-Content -LiteralPath $stageChecksums
    Assert-Checksum -FilePath $stagePetJson -RelativePath "pet/pet.json" -ChecksumLines $checksumLines
    Assert-Checksum -FilePath $stageSpritesheet -RelativePath "pet/spritesheet.webp" -ChecksumLines $checksumLines

    New-Item -ItemType Directory -Force -Path $petsRoot | Out-Null
    if (Test-Path -LiteralPath $target) {
        New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $backupPath = Join-Path $backupRoot "$PetId-$timestamp"
        Move-Item -LiteralPath $target -Destination $backupPath
    }

    New-Item -ItemType Directory -Force -Path $target | Out-Null
    Copy-Item -LiteralPath $stagePetJson -Destination (Join-Path $target "pet.json")
    Copy-Item -LiteralPath $stageSpritesheet -Destination (Join-Path $target "spritesheet.webp")

    Write-Host "Installed 菲比啾比 to $target"
    if ($null -ne $backupPath) {
        Write-Host "Previous pet backup: $backupPath"
    }
    Write-Host "Open Settings > Pets, choose Refresh, then select 菲比啾比."
} catch {
    if ($null -ne $backupPath -and -not (Test-Path -LiteralPath $target) -and (Test-Path -LiteralPath $backupPath)) {
        Move-Item -LiteralPath $backupPath -Destination $target
    }
    throw
} finally {
    if (Test-Path -LiteralPath $stage) {
        Remove-Item -LiteralPath $stage -Recurse -Force
    }
}
