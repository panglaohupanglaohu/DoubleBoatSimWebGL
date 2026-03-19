#!/usr/bin/env python3
"""Audit all backend modules for import errors."""
import importlib
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

modules = [
    'backend.channels.marine_base',
    'backend.channels.intelligent_engine',
    'backend.channels.intelligent_navigation',
    'backend.channels.compliance_digital_expert',
    'backend.channels.decision_orchestrator',
    'backend.channels.distributed_perception_hub',
    'backend.channels.energy_efficiency_channel',
    'backend.channels.energy_efficiency_manager',
    'backend.channels.efficiency_models',
    'backend.channels.eexi_calculator',
    'backend.channels.cii_calculator',
    'backend.channels.seemp_manager',
    'backend.channels.efficiency_advisor',
    'backend.channels.compliance_reporter',
    'backend.channels.engine_monitor',
    'backend.channels.nmea2000_parser',
    'backend.channels.feature_fusion_layer',
    'backend.channels.maritime_scene_model',
    'backend.channels.openbridge_command_router',
    'backend.channels.rcs_control',
    'backend.channels.structural_health_monitor',
    'backend.channels.marine_message_bus',
    'backend.storage.event_store',
    'backend.storage.data_lakehouse',
    'backend.storage.cloud_sync',
    'backend.config_loader',
]

ok = 0
err = 0
for m in modules:
    try:
        importlib.import_module(m)
        print(f'OK  {m}')
        ok += 1
    except Exception as e:
        print(f'ERR {m}: {type(e).__name__}: {e}')
        err += 1

print(f'\nResult: {ok} OK, {err} ERR out of {ok+err} modules')
