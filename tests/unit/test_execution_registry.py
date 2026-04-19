# -*- coding: utf-8 -*-
"""Tests for execution_registry, session_store, and enhanced registries.

Covers:
- ToolPermissionContext (deny_names, deny_prefixes)
- HistoryLog (add, markdown, list)
- TranscriptStore (append, compact, flush, replay)
- ToolPool (assembly, filtering)
- ExecutionRegistry (tool/command lookup, execution)
- PortRuntime (route_prompt, bootstrap_session, turn_loop)
- Session persistence (save, load, list, search, delete)
- ToolRegistry enhancements (permissions, MCP, bulk, config)
- SkillRegistry enhancements (folder, import, portability, export)
- ChatHarness session persistence + PortRuntime integration
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "backend"))


class TestToolPermissionContext(unittest.TestCase):
    """Test ToolPermissionContext — deny_names + deny_prefixes."""

    def test_empty_context_blocks_nothing(self):
        from agents.execution_registry import ToolPermissionContext
        ctx = ToolPermissionContext()
        self.assertFalse(ctx.blocks("anything"))

    def test_deny_names(self):
        from agents.execution_registry import ToolPermissionContext
        ctx = ToolPermissionContext.from_lists(deny_names=["run_shell", "run_python"])
        self.assertTrue(ctx.blocks("run_shell"))
        self.assertTrue(ctx.blocks("RUN_SHELL"))  # case-insensitive
        self.assertFalse(ctx.blocks("web_search"))

    def test_deny_prefixes(self):
        from agents.execution_registry import ToolPermissionContext
        ctx = ToolPermissionContext.from_lists(deny_prefixes=["dt_", "run_"])
        self.assertTrue(ctx.blocks("dt_camera_move"))
        self.assertTrue(ctx.blocks("run_python"))
        self.assertFalse(ctx.blocks("web_search"))

    def test_combined_deny(self):
        from agents.execution_registry import ToolPermissionContext
        ctx = ToolPermissionContext.from_lists(
            deny_names=["web_search"],
            deny_prefixes=["dt_"],
        )
        self.assertTrue(ctx.blocks("web_search"))
        self.assertTrue(ctx.blocks("dt_light_adjust"))
        self.assertFalse(ctx.blocks("ais_query"))


class TestHistoryLog(unittest.TestCase):
    """Test HistoryLog event tracking."""

    def test_add_and_list(self):
        from agents.execution_registry import HistoryLog
        log = HistoryLog()
        log.add("init", "started")
        log.add("routing", "3 matches")
        self.assertEqual(len(log.events), 2)
        self.assertEqual(log.events[0].title, "init")

    def test_as_markdown(self):
        from agents.execution_registry import HistoryLog
        log = HistoryLog()
        log.add("test", "detail value")
        md = log.as_markdown()
        self.assertIn("# Session History", md)
        self.assertIn("test: detail value", md)

    def test_to_list(self):
        from agents.execution_registry import HistoryLog
        log = HistoryLog()
        log.add("a", "b")
        items = log.to_list()
        self.assertEqual(len(items), 1)
        self.assertIn("title", items[0])
        self.assertIn("timestamp", items[0])


class TestTranscriptStore(unittest.TestCase):
    """Test TranscriptStore — append, compact, flush, replay."""

    def test_append_and_replay(self):
        from agents.session_store import TranscriptStore
        ts = TranscriptStore()
        ts.append("msg1")
        ts.append("msg2")
        self.assertEqual(len(ts.replay()), 2)

    def test_compact(self):
        from agents.session_store import TranscriptStore
        ts = TranscriptStore()
        for i in range(20):
            ts.append(f"msg{i}")
        ts.compact(5)
        self.assertEqual(len(ts.entries), 5)
        self.assertEqual(ts.entries[0], "msg15")

    def test_flush(self):
        from agents.session_store import TranscriptStore
        ts = TranscriptStore()
        self.assertFalse(ts.flushed)
        ts.flush()
        self.assertTrue(ts.flushed)

    def test_clear(self):
        from agents.session_store import TranscriptStore
        ts = TranscriptStore()
        ts.append("hello")
        ts.flush()
        ts.clear()
        self.assertEqual(len(ts.entries), 0)
        self.assertFalse(ts.flushed)


class TestToolPool(unittest.TestCase):
    """Test ToolPool assembly with filtering."""

    def test_assemble_default(self):
        from agents.execution_registry import assemble_tool_pool
        pool = assemble_tool_pool()
        self.assertGreater(pool.tool_count, 0)
        self.assertFalse(pool.simple_mode)

    def test_simple_mode(self):
        from agents.execution_registry import assemble_tool_pool
        pool = assemble_tool_pool(simple_mode=True)
        self.assertTrue(pool.simple_mode)
        self.assertLessEqual(pool.tool_count, 5)

    def test_permission_filtering(self):
        from agents.execution_registry import assemble_tool_pool, ToolPermissionContext
        ctx = ToolPermissionContext.from_lists(deny_names=["web_search"])
        pool_no_filter = assemble_tool_pool()
        pool_filtered = assemble_tool_pool(permission_context=ctx)
        self.assertIn("web_search", pool_no_filter.tool_names)
        self.assertNotIn("web_search", pool_filtered.tool_names)

    def test_as_markdown(self):
        from agents.execution_registry import assemble_tool_pool
        pool = assemble_tool_pool(simple_mode=True)
        md = pool.as_markdown()
        self.assertIn("# Tool Pool", md)
        self.assertIn("Simple mode: True", md)


class TestExecutionRegistry(unittest.TestCase):
    """Test ExecutionRegistry — tool/command lookup."""

    def test_build_and_lookup_tool(self):
        from agents.execution_registry import build_execution_registry
        reg = build_execution_registry()
        self.assertIsNotNone(reg.tool("web_search"))
        self.assertIsNotNone(reg.tool("ais_query"))
        self.assertIsNone(reg.tool("nonexistent_tool"))

    def test_lookup_command(self):
        from agents.execution_registry import build_execution_registry
        reg = build_execution_registry()
        self.assertIsNotNone(reg.command("help"))
        self.assertIsNotNone(reg.command("status"))
        self.assertIsNone(reg.command("nonexistent_cmd"))

    def test_execute_command(self):
        from agents.execution_registry import build_execution_registry
        reg = build_execution_registry()
        result = reg.execute_command("help", "test prompt")
        self.assertTrue(result.handled)
        self.assertEqual(result.kind, "command")
        self.assertIn("help", result.output)

    def test_execute_command_unknown(self):
        from agents.execution_registry import build_execution_registry
        reg = build_execution_registry()
        result = reg.execute_command("nonexistent")
        self.assertFalse(result.handled)
        self.assertIn("Unknown command", result.error)

    def test_execute_tool(self):
        from agents.execution_registry import build_execution_registry
        reg = build_execution_registry()
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(reg.execute_tool("web_search"))
        loop.close()
        self.assertEqual(result.kind, "tool")
        self.assertGreater(result.duration_ms, 0)


class TestPortRuntime(unittest.TestCase):
    """Test PortRuntime — routing, bootstrap, turn loop."""

    def test_route_prompt_finds_tools(self):
        from agents.execution_registry import PortRuntime
        rt = PortRuntime()
        matches = rt.route_prompt("weather forecast for navigation")
        self.assertGreater(len(matches), 0)
        names = [m.name for m in matches]
        self.assertTrue(any("weather" in n for n in names))

    def test_route_prompt_respects_permissions(self):
        from agents.execution_registry import PortRuntime, ToolPermissionContext
        ctx = ToolPermissionContext.from_lists(deny_names=["weather_fetch"])
        rt = PortRuntime(permission_context=ctx)
        matches = rt.route_prompt("weather forecast")
        names = [m.name for m in matches]
        self.assertNotIn("weather_fetch", names)

    def test_route_prompt_empty(self):
        from agents.execution_registry import PortRuntime
        rt = PortRuntime()
        matches = rt.route_prompt("zzzzz xyz no match")
        # May or may not match; just ensure no crash
        self.assertIsInstance(matches, list)

    def test_bootstrap_session(self):
        from agents.execution_registry import PortRuntime
        rt = PortRuntime()
        loop = asyncio.new_event_loop()
        session = loop.run_until_complete(rt.bootstrap_session("engine status check"))
        loop.close()
        self.assertEqual(session.prompt, "engine status check")
        self.assertGreater(len(session.history.events), 0)

    def test_run_turn_loop(self):
        from agents.execution_registry import PortRuntime
        rt = PortRuntime()
        loop = asyncio.new_event_loop()
        results = loop.run_until_complete(rt.run_turn_loop("ais query", max_turns=2))
        loop.close()
        self.assertGreaterEqual(len(results), 1)
        self.assertLessEqual(len(results), 2)


class TestSessionPersistence(unittest.TestCase):
    """Test session save/load/list/search/delete."""

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self._dir = Path(self._tmpdir)

    def tearDown(self):
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_save_and_load(self):
        from agents.session_store import StoredSession, save_session, load_session
        s = StoredSession(session_id="test1", agent_id="agent_a",
                          messages=["hello", "world"], input_tokens=10, output_tokens=20)
        path = save_session(s, self._dir)
        self.assertTrue(path.exists())

        loaded = load_session("test1", self._dir)
        self.assertEqual(loaded.session_id, "test1")
        self.assertEqual(loaded.agent_id, "agent_a")
        self.assertEqual(len(loaded.messages), 2)

    def test_list_sessions(self):
        from agents.session_store import StoredSession, save_session, list_sessions
        save_session(StoredSession(session_id="s1", messages=["a"]), self._dir)
        save_session(StoredSession(session_id="s2", messages=["b"]), self._dir)
        ids = list_sessions(self._dir)
        self.assertIn("s1", ids)
        self.assertIn("s2", ids)

    def test_search_sessions(self):
        from agents.session_store import StoredSession, save_session, search_sessions
        save_session(StoredSession(session_id="s1", messages=["航线规划"]), self._dir)
        save_session(StoredSession(session_id="s2", messages=["天气预报"]), self._dir)
        results = search_sessions("航线", self._dir)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].session_id, "s1")

    def test_delete_session(self):
        from agents.session_store import StoredSession, save_session, delete_session, list_sessions
        save_session(StoredSession(session_id="del_me", messages=["x"]), self._dir)
        self.assertIn("del_me", list_sessions(self._dir))
        deleted = delete_session("del_me", self._dir)
        self.assertTrue(deleted)
        self.assertNotIn("del_me", list_sessions(self._dir))

    def test_delete_nonexistent(self):
        from agents.session_store import delete_session
        self.assertFalse(delete_session("no_such_session", self._dir))


class TestToolRegistryEnhancements(unittest.TestCase):
    """Test ToolRegistry: permissions, MCP, bulk, config."""

    def test_list_with_permissions(self):
        from agents.tool_registry import ToolRegistry
        from agents.execution_registry import ToolPermissionContext
        reg = ToolRegistry()
        reg.load_defaults()
        ctx = ToolPermissionContext.from_lists(deny_names=["run_shell"], deny_prefixes=["dt_"])
        filtered = reg.list_with_permissions(ctx)
        names = [t.name for t in filtered]
        self.assertNotIn("run_shell", names)
        self.assertTrue(all(not n.startswith("dt_") for n in names))

    def test_simple_mode(self):
        from agents.tool_registry import ToolRegistry
        reg = ToolRegistry()
        reg.load_defaults()
        simple = reg.list_with_permissions(simple_mode=True)
        self.assertLessEqual(len(simple), 5)

    def test_register_mcp_tool(self):
        from agents.tool_registry import ToolRegistry
        reg = ToolRegistry()
        reg.load_defaults()
        tool = reg.register_mcp_tool("my_mcp", "Test MCP", mcp_server_url="http://localhost:9090")
        self.assertEqual(tool.source, "mcp")
        self.assertIsNotNone(reg.get_by_name("my_mcp"))
        # Cleanup
        reg.unregister_tool(tool.tool_id)
        self.assertIsNone(reg.get_by_name("my_mcp"))

    def test_bulk_update_enabled(self):
        from agents.tool_registry import ToolRegistry
        reg = ToolRegistry()
        reg.load_defaults()
        updated = reg.bulk_update_enabled([
            {"tool_id": "web_search", "enabled": False},
            {"tool_id": "ais_query", "enabled": False},
        ])
        self.assertEqual(updated, 2)

    def test_update_and_get_config(self):
        from agents.tool_registry import ToolRegistry
        reg = ToolRegistry()
        reg.load_defaults()
        tool = reg.register_mcp_tool("cfg_test", "Config test")
        reg.update_tool_config(tool.tool_id, {"api_key": "sk-test", "timeout": 30})
        config = reg.get_tool_config(tool.tool_id)
        self.assertEqual(config["api_key"], "sk-test")
        self.assertEqual(config["timeout"], 30)


class TestSkillRegistryEnhancements(unittest.TestCase):
    """Test SkillRegistry: folder, import, portability, export."""

    def test_get_skill_folder(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        reg.load_defaults()
        sid = list(reg._skills.keys())[0]
        folder = reg.get_skill_folder(sid)
        self.assertIn("files", folder)
        self.assertGreater(len(folder["files"]), 0)

    def test_get_skill_folder_not_found(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        folder = reg.get_skill_folder("nonexistent")
        self.assertIn("error", folder)

    def test_import_from_instructions_with_frontmatter(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        content = "---\nname: Test Skill\ndescription: A test\nicon: 🧪\n---\n\n## Instructions\nDo the test."
        skill = reg.import_from_instructions("fallback_name", content)
        self.assertEqual(skill.name, "Test Skill")
        self.assertIn("Instructions", skill.instructions)

    def test_import_from_instructions_no_frontmatter(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        content = "## Simple Skill\nJust do it."
        skill = reg.import_from_instructions("simple_skill", content)
        self.assertEqual(skill.name, "simple_skill")

    def test_classify_portability_tier1(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        skill = reg.create_skill("prompt_only", instructions="Just talk.")
        self.assertEqual(reg.classify_portability(skill.skill_id), 1)

    def test_classify_portability_tier2(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        skill = reg.create_skill("cli_skill", instructions="Use run_python to execute.",
                                 required_tools=["run_python"])
        self.assertEqual(reg.classify_portability(skill.skill_id), 2)

    def test_classify_portability_tier3(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        skill = reg.create_skill("platform_skill",
                                 instructions="Call channel.process_event() to trigger.")
        self.assertEqual(reg.classify_portability(skill.skill_id), 3)

    def test_export_all_as_markdown(self):
        from agents.skill_registry import SkillRegistry
        reg = SkillRegistry()
        reg.load_defaults()
        md = reg.export_all_as_markdown()
        self.assertIn("# PoseidonX Skill Registry", md)
        self.assertIn("Tier", md)


class TestChatSessionEnhancements(unittest.TestCase):
    """Test ChatSession with HistoryLog and TranscriptStore."""

    def test_session_has_history(self):
        from agents.chat_harness import ChatSession
        session = ChatSession(agent_id="test")
        session.add_user_message("hello")
        session.add_assistant_message("hi there")
        self.assertEqual(len(session.history.events), 2)

    def test_session_has_transcript(self):
        from agents.chat_harness import ChatSession
        session = ChatSession()
        session.add_user_message("msg1")
        session.add_assistant_message("reply1")
        self.assertEqual(len(session.transcript.entries), 2)
        self.assertEqual(session.transcript.entries[0], "msg1")

    def test_session_to_dict_includes_new_fields(self):
        from agents.chat_harness import ChatSession
        session = ChatSession()
        session.add_user_message("test")
        d = session.to_dict()
        self.assertIn("transcript_size", d)
        self.assertIn("history_events", d)
        self.assertIn("permission_denials", d)

    def test_session_replay(self):
        from agents.chat_harness import ChatSession
        session = ChatSession()
        session.add_user_message("a")
        session.add_user_message("b")
        replay = session.replay_messages()
        self.assertEqual(len(replay), 2)


class TestChatHarnessPortRuntime(unittest.TestCase):
    """Test ChatHarness PortRuntime integration."""

    def test_get_port_runtime(self):
        from agents.chat_harness import ChatHarness
        harness = ChatHarness()
        rt = harness.get_port_runtime()
        from agents.execution_registry import PortRuntime
        self.assertIsInstance(rt, PortRuntime)

    def test_get_port_runtime_with_permissions(self):
        from agents.chat_harness import ChatHarness, ToolPermissionContext
        harness = ChatHarness()
        ctx = ToolPermissionContext.from_lists(deny_names=["run_shell"])
        rt = harness.get_port_runtime(ctx)
        matches = rt.route_prompt("run shell command")
        names = [m.name for m in matches]
        self.assertNotIn("run_shell", names)

    def test_list_persisted_sessions(self):
        from agents.chat_harness import ChatHarness
        harness = ChatHarness()
        # Should return a list (may be empty)
        sessions = harness.list_persisted_sessions()
        self.assertIsInstance(sessions, list)

    def test_search_persisted_sessions(self):
        from agents.chat_harness import ChatHarness
        harness = ChatHarness()
        results = harness.search_persisted_sessions("nonexistent_query_xyz")
        self.assertIsInstance(results, list)


class TestPermissionDenialDataclass(unittest.TestCase):
    """Test PermissionDenial frozen dataclass."""

    def test_creation(self):
        from agents.execution_registry import PermissionDenial
        d = PermissionDenial(tool_name="run_shell", reason="Blocked by policy")
        self.assertEqual(d.tool_name, "run_shell")
        self.assertEqual(d.reason, "Blocked by policy")

    def test_frozen(self):
        from agents.execution_registry import PermissionDenial
        d = PermissionDenial(tool_name="x", reason="y")
        with self.assertRaises(AttributeError):
            d.tool_name = "z"


class TestRoutedMatch(unittest.TestCase):
    """Test RoutedMatch frozen dataclass."""

    def test_creation(self):
        from agents.execution_registry import RoutedMatch
        m = RoutedMatch(kind="tool", name="web_search", source_hint="registry", score=3)
        self.assertEqual(m.kind, "tool")
        self.assertEqual(m.score, 3)


class TestRuntimeSession(unittest.TestCase):
    """Test RuntimeSession as_markdown output."""

    def test_as_markdown(self):
        from agents.execution_registry import RuntimeSession, HistoryLog
        session = RuntimeSession(prompt="test prompt", history=HistoryLog())
        session.history.add("test", "detail")
        md = session.as_markdown()
        self.assertIn("# Runtime Session", md)
        self.assertIn("test prompt", md)
        self.assertIn("Session History", md)


if __name__ == "__main__":
    unittest.main()
