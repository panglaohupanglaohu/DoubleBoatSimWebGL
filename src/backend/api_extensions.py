# -*- coding: utf-8 -*-
"""
API Extensions - 为新 AI Native Channels 添加 API 端点
注意：由于 FastAPI 依赖问题，这里的路由函数将在 main.py 中实现
"""

from typing import Dict, Any
import logging

# API 端点定义（作为参考）
API_ENDPOINTS = {
    "/api/v1/ai-native/compliance/status": {
        "method": "GET",
        "description": "获取船舶合规状态",
        "params": ["query"]
    },
    "/api/v1/ai-native/compliance/cognitive-snapshot": {
        "method": "GET", 
        "description": "获取认知快照"
    },
    "/api/v1/ai-native/perception/events": {
        "method": "GET",
        "description": "获取感知事件流",
        "params": ["limit"]
    },
    "/api/v1/ai-native/perception/capture-snapshot": {
        "method": "GET",
        "description": "捕获感知快照"
    },
    "/api/v1/ai-native/decision/package": {
        "method": "GET",
        "description": "获取决策包"
    },
    "/api/v1/ai-native/decision/feedback": {
        "method": "POST",
        "description": "记录决策反馈",
        "params": ["action", "outcome", "confirmed_by"]
    },
    "/api/v1/ai-native/status/full-pipeline": {
        "method": "GET",
        "description": "获取完整AI Native管道状态"
    }
}

def get_api_endpoints():
    """返回所有API端点定义"""
    return API_ENDPOINTS

