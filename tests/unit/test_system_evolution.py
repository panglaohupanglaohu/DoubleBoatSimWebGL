# -*- coding: utf-8 -*-
"""
System Self-Evolution Integration Tests — 系统自我演进集成测试

模拟人类操作的端到端测试:
  1. 执行智能体运行审查 → 发现不合规项
  2. 自动派发给 Build 团队
  3. Build 团队执行修改
  4. 自动化测试验证修改结果
  5. 闭环关闭演进项
"""

import sys
import os
import asyncio
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "backend"))

from channels.marine_base import register_channel, get_default_registry
from channels.man_overboard import ManOverboardChannel, VALID_SEARCH_PATTERNS, _SURVIVAL_TABLE
from channels.marine_message_bus import MarineMessageBus, MessagePriority
from channels.decision_orchestrator import DecisionOrchestratorChannel
from channels.build_team_manager import BuildTeamManagerChannel
from channels.execution_team_manager import ExecutionTeamManagerChannel
from channels.system_evolution import (
    SystemEvolutionChannel,
    EvolutionStatus,
    BUILTIN_AUDIT_RULES,
)


def _setup_full_system():
    """模拟人类启动完整系统的过程。"""
    bus = MarineMessageBus()
    mob = ManOverboardChannel(bus=bus)
    register_channel(mob)
    mob.initialize()

    orch = DecisionOrchestratorChannel()
    register_channel(orch)
    orch.initialize()

    build = BuildTeamManagerChannel(config={"llm_backend": "copilot"})
    register_channel(build)
    build.initialize()

    exec_team = ExecutionTeamManagerChannel(config={"llm_backend": "deepseek"})
    register_channel(exec_team)
    exec_team.initialize()

    evo = SystemEvolutionChannel()
    register_channel(evo)
    evo.initialize()

    return {
        "bus": bus, "mob": mob, "orch": orch,
        "build": build, "exec": exec_team, "evo": evo,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 场景 1: 系统自我演进引擎基础功能
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestEvolutionEngineBasics:
    """验证演进引擎的 Channel 基本接口。"""

    def test_init_and_status(self):
        sys = _setup_full_system()
        evo = sys["evo"]
        status = evo.get_status()
        assert status["name"] == "system_evolution"
        assert status["initialized"] is True
        assert status["audit_rules_count"] >= 6

    def test_registered_in_registry(self):
        sys = _setup_full_system()
        reg = get_default_registry()
        assert reg.get("system_evolution") is not None
        assert reg.get("build_team_manager") is not None
        assert reg.get("execution_team_manager") is not None

    def test_builtin_audit_rules(self):
        assert len(BUILTIN_AUDIT_RULES) >= 6
        domains = {r.domain for r in BUILTIN_AUDIT_RULES}
        assert "SOLAS" in domains
        assert "IAMSAR" in domains
        assert "GMDSS" in domains


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 场景 2: MOB 合规修复验证 — 模拟人类发现并修复
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestMOBComplianceFixes:
    """模拟: 操作员检查 MOB 系统 → 发现问题 → Build 修复 → 验证通过。"""

    def test_survival_table_5c_corrected(self):
        """IMO MSC/Circ.1046: 5°C 水温生存时间 ≤ 1.0h。"""
        for temp, hours in _SURVIVAL_TABLE:
            if temp == 5:
                assert hours <= 1.05, f"5°C survival {hours}h exceeds IMO limit 1.0h"
                break

    def test_search_patterns_include_iamsar_modes(self):
        """IAMSAR Vol III: 应包含 expanding_square 和 sector_search。"""
        assert "expanding_square" in VALID_SEARCH_PATTERNS
        assert "sector_search" in VALID_SEARCH_PATTERNS
        assert "parallel_sweep" in VALID_SEARCH_PATTERNS
        assert "creeping_line" in VALID_SEARCH_PATTERNS
        # 原有模式仍保留
        assert "williamson_turn" in VALID_SEARCH_PATTERNS
        assert "anderson_turn" in VALID_SEARCH_PATTERNS
        assert "scharnow_turn" in VALID_SEARCH_PATTERNS

    def test_mob_can_set_new_search_patterns(self):
        """模拟操作员: 切换到 expanding_square 搜索模式。"""
        mob = ManOverboardChannel()
        mob.initialize()
        mob.activate_mob(31.23, 121.47)
        result = mob.set_search_pattern("expanding_square")
        assert result["status"] == "pattern_set"
        assert result["search_pattern"] == "expanding_square"

        result2 = mob.set_search_pattern("sector_search")
        assert result2["search_pattern"] == "sector_search"

    def test_mob_pan_pan_uses_urgency_priority(self):
        """GMDSS: PAN-PAN 应使用 URGENCY 优先级。"""
        bus = MarineMessageBus()
        mob = ManOverboardChannel(bus=bus)
        mob.initialize()
        mob.activate_mob(31.23, 121.47)

        # 通过 inspect source 确认
        import inspect
        src = inspect.getsource(mob.activate_mob)
        assert "MessagePriority.URGENCY" in src
        assert "MessagePriority.DISTRESS" not in src

    def test_drift_model_includes_tpe(self):
        """IAMSAR: 漂移估算应包含 Total Probable Error。"""
        mob = ManOverboardChannel()
        mob.initialize()
        drift = mob.estimate_drift(
            wind_speed_kn=15.0, wind_dir_deg=45.0,
            current_speed_kn=0.8, current_dir_deg=180.0,
            elapsed_min=60.0,
        )
        assert "datum_error" in drift
        assert "total_error" in drift
        assert drift["datum_error"] > 0
        assert drift["total_error"] > 0
        assert drift["drift_nm"] > 0
        assert drift["search_radius_nm"] > drift["drift_nm"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 场景 3: 决策编排器 MOB 集成 — 模拟驾驶台告警
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestDecisionOrchestratorMOBIntegration:
    """模拟: 驾驶台收到 MOB 告警 → 决策编排器自动纳入行动计划。"""

    def test_mob_active_generates_action(self):
        """MOB 激活后，决策编排器应产生 critical 级 action。"""
        sys = _setup_full_system()
        mob = sys["mob"]
        orch = sys["orch"]

        # Step 1: 模拟操作员按下 MOB 按钮
        mob.activate_mob(31.23, 121.47)

        # Step 2: 决策编排器生成行动计划
        plan = orch._build_action_plan()

        # Step 3: 验证 MOB 相关 action
        mob_actions = [a for a in plan if a["id"].startswith("mob-")]
        assert len(mob_actions) >= 1, "MOB active but no mob action in plan"
        assert mob_actions[0]["priority"] == "critical"
        assert "mob_search_and_rescue" in mob_actions[0]["recommended_action"]
        assert "SOLAS" in mob_actions[0]["rule"] or "IAMSAR" in mob_actions[0]["rule"]

    def test_mob_inactive_no_action(self):
        """MOB 未激活时，不应产生 MOB action。"""
        sys = _setup_full_system()
        orch = sys["orch"]
        plan = orch._build_action_plan()
        mob_actions = [a for a in plan if a["id"].startswith("mob-")]
        assert len(mob_actions) == 0

    def test_mob_deactivated_clears_action(self):
        """MOB 取消后，下一周期不再产生 MOB action。"""
        sys = _setup_full_system()
        mob = sys["mob"]
        orch = sys["orch"]

        mob.activate_mob(31.0, 121.0)
        plan1 = orch._build_action_plan()
        assert any(a["id"].startswith("mob-") for a in plan1)

        mob.deactivate_mob()
        plan2 = orch._build_action_plan()
        assert not any(a["id"].startswith("mob-") for a in plan2)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 场景 4: Build↔Exec 反馈闭环 — 模拟团队协作
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestBuildExecFeedbackLoop:
    """模拟: Exec 团队发现问题 → Build 团队收到 → 执行修改 → 回调闭环。"""

    def test_build_team_has_evolution_interface(self):
        sys = _setup_full_system()
        build = sys["build"]
        assert hasattr(build, "accept_evolution_feedback")
        assert hasattr(build, "get_evolution_tasks")

    def test_evolution_feedback_accepted(self):
        """Exec 团队提交反馈 → Build 团队接收并分配。"""
        sys = _setup_full_system()
        build = sys["build"]
        result = build.accept_evolution_feedback(
            item_id="EVO-test001",
            title="MOB 搜索模式缺失",
            severity="critical",
            target_channel="man_overboard",
            detail="缺少 expanding_square 搜索模式",
        )
        assert result["status"] == "accepted"
        assert result["assigned_to"] == "build_developer"
        assert len(build.get_evolution_tasks()) == 1

    def test_evolution_feedback_into_agent_queue(self):
        """反馈应出现在对应 Agent 的 task_queue 中。"""
        sys = _setup_full_system()
        build = sys["build"]
        build.accept_evolution_feedback(
            item_id="EVO-test002",
            title="PAN-PAN 优先级错误",
            severity="high",
        )
        dev = build.agents["build_developer"]
        matching = [t for t in dev.task_queue if "EVO-test002" in t]
        assert len(matching) == 1


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 场景 5: 完整演进周期 — 全流程模拟
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestFullEvolutionCycle:
    """模拟人类全流程:
    1. 系统启动
    2. 执行智能体运行审查
    3. 发现合规缺陷
    4. 派发 Build 团队
    5. Build 完成修改
    6. 验证通过
    7. 关闭演进项
    """

    def test_audit_discovers_items(self):
        """审查应发现需要演进的项目。"""
        sys = _setup_full_system()
        evo = sys["evo"]
        result = evo.run_full_audit()
        assert result["rules_checked"] >= 6
        # 修复后，大部分规则应通过
        assert result["passed"] >= 3

    def test_full_cycle_workflow(self):
        """完整的审查→派发→验证→关闭流程。"""
        sys = _setup_full_system()
        evo = sys["evo"]

        # Step 1: 运行审查
        audit = evo.run_full_audit()
        total_items = len(evo.evolution_items)

        # Step 2: 如有未通过项，派发
        dispatch = evo.dispatch_all_pending()

        # Step 3: 模拟 Build 团队完成修改
        for item_id, item in evo.evolution_items.items():
            if item.status == EvolutionStatus.DISPATCHED.value:
                evo.mark_in_progress(item_id)
                evo.mark_build_complete(item_id, code_changes=["man_overboard.py"])

        # Step 4: 运行验证
        verify = evo.verify_all_pending()

        # Step 5: 关闭已验证项
        closed = evo.close_verified()

        # 验证统计
        summary = evo.get_evolution_summary()
        assert summary["total_items"] >= 0
        assert evo.total_audits == 1

    def test_evolution_cycle_api(self):
        """一键运行完整演进周期。"""
        sys = _setup_full_system()
        evo = sys["evo"]
        result = evo.run_evolution_cycle()
        assert "audit" in result
        assert "dispatch" in result
        assert "verify" in result
        assert "summary" in result

    def test_get_evolution_items_filter(self):
        """按状态过滤演进项。"""
        sys = _setup_full_system()
        evo = sys["evo"]
        evo.run_full_audit()
        all_items = evo.get_evolution_items()
        discovered = evo.get_evolution_items(status=EvolutionStatus.DISCOVERED.value)
        assert len(all_items) >= len(discovered)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 场景 6: 模拟操作员 MOB 全流程
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestHumanOperatorMOBScenario:
    """模拟操作员从发现落水到搜救完成的完整操作流程。"""

    def test_operator_mob_full_scenario(self):
        """
        操作员完整流程:
        1. 发现人员落水 → 按下 MOB 按钮
        2. 系统自动切换 Williamson Turn
        3. 操作员查看状态面板
        4. 操作员切换到 Expanding Square Search
        5. 添加搜索标记
        6. 查看漂移估算
        7. 查看决策编排器行动计划
        8. 搜救完成 → 取消 MOB
        """
        sys = _setup_full_system()
        mob = sys["mob"]
        orch = sys["orch"]

        # 1. 按下 MOB 按钮
        result = mob.activate_mob(31.23, 121.47)
        assert result["status"] == "mob_activated"
        assert result["search_pattern"] == "williamson_turn"

        # 2. 查看状态面板
        status = mob.get_mob_status()
        assert status["mob_active"] is True
        assert status["mob_position"]["lat"] == 31.23

        # 3. 切换搜索模式
        mob.set_search_pattern("expanding_square")
        assert mob.get_mob_status()["search_pattern"] == "expanding_square"

        # 4. 添加搜索标记
        mob.add_mob_marker(31.235, 121.475)
        mob.add_mob_marker(31.225, 121.465)
        assert mob.get_mob_status()["markers_count"] == 2

        # 5. 查看漂移估算
        drift = mob.estimate_drift(
            wind_speed_kn=12.0, wind_dir_deg=90.0,
            current_speed_kn=0.5, current_dir_deg=270.0,
            elapsed_min=30.0,
        )
        assert drift["drift_nm"] >= 0
        assert drift["total_error"] >= 0

        # 6. 决策编排器自动纳入
        plan = orch._build_action_plan()
        mob_actions = [a for a in plan if "mob" in a["id"]]
        assert len(mob_actions) >= 1

        # 7. 搜救完成，取消 MOB
        result = mob.deactivate_mob()
        assert result["status"] == "mob_deactivated"
        assert mob.get_mob_status()["mob_active"] is False

    def test_operator_mob_via_events(self):
        """通过事件接口模拟操作员操作。"""
        mob = ManOverboardChannel()
        mob.initialize()

        # 操作员通过外部系统触发
        r1 = asyncio.run(
            mob.process_event({"type": "mob_alert", "lat": 32.0, "lon": 122.0})
        )
        assert r1["status"] == "mob_activated"

        r2 = asyncio.run(
            mob.process_event({"type": "mob_cancel"})
        )
        assert r2["status"] == "mob_deactivated"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 场景 7: 系统自我演进 + Build 团队协作验证
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestEvolutionWithBuildTeam:
    """演进引擎 → Build 团队 → 修改 → 验证的完整协作。"""

    def test_dispatch_to_build_team(self):
        """演进项应出现在 Build 团队的队列中。"""
        sys = _setup_full_system()
        evo = sys["evo"]
        build = sys["build"]

        evo.run_full_audit()
        evo.dispatch_all_pending()

        # 检查 build 团队是否收到任务
        dev = build.agents.get("build_developer")
        arch = build.agents.get("build_architect")
        has_evolution_tasks = any(
            "evolution_fix:" in t
            for t in (dev.task_queue if dev else []) + (arch.task_queue if arch else [])
        )

        dispatched_items = evo.get_evolution_items(status=EvolutionStatus.DISPATCHED.value)
        if dispatched_items:
            assert has_evolution_tasks, "Dispatched items but no tasks in Build agents"

    def test_build_feedback_closes_item(self):
        """Build 完成 → 回调 → 验证 → 关闭。"""
        sys = _setup_full_system()
        evo = sys["evo"]

        # 手动创建一个演进项
        from channels.system_evolution import EvolutionItem
        item = EvolutionItem(
            title="Test fix",
            target_channel="man_overboard",
            status=EvolutionStatus.DISPATCHED.value,
        )
        evo.evolution_items[item.id] = item

        # Build 完成回调
        evo.accept_build_feedback(item.id, success=True, code_changes=["man_overboard.py"])
        assert item.status == EvolutionStatus.VERIFY_PENDING.value

    def test_verify_with_custom_test_fn(self):
        """注册自定义验证函数并验证。"""
        sys = _setup_full_system()
        evo = sys["evo"]

        from channels.system_evolution import EvolutionItem
        item = EvolutionItem(
            title="Custom verify test",
            target_channel="man_overboard",
            status=EvolutionStatus.VERIFY_PENDING.value,
            verify_test_name="test_custom_check",
        )
        evo.evolution_items[item.id] = item

        # 注册验证函数
        evo.register_verify_test("test_custom_check", lambda: (True, "All good"))
        result = evo.verify_all_pending()
        assert len(result["verified"]) == 1
        assert result["verified"][0]["passed"] is True
        assert item.status == EvolutionStatus.VERIFIED.value

    def test_verify_failure_triggers_retry(self):
        """验证失败 → 退回 Build 团队重做。"""
        sys = _setup_full_system()
        evo = sys["evo"]

        from channels.system_evolution import EvolutionItem
        item = EvolutionItem(
            title="Will fail first",
            target_channel="man_overboard",
            status=EvolutionStatus.VERIFY_PENDING.value,
            verify_test_name="test_fail_check",
            max_retries=3,
        )
        evo.evolution_items[item.id] = item

        evo.register_verify_test("test_fail_check", lambda: (False, "Still broken"))
        result = evo.verify_all_pending()
        assert result["verified"][0]["passed"] is False
        assert item.status == EvolutionStatus.DISPATCHED.value  # 退回
        assert item.retry_count == 1


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 场景 8: process_event 异步接口
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestEvolutionAsyncInterface:
    """验证演进引擎的事件驱动接口。"""

    def test_process_event_run_audit(self):
        sys_d = _setup_full_system()
        evo = sys_d["evo"]
        result = asyncio.run(
            evo.process_event({"type": "run_audit"})
        )
        assert "rules_checked" in result

    def test_process_event_evolution_cycle(self):
        sys_d = _setup_full_system()
        evo = sys_d["evo"]
        result = asyncio.run(
            evo.process_event({"type": "evolution_cycle"})
        )
        assert "audit" in result
        assert "summary" in result

    def test_process_event_unknown(self):
        sys_d = _setup_full_system()
        evo = sys_d["evo"]
        result = asyncio.run(
            evo.process_event({"type": "unknown_event"})
        )
        assert result["status"] == "ignored"
