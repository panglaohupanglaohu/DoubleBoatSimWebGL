#!/bin/bash
echo "🧪 Poseidon 数字孪生集成测试"
echo "=============================="
echo ""

API="http://127.0.0.1:8080"

# 1. 健康检查
echo "1. 健康检查..."
HEALTH=$(curl -s $API/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ 服务在线"
else
    echo "   ❌ 服务离线"
    exit 1
fi

# 2. 技能列表
echo "2. 技能列表..."
SKILLS=$(curl -s $API/api/v1/skills | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['data']['skills']))")
echo "   ✅ 可用技能：$SKILLS 个"

# 3. 场景预设测试
echo "3. 场景预设测试..."
RESULT=$(curl -s -X POST $API/api/v1/twins/scene/control -H "Content-Type: application/json" -d '{"action":"apply_preset","params":{"preset":"stormy"}}')
if echo "$RESULT" | grep -q "success.*true"; then
    echo "   ✅ 暴风雨场景应用成功"
else
    echo "   ❌ 场景应用失败"
fi

# 4. 传感器查询
echo "4. 传感器查询..."
RESULT=$(curl -s -X POST $API/api/v1/twins/sensor/query -H "Content-Type: application/json" -d '{"sensor_type":"gps"}')
if echo "$RESULT" | grep -q "success.*true"; then
    echo "   ✅ GPS 传感器数据获取成功"
else
    echo "   ❌ 传感器查询失败"
fi

# 5. 水动力分析
echo "5. 水动力分析..."
RESULT=$(curl -s -X POST $API/api/v1/hydro/analysis -H "Content-Type: application/json" -d '{"length":150,"beam":25,"draft":8,"displacement":15000,"speed":15,"kg":7.5}')
if echo "$RESULT" | grep -q "success.*true"; then
    RESISTANCE=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['resistance']['total_resistance_kN'])")
    echo "   ✅ 水动力分析完成 (阻力：${RESISTANCE}kN)"
else
    echo "   ❌ 水动力分析失败"
fi

# 6. 故障诊断
echo "6. 故障诊断..."
RESULT=$(curl -s -X POST $API/api/v1/twins/diagnosis -H "Content-Type: application/json" -d '{"symptom":"主机转速异常下降"}')
if echo "$RESULT" | grep -q "success.*true"; then
    echo "   ✅ 故障诊断完成"
else
    echo "   ❌ 故障诊断失败"
fi

echo ""
echo "=============================="
echo "🎉 集成测试完成！"
