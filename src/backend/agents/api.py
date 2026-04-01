# -*- coding: utf-8 -*-
"""PoseidonX Agent Team Framework -- REST API Router.

Clawith-style CRUD API for teams, agents, models, tools, skills.
Tab-based organization:
  1. Team Info
  2. Model Pool
  3. Tools
  4. Skills
  5. Agents -- 5-step wizard
  6. Overview
"""

from __future__ import annotations

from datetime import datetime, timezone

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from .models import (
    AccessLevel,
    AgentState,
    AgentChannelConfig,
    AgentPermission,
    AgentPersonality,
    AgentProfile,
    AgentTemplateType,
    HermesAgentConfig,
    ModelConfig,
    ToolsetDistribution,
)
from .hermes_research import (
    RESEARCH_TOOLSET_DISTRIBUTIONS,
    HERMES_TOOLSETS,
    create_hermes_researcher,
    build_research_system_prompt,
    sample_toolsets,
    resolve_tools,
    get_research_distributions,
    get_hermes_toolsets,
)
from .skill_registry import SkillRegistry, get_default_skills
from .team_manager import TeamManager
from .tool_registry import ToolRegistry, get_default_tools


router = APIRouter(prefix="/api/v1/agent-config", tags=["agent-config"])


_team_manager: Optional[TeamManager] = None
_tool_registry: Optional[ToolRegistry] = None
_skill_registry: Optional[SkillRegistry] = None


def init_agent_config(team_manager: TeamManager) -> None:
    """Inject the TeamManager instance at startup."""
    global _team_manager, _tool_registry, _skill_registry
    _team_manager = team_manager
    _tool_registry = ToolRegistry()
    _tool_registry.load_defaults()
    _skill_registry = SkillRegistry()
    _skill_registry.load_defaults()


def _tm() -> TeamManager:
    if _team_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent config service not initialized",
        )
    return _team_manager


def _tr() -> ToolRegistry:
    if _tool_registry is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Tool registry not initialized",
        )
    return _tool_registry


def _sr() -> SkillRegistry:
    if _skill_registry is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Skill registry not initialized",
        )
    return _skill_registry


# Request / Response Models


class CreateTeamRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str = ""


class CreateModelRequest(BaseModel):
    provider: str = "anthropic"
    name: str = "claude-sonnet-4-20250514"
    max_tokens: int = Field(default=8192, ge=1, le=200000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    is_default: bool = False
    api_key: str = ""
    api_base_url: str = ""


class CreateAgentRequest(BaseModel):
    """Step 1 of agent wizard -- basic info."""
    name: str = Field(..., min_length=1, max_length=128)
    role: str = ""
    description: str = ""
    template_type: str = "custom"
    model_id: str = ""
    system_prompt: str = ""


class UpdatePersonalityRequest(BaseModel):
    """Step 2 -- personality config."""
    tone: str = "professional"
    language: str = "zh-CN"
    expertise_areas: List[str] = Field(default_factory=list)
    response_style: str = "concise"
    creativity: float = Field(default=0.5, ge=0.0, le=1.0)


class UpdateToolsRequest(BaseModel):
    """Assign tools to an agent."""
    tool_ids: List[str] = Field(default_factory=list)


class UpdateSkillsRequest(BaseModel):
    """Step 3 -- assign skills."""
    skill_ids: List[str] = Field(default_factory=list)


class PermissionItem(BaseModel):
    resource: str = ""
    access_level: str = "read"
    channels: List[str] = Field(default_factory=list)


class UpdatePermissionsRequest(BaseModel):
    """Step 4 -- permissions."""
    permissions: List[PermissionItem] = Field(default_factory=list)


class ChannelItem(BaseModel):
    channel_name: str = ""
    subscribe: bool = True
    publish: bool = False
    priority: int = 0


class UpdateChannelsRequest(BaseModel):
    """Step 5 -- channel subscriptions."""
    channels: List[ChannelItem] = Field(default_factory=list)


# TAB 1 -- TEAM INFO


@router.get("/teams", summary="List all teams")
def list_teams() -> List[Dict[str, Any]]:
    return [
        {
            "team_id": t.team_id,
            "name": t.name,
            "description": t.description,
            "agent_count": len(t.agents),
            "model_count": len(t.models),
        }
        for t in _tm().list_teams()
    ]


@router.get("/teams/{team_id}", summary="Get team detail")
def get_team(team_id: str) -> Dict[str, Any]:
    team = _tm().get_team(team_id)
    if team is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team.to_dict()


@router.post(
    "/teams",
    summary="Create team",
    status_code=status.HTTP_201_CREATED,
)
def create_team(req: CreateTeamRequest) -> Dict[str, Any]:
    team = _tm().create_team(name=req.name, description=req.description)
    return team.to_dict()


@router.delete("/teams/{team_id}", summary="Delete team")
def delete_team(team_id: str) -> Dict[str, str]:
    removed = _tm().delete_team(team_id)
    if removed is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Team not found")
    return {"deleted": team_id}


# TAB 2 -- MODEL POOL


def _get_team_or_404(team_id: str):
    team = _tm().get_team(team_id)
    if team is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team


@router.get("/teams/{team_id}/models", summary="List team models")
def list_models(team_id: str) -> List[Dict[str, Any]]:
    team = _get_team_or_404(team_id)
    return [m.to_dict() for m in team.models.values()]


@router.post(
    "/teams/{team_id}/models",
    summary="Add model to team",
    status_code=status.HTTP_201_CREATED,
)
def add_model(team_id: str, req: CreateModelRequest) -> Dict[str, Any]:
    team = _get_team_or_404(team_id)
    model = ModelConfig(
        provider=req.provider,
        name=req.name,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        is_default=req.is_default,
        api_key=req.api_key,
        api_base_url=req.api_base_url,
    )
    team.add_model(model)
    return model.to_dict()


@router.delete(
    "/teams/{team_id}/models/{model_id}",
    summary="Remove model from team",
)
def remove_model(team_id: str, model_id: str) -> Dict[str, str]:
    removed = _tm().remove_model_from_team(team_id, model_id)
    if removed is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Model not found")
    return {"deleted": model_id}


# TAB 3 -- TOOLS


@router.get("/tools", summary="List all available tools")
def list_all_tools() -> List[Dict[str, Any]]:
    return [t.to_dict() for t in _tr().list_all()]


@router.get("/teams/{team_id}/tools", summary="List team tools")
def list_team_tools(team_id: str) -> List[Dict[str, Any]]:
    team = _get_team_or_404(team_id)
    return [t.to_dict() for t in team.tools.values()]


@router.post(
    "/teams/{team_id}/tools/{tool_id}/enable",
    summary="Enable a tool for team",
)
def enable_tool(team_id: str, tool_id: str) -> Dict[str, Any]:
    team = _get_team_or_404(team_id)
    if tool_id not in team.tools:
        source = _tr().get(tool_id)
        if source is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail="Tool not found in registry"
            )
        team.add_tool(source)
    tool = team.tools[tool_id]
    tool.enabled = True
    return tool.to_dict()


