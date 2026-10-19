"""
Google Cloud Pub/Sub Adapter for AeroCredits.
Emits and queues asynchronous supply chain financing events for multi-agent workflows.
"""

from typing import Dict, Any, List, Callable
from datetime import datetime
import json
from backend.config import PUBSUB_TOPIC_INVOICE_EVENTS, GCP_PROJECT_ID


class CloudPubSubAdapter:
    """Manages asynchronous messaging and agent triggers via Cloud Pub/Sub."""

    def __init__(self, topic: str = PUBSUB_TOPIC_INVOICE_EVENTS):
        self.topic = topic
        self.project_id = GCP_PROJECT_ID
        self._subscribers: List[Callable[[Dict[str, Any]], None]] = []
        self._event_history: List[Dict[str, Any]] = []

    def publish_event(self, event_type: str, payload: Dict[str, Any], attributes: Dict[str, str] = None) -> str:
        """Publishes an event to the cloud message bus."""
        event_id = f"msg_{int(datetime.utcnow().timestamp() * 1000)}"
        message = {
            "message_id": event_id,
            "topic": self.topic,
            "event_type": event_type,
            "publish_time": datetime.utcnow().isoformat() + "Z",
            "attributes": attributes or {},
            "data": payload
        }
        self._event_history.append(message)

        # Notify active subscriber listeners
        for sub in self._subscribers:
            try:
                sub(message)
            except Exception as e:
                print(f"[PubSub Warning] Subscriber error: {e}")

        return event_id

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """Subscribes an agent listener to incoming cloud messages."""
        self._subscribers.append(callback)

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent published cloud events."""
        return self._event_history[-limit:]


# Global instance
cloud_pubsub = CloudPubSubAdapter()
