# -*- coding: utf-8 -*-
"""Comprehensive tests for src.backend.agents -- models, registries, manager, teams."""

import pytest

from src.backend.agents.models import (
    AccessLevel,
    AgentChannelConfig,
    AgentPermission,
    AgentPersonality,
    AgentProfile,
    AgentState,
    AgentTeam,
    AgentTemplateType,
    ModelConfig,
    SkillCategory,
    SkillDefinition,
    ToolCategory,
    ToolDefinition,
    Visibility,
)
from src.backend.agents.tool_registry import ToolRegistry, get_default_tools
from src.backend.agents.skill_registry import SkillRegistry, get_default_skills
from src.backend.agents.team_manager import TeamManager
from src.backend.agents.teams.build_team import create_build_team
from src.backend.agents.teams.execution_team import create_execution_team


# =========================================================================
# Models (8 tests)
# =========================================================================


class TestModelConfig:
    def test_model_config_defaults(self):
        m = ModelConfig()
        assert m.provider == "anthropic"
        assert m.name == "claude-sonnet-4-20250514"
        assert m.max_tokens == 8192
        assert m.temperature == 0.7
        assert m.is_default is False
        assert m.enabled is True
        assert len(m.model_id) == 8

    def test_model_config_to_dict(self):
        m = ModelConfig(model_id="test1", provider="openai", name="gpt-4", max_tokens=4096)
        d = m.to_dict()
        assert d["model_id"] == "test1"
        assert d["provider"] == "openai"
        assert d["name"] == "gpt-4"
        assert d["max_tokens"] == 4096
        assert isinstance(d, dict)
        assert set(d.keys()) == {
            "model_id", "provider", "name", "max_tokens",
            "temperature", "is_default", "enabled", "api_key", "api_base_url", "has_api_key",
        }


class TestAgentProfile:
    def test_agent_profile_defaults(self):
        a = AgentProfile()
        assert a.name == ""
        assert a.role == ""
        assert a.state == AgentState.IDLE
        assert a.template_type == AgentTemplateType.CUSTOM
        assert a.model_id == ""
        assert a.system_prompt == ""
        assert isinstance(a.personality, AgentPersonality)
        assert isinstance(a.permissions, list)
        assert isinstance(a.channels, list)
        assert isinstance(a.tools, list)
        assert isinstance(a.skills, list)
        assert len(a.agent_id) == 8

    def test_agent_profile_to_dict(self):
        a = AgentProfile(
            agent_id="ag1", name="Navigator", role="nav",
            description="Test navigator",
            template_type=AgentTemplateType.NAVIGATOR,
            model_id="m1",
            system_prompt="Navigate the ship",
            skills=["route_optimization"],
            tools=["ais_query"],
        )
        d = a.to_dict()
        assert d["agent_id"] == "ag1"
        assert d["name"] == "Navigator"
        assert d["role"] == "nav"
        assert d["template_type"] == "navigator"
        assert d["state"] == "idle"
        assert d["skills"] == ["route_optimization"]
        assert d["tools"] == ["ais_query"]
        assert isinstance(d["personality"], dict)
        assert "created_at" in d


class TestAgentTeam:
    def test_agent_team_add_remove_agent(self):
        team = AgentTeam(team_id="t1", name="Test")
        a1 = AgentProfile(agent_id="a1", name="Alpha")
        a2 = AgentProfile(agent_id="a2", name="Beta")
        team.add_agent(a1)
        team.add_agent(a2)
        assert len(team.agents) == 2
        assert team.get_agent("a1") is a1
        removed = team.remove_agent("a1")
        assert removed is a1
        assert len(team.agents) == 1
        assert team.get_agent("a1") is None
        assert team.remove_agent("nonexistent") is None

    def test_agent_team_add_remove_model(self):
        team = AgentTeam(team_id="t1", name="Test")
        m1 = ModelConfig(model_id="m1", name="model-a")
        m2 = ModelConfig(model_id="m2", name="model-b")
        team.add_model(m1)
        team.add_model(m2)
        assert len(team.models) == 2
        assert team.get_model("m1") is m1
        removed = team.remove_model("m1")
        assert removed is m1
        assert len(team.models) == 1
        assert team.remove_model("nonexistent") is None

    def test_agent_team_to_dict(self):
        team = AgentTeam(team_id="t1", name="TestTeam", description="desc")
        team.add_agent(AgentProfile(agent_id="a1", name="X"))
        team.add_model(ModelConfig(model_id="m1"))
        d = team.to_dict()
        assert d["team_id"] == "t1"
        assert d["name"] == "TestTeam"
        assert d["description"] == "desc"
        assert d["visibility"] == "private"
        assert "a1" in d["agents"]
        assert "m1" in d["models"]
        assert isinstance(d["tools"], dict)
        assert isinstance(d["skills"], dict)
        assert "created_at" in d


