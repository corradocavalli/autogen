from dataclasses import dataclass


@dataclass
class UserMessage:
    content: str


@dataclass
class AdvisorMessage:
    content: str


@dataclass
class SessionStartMessage:
    pass


@dataclass
class TriageMessage:
    content: str


@dataclass
class OrderMessage:
    content: str


@dataclass
class OrderUpdateMessage:
    order_id: int


# This message is used to inform the runtime that the user has finished the conversation
@dataclass
class UserTerminationMessage:
    reason: str = "User terminated the conversation"
