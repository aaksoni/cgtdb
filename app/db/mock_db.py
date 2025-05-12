from typing import Optional, Dict, List, Any
from datetime import datetime
import json
import uuid

class MockNode:
    def __init__(self, id: str, labels: List[str], properties: Dict, valid_from: datetime,
                 valid_to: Optional[datetime], context: Dict):
        self.id = id
        self.labels = labels
        self.properties = properties
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.context = context

class MockNeo4j:
    def __init__(self):
        self.nodes: Dict[str, MockNode] = {}
        self.relationships: List[Dict] = []

    def create_node(self, label: str, properties: dict, valid_from: datetime,
                   valid_to: Optional[datetime], context: dict) -> str:
        node_id = str(uuid.uuid4())
        node = MockNode(
            id=node_id,
            labels=[label],
            properties=properties,
            valid_from=valid_from,
            valid_to=valid_to,
            context=context
        )
        self.nodes[node_id] = node
        return node_id

    def create_relationship(self, source_id: str, target_id: str, rel_type: str,
                          properties: dict, valid_from: datetime,
                          valid_to: Optional[datetime], context: dict):
        rel = {
            "source_id": source_id,
            "target_id": target_id,
            "type": rel_type,
            "properties": properties,
            "valid_from": valid_from,
            "valid_to": valid_to,
            "context": context
        }
        self.relationships.append(rel)

    def get_node(self, node_id: str, timestamp: Optional[datetime] = None) -> Optional[MockNode]:
        node = self.nodes.get(node_id)
        if not node:
            return None
        
        if timestamp:
            if node.valid_from > timestamp or (node.valid_to and node.valid_to <= timestamp):
                return None
        
        return node

class MockVectorStore:
    def __init__(self):
        self.contexts: Dict[str, Dict] = {}

    def init_collection(self):
        pass

    def store_context(self, context_id: str, context_text: str, metadata: Dict[str, Any]):
        self.contexts[context_id] = {
            "text": context_text,
            "metadata": metadata
        }

    def find_similar_contexts(self, query_text: str, limit: int = 5):
        # Simple mock implementation that returns all contexts
        results = []
        for context_id, data in self.contexts.items():
            results.append({
                "id": context_id,
                "text": data["text"],
                "metadata": data["metadata"],
                "score": 0.9  # Mock similarity score
            })
            if len(results) >= limit:
                break
        return results

    def delete_context(self, context_id: str):
        if context_id in self.contexts:
            del self.contexts[context_id] 