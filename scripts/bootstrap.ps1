# Thin wrapper — all logic lives in bootstrap.py (§78 "One Core" principle).
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$PythonBin = "python"
if (Get-Command "py" -ErrorAction SilentlyContinue) {
    $PythonBin = "py"
}

& $PythonBin "$ScriptDir\bootstrap.py" @args
exit $LASTEXITCODE
