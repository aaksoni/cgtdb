from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.db.mock_db import MockNeo4j, MockVectorStore
import json

app = FastAPI(title="Contextual Graph-Temporal DB")

# Initialize mock database connections
neo4j_db = MockNeo4j()
vector_store = MockVectorStore()
vector_store.init_collection()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base Pydantic models
class NodeBase(BaseModel):
    label: str  # Remove id as it will be generated
    properties: dict
    valid_from: datetime
    valid_to: Optional[datetime]
    context: dict

class EdgeBase(BaseModel):
    source_id: str
    target_id: str
    type: str
    properties: dict
    valid_from: datetime
    valid_to: Optional[datetime]
    context: dict

class ContextSearch(BaseModel):
    query_text: str
    limit: Optional[int] = 5

class NodeResponse(BaseModel):
    id: str
    label: str
    properties: dict
    valid_from: datetime
    valid_to: Optional[datetime]
    context: dict

# REST Endpoints
@app.post("/nodes/", response_model=str)
async def create_node(node: NodeBase):
    try:
        node_id = neo4j_db.create_node(
            label=node.label,
            properties=node.properties,
            valid_from=node.valid_from,
            valid_to=node.valid_to,
            context=node.context
        )
        # Store context in vector store
        context_text = str(node.context)
        vector_store.store_context(
            context_id=str(node_id),
            context_text=context_text,
            metadata={"node_id": node_id, "label": node.label}
        )
        return node_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nodes/all", response_model=List[NodeResponse])
async def get_all_nodes():
    """Get all nodes in the database"""
    try:
        nodes = []
        for node_id, node in neo4j_db.nodes.items():
            nodes.append(NodeResponse(
                id=node.id,
                label=node.labels[0],
                properties=node.properties,
                valid_from=node.valid_from,
                valid_to=node.valid_to,
                context=node.context
            ))
        return nodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/relationships/all")
async def get_all_relationships():
    """Get all relationships in the database"""
    try:
        return neo4j_db.relationships
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/relationships/")
async def create_relationship(edge: EdgeBase):
    try:
        neo4j_db.create_relationship(
            source_id=edge.source_id,
            target_id=edge.target_id,
            rel_type=edge.type,
            properties=edge.properties,
            valid_from=edge.valid_from,
            valid_to=edge.valid_to,
            context=edge.context
        )
        return {"message": "Relationship created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nodes/{node_id}", response_model=NodeResponse)
async def get_node(node_id: str, timestamp: Optional[datetime] = None):
    try:
        node = neo4j_db.get_node(node_id, timestamp)
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        return NodeResponse(
            id=node.id,
            label=node.labels[0],
            properties=node.properties,
            valid_from=node.valid_from,
            valid_to=node.valid_to,
            context=node.context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/contexts/search/")
async def search_contexts(search: ContextSearch):
    try:
        results = vector_store.find_similar_contexts(
            query_text=search.query_text,
            limit=search.limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GraphQL types
@strawberry.type
class Node:
    id: str
    label: str
    properties: str  # JSON serialized
    valid_from: str
    valid_to: Optional[str]
    context: str  # JSON serialized

@strawberry.type
class Edge:
    source_id: str
    target_id: str
    type: str
    properties: str
    valid_from: str
    valid_to: Optional[str]
    context: str

# GraphQL Query type
@strawberry.type
class Query:
    @strawberry.field
    def get_node(self, id: str) -> Optional[Node]:
        node = neo4j_db.get_node(id)
        if not node:
            return None
        return Node(
            id=str(node.id),
            label=node.labels[0],
            properties=json.dumps(node.properties),
            valid_from=node.valid_from.isoformat(),
            valid_to=node.valid_to.isoformat() if node.valid_to else None,
            context=json.dumps(node.context)
        )

    @strawberry.field
    def get_nodes(self, label: Optional[str] = None) -> List[Node]:
        nodes = []
        for node in neo4j_db.nodes.values():
            if not label or label in node.labels:
                nodes.append(Node(
                    id=str(node.id),
                    label=node.labels[0],
                    properties=json.dumps(node.properties),
                    valid_from=node.valid_from.isoformat(),
                    valid_to=node.valid_to.isoformat() if node.valid_to else None,
                    context=json.dumps(node.context)
                ))
        return nodes

# GraphQL schema
schema = strawberry.Schema(query=Query)

# Add GraphQL endpoint
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def read_root():
    return {"message": "Welcome to Contextual Graph-Temporal DB"} 