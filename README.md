# Contextual Graph-Temporal Database System

A powerful database system that combines graph database capabilities with temporal versioning and contextual awareness.

## Features

- **Graph Database Foundation**
  - Nodes (entities) and edges (relationships)
  - Property storage on both nodes and edges
  - Advanced query capabilities

- **Temporal Dimension**
  - Time-versioning of nodes and relationships
  - Point-in-time querying
  - Temporal range queries

- **Contextual Layer**
  - Semantic context understanding
  - Context-aware querying
  - Context hierarchies

## Technology Stack

- **Graph Store**: Neo4j
- **Vector Store**: Qdrant
- **Embedding Model**: MiniLM-L6-v2
- **Backend API**: FastAPI + GraphQL
- **Temporal Handling**: Custom implementation
- **Infrastructure**: Docker + Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+

### Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd cgtdb
   ```

2. Create a `.env` file:
   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=password
   QDRANT_HOST=localhost
   QDRANT_PORT=6333
   JWT_SECRET=your-secret-key-here
   JWT_ALGORITHM=HS256
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

### API Documentation

Once the application is running, visit:
- REST API docs: `http://localhost:8000/docs`
- GraphQL Playground: `http://localhost:8000/graphql`

## Query Examples

### GraphQL Query
```graphql
query {
  getNode(id: "123") {
    id
    label
    properties
    validFrom
    validTo
    context
  }
}
```

### Temporal Query
```cypher
MATCH (n)
WHERE n.valid_from <= datetime('2024-03-14')
AND (n.valid_to IS NULL OR n.valid_to > datetime('2024-03-14'))
RETURN n
```

### Context-Aware Query
```python
vector_store.find_similar_contexts("business travel expenses", limit=5)
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Aakash Soni 