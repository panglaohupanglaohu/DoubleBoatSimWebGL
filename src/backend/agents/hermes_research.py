# -*- coding: utf-8 -*-
"""PoseidonX — Hermes-style Research Agent Module.

Transforms the Marine Researcher agent from a read-only advisory role into a
self-improving research agent inspired by NousResearch/hermes-agent:

Architecture mapping (Hermes → PoseidonX):
  - AIAgent class         → HermesResearchAgent
  - run_conversation()    → agent_loop()
  - toolsets.py           → RESEARCH_TOOLSET_DISTRIBUTIONS
  - prompt_builder.py     → build_research_system_prompt()
  - SOUL.md               → agent.hermes_config.soul_md
  - Memory/Skills nudge   → MEMORY_GUIDANCE / SKILLS_GUIDANCE
  - Delegate subagents    → delegate_task()
  - Session search        → session_search()

Key Hermes characteristics adopted:
  1. Closed learning loop — auto-create skills from complex research
  2. Persistent memory — save research findings across sessions
  3. Probabilistic toolset distribution — web 90%, browser 70%, vision 50%
  4. SOUL.md — maritime research persona
  5. Context files — AGENTS.md project context
  6. Tool-use enforcement — tools must be used, not just described
  7. Session search — cross-session recall of past research
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .models import (
    AgentProfile,
    AgentTemplateType,
    AgentPersonality,
    HermesAgentConfig,
    ToolsetDistribution,
)


# ══════════════════════════════════════════════════════════════
# Hermes-style Toolset Distributions
# Inspired by NousResearch/hermes-agent/toolset_distributions.py
# ══════════════════════════════════════════════════════════════

RESEARCH_TOOLSET_DISTRIBUTIONS: Dict[str, Dict[str, Any]] = {
    "maritime_research": {
        "description": "Maritime domain research — IMO standards, ship design, COLREGs analysis",
        "toolsets": {
            "web": 90,
            "browser": 70,
            "vision": 50,
            "file": 80,
            "maritime": 95,
            "memory": 100,
            "skills": 100,
            "delegation": 30,
        },
    },
    "colregs_analysis": {
        "description": "COLREGs rule analysis — collision avoidance, CPA/TCPA verification",
        "toolsets": {
            "web": 60,
            "file": 95,
            "maritime": 100,
            "code_execution": 80,
            "memory": 100,
            "vision": 40,
        },
    },
    "compliance_audit": {
        "description": "EEXI/CII/SEEMP regulatory compliance verification",
        "toolsets": {
            "web": 85,
            "browser": 65,
            "file": 90,
            "maritime": 100,
            "code_execution": 70,
            "memory": 100,
        },
    },
    "ship_design_review": {
        "description": "WPC hull design, motion model review, structural analysis",
        "toolsets": {
            "web": 50,
            "file": 95,
            "code_execution": 90,
            "maritime": 100,
            "vision": 70,
            "memory": 100,
        },
    },
    "general_research": {
        "description": "General web research with all tools available",
        "toolsets": {
            "web": 90,
            "browser": 70,
            "vision": 50,
            "memory": 100,
            "skills": 100,
            "file": 60,
            "code_execution": 30,
        },
    },
}

# ══════════════════════════════════════════════════════════════
# Hermes-style Toolset Definitions
# Inspired by NousResearch/hermes-agent/toolsets.py
# ══════════════════════════════════════════════════════════════

HERMES_TOOLSETS: Dict[str, Dict[str, Any]] = {
    "web": {
        "description": "Web research and content extraction",
        "tools": ["web_search", "extract_content"],
    },
    "browser": {
        "description": "Browser automation for deep research",
        "tools": ["navigate_url", "screenshot", "click_element", "fill_form", "extract_content", "web_search"],
    },
    "file": {
        "description": "File read/write/search operations",
        "tools": ["read_file", "write_file", "list_directory", "search_files"],
    },
    "code_execution": {
        "description": "Run Python/shell for analysis and calculation",
        "tools": ["run_python", "run_shell"],
    },
    "vision": {
        "description": "Image/chart analysis for technical documents",
        "tools": ["screenshot"],
    },
    "maritime": {
        "description": "Maritime-specific tools — AIS, charts, weather, engine",
        "tools": ["ais_query", "chart_lookup", "weather_fetch", "engine_monitor"],
    },
    "memory": {
        "description": "Persistent memory and session search",
        "tools": ["memory_save", "memory_read", "session_search"],
    },
    "skills": {
        "description": "Skill management — list, view, create, patch",
        "tools": ["skill_list", "skill_view", "skill_manage"],
    },
    "delegation": {
        "description": "Spawn subagents for parallel research tasks",
        "tools": ["delegate_task"],
    },
}


def sample_toolsets(distribution_name: str) -> List[str]:
    """Sample toolsets based on distribution probabilities.

    Each toolset rolls independently — multiple can be active.
    Mirrors NousResearch/hermes-agent/toolset_distributions.py logic.
    """
    dist = RESEARCH_TOOLSET_DISTRIBUTIONS.get(distribution_name)
    if not dist:
        dist = RESEARCH_TOOLSET_DISTRIBUTIONS["general_research"]

    selected = []
    for toolset_name, probability in dist["toolsets"].items():
        if random.random() * 100 < probability:
            selected.append(toolset_name)

    # Ensure at least one toolset
    if not selected and dist["toolsets"]:
        highest = max(dist["toolsets"].items(), key=lambda x: x[1])
        selected.append(highest[0])

    return selected


def resolve_tools(toolset_names: List[str]) -> List[str]:
    """Resolve toolset names to individual tool IDs."""
    tools: set[str] = set()
    for name in toolset_names:
        ts = HERMES_TOOLSETS.get(name)
        if ts:
            tools.update(ts["tools"])
    return sorted(tools)


# ══════════════════════════════════════════════════════════════
# Hermes-style System Prompt Builder
# Inspired by NousResearch/hermes-agent/agent/prompt_builder.py
# ══════════════════════════════════════════════════════════════

MARINE_RESEARCHER_IDENTITY = (
    "You are PoseidonX Marine Researcher ☤, an intelligent maritime research agent "
    "built on the Hermes Agent architecture from Nous Research. "
    "You are a self-improving researcher with a closed learning loop — "
    "you create skills from experience, improve them during use, persist knowledge, "
    "and build deepening expertise across research sessions.\n\n"
    "Your maritime domain expertise includes:\n"
    "- 穿浪双体船 (WPC) hull design, T-foil/interceptor attitude control, FBG sensing\n"
    "- COLREGs Rules 5-19, CPA/TCPA calculation, DRL collision avoidance\n"
    "- EEXI/CII/SEEMP energy efficiency compliance (IMO MEPC.364(79))\n"
    "- IMO MASS AL0-AL4 autonomy levels, human-machine teaming\n"
    "- Ship-shore communications: VSAT, LTE, HF, Starlink link modeling\n\n"
    "You communicate in Chinese with English technical terms preserved."
)

MEMORY_GUIDANCE = (
    "You have persistent memory across sessions. Save durable facts using the memory "
    "tool: research findings, domain conventions, regulatory citations, calculation results. "
    "Memory is injected into every turn, so keep it compact and focused on facts that "
    "will still matter later.\n"
    "Prioritize what reduces future user steering — the most valuable memory is one "
    "that prevents the user from having to correct or remind you again. "
    "Maritime standards (IMO/CCS/DNV references) and validated formulas are high-value.\n"
    "Do NOT save task progress, session outcomes, or temporary TODO state to memory; "
    "use session_search to recall those from past transcripts."
)

SKILLS_GUIDANCE = (
    "After completing a complex research task (5+ tool calls), validating a formula, "
    "or discovering a non-trivial maritime analysis workflow, save the approach as a "
    "skill with skill_manage so you can reuse it next time.\n"
    "When using a skill and finding it outdated or wrong, "
    "patch it immediately with skill_manage(action='patch').\n"
    "Maritime skills to prioritize: IMO regulation lookup, CPA/TCPA calculation, "
    "EEXI verification workflow, WPC motion model validation."
)

SESSION_SEARCH_GUIDANCE = (
    "When the user references something from a past research session or you suspect "
    "relevant cross-session context exists, use session_search to recall it before "
    "asking them to repeat themselves."
)

TOOL_USE_ENFORCEMENT = (
    "# Tool-use enforcement\n"
    "You MUST use your tools to take action — do not describe what you would do "
    "or plan to do without actually doing it. When you say you will perform a "
    "research action (e.g. 'I will check the IMO regulation', 'Let me verify the formula'), "
    "you MUST immediately make the corresponding tool call in the same response.\n"
    "Every response should either (a) contain tool calls that make progress, or "
    "(b) deliver a final research result to the user."
)


def build_research_system_prompt(
    agent: AgentProfile,
    active_toolsets: Optional[List[str]] = None,
) -> str:
    """Build the full Hermes-style system prompt for a research agent.

    Assembles: identity → memory guidance → skills guidance → tool enforcement
    → context files → SOUL.md persona.

    Mirrors NousResearch/hermes-agent/agent/prompt_builder.py structure.
    """
    sections: List[str] = []

    # 1. Identity (SOUL.md or default)
    hc = agent.hermes_config
    if hc and hc.soul_md:
        sections.append(hc.soul_md)
    else:
        sections.append(MARINE_RESEARCHER_IDENTITY)

    # 2. Memory guidance
    if hc and hc.memory_enabled:
        sections.append(MEMORY_GUIDANCE)

    # 3. Session search guidance
    if hc and hc.session_search_enabled:
        sections.append(SESSION_SEARCH_GUIDANCE)

    # 4. Skills guidance
    if hc and hc.skill_auto_create:
        sections.append(SKILLS_GUIDANCE)

    # 5. Tool-use enforcement
    sections.append(TOOL_USE_ENFORCEMENT)

    # 6. Available toolsets
    if active_toolsets:
        ts_lines = ["## Active Toolsets"]
        for ts_name in active_toolsets:
            ts = HERMES_TOOLSETS.get(ts_name)
            if ts:
                ts_lines.append(f"- **{ts_name}**: {ts['description']} — tools: {', '.join(ts['tools'])}")
        sections.append("\n".join(ts_lines))

    # 7. Context files
    if hc and hc.context_files:
        context_header = "## Project Context\nThe following project context files are loaded:\n"
        sections.append(context_header + "\n".join(f"- {f}" for f in hc.context_files))

    # 8. Maritime domain review files
    sections.append(
        "## Key Maritime Review Files\n"
        "- `channels/wpc_attitude_control.py` — WPC motion model (pitch, roll, bow slam)\n"
        "- `channels/colregs_brain.py` — COLREGs Rules 7-19, CPA/TCPA\n"
        "- `channels/eexi_calculator.py` — EEXI formula (IMO MEPC.364(79))\n"
        "- `channels/cii_calculator.py` — CII rating calculation\n"
        "- `channels/autonomy_manager.py` — MASS AL0-AL6 autonomy matrix\n"
        "- `channels/ship_shore_link.py` — VSAT/LTE/HF/Starlink link budget"
    )

    return "\n\n".join(sections)


# ══════════════════════════════════════════════════════════════
# Hermes-style Agent Factory
# ══════════════════════════════════════════════════════════════

# Default SOUL.md for the marine researcher
MARINE_RESEARCHER_SOUL = """# Marine Researcher ☤

