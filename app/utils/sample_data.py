from datetime import datetime, timedelta
import httpx
import json

# Sample data representing a tech company's project structure
SAMPLE_DATA = {
    "departments": [
        {
            "label": "Department",
            "properties": {
                "name": "Engineering",
                "budget": 1000000,
                "location": "San Francisco"
            },
            "context": {
                "domain": "technical",
                "level": "department"
            }
        },
        {
            "label": "Department",
            "properties": {
                "name": "Data Science",
                "budget": 800000,
                "location": "Boston"
            },
            "context": {
                "domain": "analytics",
                "level": "department"
            }
        },
        {
            "label": "Department",
            "properties": {
                "name": "Product",
                "budget": 600000,
                "location": "New York"
            },
            "context": {
                "domain": "business",
                "level": "department"
            }
        },
        {
            "label": "Department",
            "properties": {
                "name": "DevOps",
                "budget": 750000,
                "location": "Seattle"
            },
            "context": {
                "domain": "infrastructure",
                "level": "department"
            }
        }
    ],
    "projects": [
        {
            "label": "Project",
            "properties": {
                "name": "Graph Database Enhancement",
                "status": "active",
                "priority": "high",
                "deadline": "2024-06-30"
            },
            "context": {
                "domain": "database",
                "priority": "high",
                "tech_stack": ["Neo4j", "Python", "FastAPI"]
            }
        },
        {
            "label": "Project",
            "properties": {
                "name": "ML Pipeline Optimization",
                "status": "planning",
                "priority": "medium",
                "deadline": "2024-08-15"
            },
            "context": {
                "domain": "machine_learning",
                "priority": "medium",
                "tech_stack": ["Python", "TensorFlow", "Kubernetes"]
            }
        },
        {
            "label": "Project",
            "properties": {
                "name": "Cloud Migration",
                "status": "active",
                "priority": "critical",
                "deadline": "2024-05-01"
            },
            "context": {
                "domain": "infrastructure",
                "priority": "high",
                "tech_stack": ["AWS", "Terraform", "Docker"]
            }
        },
        {
            "label": "Project",
            "properties": {
                "name": "User Analytics Dashboard",
                "status": "development",
                "priority": "medium",
                "deadline": "2024-07-15"
            },
            "context": {
                "domain": "analytics",
                "priority": "medium",
                "tech_stack": ["Python", "React", "D3.js"]
            }
        }
    ],
    "employees": [
        {
            "label": "Employee",
            "properties": {
                "name": "Alice Johnson",
                "role": "Senior Engineer",
                "skills": ["Python", "Neo4j", "System Design"],
                "years_experience": 8
            },
            "context": {
                "expertise": "backend",
                "level": "senior",
                "mentor": True
            }
        },
        {
            "label": "Employee",
            "properties": {
                "name": "Bob Smith",
                "role": "Data Scientist",
                "skills": ["Python", "ML", "Statistics"],
                "years_experience": 5
            },
            "context": {
                "expertise": "machine_learning",
                "level": "mid",
                "researcher": True
            }
        },
        {
            "label": "Employee",
            "properties": {
                "name": "Carol Williams",
                "role": "Product Manager",
                "skills": ["Agile", "Strategy", "User Research"],
                "years_experience": 6
            },
            "context": {
                "expertise": "product",
                "level": "senior",
                "domain": "enterprise"
            }
        },
        {
            "label": "Employee",
            "properties": {
                "name": "David Chen",
                "role": "DevOps Engineer",
                "skills": ["AWS", "Kubernetes", "Terraform"],
                "years_experience": 4
            },
            "context": {
                "expertise": "infrastructure",
                "level": "mid",
                "on_call": True
            }
        },
        {
            "label": "Employee",
            "properties": {
                "name": "Eva Martinez",
                "role": "Frontend Engineer",
                "skills": ["React", "TypeScript", "D3.js"],
                "years_experience": 3
            },
            "context": {
                "expertise": "frontend",
                "level": "mid",
                "ui_specialist": True
            }
        },
        {
            "label": "Employee",
            "properties": {
                "name": "Frank Zhang",
                "role": "ML Engineer",
                "skills": ["Python", "TensorFlow", "MLOps"],
                "years_experience": 4
            },
            "context": {
                "expertise": "machine_learning",
                "level": "mid",
                "research_focus": "nlp"
            }
        }
    ]
}