class TestAgentPersonality:
    def test_agent_personality_to_dict(self):
        p = AgentPersonality(
            tone="calm", language="en-US",
            expertise_areas=["navigation", "weather"],
            response_style="verbose", creativity=0.8,
        )
        d = p.to_dict()
        assert d["tone"] == "calm"
        assert d["language"] == "en-US"
        assert d["expertise_areas"] == ["navigation", "weather"]
        assert d["response_style"] == "verbose"
        assert d["creativity"] == 0.8


# =========================================================================
# ToolRegistry (5 tests)
# =========================================================================


class TestToolRegistry:
    def test_tool_registry_load_defaults(self):
        tr = ToolRegistry()
        tr.load_defaults()
        assert len(tr.list_all()) == 53

    def test_tool_registry_list_by_category(self):
        tr = ToolRegistry()
        tr.load_defaults()
        browser_tools = tr.list_by_category(ToolCategory.BROWSER)
        assert len(browser_tools) == 6
        maritime_tools = tr.list_by_category(ToolCategory.MARITIME)
        assert len(maritime_tools) == 8
        dt_tools = tr.list_by_category(ToolCategory.DIGITAL_TWIN)
        assert len(dt_tools) == 8

    def test_tool_registry_enable_disable(self):
        tr = ToolRegistry()
        tr.load_defaults()
        all_tools = tr.list_all()
        tid = all_tools[0].tool_id
        assert tr.disable(tid) is True
        assert tr.get(tid).enabled is False
        assert len(tr.list_enabled()) == 52
        assert tr.enable(tid) is True
        assert tr.get(tid).enabled is True
        assert len(tr.list_enabled()) == 53
        assert tr.disable("nonexistent") is False
        assert tr.enable("nonexistent") is False

    def test_tool_registry_to_dict(self):
        tr = ToolRegistry()
        tr.load_defaults()
        d = tr.to_dict()
        assert isinstance(d, dict)
        assert len(d) == 53
        for tid, tdict in d.items():
            assert "tool_id" in tdict
            assert "name" in tdict
            assert "category" in tdict

    def test_tool_categories_covered(self):
        tr = ToolRegistry()
        tr.load_defaults()
        categories_present = {t.category for t in tr.list_all()}
        for cat in ToolCategory:
            assert cat in categories_present, "Missing category: " + str(cat)
        assert len(categories_present) == 17


# =========================================================================
# SkillRegistry (5 tests)
# =========================================================================


class TestSkillRegistry:
    def test_skill_registry_load_defaults(self):
        sr = SkillRegistry()
        sr.load_defaults()
        assert len(sr.list_all()) == 42

    def test_skill_registry_list_required(self):
        sr = SkillRegistry()
        sr.load_defaults()
        required = sr.list_required()
        assert len(required) == 3
        required_names = {s.name for s in required}
        assert required_names == {"complex_task_executor", "mcp_installer", "skill_creator"}

    def test_skill_registry_list_by_category(self):
        sr = SkillRegistry()
        sr.load_defaults()
        general = sr.list_by_category(SkillCategory.GENERAL)
        assert len(general) == 9
        dt = sr.list_by_category(SkillCategory.DIGITAL_TWIN)
        assert len(dt) == 9
        maritime = sr.list_by_category(SkillCategory.MARITIME)
        assert len(maritime) == 6

    def test_skill_registry_to_dict(self):
        sr = SkillRegistry()
        sr.load_defaults()
        d = sr.to_dict()
        assert isinstance(d, dict)
        assert len(d) == 42
        for sid, sdict in d.items():
            assert "skill_id" in sdict
            assert "name" in sdict
            assert "category" in sdict

    def test_skill_categories_covered(self):
        sr = SkillRegistry()
        sr.load_defaults()
        categories = {s.category for s in sr.list_all()}
        for cat in SkillCategory:
            assert cat in categories, "Missing category: " + str(cat)
        assert len(categories) == 12


# =========================================================================
# TeamManager (6 tests)
# =========================================================================


