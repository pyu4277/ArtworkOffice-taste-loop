# Windows PC 환경 점검 (ArtworkOffice-taste-loop 스킬 1절 ③). 아무것도 설치하지 않고 표만 출력한다.
# 사용법 (레포 폴더에서):  powershell -ExecutionPolicy Bypass -File .claude\skills\ArtworkOffice-taste-loop\scripts\check_env.ps1  (플러그인으로 설치했으면 그 폴더의 scripts\check_env.ps1)
# 출력 전체를 복사해 Claude 대화에 붙여 넣으면 계획 문서의 환경 표에 기록한다.
# Windows PowerShell 5.1 에서 한글이 깨지지 않도록 이 파일은 UTF-8 BOM 으로 저장한다.

$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Test-Command([string]$Name) { [bool](Get-Command $Name -ErrorAction SilentlyContinue) }
function Get-Ver([string]$Name) {
    try { $v = (& $Name --version 2>&1 | Select-Object -First 1); if ($v) { return ([string]$v).Substring(0, [Math]::Min(40, ([string]$v).Length)) } } catch {}
    return ''
}

$tools = @(
    @{ cmd = 'python'; use = '스킬 스크립트 (python3 대신 python 또는 py)'; level = 'required' },
    @{ cmd = 'git';    use = '커밋·push';                      level = 'required' },
    @{ cmd = 'node';   use = 'jsdom 검증·kordoc·템플릿 빌드';   level = 'required' },
    @{ cmd = 'npx';    use = 'kordoc 실행(npx -y kordoc)';      level = 'required' },
    @{ cmd = 'ieumoffice'; use = '문서 편집·변환';              level = 'optional' },
    @{ cmd = 'ffmpeg'; use = '영상 처리·단일 파일 압축';         level = 'optional' },
    @{ cmd = 'ego-browser'; use = '브라우저 화면 검수 (규칙 3.1)'; level = 'required' },
    @{ cmd = 'claude'; use = 'Claude Code';                    level = 'required' },
    @{ cmd = 'codex';  use = 'Codex 에이전트';                  level = 'agent' },
    @{ cmd = 'agy';    use = 'Antigravity CLI';                 level = 'agent' },
    @{ cmd = 'gemini'; use = 'Gemini CLI';                      level = 'agent' },
    @{ cmd = 'higgsfield'; use = 'Higgsfield CLI';              level = 'optional' }
)

Write-Host "PC 이름: $env:COMPUTERNAME · OS: $([System.Environment]::OSVersion.VersionString) · PowerShell $($PSVersionTable.PSVersion)"
Write-Host '| 도구 | 용도 | 중요도 | 판정 | 비고 |'
Write-Host '|---|---|---|---|---|'
foreach ($t in $tools) {
    $has = Test-Command $t.cmd
    if (-not $has -and $t.cmd -eq 'python') { $has = Test-Command 'py' }
    $status = if ($has) { '가능' } else { '설치 필요' }
    $note = if ($has) { Get-Ver $t.cmd } else { 'docs/setup.md · scripts\setup-local.ps1' }
    Write-Host "| $($t.cmd) | $($t.use) | $($t.level) | $status | $note |"
}

# Codex 에 등록된 MCP (figma / higgsfield)
if (Test-Command 'codex') {
    $list = (codex mcp list 2>$null | Out-String)
    foreach ($name in 'figma', 'higgsfield') {
        $reg = if ($list -match "\b$name\b") { '등록됨' } else { '등록 안 됨' }
        Write-Host "| Codex MCP $name | 디자인·생성 | optional | $reg | codex mcp add $name --url ... |"
    }
}
# 레포 .mcp.json (Claude Code 가 읽음)
$mcp = Join-Path (Get-Location) '.mcp.json'
Write-Host "| .mcp.json | Claude Code MCP(figma, higgsfield) | optional | $(if (Test-Path $mcp) { '있음 — claude 안에서 /mcp 로 인증 상태 확인' } else { '현재 폴더에 없음 (레포 루트에서 실행하세요)' }) | |"
# 스킬 연결(junction) — 다른 프로젝트에서도 쓰려면 (docs/setup.md)
$link = Join-Path $env:USERPROFILE '.claude\skills\ArtworkOffice-taste-loop'
Write-Host "| ~/.claude/skills/ArtworkOffice-taste-loop | 다른 프로젝트에서 스킬 사용 | optional | $(if (Test-Path $link) { '연결됨' } else { '없음 (이 레포 안에서는 필요 없음)' }) | |"
# Orca 는 명령으로 감지할 수 없다
Write-Host '| Orca | 여러 에이전트 병렬 실행 | agent | (감지 불가 — 사용자가 알려 주세요) | |'
if (Test-Command 'ego-browser') {
    ego-browser nodejs -e "console.log('ego-browser ready')" 2>&1 | Select-Object -First 1 | ForEach-Object { Write-Host "ego-browser 실행 확인: $_" }
}
Write-Host ''
Write-Host '위 표 전체를 복사해 Claude 대화에 붙여 넣으세요.'
