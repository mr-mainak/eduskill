from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

# Initialize once at application startup
client = MongoClient(
    "mongodb://192.168.1.31:27017/",
    serverSelectionTimeoutMS=5000,
)

db = client["eduskill"]
projects: Collection = db["projects"]


def read_project(project_id: str) -> Optional[str]:
    """
    Retrieve a project by its MongoDB ObjectId and return a formatted string.

    Args:
        project_id: MongoDB ObjectId as a string.

    Returns:
        A formatted project description, or None if the project does not exist.

    Raises:
        RuntimeError: If a database error occurs.
        ValueError: If the project_id is not a valid ObjectId.
    """

    try:
        object_id = ObjectId(project_id)
    except InvalidId as exc:
        raise ValueError(f"Invalid project id: {project_id}") from exc

    try:
        item = projects.find_one({"_id": object_id})
    except PyMongoError as exc:
        raise RuntimeError("Failed to read project from MongoDB.") from exc

    if item is None:
        return None

    components = "\n".join(
        f"- Name: {component['name']}, Quantity: {component['qty']}"
        for component in item.get("components", [])
    )

    steps = "\n".join(
        f"{index}. {step}"
        for index, step in enumerate(item.get("steps", []), start=1)
    )

    context = f"""Title: {item.get('title', '')}

Description: {item.get('description', '')}

Components:
{components}

Steps:
{steps}
"""

    return context
