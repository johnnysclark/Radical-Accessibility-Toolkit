# announce.ps1 - Speak text via JAWS, NVDA, or SAPI fallback
# Reads text from stdin and announces it through the active screen reader
# Priority: JAWS > NVDA > SAPI (Windows built-in)

$text = [Console]::In.ReadToEnd().Trim()
if (-not $text) { exit 0 }

# Try JAWS first
$jawsSpoke = $false
try {
    $jawsDllPaths = @(
        "${env:ProgramFiles}\Freedom Scientific\JAWS\*\jfwapi.dll",
        "${env:ProgramFiles(x86)}\Freedom Scientific\JAWS\*\jfwapi.dll"
    )
    foreach ($pattern in $jawsDllPaths) {
        $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            $dllPath = $found.FullName -replace '\\', '\\\\'
            Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class JFW {
    [DllImport("$dllPath", CharSet = CharSet.Unicode)]
    public static extern bool JFWSayString(string text, bool interrupt);
}
"@ -ErrorAction Stop
            $jawsSpoke = [JFW]::JFWSayString($text, $true)
            if ($jawsSpoke) { exit 0 }
        }
    }
} catch {}

# Try NVDA
try {
    $nvdaDll = "${env:ProgramFiles(x86)}\\NVDA\\nvdaControllerClient64.dll"
    if (-not (Test-Path $nvdaDll)) {
        $nvdaDll = "${env:ProgramFiles}\\NVDA\\nvdaControllerClient64.dll"
    }
    if (Test-Path $nvdaDll) {
        $nvdaPath = $nvdaDll -replace '\\', '\\\\'
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class NVDA {
    [DllImport("$nvdaPath", CharSet = CharSet.Unicode)]
    public static extern int nvdaController_speakText(string text);
    [DllImport("$nvdaPath")]
    public static extern int nvdaController_testIfRunning();
}
"@ -ErrorAction Stop
        if ([NVDA]::nvdaController_testIfRunning() -eq 0) {
            [NVDA]::nvdaController_speakText($text)
            exit 0
        }
    }
} catch {}

# SAPI fallback
try {
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.Speak($text)
    exit 0
} catch {}