def create_relationships(node_ids):
    """Create relationship data structure"""
    now = datetime.now()
    relationships = [
        # Department Memberships
        {
            "source_id": node_ids["employee_Alice Johnson"],
            "target_id": node_ids["dept_Engineering"],
            "type": "WORKS_IN",
            "properties": {"since": "2023-01-01", "role": "Team Lead"},
            "context": {"role": "team_lead"}
        },
        {
            "source_id": node_ids["employee_Bob Smith"],
            "target_id": node_ids["dept_Data Science"],
            "type": "WORKS_IN",
            "properties": {"since": "2023-03-15"},
            "context": {"role": "team_member"}
        },
        {
            "source_id": node_ids["employee_Carol Williams"],
            "target_id": node_ids["dept_Product"],
            "type": "WORKS_IN",
            "properties": {"since": "2023-02-01", "role": "Manager"},
            "context": {"role": "manager"}
        },
        {
            "source_id": node_ids["employee_David Chen"],
            "target_id": node_ids["dept_DevOps"],
            "type": "WORKS_IN",
            "properties": {"since": "2023-06-15"},
            "context": {"role": "team_member"}
        },
        {
            "source_id": node_ids["employee_Eva Martinez"],
            "target_id": node_ids["dept_Engineering"],
            "type": "WORKS_IN",
            "properties": {"since": "2023-04-01"},
            "context": {"role": "team_member"}
        },
        {
            "source_id": node_ids["employee_Frank Zhang"],
            "target_id": node_ids["dept_Data Science"],
            "type": "WORKS_IN",
            "properties": {"since": "2023-05-01"},
            "context": {"role": "team_member"}
        },

        # Project Assignments
        {
            "source_id": node_ids["employee_Alice Johnson"],
            "target_id": node_ids["project_Graph Database Enhancement"],
            "type": "LEADS",
            "properties": {"role": "Tech Lead", "hours_per_week": 30},
            "context": {"contribution": "architecture"}
        },
        {
            "source_id": node_ids["employee_Bob Smith"],
            "target_id": node_ids["project_ML Pipeline Optimization"],
            "type": "WORKS_ON",
            "properties": {"role": "Data Scientist", "hours_per_week": 20},
            "context": {"contribution": "algorithms"}
        },
        {
            "source_id": node_ids["employee_Carol Williams"],
            "target_id": node_ids["project_User Analytics Dashboard"],
            "type": "MANAGES",
            "properties": {"role": "Product Owner", "hours_per_week": 15},
            "context": {"contribution": "requirements"}
        },
        {
            "source_id": node_ids["employee_David Chen"],
            "target_id": node_ids["project_Cloud Migration"],
            "type": "LEADS",
            "properties": {"role": "DevOps Lead", "hours_per_week": 35},
            "context": {"contribution": "infrastructure"}
        },
        {
            "source_id": node_ids["employee_Eva Martinez"],
            "target_id": node_ids["project_User Analytics Dashboard"],
            "type": "WORKS_ON",
            "properties": {"role": "Frontend Developer", "hours_per_week": 25},
            "context": {"contribution": "ui_development"}
        },
        {
            "source_id": node_ids["employee_Frank Zhang"],
            "target_id": node_ids["project_ML Pipeline Optimization"],
            "type": "WORKS_ON",
            "properties": {"role": "ML Engineer", "hours_per_week": 30},
            "context": {"contribution": "model_deployment"}
        },

        # Cross-project Dependencies
        {
            "source_id": node_ids["project_ML Pipeline Optimization"],
            "target_id": node_ids["project_Cloud Migration"],
            "type": "DEPENDS_ON",
            "properties": {"type": "infrastructure", "critical": True},
            "context": {"dependency_type": "infrastructure"}
        },
        {
            "source_id": node_ids["project_User Analytics Dashboard"],
            "target_id": node_ids["project_ML Pipeline Optimization"],
            "type": "DEPENDS_ON",
            "properties": {"type": "data", "critical": False},
            "context": {"dependency_type": "data"}
        },

        # Mentorship Relationships
        {
            "source_id": node_ids["employee_Alice Johnson"],
            "target_id": node_ids["employee_Eva Martinez"],
            "type": "MENTORS",
            "properties": {"since": "2023-04-01", "focus_area": "system_design"},
            "context": {"mentorship_type": "technical"}
        },
        {
            "source_id": node_ids["employee_Bob Smith"],
            "target_id": node_ids["employee_Frank Zhang"],
            "type": "MENTORS",
            "properties": {"since": "2023-05-01", "focus_area": "machine_learning"},
            "context": {"mentorship_type": "technical"}
        }
    ]
    return relationships

async def create_sample_data():
    """Create sample nodes and relationships in the database"""
    base_url = "http://localhost:8000"
    node_ids = {}
    now = datetime.now()
    
    async with httpx.AsyncClient() as client:
        # Create department nodes
        for dept in SAMPLE_DATA["departments"]:
            response = await client.post(
                f"{base_url}/nodes/",
                json={
                    "label": dept["label"],
                    "properties": dept["properties"],
                    "valid_from": now.isoformat(),
                    "valid_to": None,
                    "context": dept["context"]
                }
            )
            if response.status_code == 200:
                node_ids[f"dept_{dept['properties']['name']}"] = response.text.strip('"')

        # Create project nodes
        for project in SAMPLE_DATA["projects"]:
            response = await client.post(
                f"{base_url}/nodes/",
                json={
                    "label": project["label"],
                    "properties": project["properties"],
                    "valid_from": now.isoformat(),
                    "valid_to": (now + timedelta(days=180)).isoformat(),
                    "context": project["context"]
                }
            )
            if response.status_code == 200:
                node_ids[f"project_{project['properties']['name']}"] = response.text.strip('"')

        # Create employee nodes
        for employee in SAMPLE_DATA["employees"]:
            response = await client.post(
                f"{base_url}/nodes/",
                json={
                    "label": employee["label"],
                    "properties": employee["properties"],
                    "valid_from": now.isoformat(),
                    "valid_to": None,
                    "context": employee["context"]
                }
            )
            if response.status_code == 200:
                node_ids[f"employee_{employee['properties']['name']}"] = response.text.strip('"')

        # Create all relationships
        relationships = create_relationships(node_ids)
        for rel in relationships:
            response = await client.post(
                f"{base_url}/relationships/",
                json={
                    **rel,
                    "valid_from": now.isoformat(),
                    "valid_to": None
                }
            )

    return node_ids

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_sample_data()) 