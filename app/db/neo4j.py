from neo4j import GraphDatabase
from typing import Optional
import os
from datetime import datetime
import json

class Neo4jConnection:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_node(self, label: str, properties: dict, valid_from: datetime,
                   valid_to: Optional[datetime], context: dict) -> str:
        with self.driver.session() as session:
            # Convert datetime to ISO format string
            valid_from_str = valid_from.isoformat()
            valid_to_str = valid_to.isoformat() if valid_to else None
            
            # Create node with temporal and contextual properties
            query = """
            CREATE (n:`{label}` {
                properties: $properties,
                valid_from: datetime($valid_from),
                valid_to: datetime($valid_to),
                context: $context
            })
            RETURN id(n) as node_id
            """.format(label=label)
            
            result = session.run(
                query,
                properties=json.dumps(properties),
                valid_from=valid_from_str,
                valid_to=valid_to_str,
                context=json.dumps(context)
            )
            return result.single()["node_id"]

    def create_relationship(self, source_id: str, target_id: str, rel_type: str,
                          properties: dict, valid_from: datetime,
                          valid_to: Optional[datetime], context: dict):
        with self.driver.session() as session:
            valid_from_str = valid_from.isoformat()
            valid_to_str = valid_to.isoformat() if valid_to else None
            
            query = """
            MATCH (source), (target)
            WHERE id(source) = $source_id AND id(target) = $target_id
            CREATE (source)-[r:`{rel_type}` {
                properties: $properties,
                valid_from: datetime($valid_from),
                valid_to: datetime($valid_to),
                context: $context
            }]->(target)
            RETURN type(r)
            """.format(rel_type=rel_type)
            
            session.run(
                query,
                source_id=source_id,
                target_id=target_id,
                properties=json.dumps(properties),
                valid_from=valid_from_str,
                valid_to=valid_to_str,
                context=json.dumps(context)
            )

    def get_node(self, node_id: str, timestamp: Optional[datetime] = None):
        with self.driver.session() as session:
            query = """
            MATCH (n)
            WHERE id(n) = $node_id
            AND (n.valid_from <= datetime($timestamp))
            AND (n.valid_to IS NULL OR n.valid_to > datetime($timestamp))
            RETURN n
            """
            
            result = session.run(
                query,
                node_id=node_id,
                timestamp=timestamp.isoformat() if timestamp else datetime.now().isoformat()
            )
            record = result.single()
            return record["n"] if record else None

    def get_nodes_by_context(self, context_key: str, context_value: str,
                           timestamp: Optional[datetime] = None):
        with self.driver.session() as session:
            query = """
            MATCH (n)
            WHERE n.context CONTAINS $context_filter
            AND (n.valid_from <= datetime($timestamp))
            AND (n.valid_to IS NULL OR n.valid_to > datetime($timestamp))
            RETURN n
            """
            
            result = session.run(
                query,
                context_filter=f'"{context_key}": "{context_value}"',
                timestamp=timestamp.isoformat() if timestamp else datetime.now().isoformat()
            )
            return [record["n"] for record in result] 