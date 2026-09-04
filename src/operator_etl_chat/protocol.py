"""Chat adapter protocols — Control-plane clients, not warehouse chatbots."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ChatNotifier(Protocol):
    """Outbound HITL / ops alerts to a chat channel."""

    def notify_hitl(self, payload: dict[str, Any]) -> bool:
        """Send a sanitized HITL escalation alert.

        Returns True if a message was delivered, False if skipped (no config)
        or if send failed after logging (fail-soft).
        """
        ...


@runtime_checkable
class ChatCommandHandler(Protocol):
    """Inbound slash / mention commands mapped to MCP or bounded run."""

    def handle_command(self, name: str, options: dict[str, Any]) -> dict[str, Any]:
        """Execute an allowlisted command; return a sanitized response dict."""
        ...
