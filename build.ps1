param(
    [string]$Python = "python",
    [string]$Name = "caps-ctrl-space",
    [switch]$InstallPyInstaller
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

function Remove-BuildArtifact {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    try {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
    catch {
        throw "Unable to remove '$Path'. Close any running '$Name.exe' process or tray instance, then try again. Original error: $($_.Exception.Message)"
    }
}

if ($InstallPyInstaller) {
    Write-Host "Installing PyInstaller..."
    & $Python -m pip install pyinstaller
}

Write-Host "Using Python:"
& $Python -c "import sys; print(sys.executable)"

Write-Host "Checking PyInstaller..."
& $Python -c "import PyInstaller; print(PyInstaller.__version__)"

$buildPath = Join-Path $projectRoot "build"
$distPath = Join-Path $projectRoot "dist"
$specPath = Join-Path $projectRoot "$Name.spec"
$rootExePath = Join-Path $projectRoot "$Name.exe"
$mainPngPath = Join-Path $projectRoot "icons\main.png"
$tempIcoPath = Join-Path $projectRoot "build\$Name.ico"

Write-Host "Cleaning previous build artifacts..."
Remove-BuildArtifact -Path $buildPath
Remove-BuildArtifact -Path $distPath
Remove-BuildArtifact -Path $specPath
Remove-BuildArtifact -Path $rootExePath

if (-not (Test-Path -LiteralPath $mainPngPath)) {
    throw "Main icon not found: $mainPngPath"
}

New-Item -ItemType Directory -Path $buildPath -Force | Out-Null

Write-Host "Generating Windows icon from icons\main.png..."
& $Python -c "from PIL import Image; img = Image.open(r'$mainPngPath'); img.save(r'$tempIcoPath', format='ICO', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"

if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $tempIcoPath)) {
    throw "Failed to generate icon file: $tempIcoPath"
}

$pyInstallerArgs = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name", $Name,
    "--icon", $tempIcoPath,
    "--uac-admin",
    "--add-data", "icons;icons",
    "--exclude-module", "numpy",
    "--exclude-module", "matplotlib",
    "--exclude-module", "pandas",
    "--exclude-module", "scipy",
    "app.py"
)

Write-Host "Building $Name.exe with administrator elevation..."
& $Python @pyInstallerArgs

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed."
}

$distExePath = Join-Path $projectRoot "dist\$Name.exe"
if (-not (Test-Path $distExePath)) {
    throw "Build completed but executable was not found: $distExePath"
}

Copy-Item -LiteralPath $distExePath -Destination $rootExePath -Force

Remove-BuildArtifact -Path $buildPath
Remove-BuildArtifact -Path $distPath
Remove-BuildArtifact -Path $specPath

Write-Host ""
Write-Host "Build completed successfully."
Write-Host "Output: $rootExePath"
Write-Host "This executable will request administrator privileges on startup."