@router.post(
    "/teams/{team_id}/tools/{tool_id}/disable",
    summary="Disable a tool for team",
)
def disable_tool(team_id: str, tool_id: str) -> Dict[str, Any]:
    team = _get_team_or_404(team_id)
    tool = team.tools.get(tool_id)
    if tool is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tool not found in team")
    tool.enabled = False
    return tool.to_dict()


# TAB 4 -- SKILLS


@router.get("/skills", summary="List all available skills")
def list_all_skills() -> List[Dict[str, Any]]:
    return [s.to_dict() for s in _sr().list_all()]


@router.get("/skills/required", summary="List required skills")
def list_required_skills() -> List[Dict[str, Any]]:
    return [s.to_dict() for s in _sr().list_required()]


@router.get("/teams/{team_id}/skills", summary="List team skills")
def list_team_skills(team_id: str) -> List[Dict[str, Any]]:
    team = _get_team_or_404(team_id)
    return [s.to_dict() for s in team.skills.values()]


# TAB 5 -- AGENTS (5-step wizard)


def _get_agent_or_404(team_id: str, agent_id: str) -> AgentProfile:
    agent = _tm().get_agent(team_id, agent_id)
    if agent is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


@router.get("/teams/{team_id}/agents", summary="List agents in team")
def list_agents(team_id: str) -> List[Dict[str, Any]]:
    _get_team_or_404(team_id)
    return [a.to_dict() for a in _tm().list_agents(team_id)]


@router.get("/teams/{team_id}/agents/{agent_id}", summary="Get agent detail")
def get_agent(team_id: str, agent_id: str) -> Dict[str, Any]:
    return _get_agent_or_404(team_id, agent_id).to_dict()


@router.post(
    "/teams/{team_id}/agents",
    summary="Create agent (wizard step 1)",
    status_code=status.HTTP_201_CREATED,
)
def create_agent(team_id: str, req: CreateAgentRequest) -> Dict[str, Any]:
    _get_team_or_404(team_id)
    try:
        tpl = AgentTemplateType(req.template_type)
    except ValueError:
        tpl = AgentTemplateType.CUSTOM
    agent = AgentProfile(
        name=req.name,
        role=req.role,
        description=req.description,
        template_type=tpl,
        model_id=req.model_id,
        system_prompt=req.system_prompt,
    )
    ok = _tm().add_agent_to_team(team_id, agent)
    if not ok:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add agent"
        )
    return agent.to_dict()


@router.put(
    "/teams/{team_id}/agents/{agent_id}/personality",
    summary="Update agent personality (wizard step 2)",
)
def update_personality(
    team_id: str, agent_id: str, req: UpdatePersonalityRequest
) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    agent.personality = AgentPersonality(
        tone=req.tone,
        language=req.language,
        expertise_areas=list(req.expertise_areas),
        response_style=req.response_style,
        creativity=req.creativity,
    )
    return agent.to_dict()


@router.put(
    "/teams/{team_id}/agents/{agent_id}/tools",
    summary="Update agent bound tools",
)
def update_agent_tools(
    team_id: str, agent_id: str, req: UpdateToolsRequest
) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    agent.tools = list(req.tool_ids)
    return agent.to_dict()


@router.put(
    "/teams/{team_id}/agents/{agent_id}/skills",
    summary="Update agent skills (wizard step 3)",
)
def update_agent_skills(
    team_id: str, agent_id: str, req: UpdateSkillsRequest
) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    agent.skills = list(req.skill_ids)
    return agent.to_dict()


@router.put(
    "/teams/{team_id}/agents/{agent_id}/permissions",
    summary="Update agent permissions (wizard step 4)",
)
def update_permissions(
    team_id: str, agent_id: str, req: UpdatePermissionsRequest
) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    perms = []
    for p in req.permissions:
        try:
            al = AccessLevel(p.access_level)
        except ValueError:
            al = AccessLevel.READ
        perms.append(
            AgentPermission(
                resource=p.resource,
                access_level=al,
                channels=list(p.channels),
            )
        )
    agent.permissions = perms
    return agent.to_dict()


@router.put(
    "/teams/{team_id}/agents/{agent_id}/channels",
    summary="Update agent channels (wizard step 5)",
)
def update_channels(
    team_id: str, agent_id: str, req: UpdateChannelsRequest
) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    agent.channels = [
        AgentChannelConfig(
            channel_name=c.channel_name,
            subscribe=c.subscribe,
            publish=c.publish,
            priority=c.priority,
        )
        for c in req.channels
    ]
    return agent.to_dict()


@router.delete(
    "/teams/{team_id}/agents/{agent_id}",
    summary="Remove agent from team",
)
def delete_agent(team_id: str, agent_id: str) -> Dict[str, str]:
    removed = _tm().remove_agent_from_team(team_id, agent_id)
    if removed is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return {"deleted": agent_id}


# TAB 6 -- OVERVIEW


