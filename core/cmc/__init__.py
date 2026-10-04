"""
KALATRACE Command & Mission Center (CMC)

Unifying facade over the four CMC subsystems:

- core.mission   (Mission Manager)
- core.command   (Command Layer)
- core.decision  (Decision Oversight)
- core.resource  (Resource Allocation)

Coordinating actual execution against KALATRACE Engines remains
the sole responsibility of engines.cognitive_orchestrator,
which already implements engine coordination against a
separate, official specification (Documento 26, Art. 7: "toda
comunicacao ocorrera por intermedio do Cognitive Orchestrator").
The CMC never talks to Engines directly. Instead, an optional
bridge (CognitiveOrchestratorExecutor, see
cognitive_orchestrator_bridge.py) adapts the Cognitive
Orchestrator to the same CommandExecutor contract used by any
other executor, so missions can trigger a cognitive cycle
through the ordinary Command dispatch path -- see
CommandMissionCenter.connect_cognitive_orchestrator().
"""

from __future__ import annotations

from .command_mission_center import CommandMissionCenter

from .cognitive_orchestrator_bridge import CognitiveOrchestratorExecutor


__all__ = [

    "CommandMissionCenter",

    "CognitiveOrchestratorExecutor",

]
