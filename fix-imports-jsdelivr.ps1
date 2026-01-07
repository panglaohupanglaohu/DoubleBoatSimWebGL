# 批量替换为 jsDelivr CDN (国内CDN)
$files = Get-ChildItem -Path "src" -Filter "*.js" -Recurse

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $modified = $false
    
    # 替换 unpkg 为 jsDelivr
    if ($content -match "https://unpkg\.com/three@") {
        $content = $content -replace "https://unpkg\.com/three@", "https://cdn.jsdelivr.net/npm/three@"
        $modified = $true
    }
    
    if ($modified) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
        Write-Host "✅ Updated: $($file.FullName)"
    }
}

Write-Host "`n🎉 已切换到 jsDelivr CDN (国内有CDN节点)!"

