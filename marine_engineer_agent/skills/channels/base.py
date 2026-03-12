# -*- coding: utf-8 -*-
"""
Channel base class — platform availability checking.

Each channel represents a platform (YouTube, Twitter, GitHub, etc.)
and provides:
  - can_handle(url) → does this URL belong to this platform?
  - check(config) → is the upstream tool installed and configured?

After installation, agents call upstream tools directly.

Example:
    >>> class MyChannel(Channel):
    ...     name = "myplatform"
    ...     description = "My Platform"
    ...     def can_handle(self, url: str) -> bool:
    ...         return "myplatform.com" in url
"""

from abc import ABC, abstractmethod


class Channel(ABC):
    """Base class for all channels.

    Each channel represents a platform and provides URL handling
    and availability checking functionality.

    Class Attributes:
        name: Internal identifier for the channel (e.g., "youtube").
        description: Human-readable description (e.g., "YouTube 视频和字幕").
        backends: List of upstream tools used by this channel.
        tier: Configuration tier (0=zero-config, 1=needs free key, 2=needs setup).
    """

    name: str = ""
    description: str = ""
    backends: list[str] = []
    tier: int = 0

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Check if this channel can handle the given URL.

        Args:
            url: URL to check.

        Returns:
            True if this channel can process the URL.
        """
        ...

    def check(self, config: object | None = None) -> tuple[str, str]:
        """Check if this channel's upstream tool is available.

        Args:
            config: Optional configuration object (not used by default).

        Returns:
            Tuple of (status, message) where status is one of:
            - 'ok': Channel is fully functional
            - 'warn': Channel works but has limitations
            - 'off': Channel is not available
            - 'error': Channel encountered an error
        """
        backends_str = "、".join(self.backends) if self.backends else "内置"
        return "ok", backends_str
