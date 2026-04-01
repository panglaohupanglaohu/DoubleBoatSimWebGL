# AI Native 4-Hour Smart Shipping UI Execution Plan (2026-03-21)

## Planning Basis

This plan is rebuilt from the document "Smart Shipping China: Elements & Pathways" and from the current Poseidon-X codebase state.

Key takeaways used for planning:

1. Smart shipping is not only an autonomous ship problem. It is a ship-shore-port-regulation-data system problem.
2. The highest-value capability chain is: sensing -> communication -> route planning -> decision/avoidance -> remote collaboration -> safety governance.
3. Core capability domains repeatedly emphasized in the document are:
   - route generation and path planning
   - ship-shore communication
   - autonomous decision and collision avoidance
   - target detection and recognition
   - remote control centre collaboration
   - redundancy, fault tolerance, and safety equivalence with conventional shipping
4. Smart shipping elements should be decomposed beyond the vessel itself. The interface should reflect at least these operational domains:
   - vessel/platform
   - navigation/perception
   - communication/shore control
   - port/environment
   - people/regulation/safety
5. A useful UI for a captain or shore operator should not present isolated modules first. It should present operational readiness first, then decision support, then subsystem drill-down.

## Current Baseline

Current strengths in the repository:

1. The backend already exposes AI Native and SVESSEL-related APIs.
2. The captain cockpit already integrates digital twin, map, mission brief, PHM, autonomy, link, and cyber status.
3. Integration and regression tests are currently green.

Current weaknesses:

1. The cockpit still reads as a feature aggregation page, not a smart shipping operations console.
2. Information hierarchy is module-first instead of mission-first.
3. The UI does not clearly express the five smart shipping element domains.
4. The UI does not make the pathway maturity visible: sensing, route planning, communication, autonomy, governance.
5. Human/shore/regulation context is not visually strong enough compared with raw technical status.

## 4-Hour Goal

In 4 hours, deliver a mission-first smart shipping cockpit that:

1. Reorganizes the page around smart shipping operational domains.
2. Makes ship-shore collaboration and remote-control readiness explicit.
3. Surfaces pathway readiness for sensing, communication, planning, autonomy, and governance.
4. Preserves all current integrations and graceful degradation behavior.
5. Produces a UI that is presentation-ready for a "China smart shipping pathway" narrative, not only a dev dashboard narrative.

## Definition of Done

The 4-hour sprint is considered complete when all of the following are true:

1. The cockpit has a visible smart shipping domain layer near the top of the page.
2. The cockpit has a pathway board showing readiness across core smart shipping capabilities.
3. Existing mission, map, analytics, and command panels still work.
4. Partial endpoint failure does not break the page refresh loop.
5. The HTML file has no editor-detected errors.
6. The page remains usable on desktop and mobile.
7. The UI language and labels reflect ship, shore, environment, and governance concerns instead of only subsystem names.

## Design Direction

### Information Hierarchy

The page should be read in this order:

1. Mission identity and system state
2. Smart shipping element domains
3. Critical operational KPIs
4. Decision and pathway readiness
5. Detailed map, command, analytics, and subsystem evidence

### UI Principles

1. Mission-first: the operator should know what matters before seeing every subsystem.
2. Domain-based: show vessel, navigation, shore, environment, and governance as first-class operational concerns.
3. Status-rich: every card should say both current state and why it matters.
4. Graceful degradation: if one endpoint fails, the board still tells a coherent story.
5. Shore-aware: the UI must communicate that smart shipping is cooperative, not ship-only automation.

## 4-Hour Breakdown

## Hour 1 - UI Information Architecture Reset

### Objective

Restructure the cockpit around smart shipping operational domains.

### Tasks

1. Add a smart shipping domain strip directly below the top bar.
2. Create five domain cards:
   - vessel platform
   - navigation and perception
   - ship-shore collaboration
   - port and environment
   - people and governance
