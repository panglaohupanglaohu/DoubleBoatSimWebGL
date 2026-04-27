#!/usr/bin/env python3
"""Bulk convert dark-theme hardcoded colors → wabi-sabi palette across all frontend HTML files."""
import re, os, sys

FRONTEND = os.path.join(os.path.dirname(__file__), '..', 'src', 'frontend')

# Files already fully converted — skip
SKIP = {
    'datacenter-digital-twin.html',
    'marine-datacenter.html',
    'datacenter-sensory-mesh.html',
    'index.html',
}
# Design demos and archived — skip
SKIP_PREFIX = ('design-demo-', 'ARCHIVED_')
SKIP_SUFFIX = ('.bak.html',)

# ── Color mapping: old → new ──
# Sorted longest-first to avoid partial matches
HEX_MAP = {
    # Neon blues → koke green
    '#38bdf8': 'oklch(0.52 0.04 160)',
    '#38BDF8': 'oklch(0.52 0.04 160)',
    '#22c4ff': 'oklch(0.52 0.04 160)',
    '#64d2ff': 'oklch(0.52 0.04 160)',
    '#22d3ee': 'oklch(0.52 0.04 160)',
    '#2563eb': 'oklch(0.52 0.04 160)',
    '#007aff': 'oklch(0.52 0.04 160)',
    '#3b82f6': 'oklch(0.52 0.04 160)',
    '#4fc3f7': 'oklch(0.52 0.04 160)',
    '#4a90e2': 'oklch(0.52 0.04 160)',
    '#00aaff': 'oklch(0.52 0.04 160)',
    '#0088ff': 'oklch(0.52 0.04 160)',
    '#5ca8ff': 'oklch(0.52 0.04 160)',
    '#2196f3': 'oklch(0.52 0.04 160)',
    '#42a5f5': 'oklch(0.52 0.04 160)',
    '#64b5f6': 'oklch(0.52 0.04 160)',
    '#90caf9': 'oklch(0.52 0.04 160)',
    '#29b6f6': 'oklch(0.52 0.04 160)',
    '#039be5': 'oklch(0.52 0.04 160)',
    '#0288d1': 'oklch(0.52 0.04 160)',
    '#0277bd': 'oklch(0.52 0.04 160)',
    '#01579b': 'oklch(0.52 0.04 160)',
    '#1565c0': 'oklch(0.52 0.04 160)',
    '#1976d2': 'oklch(0.52 0.04 160)',
    '#1e88e5': 'oklch(0.52 0.04 160)',
    '#bbdefb': 'oklch(0.82 0.004 110)',
    '#e3f2fd': 'oklch(0.91 0.004 110)',
    '#60a5fa': 'oklch(0.52 0.04 160)',
    '#93c5fd': 'oklch(0.52 0.04 160)',
    '#79a6ff': 'oklch(0.18 0.008 110)',
    '#4e74d4': 'oklch(0.18 0.008 110)',
    '#7c4dff': 'oklch(0.56 0.05 70)',
    # Neon green → koke
    '#06ffa5': 'oklch(0.52 0.04 160)',
    '#30d158': 'oklch(0.52 0.04 160)',
    '#4ade80': 'oklch(0.52 0.04 160)',
    '#86efac': 'oklch(0.52 0.04 160)',
    '#22c55e': 'oklch(0.52 0.04 160)',
    '#10b981': 'oklch(0.52 0.04 160)',
    '#34d399': 'oklch(0.52 0.04 160)',
    '#16a34a': 'oklch(0.52 0.04 160)',
    '#059669': 'oklch(0.52 0.04 160)',
    '#71d977': 'oklch(0.52 0.04 160)',
    '#7ee089': 'oklch(0.52 0.04 160)',
    '#4ecf56': 'oklch(0.52 0.04 160)',
    '#59d957': 'oklch(0.52 0.04 160)',
    '#2f9d2a': 'oklch(0.52 0.04 160)',
    '#48bb78': 'oklch(0.52 0.04 160)',
    '#6ee7b7': 'oklch(0.52 0.04 160)',
    '#81c784': 'oklch(0.52 0.04 160)',
    '#66bb6a': 'oklch(0.52 0.04 160)',
    '#43a047': 'oklch(0.52 0.04 160)',
    '#388e3c': 'oklch(0.52 0.04 160)',
    '#2e7d32': 'oklch(0.52 0.04 160)',
    '#1b5e20': 'oklch(0.52 0.04 160)',
    '#00ff66': 'oklch(0.52 0.04 160)',
    '#00cc55': 'oklch(0.52 0.04 160)',
    '#40c2a4': 'oklch(0.52 0.04 160)',
    '#26a69a': 'oklch(0.52 0.04 160)',
    '#009688': 'oklch(0.52 0.04 160)',
    '#00bcd4': 'oklch(0.52 0.04 160)',
    '#a5d6a7': 'oklch(0.82 0.004 110)',
    '#c8e6c9': 'oklch(0.91 0.004 110)',
    '#e8f5e9': 'oklch(0.96 0.003 110)',
    # Red/alarm → shu
    '#f87171': 'oklch(0.48 0.07 22)',
    '#ef4444': 'oklch(0.48 0.07 22)',
    '#ff4e4e': 'oklch(0.48 0.07 22)',
    '#dc2626': 'oklch(0.48 0.07 22)',
    '#b91c1c': 'oklch(0.48 0.07 22)',
    '#b71528': 'oklch(0.48 0.07 22)',
    '#ec6b78': 'oklch(0.48 0.07 22)',
    '#ff6e7a': 'oklch(0.48 0.07 22)',
    '#ec2637': 'oklch(0.48 0.07 22)',
    '#ff3300': 'oklch(0.48 0.07 22)',
    '#e11d48': 'oklch(0.48 0.07 22)',
    '#fb7185': 'oklch(0.48 0.07 22)',
    '#f56565': 'oklch(0.48 0.07 22)',
    '#ff453a': 'oklch(0.48 0.07 22)',
    '#ff1744': 'oklch(0.48 0.07 22)',
    '#d50000': 'oklch(0.48 0.07 22)',
    '#e53935': 'oklch(0.48 0.07 22)',
    '#c62828': 'oklch(0.48 0.07 22)',
    '#e57373': 'oklch(0.48 0.07 22)',
    '#ef5350': 'oklch(0.48 0.07 22)',
    '#f44336': 'oklch(0.48 0.07 22)',
    '#ff5252': 'oklch(0.48 0.07 22)',
    '#ffcdd2': 'oklch(0.91 0.004 110)',
    '#ffebee': 'oklch(0.96 0.003 110)',
    # Yellow/warn → kitsune
    '#fbbf24': 'oklch(0.56 0.05 70)',
    '#ffc83d': 'oklch(0.56 0.05 70)',
    '#f59e0b': 'oklch(0.56 0.05 70)',
    '#eab308': 'oklch(0.56 0.05 70)',
    '#facc15': 'oklch(0.56 0.05 70)',
    '#ff9a2f': 'oklch(0.56 0.05 70)',
    '#dcdc5b': 'oklch(0.56 0.05 70)',
    '#dcdc7a': 'oklch(0.56 0.05 70)',
    '#dbd84b': 'oklch(0.56 0.05 70)',
    '#c9d24a': 'oklch(0.56 0.05 70)',
    '#e6a400': 'oklch(0.56 0.05 70)',
    '#a8950d': 'oklch(0.56 0.05 70)',
    '#d97706': 'oklch(0.56 0.05 70)',
    '#ca8a04': 'oklch(0.56 0.05 70)',
    '#fed7aa': 'oklch(0.56 0.05 70)',
    '#f6ad55': 'oklch(0.56 0.05 70)',
    '#ff9f0a': 'oklch(0.56 0.05 70)',
    '#fb8c00': 'oklch(0.56 0.05 70)',
    '#ff9800': 'oklch(0.56 0.05 70)',
    '#ffa726': 'oklch(0.56 0.05 70)',
    '#ffb74d': 'oklch(0.56 0.05 70)',
    '#ffcc80': 'oklch(0.56 0.05 70)',
    '#ffe0b2': 'oklch(0.91 0.004 110)',
    '#fff3e0': 'oklch(0.96 0.003 110)',
    '#ffca28': 'oklch(0.56 0.05 70)',
    '#ffd54f': 'oklch(0.56 0.05 70)',
    '#ffecb3': 'oklch(0.91 0.004 110)',
    '#fff8e1': 'oklch(0.96 0.003 110)',
    # Purple → muted
    '#a78bfa': 'oklch(0.55 0.005 110)',
    '#bf5af2': 'oklch(0.55 0.005 110)',
    '#6b21a8': 'oklch(0.55 0.005 110)',
    '#9a3412': 'oklch(0.48 0.07 22)',
    '#1e40af': 'oklch(0.52 0.04 160)',
    '#8b5cf6': 'oklch(0.55 0.005 110)',
    '#7c3aed': 'oklch(0.55 0.005 110)',
    '#c084fc': 'oklch(0.55 0.005 110)',
    '#5e5ce6': 'oklch(0.18 0.008 110)',
    # Dark backgrounds → light stone
    '#060d1a': 'oklch(0.96 0.003 110)',
    '#04060c': 'oklch(0.96 0.003 110)',
    '#04070d': 'oklch(0.96 0.003 110)',
    '#04080f': 'oklch(0.96 0.003 110)',
    '#040912': 'oklch(0.96 0.003 110)',
    '#060a14': 'oklch(0.96 0.003 110)',
    '#0a0e14': 'oklch(0.96 0.003 110)',
    '#0a0e1a': 'oklch(0.96 0.003 110)',
    '#0a1122': 'oklch(0.93 0.003 110)',
    '#0a1220': 'oklch(0.93 0.003 110)',
    '#0a1a30': 'oklch(0.82 0.004 110)',
    '#111e34': 'oklch(0.91 0.004 110)',
    '#1a2744': 'oklch(0.91 0.004 110)',
    '#1a2a3a': 'oklch(0.91 0.004 110)',
    '#1f2a44': 'oklch(0.91 0.004 110)',
    '#1a1a2e': 'oklch(0.93 0.003 110)',
    '#0f172a': 'oklch(0.96 0.003 110)',
    '#020617': 'oklch(0.96 0.003 110)',
    '#1e293b': 'oklch(0.93 0.003 110)',
    '#0f0f0f': 'oklch(0.96 0.003 110)',
    '#111111': 'oklch(0.96 0.003 110)',
    '#1a1a1a': 'oklch(0.93 0.003 110)',
    '#171717': 'oklch(0.93 0.003 110)',
    '#242424': 'oklch(0.93 0.003 110)',
    '#121212': 'oklch(0.96 0.003 110)',
    '#0d0d0d': 'oklch(0.96 0.003 110)',
    '#222222': 'oklch(0.93 0.003 110)',
    '#1e1e1e': 'oklch(0.93 0.003 110)',
    '#2c2c2c': 'oklch(0.82 0.004 110)',
    '#333333': 'oklch(0.82 0.004 110)',
    '#333': 'oklch(0.82 0.004 110)',
    '#18181b': 'oklch(0.96 0.003 110)',
    '#0c0c0c': 'oklch(0.96 0.003 110)',
    '#334155': 'oklch(0.82 0.004 110)',
    # Medium grays → appropriate stone tones
    '#444444': 'oklch(0.72 0.006 110)',
    '#444': 'oklch(0.72 0.006 110)',
    '#555555': 'oklch(0.72 0.006 110)',
    '#555': 'oklch(0.72 0.006 110)',
    '#666666': 'oklch(0.65 0.005 110)',
    '#666': 'oklch(0.65 0.005 110)',
    '#777777': 'oklch(0.60 0.005 110)',
    '#777': 'oklch(0.60 0.005 110)',
    '#888888': 'oklch(0.55 0.005 110)',
    '#888': 'oklch(0.55 0.005 110)',
    '#999999': 'oklch(0.55 0.005 110)',
    '#999': 'oklch(0.55 0.005 110)',
    '#6d6d6d': 'oklch(0.55 0.005 110)',
    '#9e9e9e': 'oklch(0.55 0.005 110)',
    '#6b8cae': 'oklch(0.55 0.005 110)',
    '#9bb3cd': 'oklch(0.55 0.005 110)',
    '#5b7894': 'oklch(0.55 0.005 110)',
    '#64748b': 'oklch(0.55 0.005 110)',
    '#94a3b8': 'oklch(0.55 0.005 110)',
    '#aaaaaa': 'oklch(0.55 0.005 110)',
    '#aaa': 'oklch(0.55 0.005 110)',
    '#bdbdbd': 'oklch(0.55 0.005 110)',
    '#d8d8d8': 'oklch(0.82 0.004 110)',
    '#ccc': 'oklch(0.82 0.004 110)',
    '#cccccc': 'oklch(0.82 0.004 110)',
    '#ddd': 'oklch(0.82 0.004 110)',
    '#dddddd': 'oklch(0.82 0.004 110)',
    '#eee': 'oklch(0.91 0.004 110)',
    '#eeeeee': 'oklch(0.91 0.004 110)',
    '#e5e7eb': 'oklch(0.91 0.004 110)',
    '#d1d5db': 'oklch(0.82 0.004 110)',
    '#f3f4f6': 'oklch(0.96 0.003 110)',
    '#f9fafb': 'oklch(0.96 0.003 110)',
    '#475569': 'oklch(0.55 0.005 110)',
    '#374151': 'oklch(0.55 0.005 110)',
    '#4b5563': 'oklch(0.55 0.005 110)',
    '#6b7280': 'oklch(0.55 0.005 110)',
    '#9ca3af': 'oklch(0.55 0.005 110)',
    '#718096': 'oklch(0.55 0.005 110)',
    '#a0aec0': 'oklch(0.55 0.005 110)',
    '#4a5568': 'oklch(0.55 0.005 110)',
    '#2d3748': 'oklch(0.82 0.004 110)',
    '#e0e6f0': 'oklch(0.91 0.004 110)',
    '#e0f0ff': 'oklch(0.91 0.004 110)',
    # Light/white text → sumi or shironeri
    '#e2f2ff': 'oklch(0.18 0.008 110)',
    '#f0f6ff': 'oklch(0.18 0.008 110)',
    '#f1f5f9': 'oklch(0.18 0.008 110)',
    '#e2e8f0': 'oklch(0.18 0.008 110)',
    '#cbd5e1': 'oklch(0.55 0.005 110)',
    '#fff': 'oklch(0.96 0.003 110)',
    '#ffffff': 'oklch(0.96 0.003 110)',
    '#FFFFFF': 'oklch(0.96 0.003 110)',
    '#111': 'oklch(0.18 0.008 110)',
    '#000': 'oklch(0.18 0.008 110)',
    '#000000': 'oklch(0.18 0.008 110)',
    # Specific UI colors
    '#6f8f6f': 'oklch(0.52 0.04 160)',
    '#2a47e6': 'oklch(0.52 0.04 160)',
    # Pass 3 — remaining case-sensitive + new colors
    '#F59E0B': 'oklch(0.56 0.05 70)',
    '#0F172A': 'oklch(0.96 0.003 110)',
    '#818CF8': 'oklch(0.55 0.005 110)',
    '#00E5FF': 'oklch(0.52 0.04 160)',
    '#EF4444': 'oklch(0.48 0.07 22)',
    '#10B981': 'oklch(0.52 0.04 160)',
    '#3B82F6': 'oklch(0.52 0.04 160)',
    '#a0a0a0': 'oklch(0.55 0.005 110)',
    '#fc8181': 'oklch(0.48 0.07 22)',
    '#fca5a5': 'oklch(0.48 0.07 22)',
    '#f85149': 'oklch(0.48 0.07 22)',
    '#e0e0e0': 'oklch(0.82 0.004 110)',
    '#3fb950': 'oklch(0.52 0.04 160)',
    '#30363d': 'oklch(0.82 0.004 110)',
    '#dff7ff': 'oklch(0.91 0.004 110)',
    '#c9d1d9': 'oklch(0.55 0.005 110)',
    '#c8d8e8': 'oklch(0.82 0.004 110)',
    '#0891b2': 'oklch(0.52 0.04 160)',
    '#ff4444': 'oklch(0.48 0.07 22)',
    '#f97316': 'oklch(0.56 0.05 70)',
    '#f2f5fa': 'oklch(0.96 0.003 110)',
    '#ba68c8': 'oklch(0.55 0.005 110)',
    '#7fa0b5': 'oklch(0.55 0.005 110)',
    '#58a6ff': 'oklch(0.52 0.04 160)',
    '#8b949e': 'oklch(0.55 0.005 110)',
    '#161b22': 'oklch(0.96 0.003 110)',
    '#21262d': 'oklch(0.93 0.003 110)',
    '#0d1117': 'oklch(0.96 0.003 110)',
    '#b1bac4': 'oklch(0.55 0.005 110)',
    '#d2a8ff': 'oklch(0.55 0.005 110)',
    '#79c0ff': 'oklch(0.52 0.04 160)',
    '#7ee787': 'oklch(0.52 0.04 160)',
    '#ffa657': 'oklch(0.56 0.05 70)',
    '#e8e8e8': 'oklch(0.91 0.004 110)',
    '#f0f0f0': 'oklch(0.91 0.004 110)',
    '#b0b0b0': 'oklch(0.55 0.005 110)',
    '#c0c0c0': 'oklch(0.72 0.006 110)',
    '#d0d0d0': 'oklch(0.82 0.004 110)',
    '#808080': 'oklch(0.55 0.005 110)',
    '#606060': 'oklch(0.55 0.005 110)',
    '#505050': 'oklch(0.72 0.006 110)',
    '#404040': 'oklch(0.72 0.006 110)',
    '#303030': 'oklch(0.82 0.004 110)',
    '#202020': 'oklch(0.93 0.003 110)',
    '#151515': 'oklch(0.93 0.003 110)',
    '#101010': 'oklch(0.96 0.003 110)',
    '#e6e6e6': 'oklch(0.91 0.004 110)',
    '#e4e4e4': 'oklch(0.91 0.004 110)',
    '#d4d4d4': 'oklch(0.82 0.004 110)',
    '#d4d4d8': 'oklch(0.82 0.004 110)',
    '#a1a1aa': 'oklch(0.55 0.005 110)',
    '#71717a': 'oklch(0.55 0.005 110)',
    '#52525b': 'oklch(0.55 0.005 110)',
    '#3f3f46': 'oklch(0.72 0.006 110)',
    '#27272a': 'oklch(0.82 0.004 110)',
    '#fafafa': 'oklch(0.96 0.003 110)',
    '#f5f5f5': 'oklch(0.96 0.003 110)',
    '#f4f4f5': 'oklch(0.96 0.003 110)',
    # Pass 4 — stragglers
    '#ffd60a': 'oklch(0.56 0.05 70)',
    '#ff6b6b': 'oklch(0.48 0.07 22)',
    '#e8eef6': 'oklch(0.91 0.004 110)',
    '#e01b24': 'oklch(0.48 0.07 22)',
    '#b0bec5': 'oklch(0.55 0.005 110)',
    '#aaddff': 'oklch(0.82 0.004 110)',
    '#9f7aea': 'oklch(0.55 0.005 110)',
    '#7f93ad': 'oklch(0.55 0.005 110)',
    '#7dd3fc': 'oklch(0.52 0.04 160)',
    '#78909c': 'oklch(0.55 0.005 110)',
    '#4a5d78': 'oklch(0.55 0.005 110)',
    '#0a0f1e': 'oklch(0.96 0.003 110)',
    '#07111f': 'oklch(0.96 0.003 110)',
    '#00ff88': 'oklch(0.52 0.04 160)',
    '#00e676': 'oklch(0.52 0.04 160)',
    '#ffaa00': 'oklch(0.56 0.05 70)',
    '#ff375f': 'oklch(0.48 0.07 22)',
    '#feb2b2': 'oklch(0.48 0.07 22)',
    '#fde047': 'oklch(0.56 0.05 70)',
    '#f0883e': 'oklch(0.56 0.05 70)',
    '#edf1f8': 'oklch(0.96 0.003 110)',
    '#d9f6ff': 'oklch(0.91 0.004 110)',
    '#d8f7ff': 'oklch(0.91 0.004 110)',
    '#d7f7ff': 'oklch(0.91 0.004 110)',
    '#c4b5fd': 'oklch(0.55 0.005 110)',
    '#c0357a': 'oklch(0.48 0.07 22)',
    '#9ec7d9': 'oklch(0.82 0.004 110)',
    '#8b4513': 'oklch(0.56 0.05 70)',
    '#8a9bb4': 'oklch(0.55 0.005 110)',
    '#ff0000': 'oklch(0.48 0.07 22)',
    '#00ff00': 'oklch(0.52 0.04 160)',
    '#0000ff': 'oklch(0.52 0.04 160)',
    '#ff00ff': 'oklch(0.55 0.005 110)',
    '#00ffff': 'oklch(0.52 0.04 160)',
    '#ffff00': 'oklch(0.56 0.05 70)',
    '#5eead4': 'oklch(0.52 0.04 160)',
    '#2dd4bf': 'oklch(0.52 0.04 160)',
    '#14b8a6': 'oklch(0.52 0.04 160)',
    '#0d9488': 'oklch(0.52 0.04 160)',
    '#115e59': 'oklch(0.52 0.04 160)',
    '#a3e635': 'oklch(0.52 0.04 160)',
    '#84cc16': 'oklch(0.52 0.04 160)',
    '#65a30d': 'oklch(0.52 0.04 160)',
    '#4d7c0f': 'oklch(0.52 0.04 160)',
    '#e879f9': 'oklch(0.55 0.005 110)',
    '#d946ef': 'oklch(0.55 0.005 110)',
    '#a855f7': 'oklch(0.55 0.005 110)',
    '#9333ea': 'oklch(0.55 0.005 110)',
    '#7e22ce': 'oklch(0.55 0.005 110)',
    '#581c87': 'oklch(0.55 0.005 110)',
    '#6d28d9': 'oklch(0.55 0.005 110)',
    '#4c1d95': 'oklch(0.55 0.005 110)',
    '#312e81': 'oklch(0.55 0.005 110)',
    '#1e3a5f': 'oklch(0.91 0.004 110)',
    '#0b1c2f': 'oklch(0.96 0.003 110)',
    '#162447': 'oklch(0.91 0.004 110)',
    '#1b1b2f': 'oklch(0.93 0.003 110)',
    '#0c1426': 'oklch(0.96 0.003 110)',
    '#2196F3': 'oklch(0.52 0.04 160)',
    '#4CAF50': 'oklch(0.52 0.04 160)',
    '#FF9800': 'oklch(0.56 0.05 70)',
    '#F44336': 'oklch(0.48 0.07 22)',
    '#9C27B0': 'oklch(0.55 0.005 110)',
    '#FF5722': 'oklch(0.48 0.07 22)',
    '#607D8B': 'oklch(0.55 0.005 110)',
    '#795548': 'oklch(0.56 0.05 70)',
    '#FFEB3B': 'oklch(0.56 0.05 70)',
    '#00BCD4': 'oklch(0.52 0.04 160)',
    '#8BC34A': 'oklch(0.52 0.04 160)',
    '#CDDC39': 'oklch(0.56 0.05 70)',
    '#03A9F4': 'oklch(0.52 0.04 160)',
    '#009688': 'oklch(0.52 0.04 160)',
    '#FFC107': 'oklch(0.56 0.05 70)',
    '#673AB7': 'oklch(0.55 0.005 110)',
    '#3F51B5': 'oklch(0.52 0.04 160)',
    '#E91E63': 'oklch(0.48 0.07 22)',
    # Pass 5 — final stragglers
    '#87cefa': 'oklch(0.52 0.04 160)',
    '#7fd8ff': 'oklch(0.52 0.04 160)',
    '#7ddcff': 'oklch(0.52 0.04 160)',
    '#7a8fa6': 'oklch(0.55 0.005 110)',
    '#4caf50': 'oklch(0.52 0.04 160)',
    '#484f58': 'oklch(0.72 0.006 110)',
    '#2a3a52': 'oklch(0.91 0.004 110)',
    '#222': 'oklch(0.93 0.003 110)',
    '#1a5fb4': 'oklch(0.52 0.04 160)',
    '#1a2440': 'oklch(0.91 0.004 110)',
    '#182030': 'oklch(0.93 0.003 110)',
    '#080e1c': 'oklch(0.96 0.003 110)',
    '#06b6d4': 'oklch(0.52 0.04 160)',
    '#06101d': 'oklch(0.96 0.003 110)',
    '#ffd180': 'oklch(0.56 0.05 70)',
    '#ffcf70': 'oklch(0.56 0.05 70)',
    '#ffc857': 'oklch(0.56 0.05 70)',
    '#ffb347': 'oklch(0.56 0.05 70)',
    '#ff8800': 'oklch(0.56 0.05 70)',
    '#ff8a65': 'oklch(0.56 0.05 70)',
    '#ff7043': 'oklch(0.48 0.07 22)',
    '#ff5722': 'oklch(0.48 0.07 22)',
    '#dd2c00': 'oklch(0.48 0.07 22)',
    '#bf360c': 'oklch(0.48 0.07 22)',
    '#0b1428': 'oklch(0.96 0.003 110)',
    '#0e1929': 'oklch(0.96 0.003 110)',
    '#0e1a2b': 'oklch(0.96 0.003 110)',
    '#0f1b2e': 'oklch(0.96 0.003 110)',
    '#101b2e': 'oklch(0.96 0.003 110)',
    '#112240': 'oklch(0.91 0.004 110)',
    '#122240': 'oklch(0.91 0.004 110)',
    '#132a46': 'oklch(0.91 0.004 110)',
    '#142b48': 'oklch(0.91 0.004 110)',
    '#152d4a': 'oklch(0.91 0.004 110)',
    '#1c3354': 'oklch(0.91 0.004 110)',
    '#1d3557': 'oklch(0.91 0.004 110)',
    '#233e5c': 'oklch(0.91 0.004 110)',
    '#264653': 'oklch(0.91 0.004 110)',
    '#2a4a6b': 'oklch(0.82 0.004 110)',
    '#355070': 'oklch(0.82 0.004 110)',
    '#546e7a': 'oklch(0.55 0.005 110)',
    '#455a64': 'oklch(0.55 0.005 110)',
    '#37474f': 'oklch(0.55 0.005 110)',
    '#263238': 'oklch(0.82 0.004 110)',
    '#cab': 'oklch(0.72 0.006 110)',
    # Final pass — all remaining 86 unique values
    # safety-emergency
    '#b71c1c': 'oklch(0.48 0.07 22)',
    # crew-management
    '#fb923c': 'oklch(0.56 0.05 70)',
    # navigation-v2 (12)
    '#00cc66': 'oklch(0.52 0.04 160)',
    '#0e1420': 'oklch(0.96 0.003 110)',
    '#0e1a28': 'oklch(0.96 0.003 110)',
    '#121820': 'oklch(0.96 0.003 110)',
    '#141c28': 'oklch(0.93 0.003 110)',
    '#1a2230': 'oklch(0.93 0.003 110)',
    '#1a2a3e': 'oklch(0.91 0.004 110)',
    '#1e2a3a': 'oklch(0.91 0.004 110)',
    '#2a3a4e': 'oklch(0.82 0.004 110)',
    '#c8d4e0': 'oklch(0.82 0.004 110)',
    '#ecd': 'oklch(0.91 0.004 110)',
    '#ff3344': 'oklch(0.48 0.07 22)',
    # cms-health
    '#0078d4': 'oklch(0.52 0.04 160)',
    # datacenter-ratchet-evolution (4)
    '#050810': 'oklch(0.96 0.003 110)',
    '#081209': 'oklch(0.96 0.003 110)',
    '#0a1428': 'oklch(0.93 0.003 110)',
    '#0f2017': 'oklch(0.96 0.003 110)',
    # system-evolution (3)
    '#080e1a': 'oklch(0.96 0.003 110)',
    '#3a8cbf': 'oklch(0.52 0.04 160)',
    '#63e6be': 'oklch(0.52 0.04 160)',
    # thruster-control2 (11)
    '#003399': 'oklch(0.52 0.04 160)',
    '#006644': 'oklch(0.52 0.04 160)',
    '#0d1424': 'oklch(0.96 0.003 110)',
    '#1a2035': 'oklch(0.93 0.003 110)',
    '#2d3a52': 'oklch(0.82 0.004 110)',
    '#3d0000': 'oklch(0.48 0.07 22)',
    '#8b0000': 'oklch(0.48 0.07 22)',
    '#8b5e00': 'oklch(0.56 0.05 70)',
    '#ff2d2d': 'oklch(0.48 0.07 22)',
    '#ffb100': 'oklch(0.56 0.05 70)',
    '#effca': 'oklch(0.96 0.003 110)',
    # navigation-v3 (1)
    '#0b1120': 'oklch(0.96 0.003 110)',
    # agent-team-config (13)
    '#039': 'oklch(0.52 0.04 160)',
    '#1c2333': 'oklch(0.93 0.003 110)',
    '#1c71d8': 'oklch(0.52 0.04 160)',
    '#26a269': 'oklch(0.52 0.04 160)',
    '#6a7d96': 'oklch(0.55 0.005 110)',
    '#c88800': 'oklch(0.56 0.05 70)',
    '#d0d7de': 'oklch(0.82 0.004 110)',
    '#d63384': 'oklch(0.48 0.07 22)',
    '#e040a0': 'oklch(0.48 0.07 22)',
    '#eef3f9': 'oklch(0.96 0.003 110)',
    '#eef4fb': 'oklch(0.96 0.003 110)',
    '#faf0fa': 'oklch(0.96 0.003 110)',
    '#ff4d8d': 'oklch(0.48 0.07 22)',
    # worldmonitor-ar-cas-pro (11)
    '#06121f': 'oklch(0.96 0.003 110)',
    '#07131e': 'oklch(0.96 0.003 110)',
    '#08101b': 'oklch(0.96 0.003 110)',
    '#0a1f34': 'oklch(0.93 0.003 110)',
    '#0a2438': 'oklch(0.91 0.004 110)',
    '#90cdf4': 'oklch(0.52 0.04 160)',
    '#9ae6b4': 'oklch(0.52 0.04 160)',
    '#9cb8c7': 'oklch(0.82 0.004 110)',
    '#a6c3d3': 'oklch(0.82 0.004 110)',
    '#e9fbff': 'oklch(0.96 0.003 110)',
    '#fbd38d': 'oklch(0.56 0.05 70)',
    # captain-cockpit (9)
    '#091727': 'oklch(0.96 0.003 110)',
    '#35c8ff': 'oklch(0.52 0.04 160)',
    '#6ef5a1': 'oklch(0.52 0.04 160)',
    '#94a9bc': 'oklch(0.55 0.005 110)',
    '#98f5a7': 'oklch(0.52 0.04 160)',
    '#9af6bd': 'oklch(0.52 0.04 160)',
    '#eef7ff': 'oklch(0.96 0.003 110)',
    '#ff7272': 'oklch(0.48 0.07 22)',
    '#ff7d7d': 'oklch(0.48 0.07 22)',
    # digital-twin (20)
    '#050a12': 'oklch(0.96 0.003 110)',
    '#091321': 'oklch(0.96 0.003 110)',
    '#15314a': 'oklch(0.91 0.004 110)',
    '#16213e': 'oklch(0.91 0.004 110)',
    '#1a1aff': 'oklch(0.52 0.04 160)',
    '#1a4a8c': 'oklch(0.52 0.04 160)',
    '#73e6ff': 'oklch(0.52 0.04 160)',
    '#8b6914': 'oklch(0.56 0.05 70)',
    '#8ca2bd': 'oklch(0.55 0.005 110)',
    '#9ed9ff': 'oklch(0.52 0.04 160)',
    '#c7d6e5': 'oklch(0.82 0.004 110)',
    '#cc0000': 'oklch(0.48 0.07 22)',
    '#cfe9f6': 'oklch(0.91 0.004 110)',
    '#d9e6f2': 'oklch(0.91 0.004 110)',
    '#d9eef7': 'oklch(0.91 0.004 110)',
    '#edf6ff': 'oklch(0.96 0.003 110)',
    '#fda4af': 'oklch(0.48 0.07 22)',
    '#fdba74': 'oklch(0.56 0.05 70)',
    '#fecaca': 'oklch(0.48 0.07 22)',
    '#fef3c7': 'oklch(0.56 0.05 70)',
}