class TestTeamManager:
    def test_create_team(self):
        tm = TeamManager()
        team = tm.create_team("NavTeam", description="Navigation team")
        assert team.name == "NavTeam"
        assert team.description == "Navigation team"
        assert len(team.team_id) > 0

    def test_get_team(self):
        tm = TeamManager()
        team = tm.create_team("T1")
        fetched = tm.get_team(team.team_id)
        assert fetched is team
        assert tm.get_team("nonexistent") is None

    def test_list_teams(self):
        tm = TeamManager()
        assert len(tm.list_teams()) == 0
        tm.create_team("A")
        tm.create_team("B")
        assert len(tm.list_teams()) == 2

    def test_delete_team(self):
        tm = TeamManager()
        team = tm.create_team("Del")
        tid = team.team_id
        removed = tm.delete_team(tid)
        assert removed is team
        assert tm.get_team(tid) is None
        assert tm.delete_team(tid) is None

    def test_add_agent_to_team(self):
        tm = TeamManager()
        team = tm.create_team("T")
        agent = AgentProfile(agent_id="a1", name="Nav")
        assert tm.add_agent_to_team(team.team_id, agent) is True
        assert tm.get_agent(team.team_id, "a1") is agent
        assert tm.add_agent_to_team("nonexistent", agent) is False

    def test_team_overview(self):
        tm = TeamManager()
        team = tm.create_team("Overview")
        a1 = AgentProfile(agent_id="a1", name="Alpha", role="r1")
        a2 = AgentProfile(agent_id="a2", name="Beta", role="r2")
        tm.add_agent_to_team(team.team_id, a1)
        tm.add_agent_to_team(team.team_id, a2)
        ov = tm.get_team_overview(team.team_id)
        assert ov is not None
        assert ov["agent_count"] == 2
        assert ov["name"] == "Overview"
        assert len(ov["agents"]) == 2
        agents_by_id = {a["agent_id"]: a for a in ov["agents"]}
        assert agents_by_id["a1"]["name"] == "Alpha"
        assert agents_by_id["a2"]["state"] == "idle"
        assert tm.get_team_overview("nonexistent") is None


# =========================================================================
# Build Team (3 tests)
# =========================================================================


class TestBuildTeam:
    def test_create_build_team_agents(self):
        team = create_build_team()
        assert len(team.agents) == 7
        agent_ids = set(team.agents.keys())
        expected = {
            "build_pm", "build_researcher", "build_architect",
            "build_developer", "build_tester", "build_deployer",
            "build_doc_writer",
        }
        assert agent_ids == expected

    def test_create_build_team_models(self):
        team = create_build_team()
        assert len(team.models) == 2
        model_ids = set(team.models.keys())
        assert model_ids == {"copilot", "deepseek"}
        assert team.models["copilot"].is_default is True

    def test_build_team_serialization(self):
        team = create_build_team()
        d = team.to_dict()
        assert d["team_id"] == "build_system"
        assert d["name"] == "PoseidonX Build System"
        assert len(d["agents"]) == 7
        assert len(d["models"]) == 2
        for aid, adict in d["agents"].items():
            assert "name" in adict
            assert "role" in adict
            assert "personality" in adict
            assert isinstance(adict["personality"], dict)


# =========================================================================
# Execution Team (3 tests)
# =========================================================================


class TestExecutionTeam:
    def test_create_execution_team_agents(self):
        team = create_execution_team()
        assert len(team.agents) == 10
        ship_ids = {
            "ship_captain", "ship_chief_officer", "ship_second_officer",
            "ship_route_planner", "ship_navigator", "ship_engineer",
        }
        shore_ids = {
            "shore_expert", "shore_safety", "shore_planner", "shore_dispatcher",
        }
        agent_ids = set(team.agents.keys())
        assert ship_ids.issubset(agent_ids)
        assert shore_ids.issubset(agent_ids)
        assert agent_ids == ship_ids | shore_ids

    def test_create_execution_team_models(self):
        team = create_execution_team()
        assert len(team.models) == 2
        model_ids = set(team.models.keys())
        assert model_ids == {"qwen_plus", "deepseek_v3"}
        assert team.models["qwen_plus"].is_default is True

    def test_execution_team_serialization(self):
        team = create_execution_team()
        d = team.to_dict()
        assert d["team_id"] == "execution_system"
        assert d["name"] == "PoseidonX Execution System"
        assert len(d["agents"]) == 10
        assert len(d["models"]) == 2
        for aid, adict in d["agents"].items():
            assert "name" in adict
            assert "role" in adict
            assert "personality" in adict
            assert "permissions" in adict
            assert "channels" in adict
            assert len(adict["permissions"]) > 0
            assert len(adict["channels"]) > 0