def register_ai_native_endpoints(app):
    """在主应用中注册AI Native端点"""
    # Import inside function to avoid circular dependencies
    from channels.marine_base import get_default_registry
    from channels.compliance_digital_expert import ComplianceDigitalExpertChannel
    from channels.distributed_perception_hub import DistributedPerceptionHubChannel
    from channels.decision_orchestrator import DecisionOrchestratorChannel
    from fastapi import HTTPException
    
    @app.get("/api/v1/ai-native/compliance/status")
    async def get_compliance_status(query: str = "overall"):
        """获取船舶合规状态"""
        registry = get_default_registry()
        channel = registry.get("compliance_digital_expert")
        
        if not channel:
            raise HTTPException(status_code=404, detail="Compliance Digital Expert channel not found")
        
        if not isinstance(channel, ComplianceDigitalExpertChannel):
            raise HTTPException(status_code=500, detail="Invalid channel type")
        
        try:
            result = channel.query_compliance_status(query)
            return {
                "channel": "compliance_digital_expert",
                "query": query,
                "result": result,
                "timestamp": result.get("timestamp")
            }
        except Exception as e:
            logger.error(f"Compliance status query failed: {e}")
            raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    @app.get("/api/v1/ai-native/compliance/cognitive-snapshot")
    async def get_cognitive_snapshot():
        """获取认知快照"""
        registry = get_default_registry()
        channel = registry.get("compliance_digital_expert")
        
        if not channel:
            raise HTTPException(status_code=404, detail="Compliance Digital Expert channel not found")
        
        if not isinstance(channel, ComplianceDigitalExpertChannel):
            raise HTTPException(status_code=500, detail="Invalid channel type")
        
        try:
            snapshot = channel.build_cognitive_snapshot()
            return {
                "channel": "compliance_digital_expert",
                "endpoint": "cognitive-snapshot",
                "result": snapshot,
                "timestamp": snapshot.get("timestamp")
            }
        except Exception as e:
            logger.error(f"Cognitive snapshot failed: {e}")
            raise HTTPException(status_code=500, detail=f"Snapshot failed: {str(e)}")

    @app.get("/api/v1/ai-native/perception/events")
    async def get_perception_events(limit: int = 20):
        """获取感知事件流"""
        registry = get_default_registry()
        channel = registry.get("distributed_perception_hub")
        
        if not channel:
            raise HTTPException(status_code=404, detail="Distributed Perception Hub channel not found")
        
        if not isinstance(channel, DistributedPerceptionHubChannel):
            raise HTTPException(status_code=500, detail="Invalid channel type")
        
        try:
            events = channel.get_latest_events(limit)
            return {
                "channel": "distributed_perception_hub",
                "endpoint": "events",
                "result": {
                    "events": events,
                    "count": len(events),
                    "limit": limit
                },
                "timestamp": events[0]["timestamp"] if events else None
            }
        except Exception as e:
            logger.error(f"Perception events query failed: {e}")
            raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    @app.get("/api/v1/ai-native/perception/capture-snapshot")
    async def capture_perception_snapshot():
        """捕获感知快照"""
        registry = get_default_registry()
        channel = registry.get("distributed_perception_hub")
        
        if not channel:
            raise HTTPException(status_code=404, detail="Distributed Perception Hub channel not found")
        
        if not isinstance(channel, DistributedPerceptionHubChannel):
            raise HTTPException(status_code=500, detail="Invalid channel type")
        
        try:
            captured = channel.capture_system_snapshot()
            return {
                "channel": "distributed_perception_hub",
                "endpoint": "capture-snapshot",
                "result": {
                    "captured_events": len(captured),
                    "total_events": len(channel.events),
                    "fusion_events": len([e for e in channel.events if "fusion" in e.event_type])
                },
                "timestamp": captured[0].timestamp if captured else None
            }
        except Exception as e:
            logger.error(f"Perception snapshot capture failed: {e}")
            raise HTTPException(status_code=500, detail=f"Capture failed: {str(e)}")

    @app.get("/api/v1/ai-native/decision/package")
    async def get_decision_package():
        """获取决策包"""
        registry = get_default_registry()
        channel = registry.get("decision_orchestrator")
        
        if not channel:
            raise HTTPException(status_code=404, detail="Decision Orchestrator channel not found")
        
        if not isinstance(channel, DecisionOrchestratorChannel):
            raise HTTPException(status_code=500, detail="Invalid channel type")
        
        try:
            package = channel.build_decision_package()
            return {
                "channel": "decision_orchestrator",
                "endpoint": "package",
                "result": package,
                "timestamp": package.get("generated_at")
            }
        except Exception as e:
            logger.error(f"Decision package query failed: {e}")
            raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    @app.post("/api/v1/ai-native/decision/feedback")
    async def record_decision_feedback(action: str, outcome: str, confirmed_by: str = "user"):
        """记录决策反馈"""
        registry = get_default_registry()
        channel = registry.get("decision_orchestrator")
        
        if not channel:
            raise HTTPException(status_code=404, detail="Decision Orchestrator channel not found")
        
        if not isinstance(channel, DecisionOrchestratorChannel):
            raise HTTPException(status_code=500, detail="Invalid channel type")
        
        try:
            feedback = channel.record_feedback(action, outcome, confirmed_by)
            return {
                "channel": "decision_orchestrator",
                "endpoint": "feedback",
                "result": feedback,
                "feedback_records_count": len(channel.feedback_records)
            }
        except Exception as e:
            logger.error(f"Decision feedback recording failed: {e}")
            raise HTTPException(status_code=500, detail=f"Recording failed: {str(e)}")

    @app.get("/api/v1/ai-native/status/full-pipeline")
    async def get_full_pipeline_status():
        """获取完整AI Native管道状态"""
        registry = get_default_registry()
        
        compliance_ch = registry.get("compliance_digital_expert")
        perception_ch = registry.get("distributed_perception_hub")
        decision_ch = registry.get("decision_orchestrator")
        
        # Build comprehensive status
        status = {
            "pipeline": "ai_native_cognitive_pipeline",
            "timestamp": "",
            "components": {
                "compliance": {
                    "available": compliance_ch is not None,
                    "status": compliance_ch.get_status() if compliance_ch else None,
                    "cognitive_snapshot": compliance_ch.build_cognitive_snapshot() if compliance_ch else None
                },
                "perception": {
                    "available": perception_ch is not None,
                    "status": perception_ch.get_status() if perception_ch else None,
                    "latest_events": perception_ch.get_latest_events(5) if perception_ch else None
                },
                "decision": {
                    "available": decision_ch is not None,
                    "status": decision_ch.get_status() if decision_ch else None,
                    "decision_package": decision_ch.build_decision_package() if decision_ch else None
                }
            },
            "pipeline_health": "degraded"  # default
        }
        
        # Determine overall health
        all_available = all([
            compliance_ch is not None,
            perception_ch is not None,
            decision_ch is not None
        ])
        
        if all_available:
            status["pipeline_health"] = "operational"
        elif any([compliance_ch, perception_ch, decision_ch]):
            status["pipeline_health"] = "partial"
        
        return status