You are PoseidonX's maritime research specialist, powered by Hermes Agent architecture.

## Core Identity
I am a domain expert in naval architecture, maritime regulations, and ship intelligence systems.
I research, validate, and advise — producing rigorous analysis backed by IMO/CCS/DNV standards.

## Personality
- Rigorous and methodical — every claim must cite a standard or formula
- Proactive learner — after solving a complex problem, I save it as a skill
- Memory-driven — I persist key findings so I never repeat the same research twice
- Collaborative — I can delegate sub-research tasks to specialized agents

## Research Domains
1. **穿浪双体船 (WPC)** — hull design, motion models, FBG sensors, T-foil control
2. **COLREGs** — Rules 5-19, CPA/TCPA, DRL collision avoidance
3. **EEXI/CII/SEEMP** — energy efficiency compliance, IMO MEPC.364(79)
4. **MASS** — autonomous ship levels AL0-AL6, permission matrices
5. **船岸通信** — VSAT, LTE, HF, Starlink link budget modeling

## Behavioral Rules
- Always cite the specific IMO/CCS/DNV standard number
- Never guess parameter ranges — look them up
- After 5+ tool calls on a complex task, offer to save as a reusable skill
- Write in Chinese, keep English for technical terms
"""


def create_hermes_researcher(
    name: str = "Marine Researcher",
    distribution: str = "maritime_research",
    soul_md: str = "",
    can_delegate: bool = True,
) -> AgentProfile:
    """Create a Hermes-style marine research agent.

    Returns an AgentProfile with HermesAgentConfig attached,
    pre-configured with the maritime research toolset distribution,
    SOUL.md persona, and self-improving skill/memory capabilities.
    """
    dist = RESEARCH_TOOLSET_DISTRIBUTIONS.get(distribution)
    if not dist:
        dist = RESEARCH_TOOLSET_DISTRIBUTIONS["maritime_research"]

    hermes_config = HermesAgentConfig(
        max_iterations=90,
        iteration_budget=90,
        toolset_distribution=ToolsetDistribution(
            name=distribution,
            description=dist["description"],
            toolsets=dict(dist["toolsets"]),
        ),
        enabled_toolsets=list(dist["toolsets"].keys()),
        disabled_toolsets=[],
        memory_enabled=True,
        session_search_enabled=True,
        skill_auto_create=True,
        soul_md=soul_md or MARINE_RESEARCHER_SOUL,
        context_files=[
            "AGENTS.md",
            "docs/SJTU_REQUIREMENTS_ANALYSIS.md",
            "docs/requirements_analysis.md",
            "docs/gap_analysis.md",
        ],
        can_delegate=can_delegate,
        max_subagents=3,
        platform="cli",
    )

    agent = AgentProfile(
        name=name,
        role="海洋研究员 (Hermes Agent)",
        description=(
            "Hermes-style self-improving maritime research agent — "
            "穿浪双体船(WPC)、COLREGs、EEXI/CII/SEEMP、MASS自主等级、船岸通信。"
            "Closed learning loop with skills, memory, and session search."
        ),
        template_type=AgentTemplateType.HERMES_RESEARCHER,
        system_prompt="",  # Built dynamically via build_research_system_prompt()
        personality=AgentPersonality(
            tone="professional",
            language="zh-CN",
            expertise_areas=[
                "WPC hull design",
                "COLREGs collision avoidance",
                "EEXI/CII/SEEMP compliance",
                "MASS autonomy levels",
                "ship-shore communications",
                "IMO/CCS/DNV standards",
            ],
            response_style="rigorous",
            creativity=0.3,
        ),
        tools=[],  # Resolved dynamically from toolset distribution
        skills=[],  # Populated from research skill registry
        hermes_config=hermes_config,
    )

    # Build the initial system prompt
    active_toolsets = sample_toolsets(distribution)
    agent.system_prompt = build_research_system_prompt(agent, active_toolsets)
    agent.tools = resolve_tools(active_toolsets)

    return agent


# ══════════════════════════════════════════════════════════════
# Hermes-style Agent Loop (simplified)
# Inspired by NousResearch/hermes-agent/run_agent.py AIAgent class
# ══════════════════════════════════════════════════════════════

@dataclass
class AgentTurn:
    """A single turn in the agent conversation loop."""
    role: str = "user"
    content: str = ""
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AgentSession:
    """Hermes-style conversation session for the research agent."""
    session_id: str = ""
    agent_id: str = ""
    messages: List[AgentTurn] = field(default_factory=list)
    api_call_count: int = 0
    max_iterations: int = 90
    skills_created: List[str] = field(default_factory=list)
    memories_saved: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "turn_count": len(self.messages),
            "api_call_count": self.api_call_count,
            "max_iterations": self.max_iterations,
            "skills_created": self.skills_created,
            "memories_saved": self.memories_saved,
        }


def get_research_distributions() -> Dict[str, Dict[str, Any]]:
    """Return all available research toolset distributions."""
    return {k: {"description": v["description"], "toolsets": v["toolsets"]}
            for k, v in RESEARCH_TOOLSET_DISTRIBUTIONS.items()}


def get_hermes_toolsets() -> Dict[str, Dict[str, Any]]:
    """Return all Hermes-style toolset definitions."""
    return {k: {"description": v["description"], "tools": v["tools"]}
            for k, v in HERMES_TOOLSETS.items()}