# Three.js 0x hex colors → wabi-sabi equivalents
THREEJS_MAP = {
    '0x020408': '0xf5f2ed',   # near-black → shironeri
    '0x0b1525': '0xddd9d2',   # dark navy → fog stone
    '0x060d1a': '0xf5f2ed',   # dark → shironeri
    '0x04070d': '0xf5f2ed',
    '0x0a1220': '0xe8e4de',
    '0x38bdf8': '0x7a9b7a',   # neon blue → koke
    '0x22c4ff': '0x7a9b7a',
    '0x06ffa5': '0x7a9b7a',   # neon green → koke
    '0xf87171': '0x9b5a4a',   # red → shu
    '0xef4444': '0x9b5a4a',
    '0xfbbf24': '0xa89060',   # yellow → kitsune
    '0xa78bfa': '0x8a8378',   # purple → muted
    '0x111111': '0xf5f2ed',
    '0x1a1a1a': '0xe8e4de',
    '0x222222': '0xe8e4de',
    '0x333333': '0xddd9d2',
    '0x444444': '0xc8c3ba',
    '0xffffff': '0xfaf8f4',
    '0x000000': '0x4a4640',
}

# rgba patterns to replace
RGBA_MAP = [
    # Dark transparent backgrounds → light transparent
    (r'rgba\(0,\s*0,\s*0,\s*(0\.[3-9]\d*|1)\)', r'oklch(0 0 0 / \1)'),
    (r'rgba\(0,\s*0,\s*0,\s*0\.([012]\d*)\)', r'oklch(0 0 0 / 0.\1)'),
    (r'rgba\(10,\s*18,\s*32,\s*[\d.]+\)', 'oklch(0.93 0.003 110 / 0.9)'),
    (r'rgba\(4,\s*7,\s*13,\s*[\d.]+\)', 'oklch(0.93 0.003 110 / 0.95)'),
    (r'rgba\(4,\s*9,\s*18,\s*[\d.]+\)', 'oklch(0.93 0.003 110 / 0.92)'),
    (r'rgba\(6,\s*10,\s*18,\s*[\d.]+\)', 'oklch(0.93 0.003 110 / 0.95)'),
    (r'rgba\(15,\s*32,\s*55,\s*[\d.]+\)', 'oklch(0.94 0.003 110 / 0.4)'),
    # Neon blue transparent → koke transparent
    (r'rgba\(56,\s*189,\s*248,\s*([\d.]+)\)', r'oklch(0.52 0.04 160 / \1)'),
    (r'rgba\(34,\s*196,\s*255,\s*([\d.]+)\)', r'oklch(0.52 0.04 160 / \1)'),
    (r'rgba\(100,\s*210,\s*255,\s*([\d.]+)\)', r'oklch(0.52 0.04 160 / \1)'),
    (r'rgba\(100,\s*180,\s*255,\s*([\d.]+)\)', r'oklch(0.82 0.004 110 / \1)'),
    (r'rgba\(125,\s*211,\s*252,\s*([\d.]+)\)', r'oklch(0.82 0.004 110 / \1)'),
    # Neon green transparent → koke transparent
    (r'rgba\(6,\s*255,\s*165,\s*([\d.]+)\)', r'oklch(0.52 0.04 160 / \1)'),
    (r'rgba\(48,\s*209,\s*88,\s*([\d.]+)\)', r'oklch(0.52 0.04 160 / \1)'),
    # Red transparent → shu transparent
    (r'rgba\(248,\s*113,\s*113,\s*([\d.]+)\)', r'oklch(0.48 0.07 22 / \1)'),
    (r'rgba\(239,\s*68,\s*68,\s*([\d.]+)\)', r'oklch(0.48 0.07 22 / \1)'),
    (r'rgba\(220,\s*38,\s*38,\s*([\d.]+)\)', r'oklch(0.48 0.07 22 / \1)'),
    (r'rgba\(203,\s*19,\s*29,\s*([\d.]+)\)', r'oklch(0.48 0.07 22 / \1)'),
    # Yellow transparent → kitsune transparent
    (r'rgba\(251,\s*191,\s*36,\s*([\d.]+)\)', r'oklch(0.56 0.05 70 / \1)'),
    (r'rgba\(254,\s*155,\s*41,\s*([\d.]+)\)', r'oklch(0.56 0.05 70 / \1)'),
    (r'rgba\(233,\s*195,\s*0,\s*([\d.]+)\)', r'oklch(0.56 0.05 70 / \1)'),
    (r'rgba\(255,\s*219,\s*55,\s*([\d.]+)\)', r'oklch(0.56 0.05 70 / \1)'),
    # Purple transparent → muted transparent
    (r'rgba\(167,\s*139,\s*250,\s*([\d.]+)\)', r'oklch(0.55 0.005 110 / \1)'),
    (r'rgba\(191,\s*90,\s*242,\s*([\d.]+)\)', r'oklch(0.55 0.005 110 / \1)'),
    # Light transparent → adapt
    (r'rgba\(255,\s*255,\s*255,\s*([\d.]+)\)', r'oklch(1 0 0 / \1)'),
    # White text fallback
    (r'rgba\(255,\s*171,\s*0,\s*([\d.]+)\)', r'oklch(0.56 0.05 70 / \1)'),
    (r'rgba\(38,\s*61,\s*255,\s*([\d.]+)\)', r'oklch(0.52 0.04 160 / \1)'),
]