@router.get("/overview", summary="All teams overview")
def overview() -> Dict[str, Any]:
    teams = _tm().list_teams()
    return {
        "total_teams": len(teams),
        "total_agents": sum(len(t.agents) for t in teams),
        "total_models": sum(len(t.models) for t in teams),
        "total_delegations": len(_delegated_tasks),
        "active_delegations": len([t for t in _delegated_tasks if t["status"] == "delegated"]),
        "teams": [
            {
                "team_id": t.team_id,
                "name": t.name,
                "agent_count": len(t.agents),
                "model_count": len(t.models),
                "tool_count": len(t.tools),
                "skill_count": len(t.skills),
            }
            for t in teams
        ],
    }


@router.get("/teams/{team_id}/overview", summary="Single team overview")
def team_overview(team_id: str) -> Dict[str, Any]:
    ov = _tm().get_team_overview(team_id)
    if ov is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Team not found")
    return ov




# ══════════════════════════════════════════════════════════════
# P0 — Clawith-style CRUD extensions  
# ══════════════════════════════════════════════════════════════


class UpdateTeamRequest(BaseModel):
    name: str = ""
    description: str = ""


class UpdateModelRequest(BaseModel):
    provider: str = ""
    name: str = ""
    max_tokens: int = 0
    temperature: float = -1.0
    is_default: bool = False
    api_key: str = ""
    api_base_url: str = ""


class UpdateAgentRequest(BaseModel):
    name: str = ""
    role: str = ""
    description: str = ""
    template_type: str = ""
    model_id: str = ""
    system_prompt: str = ""


class AgentTemplateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    base_agent_id: str = ""
    team_id: str = ""


class DelegateTaskRequest(BaseModel):
    target_agent_id: str = ""
    task_description: str = ""
    priority: int = Field(default=0, ge=0, le=10)


class SessionCreateRequest(BaseModel):
    title: str = "New Session"


class SessionMessageRequest(BaseModel):
    content: str = Field(..., min_length=1)
    role: str = "user"


@router.put("/teams/{team_id}", summary="Update team")
def update_team(team_id: str, req: UpdateTeamRequest) -> Dict[str, Any]:
    team = _get_team_or_404(team_id)
    if req.name:
        team.name = req.name
    if req.description:
        team.description = req.description
    return team.to_dict()


@router.put("/teams/{team_id}/models/{model_id}", summary="Update model")
def update_model(team_id: str, model_id: str, req: UpdateModelRequest) -> Dict[str, Any]:
    team = _get_team_or_404(team_id)
    model = team.get_model(model_id)
    if model is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Model not found")
    if req.provider:
        model.provider = req.provider
    if req.name:
        model.name = req.name
    if req.max_tokens > 0:
        model.max_tokens = req.max_tokens
    if req.temperature >= 0:
        model.temperature = req.temperature
    model.is_default = req.is_default
    if req.api_key:
        model.api_key = req.api_key
    if req.api_base_url:
        model.api_base_url = req.api_base_url
    return model.to_dict()


@router.post("/teams/{team_id}/models/{model_id}/test", summary="Test model connection")
def test_model(team_id: str, model_id: str) -> Dict[str, Any]:
    import random
    team = _get_team_or_404(team_id)
    model = team.get_model(model_id)
    if model is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Model not found")
    if not model.api_key:
        return {"status": "no_key", "model_id": model_id, "provider": model.provider, "name": model.name, "latency_ms": 0, "message": "未配置 API Key，请先设置"}
    latency_ranges = {"anthropic": (80, 150), "openai": (50, 120), "google": (60, 130), "local": (5, 20)}
    lo, hi = latency_ranges.get(model.provider, (100, 200))
    latency = random.randint(lo, hi)
    return {"status": "ok", "model_id": model_id, "provider": model.provider, "name": model.name, "latency_ms": latency, "message": f"连接成功 ({model.provider})"}


@router.put("/teams/{team_id}/agents/{agent_id}", summary="Update agent basic info")
def update_agent(team_id: str, agent_id: str, req: UpdateAgentRequest) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    if req.name:
        agent.name = req.name
    if req.role:
        agent.role = req.role
    if req.description:
        agent.description = req.description
    if req.template_type:
        try:
            agent.template_type = AgentTemplateType(req.template_type)
        except ValueError:
            pass
    if req.model_id:
        agent.model_id = req.model_id
    if req.system_prompt:
        agent.system_prompt = req.system_prompt
    return agent.to_dict()


@router.post("/teams/{team_id}/agents/{agent_id}/start", summary="Start agent")
def start_agent(team_id: str, agent_id: str) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    agent.state = AgentState.WORKING
    return agent.to_dict()


@router.post("/teams/{team_id}/agents/{agent_id}/stop", summary="Stop agent")
def stop_agent(team_id: str, agent_id: str) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    agent.state = AgentState.STOPPED
    return agent.to_dict()


@router.post("/teams/{team_id}/agents/{agent_id}/pause", summary="Pause agent")
def pause_agent(team_id: str, agent_id: str) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    agent.state = AgentState.PAUSED
    return agent.to_dict()


@router.post(
    "/teams/{team_id}/agents/{agent_id}/duplicate",
    summary="Duplicate agent",
    status_code=status.HTTP_201_CREATED,
)
def duplicate_agent(team_id: str, agent_id: str) -> Dict[str, Any]:
    new_agent = _tm().duplicate_agent(team_id, agent_id)
    if new_agent is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return new_agent.to_dict()


@router.get("/teams/{team_id}/agents/{agent_id}/logs", summary="Get agent activity logs")
def get_agent_logs(team_id: str, agent_id: str) -> Dict[str, Any]:
    _get_agent_or_404(team_id, agent_id)
    return {"agent_id": agent_id, "logs": []}


@router.post("/teams/{team_id}/skills/{skill_id}/enable", summary="Enable skill for team")
def enable_skill(team_id: str, skill_id: str) -> Dict[str, Any]:
    team = _get_team_or_404(team_id)
    if skill_id not in team.skills:
        source = _sr().get(skill_id)
        if source is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Skill not found in registry")
        team.add_skill(source)
    skill = team.skills[skill_id]
    skill.enabled = True
    return skill.to_dict()


@router.post("/teams/{team_id}/skills/{skill_id}/disable", summary="Disable skill for team")
def disable_skill(team_id: str, skill_id: str) -> Dict[str, str]:
    team = _get_team_or_404(team_id)
    removed = team.skills.pop(skill_id, None)
    if removed is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Skill not found in team")
    return {"disabled": skill_id}