# Bridge Command Integration tests
class TestBridgeCommandIntegration:
    def test_classify_camera_intent(self):
        from src.backend.agents.api import _classify_bridge_intent
        assert _classify_bridge_intent("top view") == "dt_camera_control"
        assert _classify_bridge_intent("front view") == "dt_camera_control"
        assert _classify_bridge_intent("iso view") == "dt_camera_control"

    def test_classify_navigation_intent(self):
        from src.backend.agents.api import _classify_bridge_intent
        assert _classify_bridge_intent("route to shanghai") == "navigation_assessment"
        assert _classify_bridge_intent("navigate heading 270") == "navigation_assessment"

    def test_classify_engine_intent(self):
        from src.backend.agents.api import _classify_bridge_intent
        assert _classify_bridge_intent("engine rpm") == "engine_diagnostics"

    def test_classify_colregs_intent(self):
        from src.backend.agents.api import _classify_bridge_intent
        assert _classify_bridge_intent("collision risk") == "colregs_compliance"

    def test_classify_general_intent(self):
        from src.backend.agents.api import _classify_bridge_intent
        assert _classify_bridge_intent("hello") == "general_assist"

    def test_find_agent_no_teams(self):
        from src.backend.agents.api import _find_agent_for_skill
        team, agent = _find_agent_for_skill("dt_camera_control")
        # May or may not find depending on init state; just verify no crash
        assert team is None or hasattr(team, 'team_id')

    def test_parse_tool_invocations_empty(self):
        from src.backend.agents.api import _parse_tool_invocations
        result = _parse_tool_invocations("hello world")
        assert result == []

    def test_parse_tool_invocations_with_tool(self):
        from src.backend.agents.api import _parse_tool_invocations
        text = "执行工具: dt_camera_move\n参数: { \"view_preset\": \"top\" }"
        result = _parse_tool_invocations(text)
        assert len(result) == 1
        assert result[0]["tool"] == "dt_camera_move"

    def test_bridge_command_endpoint_no_agent(self):
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from src.backend.agents.api import router, init_agent_config
        from src.backend.agents.team_manager import TeamManager

        app = FastAPI()
        app.include_router(router)
        init_agent_config(TeamManager())

        client = TestClient(app)
        resp = client.post("/api/v1/agent-config/bridge/command", json={"command": "top view"})
        assert resp.status_code == 200
        data = resp.json()
        assert "handled" in data
        assert "intent" in data
        assert data["intent"] == "dt_camera_control"


# =========================================================================
# Hermes Research Agent (10 tests)
# =========================================================================


class TestHermesResearchAgent:
    """Tests for the Hermes-style self-improving research agent."""

    def test_create_hermes_researcher(self):
        from src.backend.agents.hermes_research import create_hermes_researcher
        agent = create_hermes_researcher("test_researcher")
        assert agent.name == "test_researcher"
        assert agent.is_hermes_agent is True
        assert agent.hermes_config is not None
        assert agent.template_type == AgentTemplateType.HERMES_RESEARCHER

    def test_hermes_config_defaults(self):
        from src.backend.agents.models import HermesAgentConfig
        cfg = HermesAgentConfig()
        assert cfg.max_iterations == 90
        assert cfg.memory_enabled is True
        assert cfg.session_search_enabled is True
        assert cfg.skill_auto_create is True
        assert cfg.can_delegate is False
        assert cfg.max_subagents == 3

    def test_hermes_config_to_dict(self):
        from src.backend.agents.models import HermesAgentConfig
        cfg = HermesAgentConfig(max_iterations=50, soul_md="test soul")
        d = cfg.to_dict()
        assert d["max_iterations"] == 50
        assert d["soul_md"] == "test soul"
        assert "memory_enabled" in d
        assert "toolset_distribution" in d

    def test_agent_profile_is_hermes(self):
        from src.backend.agents.hermes_research import create_hermes_researcher
        agent = create_hermes_researcher("h_test")
        assert agent.is_hermes_agent is True
        d = agent.to_dict()
        assert d["is_hermes_agent"] is True
        assert "hermes_config" in d

    def test_non_hermes_agent_flag(self):
        agent = AgentProfile(agent_id="std", name="Standard Agent")
        assert agent.is_hermes_agent is False
        d = agent.to_dict()
        assert d["is_hermes_agent"] is False

    def test_sample_toolsets_returns_list(self):
        from src.backend.agents.hermes_research import sample_toolsets
        result = sample_toolsets("maritime_research")
        assert isinstance(result, list)
        assert len(result) >= 1  # at least one toolset guaranteed

    def test_sample_toolsets_fallback(self):
        from src.backend.agents.hermes_research import sample_toolsets
        result = sample_toolsets("nonexistent_distribution")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_resolve_tools(self):
        from src.backend.agents.hermes_research import resolve_tools
        tools = resolve_tools(["web", "maritime"])
        assert isinstance(tools, list)
        assert "web_search" in tools
        assert "chart_lookup" in tools

    def test_research_distributions_complete(self):
        from src.backend.agents.hermes_research import get_research_distributions
        dists = get_research_distributions()
        assert len(dists) == 5
        assert "maritime_research" in dists
        assert "colregs_analysis" in dists
        assert "compliance_audit" in dists

    def test_hermes_toolsets_complete(self):
        from src.backend.agents.hermes_research import get_hermes_toolsets
        ts = get_hermes_toolsets()
        assert len(ts) == 9
        assert "web" in ts
        assert "maritime" in ts
        assert "memory" in ts
        assert "delegation" in ts
