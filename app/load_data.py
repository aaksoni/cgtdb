import asyncio
from app.utils.sample_data import create_sample_data

async def main():
    print("Loading sample data into the database...")
    node_ids = await create_sample_data()
    print("Sample data loaded successfully!")
    print(f"Created {len(node_ids)} nodes")

if __name__ == "__main__":
    asyncio.run(main()) 