3. Update the header copy to reflect smart shipping elements and pathways.
4. Keep existing KPI cards, but make them the second layer rather than the first story.

### UI Output

Each domain card must include:

1. domain label
2. readiness grade
3. one short evidence line
4. one short operational implication line

### Validation

1. All domain cards render even if some APIs fail.
2. No layout break on desktop and mobile.
3. Visual hierarchy is clearly better than the current module stack.

## Hour 2 - Pathway Board and Mission Readiness

### Objective

Turn the page into a pathway-oriented operations board.

### Tasks

1. Add a pathway panel in the sidebar.
2. Define pathway stages aligned with the report:
   - sensing fusion
   - communication and RCC
   - route planning and avoidance
   - autonomy and execution
   - safety and governance
3. For each stage, compute:
   - current status
   - supporting evidence
   - a simple readiness meter
4. Use existing data first; do not add backend coupling unless required.

### Validation

1. Pathway board reads as a compact maturity/status narrative.
2. Pathway states reflect real values from the current APIs.
3. The board is understandable without opening dev tools.

## Hour 3 - Data Normalization and Interaction Hardening

### Objective

Build a UI model that matches smart shipping concepts instead of backend object boundaries.

### Tasks

1. Introduce a smart shipping normalization layer in the cockpit script.
2. Derive domain readiness from existing metrics:
   - PHM, SHM for vessel platform
   - collision risk and scene for navigation/perception
   - link quality and autonomy authority for ship-shore
   - map/worldmonitor/scene context for port and environment
   - cyber threat and compliance/autonomy context for people and governance
3. Add tone mapping and badge mapping for all derived states.
4. Preserve Promise.allSettled behavior for new derived views.
5. Extend command chips to better reflect smart shipping operational language.

### Validation

1. No uncaught JS exceptions.
2. Derived views still render with missing optional fields.
3. Existing mission and analytics features remain intact.

## Hour 4 - Final UI Polish and Operational Verification

### Objective

Make the page review-ready and execution-ready.

### Tasks

1. Refine spacing, card density, and responsive behavior.
2. Verify badge semantics are consistent across domain cards, pathway cards, and KPI cards.
3. Validate that the cockpit still refreshes cleanly under partial endpoint failure.
4. Run editor diagnostics and targeted regression validation if needed.
5. Record what remains for the next iteration.

### Validation

1. No editor-detected errors in the modified files.
2. Existing regression status remains green or unchanged.
3. UI now supports a smart shipping operations narrative for demo and review.

## Immediate Coding Scope

This sprint will implement now:

1. A smart shipping domain strip.
2. A pathway readiness board.
3. A smarter normalization layer for domain/pathway rendering.
4. Updated copy and command labels aligned to smart shipping language.
5. Responsive behavior preservation.

## Deferred Scope

These items are intentionally not included in the 4-hour sprint unless blockers appear:

1. New backend APIs only for UI decoration.
2. Full port-call operational workflow.
3. Cargo chain and logistics visualization.
4. Dedicated RCC page.
5. Historical playback timeline.

## Risks and Controls

1. Risk: the UI becomes visually denser but less readable.
   Control: domain strip stays concise; pathway board remains compact.

2. Risk: current APIs do not expose every smart shipping element explicitly.
   Control: derive domain status from the nearest stable signals and label inferred states clearly.

3. Risk: new UI logic introduces brittle coupling.
   Control: keep all derived logic in one normalization layer and preserve fallback defaults.

4. Risk: mobile layout degrades.
   Control: ensure the new sections collapse into stacked cards below 1100px and 720px breakpoints.

## Expected Sprint Outcome

At the end of this 4-hour sprint, Poseidon-X should present itself less like a technical integration page and more like a Chinese smart shipping command surface that communicates:

1. what the ship knows
2. how the ship collaborates with shore
3. how route, autonomy, and safety decisions are progressing
4. whether the platform is operationally and regulatorily ready

That is the right UI direction for the document's "elements and pathways" framing.