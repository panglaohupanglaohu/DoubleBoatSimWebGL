# -*- coding: utf-8 -*-
"""
MOB (Man Overboard) 端到端场景测试

完整模拟 MOB 告警流程:
  1. 初始化 ManOverboardChannel
  2. 激活 MOB 告警 (lat=31.23, lon=121.47)
  3. 验证状态变更
  4. 测试漂移估算 (风速 15kn, 流速 0.8kn)
  5. 设置搜索模式 (williamson_turn)
  6. 添加搜索标记
  7. 检查生存时间估算 (不同水温)
  8. 验证消息总线 PAN-PAN 广播
  9. 取消 MOB 告警
  10. 验证复位状态
"""

import sys
import time
import traceback

from channels.man_overboard import (
    ManOverboardChannel,
    VALID_SEARCH_PATTERNS,
    _estimate_survival_hours,
)
from channels.marine_message_bus import (
    MarineMessageBus,
    MarineMessage,
    MessageType,
    MessagePriority,
)

PASS = 0
FAIL = 0
ERRORS = []


def check(label: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        msg = f"  ❌ {label}" + (f" — {detail}" if detail else "")
        print(msg)
        ERRORS.append(msg)


def main():
    global PASS, FAIL

    print("=" * 70)
    print("MOB 端到端场景测试")
    print("=" * 70)

    # ── Step 1: 初始化 ──────────────────────────────────────────────────────
    print("\n🔧 Step 1: 初始化 ManOverboardChannel + MessageBus")
    bus = MarineMessageBus("test_bus")
    ch = ManOverboardChannel(bus=bus)
    ok = ch.initialize()
    check("Channel 初始化成功", ok is True)
    check("Channel 处于待命状态", ch._mob_active is False)
    check("搜索模式初始为 none", ch._search_pattern == "none")
    check("无 MOB 位置记录", ch._mob_position is None)

    # 注册 bus subscriber 用于验证 PAN-PAN 广播
    received_messages = []

    def on_msg(msg):
        received_messages.append(msg)

    bus.register_channel("bridge_monitor", None)
    bus.subscribe("bridge_monitor", {MessageType.URGENCY_PAN_PAN}, callback=on_msg)

    # ── Step 2: 激活 MOB 告警 ───────────────────────────────────────────────
    print("\n🚨 Step 2: 激活 MOB 告警 (31.23°N, 121.47°E)")
    result = ch.activate_mob(31.23, 121.47)
    check("返回 mob_activated", result["status"] == "mob_activated")
    check("位置 lat=31.23", result["position"]["lat"] == 31.23)
    check("位置 lon=121.47", result["position"]["lon"] == 121.47)
    check("包含时间戳", "timestamp" in result["position"])
    check("默认搜索模式 williamson_turn",
          result["search_pattern"] == "williamson_turn")

    # ── Step 3: 验证状态变更 ────────────────────────────────────────────────
    print("\n📊 Step 3: 验证状态变更")
    check("mob_active=True", ch._mob_active is True)
    check("_mob_activated_at 已设置", ch._mob_activated_at is not None)

    status = ch.get_mob_status()
    check("get_mob_status.mob_active=True", status["mob_active"] is True)
    check("get_mob_status 含 survival_estimate",
          "survival_estimate" in status)
    check("get_mob_status 含 elapsed_minutes",
          "elapsed_minutes" in status)

    gen_status = ch.get_status()
    check("get_status.name == man_overboard",
          gen_status["name"] == "man_overboard")
    check("get_status.mob_active=True", gen_status["mob_active"] is True)

    # ── Step 4: 漂移估算 ───────────────────────────────────────────────────
    print("\n🌊 Step 4: 漂移估算 (wind=15kn, current=0.8kn, elapsed=30min)")
    drift = ch.estimate_drift(
        wind_speed_kn=15.0,
        wind_dir_deg=45.0,
        current_speed_kn=0.8,
        current_dir_deg=180.0,
        elapsed_min=30.0,
    )
    check("返回 drift_nm", "drift_nm" in drift)
    check("返回 search_radius_nm", "search_radius_nm" in drift)
    check("drift_nm > 0", drift["drift_nm"] > 0,
          f"drift_nm={drift['drift_nm']}")
    check("search_radius_nm > drift_nm",
          drift["search_radius_nm"] > drift["drift_nm"],
          f"search_r={drift['search_radius_nm']}")
    check("elapsed_min=30.0", drift["elapsed_min"] == 30.0)

    # 零漂移边界
    drift0 = ch.estimate_drift(elapsed_min=0.0)
    # elapsed_min=0 but ch is active so it uses _elapsed_minutes()
    # just check it returns a dict
    check("零elapsed返回有效字典", "drift_nm" in drift0)

    # ── Step 5: 设置搜索模式 ────────────────────────────────────────────────
    print("\n🔍 Step 5: 搜索模式设置")
    for pattern in VALID_SEARCH_PATTERNS:
        r = ch.set_search_pattern(pattern)
        check(f"搜索模式 {pattern} 设置成功", r["status"] == "pattern_set")

    r_bad = ch.set_search_pattern("zigzag_999")
    check("无效搜索模式被拒绝", r_bad["status"] == "error")

    # ── Step 6: 添加搜索标记 ────────────────────────────────────────────────
    print("\n📍 Step 6: 添加搜索标记")
    markers_to_add = [
        (31.231, 121.471),
        (31.232, 121.472),
        (31.235, 121.475),
    ]
    for i, (lat, lon) in enumerate(markers_to_add, 1):
        r = ch.add_mob_marker(lat, lon)
        check(f"标记 {i} 添加成功", r["status"] == "marker_added")
        check(f"标记计数={i}", r["total_markers"] == i)

    status_after = ch.get_mob_status()
    check("markers_count == 3", status_after["markers_count"] == 3)

    # ── Step 7: 生存时间估算 ────────────────────────────────────────────────
    print("\n🌡️  Step 7: 不同水温下的生存时间估算")
    test_temps = [
        (1.0, 0.75, "极冷 ≤2°C → 最短生存"),
        (5.0, 1.5, "冷水 5°C"),
        (10.0, 3.0, "10°C"),
        (15.0, 6.0, "15°C"),
        (20.0, 12.0, "20°C"),
        (25.0, 24.0, "25°C"),
        (30.0, 24.0, "暖水 30°C → 最大生存"),
    ]
    for temp, expected, desc in test_temps:
        h = _estimate_survival_hours(temp)
        check(f"水温 {temp}°C({desc}): {h}h ≈ {expected}h",
              abs(h - expected) < 0.01,
              f"got {h}")

    # 通过 channel 接口验证
    ch._water_temp_c = 10.0
    s = ch.get_mob_status()
    check("通过status获取生存估算 10°C→3h",
          abs(s["survival_estimate"]["estimated_hours"] - 3.0) < 0.1)

    # ── Step 8: 消息总线 PAN-PAN 广播验证 ──────────────────────────────────
    print("\n📡 Step 8: 消息总线 PAN-PAN 广播验证")
    check("bus 收到至少一条消息", len(bus._message_log) >= 1,
          f"log count={len(bus._message_log)}")
    pan_msgs = [m for m in bus._message_log
                if m.message_type == MessageType.URGENCY_PAN_PAN]
    check("存在 PAN-PAN 类型消息", len(pan_msgs) >= 1,
          f"pan_pan count={len(pan_msgs)}")
    if pan_msgs:
        msg = pan_msgs[0]
        check("PAN-PAN sender=man_overboard",
              msg.sender_channel == "man_overboard")
        check("PAN-PAN priority=DISTRESS",
              msg.priority == MessagePriority.DISTRESS)
        check("PAN-PAN subject=mob.activated",
              msg.subject == "mob.activated")
        check("PAN-PAN content 含 lat",
              msg.content.get("lat") == 31.23)

    # ── Step 9: 取消 MOB 告警 ───────────────────────────────────────────────
    print("\n🔄 Step 9: 取消 MOB 告警")
    cancel_result = ch.deactivate_mob()
    check("返回 mob_deactivated", cancel_result["status"] == "mob_deactivated")

    # ── Step 10: 验证复位状态 ───────────────────────────────────────────────
    print("\n✔️  Step 10: 验证复位状态")
    check("mob_active=False", ch._mob_active is False)
    check("mob_position=None", ch._mob_position is None)
    check("mob_activated_at=None", ch._mob_activated_at is None)
    check("search_pattern=none", ch._search_pattern == "none")
    check("markers 已清空", len(ch._mob_markers) == 0)

    final_status = ch.get_mob_status()
    check("get_mob_status.mob_active=False",
          final_status["mob_active"] is False)
    check("get_mob_status.markers_count=0",
          final_status["markers_count"] == 0)

    # ── 汇总 ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    total = PASS + FAIL
    print(f"MOB E2E 结果: {PASS}/{total} 通过, {FAIL} 失败")
    if ERRORS:
        print("\n失败项:")
        for e in ERRORS:
            print(e)
    print("=" * 70)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(2)