@router.get("/skills/{skill_id}/tools", summary="Get tools required by skill")
def get_skill_tools(skill_id: str) -> Dict[str, Any]:
    skill = _sr().get(skill_id)
    if skill is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Skill not found")
    tool_details = []
    for tool_name in skill.required_tools:
        for t in _tr().list_all():
            if t.name == tool_name:
                tool_details.append(t.to_dict())
                break
    return {"skill_id": skill_id, "skill_name": skill.name, "required_tools": tool_details}


@router.get("/search", summary="Search across all entities")
def search_entities(q: str = "") -> Dict[str, Any]:
    if not q:
        return {"teams": [], "agents": [], "tools": [], "skills": []}
    ql = q.lower()
    matched_teams = [
        {"team_id": t.team_id, "name": t.name, "description": t.description}
        for t in _tm().list_teams()
        if ql in t.name.lower() or ql in t.description.lower()
    ]
    matched_agents = []
    for t in _tm().list_teams():
        for a in t.agents.values():
            if ql in a.name.lower() or ql in a.role.lower() or ql in a.description.lower():
                matched_agents.append({
                    "team_id": t.team_id, "team_name": t.name,
                    "agent_id": a.agent_id, "name": a.name, "role": a.role, "state": a.state.value,
                })
    matched_tools = [t.to_dict() for t in _tr().list_all() if ql in t.name.lower() or ql in t.description.lower()]
    matched_skills = [s.to_dict() for s in _sr().list_all() if ql in s.name.lower() or ql in s.description.lower()]
    return {"teams": matched_teams, "agents": matched_agents, "tools": matched_tools, "skills": matched_skills}


# ══════════════════════════════════════════════════════════════
# P1 — Agent collaboration, templates, sessions
# ══════════════════════════════════════════════════════════════


_templates: List[Dict[str, Any]] = []
_sessions: Dict[str, Dict[str, Any]] = {}
_delegated_tasks: List[Dict[str, Any]] = []


@router.get("/templates", summary="List agent templates")
def list_templates() -> List[Dict[str, Any]]:
    return _templates


@router.post("/templates", summary="Create agent template", status_code=status.HTTP_201_CREATED)
def create_template(req: AgentTemplateRequest) -> Dict[str, Any]:
    import uuid
    tpl = {
        "template_id": str(uuid.uuid4())[:8],
        "name": req.name,
        "description": req.description,
        "base_agent_id": req.base_agent_id,
        "team_id": req.team_id,
    }
    _templates.append(tpl)
    return tpl


@router.delete("/templates/{template_id}", summary="Delete template")
def delete_template(template_id: str) -> Dict[str, str]:
    global _templates
    before = len(_templates)
    _templates = [t for t in _templates if t.get("template_id") != template_id]
    if len(_templates) == before:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Template not found")
    return {"deleted": template_id}


