# 批量替换 CDN 导入为本地导入
# Batch replace CDN imports with local imports

$files = Get-ChildItem -Path "src" -Filter "*.js" -Recurse

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $modified = $false
    
    # 替换 Three.js CDN 导入
    if ($content -match "import \* as THREE from 'https://esm\.sh/three@0\.165\.0';") {
        # 计算相对路径深度
        $depth = ($file.DirectoryName.Replace((Get-Location).Path, "").Split('\').Length - 1)
        $relativePath = ("..\" * $depth) + "public\lib\three.module.js"
        $relativePath = $relativePath.Replace('\', '/')
        
        $content = $content -replace "import \* as THREE from 'https://esm\.sh/three@0\.165\.0';", "import * as THREE from '$relativePath';"
        $modified = $true
    }
    
    # 替换 CANNON CDN 导入
    if ($content -match "import \* as CANNON from 'https://esm\.sh/cannon-es@0\.20\.0';") {
        $depth = ($file.DirectoryName.Replace((Get-Location).Path, "").Split('\').Length - 1)
        $relativePath = ("..\" * $depth) + "public\lib\cannon-es.js"
        $relativePath = $relativePath.Replace('\', '/')
        
        $content = $content -replace "import \* as CANNON from 'https://esm\.sh/cannon-es@0\.20\.0';", "import * as CANNON from '$relativePath';"
        $modified = $true
    }
    
    if ($modified) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
        Write-Host "✅ Updated: $($file.FullName)"
    }
}

Write-Host "`n🎉 Batch replacement completed!"

