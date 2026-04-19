# -*- coding: utf-8 -*-
"""Tests for UltraPlan ChatHarness, ToolRegistry, and SkillRegistry enhancements."""

import sys
import os
import unittest
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend'))


def _run(coro):
    """Run an async coroutine synchronously."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestExecutionPlan(unittest.TestCase):
    """Test ExecutionPlan and PlanStep data structures."""

    def test_create_empty_plan(self):
        from agents.chat_harness import ExecutionPlan
        plan = ExecutionPlan(goal="test")
        self.assertEqual(plan.goal, "test")
        self.assertEqual(len(plan.steps), 0)
        self.assertEqual(plan.progress, 1.0)

    def test_add_steps(self):
        from agents.chat_harness import ExecutionPlan
        plan = ExecutionPlan(goal="navigate")
        plan.add_step("tool_call", "query AIS", tool_name="ais_query")
        plan.add_step("think", "analyze")
        plan.add_step("respond", "report")
        self.assertEqual(len(plan.steps), 3)
        self.assertEqual(plan.steps[0].step_id, 1)
        self.assertEqual(plan.steps[1].action, "think")
        self.assertEqual(plan.steps[2].action, "respond")

    def test_plan_progress(self):
        from agents.chat_harness import ExecutionPlan, PlanStepStatus
        plan = ExecutionPlan(goal="test")
        plan.add_step("think", "step1")
        plan.add_step("respond", "step2")
        self.assertAlmostEqual(plan.progress, 0.0)
        plan.steps[0].status = PlanStepStatus.COMPLETED
        self.assertAlmostEqual(plan.progress, 0.5)
        plan.steps[1].status = PlanStepStatus.COMPLETED
        self.assertAlmostEqual(plan.progress, 1.0)

    def test_plan_to_dict(self):
        from agents.chat_harness import ExecutionPlan
        plan = ExecutionPlan(goal="test goal")
        plan.add_step("tool_call", "query", tool_name="ais_query")
        d = plan.to_dict()
        self.assertEqual(d["goal"], "test goal")
        self.assertEqual(len(d["steps"]), 1)
        self.assertIn("plan_id", d)
        self.assertIn("progress", d)

    def test_plan_step_dependencies(self):
        from agents.chat_harness import ExecutionPlan
        plan = ExecutionPlan(goal="complex")
        plan.add_step("tool_call", "step1", tool_name="ais_query")
        plan.add_step("tool_call", "step2", tool_name="weather_fetch", depends_on=[1])
        plan.add_step("tool_call", "step3", tool_name="route_calculate", depends_on=[1, 2])
        self.assertEqual(plan.steps[2].depends_on, [1, 2])


class TestBuildPlanFromPrompt(unittest.TestCase):
    """Test the rule-based plan builder."""

    def test_navigation_plan(self):
        from agents.chat_harness import build_plan_from_prompt
        plan = build_plan_from_prompt("请帮我规划一条从上海到宁波的航线")
        self.assertEqual(plan.status, "pending")
        self.assertGreater(len(plan.steps), 2)
        tool_steps = [s for s in plan.steps if s.action == "tool_call"]
        self.assertGreater(len(tool_steps), 0)

    def test_colregs_plan(self):
        from agents.chat_harness import build_plan_from_prompt
        plan = build_plan_from_prompt("检查周围船舶的CPA/TCPA避碰态势")
        tool_names = [s.tool_name for s in plan.steps if s.tool_name]
        self.assertIn("ais_query", tool_names)

    def test_engine_plan(self):
        from agents.chat_harness import build_plan_from_prompt
        plan = build_plan_from_prompt("查看主机发动机状态")
        tool_names = [s.tool_name for s in plan.steps if s.tool_name]
        self.assertIn("engine_status", tool_names)

    def test_weather_plan(self):
        from agents.chat_harness import build_plan_from_prompt
        plan = build_plan_from_prompt("未来24小时天气预报")
        tool_names = [s.tool_name for s in plan.steps if s.tool_name]
        self.assertIn("weather_fetch", tool_names)

    def test_general_plan_minimal(self):
        from agents.chat_harness import build_plan_from_prompt
        plan = build_plan_from_prompt("你好")
        self.assertGreater(len(plan.steps), 0)
        # General plan should have think + respond
        actions = [s.action for s in plan.steps]
        self.assertIn("think", actions)
        self.assertIn("respond", actions)

    def test_research_plan(self):
        from agents.chat_harness import build_plan_from_prompt
        plan = build_plan_from_prompt("研究IMO MASS自主等级标准")
        tool_names = [s.tool_name for s in plan.steps if s.tool_name]
        self.assertIn("web_search", tool_names)


class TestAgentLoopResult(unittest.TestCase):
    """Test AgentLoopResult structure."""

    def test_agent_loop_result_to_dict(self):
        from agents.chat_harness import AgentLoopResult, ExecutionPlan
        result = AgentLoopResult(
            plan=ExecutionPlan(goal="test"),
            final_response="done",
            iterations=3,
        )
        d = result.to_dict()
        self.assertEqual(d["final_response"], "done")
        self.assertEqual(d["iterations"], 3)
        self.assertIn("plan", d)


class TestToolRegistryEnhanced(unittest.TestCase):
    """Test enhanced ToolRegistry with per-agent binding."""

    def test_bind_tools_to_agent(self):
        from agents.tool_registry import ToolRegistry
        reg = ToolRegistry()
        reg.load_defaults()
        all_tools = reg.list_all()
        # Bind only 3 tools to an agent
        reg.bind_tools_to_agent("agent_1", ["web_search", "ais_query", "weather_fetch"])
        agent_tools = reg.get_agent_tools("agent_1")
        self.assertEqual(len(agent_tools), 3)
        agent_ids = reg.get_agent_tool_ids("agent_1")
        # tool_ids are generated from names, so check count
        self.assertEqual(len(agent_ids), 3)

    def test_unbind_agent_fallback(self):
        from agents.tool_registry import ToolRegistry
        reg = ToolRegistry()
        reg.load_defaults()
        all_enabled = reg.list_enabled()
        reg.bind_tools_to_agent("agent_2", ["web_search"])
        self.assertEqual(len(reg.get_agent_tools("agent_2")), 1)
        reg.unbind_agent("agent_2")
        # After unbinding, should fall back to all enabled
        self.assertEqual(len(reg.get_agent_tools("agent_2")), len(all_enabled))

    def test_openai_schema_generation(self):
        from agents.tool_registry import ToolRegistry
        reg = ToolRegistry()
        reg.load_defaults()
        schema = reg.get_openai_tools_schema()
        self.assertGreater(len(schema), 0)
        first = schema[0]
        self.assertEqual(first["type"], "function")
        self.assertIn("function", first)
        self.assertIn("name", first["function"])
        self.assertIn("parameters", first["function"])

    def test_search_tools(self):
        from agents.tool_registry import ToolRegistry
        reg = ToolRegistry()
        reg.load_defaults()
        results = reg.search("weather")
        self.assertGreater(len(results), 0)
        for t in results:
            self.assertTrue(
                "weather" in t.name.lower() or "weather" in t.description.lower()
            )

    def test_get_by_name(self):
        from agents.tool_registry import ToolRegistry
        reg = ToolRegistry()
        reg.load_defaults()
        tool = reg.get_by_name("web_search")
        self.assertIsNotNone(tool)
        self.assertEqual(tool.name, "web_search")


class TestSkillRegistryEnhanced(unittest.TestCase):
    """Test enhanced SkillRegistry with runtime creation and search."""

    def test_list_enabled(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        reg.load_defaults()
        enabled = reg.list_enabled()
        self.assertGreater(len(enabled), 0)

    def test_enable_disable(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        reg.load_defaults()
        skills = reg.list_all()
        if not skills:
            self.skipTest("No skills loaded")
        first = skills[0]
        reg.disable(first.skill_id)
        self.assertFalse(first.enabled)
        reg.enable(first.skill_id)
        self.assertTrue(first.enabled)

    def test_search_skills(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        reg.load_defaults()
        results = reg.search("navigation")
        self.assertGreater(len(results), 0)

    def test_create_skill_runtime(self):
        from agents.skill_registry import SkillRegistry
        from agents.models import SkillCategory
        reg = SkillRegistry()
        skill = reg.create_skill(
            name="test_skill",
            description="A test skill",
            category=SkillCategory.GENERAL,
            instructions="## Test\n\n1. Do thing\n2. Done",
            required_tools=["web_search"],
        )
        self.assertEqual(skill.name, "test_skill")
        self.assertEqual(skill.source, "runtime")
        # Should be findable
        self.assertIsNotNone(reg.get(skill.skill_id))

    def test_patch_skill(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        reg.load_defaults()
        skills = reg.list_all()
        if not skills:
            self.skipTest("No skills loaded")
        first = skills[0]
        reg.patch_skill(first.skill_id, description="patched description")
        self.assertEqual(first.description, "patched description")

    def test_delete_skill(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        reg.load_defaults()
        initial = len(reg.list_all())
        skills = reg.list_all()
        if not skills:
            self.skipTest("No skills")
        reg.delete_skill(skills[0].skill_id)
        self.assertEqual(len(reg.list_all()), initial - 1)

    def test_get_instructions(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        reg.load_defaults()
        skills = reg.list_all()
        if not skills:
            self.skipTest("No skills")
        instr = reg.get_instructions(skills[0].skill_id)
        self.assertIsInstance(instr, str)

    def test_get_required_tools(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        reg.load_defaults()
        skills = reg.list_all()
        for s in skills:
            tools = reg.get_required_tools(s.skill_id)
            self.assertIsInstance(tools, list)
            break

    def test_get_by_slug(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        reg.load_defaults()
        skills = reg.list_all()
        if not skills:
            self.skipTest("No skills")
        found = reg.get_by_slug(skills[0].name)
        self.assertIsNotNone(found)


class TestChatHarnessUltraPlan(unittest.TestCase):
    """Test ChatHarness ultraplan integration."""

    def test_harness_has_agent_loop(self):
        from agents.chat_harness import ChatHarness
        harness = ChatHarness()
        self.assertTrue(hasattr(harness, 'agent_loop'))
        self.assertTrue(asyncio.iscoroutinefunction(harness.agent_loop))

    def test_harness_has_agent_loop_stream(self):
        from agents.chat_harness import ChatHarness
        harness = ChatHarness()
        self.assertTrue(hasattr(harness, 'agent_loop_stream'))

    def test_plan_step_status_enum(self):
        from agents.chat_harness import PlanStepStatus
        self.assertEqual(PlanStepStatus.PENDING.value, "pending")
        self.assertEqual(PlanStepStatus.COMPLETED.value, "completed")
        self.assertEqual(PlanStepStatus.FAILED.value, "failed")

    def test_execution_plan_completed_steps(self):
        from agents.chat_harness import ExecutionPlan, PlanStepStatus
        plan = ExecutionPlan(goal="test")
        plan.add_step("think", "s1")
        plan.add_step("respond", "s2")
        plan.add_step("tool_call", "s3", tool_name="web_search")
        self.assertEqual(plan.completed_steps, 0)
        plan.steps[0].status = PlanStepStatus.COMPLETED
        plan.steps[2].status = PlanStepStatus.COMPLETED
        self.assertEqual(plan.completed_steps, 2)


class TestToolExecutorIntegration(unittest.TestCase):
    """Test tool executor with the registry."""

    def test_execute_weather_fetch(self):
        from agents.tool_executor import get_tool_executor
        executor = get_tool_executor()
        result = _run(executor.execute("weather_fetch", {"lat": 31.2, "lon": 121.5}))
        self.assertTrue(result.success)
        self.assertIn("风速", result.output)

    def test_execute_ais_query(self):
        from agents.tool_executor import get_tool_executor
        executor = get_tool_executor()
        result = _run(executor.execute("ais_query", {}))
        self.assertTrue(result.success)
        self.assertIn("AIS", result.output)

    def test_execute_colregs_check(self):
        from agents.tool_executor import get_tool_executor
        executor = get_tool_executor()
        result = _run(executor.execute("colregs_check", {
            "own_vessel": {"position": {"lat": 31.2, "lon": 121.5}},
            "target_vessel": {"position": {"lat": 31.3, "lon": 121.6}},
        }))
        self.assertTrue(result.success)
        self.assertIn("COLREGs", result.output)

    def test_execute_engine_status(self):
        from agents.tool_executor import get_tool_executor
        executor = get_tool_executor()
        result = _run(executor.execute("engine_status", {"engine_id": "main"}))
        self.assertTrue(result.success)
        self.assertIn("RPM", result.output)

    def test_execute_unknown_tool(self):
        from agents.tool_executor import get_tool_executor
        executor = get_tool_executor()
        result = _run(executor.execute("nonexistent_tool", {}))
        self.assertFalse(result.success)
        self.assertIn("Unknown tool", result.error)

    def test_execution_history(self):
        from agents.tool_executor import get_tool_executor
        executor = get_tool_executor()
        _run(executor.execute("weather_fetch", {"lat": 30, "lon": 120}))
        history = executor.get_history(limit=5)
        self.assertGreater(len(history), 0)
        self.assertIn("tool_name", history[-1])

    def test_execute_memory_save_read(self):
        from agents.tool_executor import get_tool_executor
        executor = get_tool_executor()
        # Save
        result = _run(executor.execute("memory_save", {
            "key": "test_key", "content": "test_value", "category": "test"
        }))
        self.assertTrue(result.success)
        # Read
        result = _run(executor.execute("memory_read", {"key": "test_key"}))
        self.assertTrue(result.success)

    def test_execute_route_calculate(self):
        from agents.tool_executor import get_tool_executor
        executor = get_tool_executor()
        result = _run(executor.execute("route_calculate", {
            "origin": {"lat": 31.2, "lon": 121.5},
            "destination": {"lat": 22.3, "lon": 114.2},
        }))
        self.assertTrue(result.success)
        self.assertIn("nm", result.output)


class TestChatHarnessSessions(unittest.TestCase):
    """Test session management."""

    def test_create_session(self):
        from agents.chat_harness import ChatHarness
        harness = ChatHarness()
        session = harness.get_or_create_session(agent_id="test_agent")
        self.assertEqual(session.agent_id, "test_agent")
        self.assertEqual(session.turn_count, 0)

    def test_session_persistence(self):
        from agents.chat_harness import ChatHarness
        harness = ChatHarness()
        s1 = harness.get_or_create_session(session_id="s1", agent_id="a1")
        s1.add_user_message("hello")
        s1.add_assistant_message("hi")
        s2 = harness.get_or_create_session(session_id="s1")
        self.assertEqual(s1.session_id, s2.session_id)
        self.assertEqual(len(s2.messages), 2)

    def test_list_sessions(self):
        from agents.chat_harness import ChatHarness
        harness = ChatHarness()
        harness.get_or_create_session(session_id="x1", agent_id="a1")
        harness.get_or_create_session(session_id="x2", agent_id="a2")
        harness.get_or_create_session(session_id="x3", agent_id="a1")
        all_sessions = harness.list_sessions()
        self.assertEqual(len(all_sessions), 3)
        a1_sessions = harness.list_sessions(agent_id="a1")
        self.assertEqual(len(a1_sessions), 2)

    def test_session_compaction(self):
        from agents.chat_harness import ChatSession
        session = ChatSession(compact_after=10)
        for i in range(20):
            session.add_user_message(f"msg {i}")
            session.add_assistant_message(f"reply {i}")
        session.compact_if_needed()
        self.assertLessEqual(len(session.messages), 15)


class TestProviderConfig(unittest.TestCase):
    """Test ProviderConfig building."""

    def test_from_env(self):
        from agents.chat_harness import ProviderConfig
        config = ProviderConfig.from_env()
        self.assertIsNotNone(config.provider)
        self.assertIsNotNone(config.model)

    def test_from_settings(self):
        from agents.chat_harness import ProviderConfig
        settings = {"llm": {"provider": "local", "model": "llama3"}}
        config = ProviderConfig.from_settings(settings)
        self.assertEqual(config.model, "llama3")

    def test_resolve_base_url(self):
        from agents.chat_harness import ProviderConfig, LLMProvider
        config = ProviderConfig(provider=LLMProvider.DEEPSEEK)
        url = config.resolve_base_url()
        self.assertIn("deepseek", url)

    def test_custom_base_url(self):
        from agents.chat_harness import ProviderConfig
        config = ProviderConfig(api_base_url="http://localhost:8080/v1/")
        url = config.resolve_base_url()
        self.assertEqual(url, "http://localhost:8080/v1")


if __name__ == "__main__":
    unittest.main()
