# -*- coding: utf-8 -*-
"""
Agent Team Scheduler - 双智能体团队统一调度器

驱动构建团队和执行团队按各自的调度频率运行。
提供统一的启动 / 停止 / 监控接口和每小时汇报机制。
可以在 FastAPI 的 lifespan 中作为后台 asyncio 任务运行。
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentTeamScheduler:
    """统一调度引擎：驱动构建团队和执行团队."""

    # 调度器自身 tick 间隔 (秒) — 越小越精确
    TICK_INTERVAL = 15

    # 每小时汇报间隔 (秒)
    HOURLY_REPORT_INTERVAL = 3600

    def __init__(
        self,
        build_team=None,
        execution_team=None,
        channel_registry=None,
    ):
        self.build_team = build_team
        self.execution_team = execution_team
        self.channel_registry = channel_registry

        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._last_hourly_report: Optional[float] = None
        self._tick_count = 0
        self._start_time: Optional[float] = None
        self.reports: List[Dict[str, Any]] = []

    # ── 启动 / 停止 ────────────────────────────────────────

    async def start(self):
        """启动调度器 (作为 asyncio 后台任务)."""
        if self._running:
            return
        self._running = True
        self._start_time = time.monotonic()
        self._last_hourly_report = self._start_time
        self._task = asyncio.create_task(self._scheduler_loop())
        logger.info("📅 AgentTeamScheduler started (tick=%ds)", self.TICK_INTERVAL)

    async def stop(self):
        """停止调度器."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("📅 AgentTeamScheduler stopped")

    # ── 主循环 ──────────────────────────────────────────────

    async def _scheduler_loop(self):
        while self._running:
            try:
                now = datetime.now()
                self._tick_count += 1

                # 驱动构建团队
                if self.build_team:
                    try:
                        await asyncio.get_event_loop().run_in_executor(None, self.build_team.tick, now)
                    except Exception as exc:
                        logger.error("Build team tick error: %s", exc)

                # 驱动执行团队
                if self.execution_team:
                    try:
                        registry_dict = None
                        if self.channel_registry:
                            registry_dict = {
                                name: self.channel_registry.get(name)
                                for name in self.channel_registry.list_channels()
                            }
                        await asyncio.get_event_loop().run_in_executor(None, self.execution_team.tick, now, registry_dict)
                    except Exception as exc:
                        logger.error("Execution team tick error: %s", exc)

                # 每小时生成报告
                elapsed = time.monotonic() - (self._last_hourly_report or 0)
                if elapsed >= self.HOURLY_REPORT_INTERVAL:
                    self._generate_combined_report()
                    self._last_hourly_report = time.monotonic()

            except Exception as exc:
                logger.error("Scheduler loop error: %s", exc)

            await asyncio.sleep(self.TICK_INTERVAL)

    # ── 手动 tick (测试用) ──────────────────────────────────

    def tick_once(self, now: Optional[datetime] = None):
        """同步驱动一次 tick (主要用于测试)."""
        now = now or datetime.now()
        self._tick_count += 1
        results: Dict[str, Any] = {"tick": self._tick_count, "time": now.isoformat()}
        if self.build_team:
            results["build"] = self.build_team.tick(now)
        if self.execution_team:
            results["execution"] = self.execution_team.tick(now)
        return results

    # ── 汇报 ────────────────────────────────────────────────

    def _generate_combined_report(self) -> Dict[str, Any]:
        report: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "scheduler_ticks": self._tick_count,
            "uptime_seconds": round(time.monotonic() - (self._start_time or 0), 1),
        }

        if self.build_team:
            hr = self.build_team.generate_hourly_report()
            report["build_team"] = hr.to_dict()

        if self.execution_team:
            er = self.execution_team.generate_execution_report()
            report["execution_team"] = er.to_dict()

        self.reports.append(report)
        logger.info(
            "📊 Combined hourly report generated (tick #%d)", self._tick_count
        )
        return report

    def generate_report_now(self) -> Dict[str, Any]:
        """手动生成一份联合报告."""
        return self._generate_combined_report()

    # ── 状态 ────────────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        return {
            "running": self._running,
            "tick_count": self._tick_count,
            "tick_interval_sec": self.TICK_INTERVAL,
            "hourly_report_interval_sec": self.HOURLY_REPORT_INTERVAL,
            "reports_generated": len(self.reports),
            "uptime_seconds": (
                round(time.monotonic() - self._start_time, 1) if self._start_time else 0
            ),
            "build_team_active": self.build_team is not None,
            "execution_team_active": self.execution_team is not None,
            "latest_report": self.reports[-1] if self.reports else None,
        }


__all__ = ["AgentTeamScheduler"]
