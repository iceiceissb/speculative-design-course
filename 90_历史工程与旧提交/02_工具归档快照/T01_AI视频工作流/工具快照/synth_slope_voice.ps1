$ErrorActionPreference = 'Stop'
$voiceFolder = $env:SLOPE_VOICE_OUT
if (-not $voiceFolder) { throw 'SLOPE_VOICE_OUT is required' }
$dialogueLines = Get-Content -LiteralPath (Join-Path $voiceFolder 'lines.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$speaker = New-Object -ComObject SAPI.SpVoice
$token = $speaker.GetVoices() | Where-Object { $_.GetDescription() -match 'Huihui' } | Select-Object -First 1
if (-not $token) { throw 'No installed Huihui Chinese offline voice' }
$speaker.Voice = $token
$speaker.Rate = -1
$speaker.Volume = 100
foreach ($line in $dialogueLines) {
    $wavePath = Join-Path $voiceFolder ($line.id + '_local.wav')
    $stream = New-Object -ComObject SAPI.SpFileStream
    try {
        $stream.Open($wavePath, 3, $false)
        $speaker.AudioOutputStream = $stream
        $null = $speaker.Speak([string]$line.text, 0)
    } finally {
        $stream.Close()
    }
}
@{name = $token.GetDescription(); backend = 'Windows SAPI (offline)'; rate = -1} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $voiceFolder 'local-voice.json') -Encoding UTF8
