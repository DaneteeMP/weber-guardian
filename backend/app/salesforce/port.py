"""Sync port to Salesforce (F3 seam, no implementation).

Declares the boundary F4+ will implement against the real org
(push Guardian offers, pull customer master data). Importing this
module must never touch the network.
"""
from abc import ABC, abstractmethod


class SyncPort(ABC):
    """Outbound Salesforce synchronization contract."""

    @abstractmethod
    def push_offer(self, offer_id: str) -> None:
        """Publish a Guardian offer to Salesforce. Not implemented in F3."""
        raise NotImplementedError

    @abstractmethod
    def pull_customers(self, subsidiary_id: str) -> None:
        """Fetch customer master data from Salesforce. Not implemented in F3."""
        raise NotImplementedError
