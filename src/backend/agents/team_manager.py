# -*- coding: utf-8 -*-
"""PoseidonX Agent Team Framework — Team Manager.

Manages multiple AgentTeam instances and provides CRUD operations for
teams, agents, and models.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import AgentProfile, AgentTeam, ModelConfig


class TeamManager:
    """Manages the lifecycle of agent teams."""

    def __init__(self) -> None:
        self._teams: Dict[str, AgentTeam] = {}

    # ── Team CRUD ──────────────────────────────────────────────────────

    def create_team(
        self,
        name: str,
        description: str = "",
        **kwargs: Any,
    ) -> AgentTeam:
        """Create a new team and register it."""
        team = AgentTeam(name=name, description=description, **kwargs)
        self._teams[team.team_id] = team
        return team

    def get_team(self, team_id: str) -> Optional[AgentTeam]:
        """Get a team by ID."""
        return self._teams.get(team_id)

    def list_teams(self) -> List[AgentTeam]:
        """Return all teams."""
        return list(self._teams.values())

    def delete_team(self, team_id: str) -> Optional[AgentTeam]:
        """Delete a team. Returns the removed team or None."""
        return self._teams.pop(team_id, None)

    # ── Agent management ───────────────────────────────────────────────

    def add_agent_to_team(
        self,
        team_id: str,
        agent: AgentProfile,
    ) -> bool:
        """Add an agent to a team. Returns True on success."""
        team = self._teams.get(team_id)
        if team is None:
            return False
        team.add_agent(agent)
        return True

    def remove_agent_from_team(
        self,
        team_id: str,
        agent_id: str,
    ) -> Optional[AgentProfile]:
        """Remove an agent from a team."""
        team = self._teams.get(team_id)
        if team is None:
            return None
        return team.remove_agent(agent_id)

    def get_agent(
        self,
        team_id: str,
        agent_id: str,
    ) -> Optional[AgentProfile]:
        """Get a specific agent from a team."""
        team = self._teams.get(team_id)
        if team is None:
            return None
        return team.get_agent(agent_id)

    def list_agents(self, team_id: str) -> List[AgentProfile]:
        """List all agents in a team."""
        team = self._teams.get(team_id)
        if team is None:
            return []
        return list(team.agents.values())

    # ── Model management ───────────────────────────────────────────────

    def add_model_to_team(
        self,
        team_id: str,
        model: ModelConfig,
    ) -> bool:
        """Add a model to a team. Returns True on success."""
        team = self._teams.get(team_id)
        if team is None:
            return False
        team.add_model(model)
        return True

    def remove_model_from_team(
        self,
        team_id: str,
        model_id: str,
    ) -> Optional[ModelConfig]:
        """Remove a model from a team."""
        team = self._teams.get(team_id)
        if team is None:
            return None
        return team.remove_model(model_id)

    # ── Overview ───────────────────────────────────────────────────────

    def get_team_overview(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Return a summary dict for a team."""
        team = self._teams.get(team_id)
        if team is None:
            return None
        return {
            "team_id": team.team_id,
            "name": team.name,
            "description": team.description,
            "agent_count": len(team.agents),
            "model_count": len(team.models),
            "tool_count": len(team.tools),
            "skill_count": len(team.skills),
            "agents": [
                {"agent_id": a.agent_id, "name": a.name, "role": a.role, "state": a.state.value}
                for a in team.agents.values()
            ],
        }


    # ── Update operations ─────────────────────────────────────

    def update_team(
        self,
        team_id: str,
        **kwargs: Any,
    ) -> Optional[AgentTeam]:
        """Update team fields. Returns updated team or None."""
        team = self._teams.get(team_id)
        if team is None:
            return None
        for key, value in kwargs.items():
            if hasattr(team, key) and key not in ("team_id", "created_at"):
                setattr(team, key, value)
        return team

    def duplicate_agent(
        self,
        team_id: str,
        agent_id: str,
    ) -> Optional[AgentProfile]:
        """Deep copy an agent within a team. Returns new agent or None."""
        import copy
        team = self._teams.get(team_id)
        if team is None:
            return None
        original = team.get_agent(agent_id)
        if original is None:
            return None
        new_agent = copy.deepcopy(original)
        new_agent.agent_id = ""  # triggers __post_init__ to generate new ID
        new_agent.__post_init__()
        new_agent.name = original.name + " (副本)"
        team.add_agent(new_agent)
        return new_agent

    # ── Serialization ──────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all teams to dict."""
        return {tid: t.to_dict() for tid, t in self._teams.items()}
