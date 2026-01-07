# 批量替换为 unpkg CDN
$files = Get-ChildItem -Path "src" -Filter "*.js" -Recurse

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $modified = $false
    
    # 替换本地 Three.js 为 unpkg CDN
    if ($content -match "import \* as THREE from '\.\./") {
        $content = $content -replace "import \* as THREE from '\.\./.*?public/lib/three\.module\.js';", "import * as THREE from 'https://unpkg.com/three@0.165.0/build/three.module.js';"
        $modified = $true
    }
    
    if ($content -match "import \* as THREE from '\.\.\.") {
        $content = $content -replace "import \* as THREE from '\.\.\..*?public/lib/three\.module\.js';", "import * as THREE from 'https://unpkg.com/three@0.165.0/build/three.module.js';"
        $modified = $true
    }
    
    if ($modified) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
        Write-Host "✅ Updated: $($file.FullName)"
    }
}

Write-Host "`n🎉 Batch replacement completed!"

