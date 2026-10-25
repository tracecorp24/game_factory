"""
Projects REST API endpoints.
CreativeForge Intelligence Studio v3.0 - Section J.
"""

from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="", tags=["Projects"])

# In-memory store
_PROJECTS: Dict[str, Dict[str, Any]] = {
    "proj_gem_rush": {
        "id": "proj_gem_rush",
        "workspace_id": "ws_default",
        "name": "Gem Rush: Match-3 Arena",
        "type": "mobile_game_creative",
        "created_at": "2026-10-25T10:00:00Z",
    }
}


class ProjectCreate(BaseModel):
    name: str = Field(..., examples=["Royal Tile Crush"])
    workspace_id: str = Field(default="ws_default")
    type: str = Field(default="mobile_game_creative")
    settings: Dict[str, Any] = Field(default_factory=dict)


@router.post("/projects", status_code=201)
async def create_project(payload: ProjectCreate):
    """Create a new CreativeForge project."""
    project_id = f"proj_{uuid.uuid4().hex[:8]}"
    project = {
        "id": project_id,
        "workspace_id": payload.workspace_id,
        "name": payload.name,
        "type": payload.type,
        "settings": payload.settings,
        "created_at": "2026-10-25T12:00:00Z",
    }
    _PROJECTS[project_id] = project
    return project


@router.get("/projects")
async def list_projects(workspace_id: Optional[str] = None):
    """List all projects, optionally filtered by workspace."""
    if workspace_id:
        return [p for p in _PROJECTS.values() if p.get("workspace_id") == workspace_id]
    return list(_PROJECTS.values())


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details by ID."""
    if project_id not in _PROJECTS:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    return _PROJECTS[project_id]
