# 批量替换为本地文件（不再使用CDN）
$files = Get-ChildItem -Path "src" -Filter "*.js" -Recurse

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $modified = $false
    
    # 计算相对路径深度
    $depth = ($file.DirectoryName.Replace((Get-Location).Path, "")).Split('\').Count - 1
    $relativePath = ("../" * $depth) + "public/lib/three.module.js"
    
    # 替换 jsDelivr CDN 为本地文件
    if ($content -match "https://cdn\.jsdelivr\.net/npm/three@") {
        $content = $content -replace "https://cdn\.jsdelivr\.net/npm/three@0\.165\.0/build/three\.module\.js", $relativePath
        $content = $content -replace "https://cdn\.jsdelivr\.net/npm/three@0\.165\.0/examples/jsm/controls/OrbitControls\.js", $relativePath.Replace("three.module.js", "OrbitControls.js")
        $modified = $true
    }
    
    if ($modified) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
        Write-Host "✅ Updated: $($file.FullName)"
    }
}

Write-Host "`n🎉 已切换回本地文件（完全离线）!"

