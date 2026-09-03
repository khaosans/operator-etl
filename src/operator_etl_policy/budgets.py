from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RunBudget:
    max_llm_calls: int = 2
    max_tool_calls: int = 30
    llm_calls: int = 0
    tool_calls: int = 0

    def record_llm(self) -> None:
        self.llm_calls += 1
        if self.llm_calls > self.max_llm_calls:
            raise BudgetExceeded(f"LLM budget exceeded ({self.max_llm_calls})")

    def record_tool(self) -> None:
        self.tool_calls += 1
        if self.tool_calls > self.max_tool_calls:
            raise BudgetExceeded(f"Tool budget exceeded ({self.max_tool_calls})")


class BudgetExceeded(Exception):
    pass
