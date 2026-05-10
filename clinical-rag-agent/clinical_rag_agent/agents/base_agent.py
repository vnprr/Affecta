from dataclasses import dataclass


@dataclass
class BaseAgent:
    name: str
    goal: str