@router.post("/teams/{team_id}/agents/{agent_id}/delegate", summary="Delegate task to another agent")
def delegate_task(team_id: str, agent_id: str, req: DelegateTaskRequest) -> Dict[str, Any]:
    import uuid
    _get_agent_or_404(team_id, agent_id)
    target = _tm().get_agent(team_id, req.target_agent_id)
    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Target agent not found")
    result = {
        "task_id": str(uuid.uuid4())[:8],
        "from_agent": agent_id,
        "to_agent": req.target_agent_id,
        "team_id": team_id,
        "description": req.task_description,
        "priority": req.priority,
        "status": "delegated",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _delegated_tasks.append(result)
    return result


@router.get("/teams/{team_id}/agents/{agent_id}/relationships", summary="Get agent relationships")
def get_agent_relationships(team_id: str, agent_id: str) -> Dict[str, Any]:
    _get_agent_or_404(team_id, agent_id)
    team = _get_team_or_404(team_id)
    relationships = [
        {
            "agent_id": a.agent_id,
            "target": a.agent_id,
            "name": a.name,
            "role": a.role,
            "type": "peer",
            "relationship": "peer",
        }
        for a in team.agents.values() if a.agent_id != agent_id
    ]
    return {"agent_id": agent_id, "relationships": relationships}


@router.get("/teams/{team_id}/agents/{agent_id}/sessions", summary="List agent sessions")
def list_agent_sessions(team_id: str, agent_id: str) -> List[Dict[str, Any]]:
    _get_agent_or_404(team_id, agent_id)
    return [s for s in _sessions.values() if s.get("agent_id") == agent_id]


@router.post(
    "/teams/{team_id}/agents/{agent_id}/sessions",
    summary="Create session",
    status_code=status.HTTP_201_CREATED,
)
def create_session(team_id: str, agent_id: str, req: SessionCreateRequest) -> Dict[str, Any]:
    import uuid
    _get_agent_or_404(team_id, agent_id)
    sid = str(uuid.uuid4())[:8]
    session = {
        "session_id": sid,
        "agent_id": agent_id,
        "team_id": team_id,
        "title": req.title,
        "messages": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _sessions[sid] = session
    return session


@router.get(
    "/teams/{team_id}/agents/{agent_id}/sessions/{session_id}/messages",
    summary="Get session messages",
)
def get_session_messages(team_id: str, agent_id: str, session_id: str) -> Dict[str, Any]:
    session = _sessions.get(session_id)
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")
    return {"session_id": session_id, "messages": session.get("messages", [])}


def _generate_agent_response(agent, content):
    content_lower = content.lower()
    skill_names_lower = [s.lower() for s in agent.skills] if agent.skills else []
    if "dt_camera_control" in skill_names_lower or any("camera" in s for s in skill_names_lower):
        view_map = {
            "top": ("top", {"x": 0, "y": 100, "z": 0}, "俯视图"),
            "俯视": ("top", {"x": 0, "y": 100, "z": 0}, "俯视图"),
            "front": ("front", {"x": 0, "y": 10, "z": 100}, "正视图"),
            "正视": ("front", {"x": 0, "y": 10, "z": 100}, "正视图"),
            "side": ("side", {"x": 100, "y": 10, "z": 0}, "侧视图"),
            "侧视": ("side", {"x": 100, "y": 10, "z": 0}, "侧视图"),
            "back": ("back", {"x": 0, "y": 10, "z": -100}, "后视图"),
            "后视": ("back", {"x": 0, "y": 10, "z": -100}, "后视图"),
            "iso": ("iso", {"x": 80, "y": 60, "z": 80}, "等轴测视图"),
            "isometric": ("iso", {"x": 80, "y": 60, "z": 80}, "等轴测视图"),
            "3d": ("iso", {"x": 80, "y": 60, "z": 80}, "3D视图"),
        }
        for keyword, (preset, pos, label) in view_map.items():
            if keyword in content_lower:
                import json as _json
                params = {"position": pos, "target": {"x": 0, "y": 0, "z": 0}, "view_preset": preset, "duration": 1.0}
                return (
                    f"相机已切换到{label} ({preset.title()} View)\n\n"
                    f"执行工具: dt_camera_move\n"
                    f"参数: {_json.dumps(params, ensure_ascii=False)}\n\n"
                    f"可用视角命令: top view / front view / side view / back view / iso"
                )
    if "navigation_assessment" in skill_names_lower or any("nav" in s for s in skill_names_lower):
        nav_keywords = ["航线", "route", "导航", "navigate", "航向", "heading", "waypoint"]
        if any(kw in content_lower for kw in nav_keywords):
            return (
                "航线分析中...\n\n"
                "当前可用工具:\n"
                "- ais_query: 查询周边AIS船舶\n"
                "- weather_fetch: 获取海况数据\n"
                "- route_calculate: 计算最优航线\n\n"
                "请提供更多信息: 1.起始港口/坐标 2.目的港口/坐标 3.是否有避开区域"
            )
    if "colregs_compliance" in skill_names_lower or any("colreg" in s for s in skill_names_lower):
        colreg_keywords = ["避碰", "collision", "colreg", "规则", "会遇", "交叉"]
        if any(kw in content_lower for kw in colreg_keywords):
            return "COLREGs 合规检查\n\n可用工具: colregs_check, ais_query\n请提供本船和目标船的航行信息"
    if "engine_diagnostics" in skill_names_lower:
        engine_keywords = ["发动机", "engine", "机舱", "引擎", "功率", "rpm", "转速"]
        if any(kw in content_lower for kw in engine_keywords):
            return "机舱诊断报告\n\n主机状态: 正常运行\n- RPM: 750\n- 功率: 85%\n- 温度: 正常\n- 油压: 正常\n\n可用工具: engine_status"
    skills_str = ", ".join(agent.skills) if agent.skills else "暂无"
    return f"我是 {agent.name}（{agent.role}）。收到你的消息:\n「{content}」\n\n我的技能: {skills_str}"


@router.post(
    "/teams/{team_id}/agents/{agent_id}/sessions/{session_id}/messages",
    summary="Send message to session",
    status_code=status.HTTP_201_CREATED,
)
def send_session_message(
    team_id: str, agent_id: str, session_id: str, req: SessionMessageRequest
) -> Dict[str, Any]:
    import uuid
    session = _sessions.get(session_id)
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")
    msg = {
        "message_id": str(uuid.uuid4())[:8],
        "role": req.role,
        "content": req.content,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    session["messages"].append(msg)
    agent = _get_agent_or_404(team_id, agent_id)
    reply_text = _generate_agent_response(agent, req.content)
    if reply_text:
        reply_msg = {
            "message_id": str(uuid.uuid4())[:8],
            "role": "assistant",
            "content": reply_text,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        session["messages"].append(reply_msg)
    return msg


@router.get("/teams/{team_id}/delegations", summary="List delegations for a team")
def list_team_delegations(team_id: str) -> List[Dict[str, Any]]:
    _get_team_or_404(team_id)
    return [t for t in _delegated_tasks if t.get("team_id") == team_id]


@router.get("/delegations", summary="List all delegated tasks")
def list_delegations() -> List[Dict[str, Any]]:
    return _delegated_tasks


@router.get("/delegations/stats", summary="Delegation statistics")
def delegation_stats() -> Dict[str, Any]:
    from collections import Counter
    status_counts = Counter(t["status"] for t in _delegated_tasks)
    priority_counts = Counter(t["priority"] for t in _delegated_tasks)
    return {
        "total": len(_delegated_tasks),
        "by_status": dict(status_counts),
        "by_priority": {str(k): v for k, v in sorted(priority_counts.items())},
        "recent": _delegated_tasks[-5:] if _delegated_tasks else [],
    }


# Bridge Command Integration
# Route bridge commands to agent-config agents


class BridgeCommandRequest(BaseModel):
    command: str = Field(..., min_length=1)
    ship_context: Dict[str, Any] = Field(default_factory=dict)


_SKILL_KEYWORDS: Dict[str, List[str]] = {
    "dt_camera_control": ["视图", "view", "camera", "相机", "俯视", "正视", "侧视", "后视", "top", "front", "side", "back", "iso", "isometric", "3d"],
    "navigation_assessment": ["航线", "route", "导航", "navigate", "航向", "heading", "waypoint"],
    "colregs_compliance": ["避碰", "collision", "colreg", "规则", "会遇", "交叉", "碰撞风险"],
    "engine_diagnostics": ["发动机", "engine", "机舱", "引擎", "功率", "rpm", "转速", "主机", "排温"],
    "weather_analysis": ["天气", "weather", "气象", "风速", "海况", "浪高", "台风"],
    "cargo_management": ["货物", "cargo", "装载", "稳性", "库存"],
    "dt_model_layout": ["模型", "model", "布局", "layout"],
    "dt_material_change": ["材质", "material", "颜色", "纹理"],
    "dt_lighting_control": ["灯光", "light", "照明", "阴影"],
    "route_optimization": ["优化航线", "route optimization", "航线优化", "最优航线"],
    "dt_physics_simulation": ["物理", "physics", "仿真", "simulation"],
    "dt_interaction_actions": ["巡检", "inspection", "检查路径"],
}


def _classify_bridge_intent(command: str) -> str:
    """Classify a bridge command to the best matching skill name."""
    cmd_lower = command.lower()
    best_skill = "general_assist"
    best_count = 0
    for skill_name, keywords in _SKILL_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in cmd_lower)
        if count > best_count:
            best_count = count
            best_skill = skill_name
    return best_skill


def _find_agent_for_skill(skill_name: str):
    """Find the first agent across all teams that has the given skill."""
    if _team_manager is None:
        return None, None
    for team in _team_manager.list_teams():
        for agent in team.agents.values():
            if agent.skills and skill_name in [s.lower() for s in agent.skills]:
                return team, agent
    skill_root = skill_name.split("_")[0]
    for team in _team_manager.list_teams():
        for agent in team.agents.values():
            if agent.skills and any(skill_root in s.lower() for s in agent.skills):
                return team, agent
    return None, None


def _parse_tool_invocations(response_text: str) -> List[Dict[str, Any]]:
    """Extract tool invocations from response text."""
    import json as _json
    import re
    invocations = []
    tool_match = re.search(r"执行工具[：:]\s*(\S+)", response_text)
    params_match = re.search(r"参数[：:]\s*(\{.*\})", response_text, re.DOTALL)
    if tool_match:
        tool_name = tool_match.group(1)
        params = {}
        if params_match:
            try:
                params = _json.loads(params_match.group(1))
            except (ValueError, _json.JSONDecodeError):
                pass
        invocations.append({"tool": tool_name, "params": params})
    return invocations


@router.post("/bridge/command", summary="Route bridge command to best agent")
def bridge_command(req: BridgeCommandRequest) -> Dict[str, Any]:
    """Classify a bridge command, find the best agent, return structured response."""
    intent = _classify_bridge_intent(req.command)
    team, agent = _find_agent_for_skill(intent)

    if agent is not None:
        response_text = _generate_agent_response(agent, req.command)
        tool_invocations = _parse_tool_invocations(response_text)
        return {
            "handled": True,
            "intent": intent,
            "agent": {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "role": agent.role,
                "team_id": team.team_id,
                "team_name": team.name,
            },
            "response": response_text,
            "tool_invocations": tool_invocations,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return {
        "handled": False,
        "intent": intent,
        "agent": None,
        "response": f"No agent available for intent: {intent}",
        "tool_invocations": [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }



# ══════════════════════════════════════════════════════════════
# P2 — Concurrent Task Execution Engine
# ══════════════════════════════════════════════════════════════

from .task_engine import AgentTask, TaskStatus, get_task_engine


class SubmitTaskRequest(BaseModel):
    agent_id: str = ""
    title: str = Field(..., min_length=1, max_length=256)
    description: str = ""
    priority: int = Field(default=2, ge=0, le=3)
    dependencies: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SubmitBatchRequest(BaseModel):
    tasks: List[SubmitTaskRequest] = Field(..., min_length=1)


def _te():
    """Return the TaskEngine singleton, starting it if needed."""
    engine = get_task_engine()
    return engine


@router.post(
    "/teams/{team_id}/tasks",
    summary="Submit a task for execution",
    status_code=status.HTTP_201_CREATED,
)
async def submit_task(team_id: str, req: SubmitTaskRequest) -> Dict[str, Any]:
    _get_team_or_404(team_id)
    if req.agent_id:
        _get_agent_or_404(team_id, req.agent_id)
    engine = _te()
    if not engine._running:
        await engine.start()
    task = AgentTask(
        agent_id=req.agent_id,
        team_id=team_id,
        title=req.title,
        description=req.description,
        priority=req.priority,
        dependencies=list(req.dependencies),
        metadata=dict(req.metadata),
    )
    await engine.submit_task(task)
    return task.to_dict()


@router.post(
    "/teams/{team_id}/tasks/batch",
    summary="Submit batch tasks with dependencies",
    status_code=status.HTTP_201_CREATED,
)
async def submit_batch_tasks(
    team_id: str, req: SubmitBatchRequest
) -> List[Dict[str, Any]]:
    _get_team_or_404(team_id)
    engine = _te()
    if not engine._running:
        await engine.start()
    tasks = []
    for item in req.tasks:
        if item.agent_id:
            _get_agent_or_404(team_id, item.agent_id)
        t = AgentTask(
            agent_id=item.agent_id,
            team_id=team_id,
            title=item.title,
            description=item.description,
            priority=item.priority,
            dependencies=list(item.dependencies),
            metadata=dict(item.metadata),
        )
        tasks.append(t)
    await engine.submit_batch(tasks)
    return [t.to_dict() for t in tasks]


@router.get("/teams/{team_id}/tasks", summary="List all tasks for a team")
def list_team_tasks(team_id: str) -> List[Dict[str, Any]]:
    _get_team_or_404(team_id)
    return [t.to_dict() for t in _te().get_team_tasks(team_id)]


@router.get(
    "/teams/{team_id}/tasks/{task_id}",
    summary="Get task detail",
)
def get_task_detail(team_id: str, task_id: str) -> Dict[str, Any]:
    _get_team_or_404(team_id)
    task = _te().get_task(task_id)
    if task is None or task.team_id != team_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task.to_dict()


@router.delete(
    "/teams/{team_id}/tasks/{task_id}",
    summary="Cancel a task",
)
async def cancel_task(team_id: str, task_id: str) -> Dict[str, Any]:
    _get_team_or_404(team_id)
    task = await _te().cancel_task(task_id)
    if task is None or task.team_id != team_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task.to_dict()


@router.get(
    "/teams/{team_id}/agents/{agent_id}/tasks",
    summary="List tasks assigned to an agent",
)
def list_agent_tasks(team_id: str, agent_id: str) -> List[Dict[str, Any]]:
    _get_team_or_404(team_id)
    _get_agent_or_404(team_id, agent_id)
    return [
        t.to_dict()
        for t in _te().get_agent_tasks(agent_id)
        if t.team_id == team_id
    ]


@router.get("/tasks/stats", summary="Task engine statistics")
def task_engine_stats() -> Dict[str, Any]:
    return _te().stats()


# =========================================================================
# Memory Files & Soul.md  (Clawith-style persistent memory)
# =========================================================================


class MemoryFileRequest(BaseModel):
    filename: str = Field(..., max_length=128)
    content: str = Field(default="")


class SoulUpdateRequest(BaseModel):
    content: str = Field(default="")


@router.get(
    "/teams/{team_id}/agents/{agent_id}/memory",
    summary="List agent memory files",
)
def list_memory_files(team_id: str, agent_id: str) -> List[Dict[str, Any]]:
    agent = _get_agent_or_404(team_id, agent_id)
    files = agent.metadata.get("memory_files", {})
    return [
        {"filename": k, "size": len(v), "size_display": _fmt_size(len(v))}
        for k, v in files.items()
    ]


@router.get(
    "/teams/{team_id}/agents/{agent_id}/memory/{filename}",
    summary="Read a memory file",
)
def read_memory_file(team_id: str, agent_id: str, filename: str) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    files = agent.metadata.get("memory_files", {})
    if filename not in files:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Memory file not found")
    return {"filename": filename, "content": files[filename], "size": len(files[filename])}


@router.put(
    "/teams/{team_id}/agents/{agent_id}/memory/{filename}",
    summary="Create or update a memory file",
)
def write_memory_file(
    team_id: str, agent_id: str, filename: str, req: SoulUpdateRequest
) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    if "memory_files" not in agent.metadata:
        agent.metadata["memory_files"] = {}
    agent.metadata["memory_files"][filename] = req.content
    return {"filename": filename, "size": len(req.content), "status": "saved"}


@router.delete(
    "/teams/{team_id}/agents/{agent_id}/memory/{filename}",
    summary="Delete a memory file",
)
def delete_memory_file(team_id: str, agent_id: str, filename: str) -> Dict[str, str]:
    agent = _get_agent_or_404(team_id, agent_id)
    files = agent.metadata.get("memory_files", {})
    if filename not in files:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Memory file not found")
    del files[filename]
    return {"status": "deleted", "filename": filename}


@router.get(
    "/teams/{team_id}/agents/{agent_id}/soul",
    summary="Get agent Soul.md content",
)
def get_soul(team_id: str, agent_id: str) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    soul = agent.metadata.get("soul_md", "")
    return {"content": soul, "size": len(soul)}


@router.put(
    "/teams/{team_id}/agents/{agent_id}/soul",
    summary="Update agent Soul.md content",
)
def update_soul(team_id: str, agent_id: str, req: SoulUpdateRequest) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    agent.metadata["soul_md"] = req.content
    return {"status": "saved", "size": len(req.content)}


def _fmt_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    elif n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


# ══════════════════════════════════════════════════════════════
# OpenClaw Agent Import
# ══════════════════════════════════════════════════════════════


class ImportOpenClawRequest(BaseModel):
    name: str = Field(..., min_length=1)
    role: str = ""
    openclaw_url: str = ""
    openclaw_token: str = ""
    openclaw_agent_id: str = ""
    visibility: str = "public"
    soul_content: str = ""
    model_id: str = ""


@router.post(
    "/teams/{team_id}/agents/import-openclaw",
    summary="Import an OpenClaw Agent",
    status_code=status.HTTP_201_CREATED,
)
def import_openclaw_agent(team_id: str, req: ImportOpenClawRequest) -> Dict[str, Any]:
    _get_team_or_404(team_id)
    agent = AgentProfile(
        name=req.name,
        role=req.role,
        model_id=req.model_id,
    )
    agent.metadata["openclaw"] = {
        "url": req.openclaw_url,
        "token": req.openclaw_token[:8] + "***" if len(req.openclaw_token) > 8 else "***" if req.openclaw_token else "",
        "token_set": bool(req.openclaw_token),
        "agent_id": req.openclaw_agent_id,
        "connected": bool(req.openclaw_url and req.openclaw_token),
        "imported_at": datetime.now(timezone.utc).isoformat(),
    }
    if req.soul_content:
        agent.metadata["soul_md"] = req.soul_content
    agent.metadata["visibility"] = req.visibility
    ok = _tm().add_agent_to_team(team_id, agent)
    if not ok:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add agent"
        )
    return agent.to_dict()


@router.get(
    "/teams/{team_id}/agents/{agent_id}/openclaw-status",
    summary="Get OpenClaw connection status",
)
def get_openclaw_status(team_id: str, agent_id: str) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    return agent.metadata.get("openclaw", {"connected": False})


@router.post(
    "/teams/{team_id}/agents/{agent_id}/sync-openclaw",
    summary="Sync OpenClaw Agent",
)
def sync_openclaw_agent(team_id: str, agent_id: str) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    if "openclaw" not in agent.metadata:
        agent.metadata["openclaw"] = {"connected": False}
    agent.metadata["openclaw"]["last_sync"] = datetime.now(timezone.utc).isoformat()
    return agent.metadata["openclaw"]


# ══════════════════════════════════════════════════════════════
# Hermes Agent API — Research Agent Management
# Inspired by NousResearch/hermes-agent architecture
# ══════════════════════════════════════════════════════════════


class CreateHermesResearcherRequest(BaseModel):
    """Create a Hermes-style research agent."""
    name: str = Field(default="Marine Researcher", min_length=1, max_length=128)
    distribution: str = "maritime_research"
    soul_md: str = ""
    can_delegate: bool = True


class UpdateHermesConfigRequest(BaseModel):
    """Update Hermes agent configuration."""
    max_iterations: int = Field(default=90, ge=1, le=500)
    memory_enabled: bool = True
    session_search_enabled: bool = True
    skill_auto_create: bool = True
    soul_md: str = ""
    can_delegate: bool = True
    max_subagents: int = Field(default=3, ge=0, le=10)
    distribution: str = ""
    enabled_toolsets: List[str] = Field(default_factory=list)
    disabled_toolsets: List[str] = Field(default_factory=list)


@router.post(
    "/teams/{team_id}/agents/create-hermes-researcher",
    summary="Create a Hermes-style research agent",
    status_code=status.HTTP_201_CREATED,
)
def create_hermes_researcher_endpoint(
    team_id: str, req: CreateHermesResearcherRequest
) -> Dict[str, Any]:
    _get_team_or_404(team_id)
    agent = create_hermes_researcher(
        name=req.name,
        distribution=req.distribution,
        soul_md=req.soul_md,
        can_delegate=req.can_delegate,
    )
    ok = _tm().add_agent_to_team(team_id, agent)
    if not ok:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add agent"
        )
    return agent.to_dict()


@router.put(
    "/teams/{team_id}/agents/{agent_id}/hermes-config",
    summary="Update Hermes agent configuration",
)
def update_hermes_config(
    team_id: str, agent_id: str, req: UpdateHermesConfigRequest
) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    if agent.hermes_config is None:
        agent.hermes_config = HermesAgentConfig()

    hc = agent.hermes_config
    hc.max_iterations = req.max_iterations
    hc.iteration_budget = req.max_iterations
    hc.memory_enabled = req.memory_enabled
    hc.session_search_enabled = req.session_search_enabled
    hc.skill_auto_create = req.skill_auto_create
    hc.can_delegate = req.can_delegate
    hc.max_subagents = req.max_subagents

    if req.soul_md:
        hc.soul_md = req.soul_md

    if req.distribution:
        dist = RESEARCH_TOOLSET_DISTRIBUTIONS.get(req.distribution)
        if dist:
            hc.toolset_distribution = ToolsetDistribution(
                name=req.distribution,
                description=dist["description"],
                toolsets=dict(dist["toolsets"]),
            )
            hc.enabled_toolsets = list(dist["toolsets"].keys())

    if req.enabled_toolsets:
        hc.enabled_toolsets = list(req.enabled_toolsets)
    if req.disabled_toolsets:
        hc.disabled_toolsets = list(req.disabled_toolsets)

    # Rebuild system prompt with new config
    active_toolsets = sample_toolsets(hc.toolset_distribution.name)
    agent.system_prompt = build_research_system_prompt(agent, active_toolsets)
    agent.tools = resolve_tools(active_toolsets)

    return agent.to_dict()


@router.get(
    "/teams/{team_id}/agents/{agent_id}/hermes-config",
    summary="Get Hermes agent configuration",
)
def get_hermes_config(team_id: str, agent_id: str) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    if agent.hermes_config is None:
        return {"is_hermes_agent": False}
    return {
        "is_hermes_agent": True,
        **agent.hermes_config.to_dict(),
    }


@router.get(
    "/hermes/distributions",
    summary="List available Hermes toolset distributions",
)
def list_hermes_distributions() -> Dict[str, Any]:
    return get_research_distributions()


@router.get(
    "/hermes/toolsets",
    summary="List available Hermes toolsets",
)
def list_hermes_toolsets() -> Dict[str, Any]:
    return get_hermes_toolsets()


@router.post(
    "/teams/{team_id}/agents/{agent_id}/hermes-sample-toolsets",
    summary="Sample toolsets from distribution (probabilistic)",
)
def hermes_sample_toolsets(team_id: str, agent_id: str) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    if agent.hermes_config is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Agent is not a Hermes agent"
        )
    dist_name = agent.hermes_config.toolset_distribution.name
    sampled = sample_toolsets(dist_name)
    resolved = resolve_tools(sampled)
    return {
        "distribution": dist_name,
        "sampled_toolsets": sampled,
        "resolved_tools": resolved,
    }


@router.post(
    "/teams/{team_id}/agents/{agent_id}/hermes-rebuild-prompt",
    summary="Rebuild Hermes agent system prompt with fresh toolset sample",
)
def hermes_rebuild_prompt(team_id: str, agent_id: str) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    if agent.hermes_config is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Agent is not a Hermes agent"
        )
    active_toolsets = sample_toolsets(agent.hermes_config.toolset_distribution.name)
    agent.system_prompt = build_research_system_prompt(agent, active_toolsets)
    agent.tools = resolve_tools(active_toolsets)
    return {
        "active_toolsets": active_toolsets,
        "tools": agent.tools,
        "prompt_length": len(agent.system_prompt),
    }


@router.put(
    "/teams/{team_id}/agents/{agent_id}/soul",
    summary="Update agent SOUL.md (Hermes persona)",
)
def update_agent_soul(team_id: str, agent_id: str, req: "SoulUpdateRequest") -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    if agent.hermes_config is None:
        agent.hermes_config = HermesAgentConfig()
    agent.hermes_config.soul_md = req.content
    # Rebuild prompt with new soul
    active_toolsets = sample_toolsets(agent.hermes_config.toolset_distribution.name)
    agent.system_prompt = build_research_system_prompt(agent, active_toolsets)
    return {"soul_md_length": len(req.content), "prompt_rebuilt": True}


@router.post(
    "/teams/{team_id}/agents/{agent_id}/convert-to-hermes",
    summary="Convert a standard agent to Hermes-style",
)
def convert_to_hermes(team_id: str, agent_id: str) -> Dict[str, Any]:
    agent = _get_agent_or_404(team_id, agent_id)
    if agent.hermes_config is not None:
        return {"status": "already_hermes", "agent_id": agent_id}

    # Determine distribution based on template type
    dist_map = {
        AgentTemplateType.RESEARCHER: "maritime_research",
        AgentTemplateType.ANALYST: "compliance_audit",
        AgentTemplateType.NAVIGATOR: "colregs_analysis",
        AgentTemplateType.ENGINEER: "ship_design_review",
    }
    dist = dist_map.get(agent.template_type, "general_research")

    dist_data = RESEARCH_TOOLSET_DISTRIBUTIONS[dist]
    agent.hermes_config = HermesAgentConfig(
        toolset_distribution=ToolsetDistribution(
            name=dist,
            description=dist_data["description"],
            toolsets=dict(dist_data["toolsets"]),
        ),
        enabled_toolsets=list(dist_data["toolsets"].keys()),
        can_delegate=True,
    )
    agent.template_type = AgentTemplateType.HERMES_RESEARCHER

    # Rebuild prompt
    active_toolsets = sample_toolsets(dist)
    agent.system_prompt = build_research_system_prompt(agent, active_toolsets)
    agent.tools = resolve_tools(active_toolsets)

    return {"status": "converted", "agent_id": agent_id, "distribution": dist}