# CSS gradient patterns
GRADIENT_MAP = [
    # Neon gradients → stone/earth gradients
    (r'linear-gradient\(135deg,\s*var\(--cyan\),\s*var\(--green\),\s*var\(--purple\)\)',
     'oklch(0.18 0.008 110)'),
    (r'linear-gradient\(135deg,\s*var\(--blue\),\s*#5e5ce6\)',
     'oklch(0.18 0.008 110)'),
    (r'linear-gradient\(180deg,\s*rgba\(10,18,32,[\d.]+\),\s*rgba\(4,7,13,[\d.]+\)\)',
     'oklch(0.93 0.003 110)'),
    (r'radial-gradient\(ellipse at [\d]+% [\d]+%,\s*rgba\(\d+,\d+,\d+,[\d.]+\),\s*transparent [\d]+%\)',
     'transparent'),
]

def should_skip(filename):
    if filename in SKIP:
        return True
    for prefix in SKIP_PREFIX:
        if filename.startswith(prefix):
            return True
    for suffix in SKIP_SUFFIX:
        if filename.endswith(suffix):
            return True
    return False

def replace_colors(text):
    """Apply all color replacements."""
    original = text

    # Apply gradient replacements first (before hex, to avoid partial matches)
    for pattern, replacement in GRADIENT_MAP:
        text = re.sub(pattern, replacement, text)

    # Apply hex replacements (longest first to avoid partial matches)
    sorted_hex = sorted(HEX_MAP.keys(), key=len, reverse=True)
    for old, new in [(k, HEX_MAP[k]) for k in sorted_hex]:
        text = text.replace(old, new)

    # Apply case-insensitive hex replacements for common patterns
    def hex_ci_replace(match):
        val = match.group(0).lower()
        return HEX_MAP.get(val, match.group(0))
    text = re.sub(r'#[0-9a-fA-F]{6}(?![0-9a-fA-F])', hex_ci_replace, text)

    # Apply Three.js 0x hex replacements
    sorted_3js = sorted(THREEJS_MAP.keys(), key=len, reverse=True)
    for old, new in [(k, THREEJS_MAP[k]) for k in sorted_3js]:
        text = text.replace(old, new)

    # Apply rgba replacements
    for pattern, replacement in RGBA_MAP:
        text = re.sub(pattern, replacement, text)

    # Replace background:linear-gradient dark patterns
    text = re.sub(
        r'background:\s*radial-gradient\([^)]+\),\s*\n?\s*radial-gradient\([^)]+\),\s*\n?\s*linear-gradient\(180deg,[^)]+\)',
        'background: oklch(0.96 0.003 110)',
        text
    )

    # Context-aware: text color should be dark on light backgrounds
    # Fix "color: oklch(0.96 ...)" → sumi (dark text) — was white text on dark bg
    text = re.sub(
        r'(?<!\bbackground-)color\s*:\s*oklch\(0\.96\s+0\.003\s+110\)',
        'color: oklch(0.18 0.008 110)',
        text
    )
    # Fix "color: oklch(0.93 ...)" → sumi
    text = re.sub(
        r'(?<!\bbackground-)color\s*:\s*oklch\(0\.93\s+0\.003\s+110\)',
        'color: oklch(0.18 0.008 110)',
        text
    )
    # Fix "color: oklch(0.91 ...)" → slightly lighter sumi
    text = re.sub(
        r'(?<!\bbackground-)color\s*:\s*oklch\(0\.91\s+0\.004\s+110\)',
        'color: oklch(0.25 0.006 110)',
        text
    )
    # Fix JS: .color = 'oklch(0.96...)' where context is text
    text = re.sub(
        r"\.color\s*=\s*['\"]oklch\(0\.96\s+0\.003\s+110\)['\"]",
        ".color = 'oklch(0.18 0.008 110)'",
        text
    )
    text = re.sub(
        r"\.color\s*=\s*['\"]oklch\(0\.93\s+0\.003\s+110\)['\"]",
        ".color = 'oklch(0.18 0.008 110)'",
        text
    )
    # Fix "fill: oklch(0.96...)" → dark (SVG text)
    text = re.sub(
        r'fill\s*:\s*oklch\(0\.96\s+0\.003\s+110\)',
        'fill: oklch(0.18 0.008 110)',
        text
    )
    # Fix "stroke: oklch(0.96...)" → dark (SVG lines)
    text = re.sub(
        r'stroke\s*:\s*oklch\(0\.96\s+0\.003\s+110\)',
        'stroke: oklch(0.55 0.005 110)',
        text
    )

    # Flatten border-radius for panels/cards (wabi-sabi: sharp corners)
    # Keep radius for toggle-switch, pill, badge elements (functional rounding)
    def flatten_radius(match):
        full = match.group(0)
        val = int(match.group(1))
        if val >= 8:
            return 'border-radius:0'
        return full
    text = re.sub(r'border-radius:\s*(\d+)px', flatten_radius, text)

    return text

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    new_text = replace_colors(text)

    if new_text != text:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_text)
        changes = sum(1 for a, b in zip(text.split('\n'), new_text.split('\n')) if a != b)
        print(f"  ✓ {os.path.basename(filepath)}: {changes} lines changed")
        return True
    else:
        print(f"  · {os.path.basename(filepath)}: no changes")
        return False

def main():
    changed = 0
    total = 0
    for filename in sorted(os.listdir(FRONTEND)):
        if not filename.endswith('.html'):
            continue
        if should_skip(filename):
            continue
        filepath = os.path.join(FRONTEND, filename)
        total += 1
        if process_file(filepath):
            changed += 1
    print(f"\nDone: {changed}/{total} files modified")

if __name__ == '__main__':
    main()
