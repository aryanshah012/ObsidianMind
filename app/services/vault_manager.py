"""
Vault & Workspace Manager for ObsidianMind.
Handles creation, listing, switching, and deletion of isolated knowledge workspaces.
"""

import json
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config import settings


class VaultMetadata(BaseModel):
    id: str
    name: str
    description: str = ""
    icon: str = "Folder"  # Folder, GraduationCap, Cpu, BookOpen, Briefcase, Code, Sparkles
    color: str = "#2E7D6A"
    is_default: bool = False
    created_at: float = Field(default_factory=time.time)
    collection_name: str


DEFAULT_VAULTS: List[Dict[str, Any]] = [
    {
        "id": "default",
        "name": "Primary Vault",
        "description": "Default personal knowledge vault with general notes and study guides",
        "icon": "Folder",
        "color": "#2E7D6A",
        "is_default": True,
        "collection_name": "obsidian_vault",
    },
    {
        "id": "academics",
        "name": "College & Academics",
        "description": "Courses, identity documents, grade records, and syllabus notes",
        "icon": "GraduationCap",
        "color": "#3B82F6",
        "is_default": False,
        "collection_name": "obsidian_vault_academics",
    },
    {
        "id": "ai-research",
        "name": "AI & Research",
        "description": "Machine learning papers, Transformer architectures, and RAG guides",
        "icon": "Cpu",
        "color": "#8B5CF6",
        "is_default": False,
        "collection_name": "obsidian_vault_research",
    },
]


class VaultManager:
    """Manages workspace vaults and persists configuration in data/vaults.json."""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_file = storage_path or (settings.DATA_DIR / "vaults.json")
        self.active_vault_id: str = "default"
        self._load_vaults()

    def _load_vaults(self) -> None:
        """Load vault list from disk, initializing defaults if file does not exist."""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_file.exists():
            self._save_vaults(DEFAULT_VAULTS, active_id="default")
            self.vaults = [VaultMetadata(**v) for v in DEFAULT_VAULTS]
            self.active_vault_id = "default"
            return

        try:
            data = json.loads(self.storage_file.read_text(encoding="utf-8"))
            vault_list = data.get("vaults", [])
            if not vault_list:
                vault_list = DEFAULT_VAULTS
            self.vaults = [VaultMetadata(**v) for v in vault_list]
            self.active_vault_id = data.get("active_vault_id", "default")
            
            # Ensure active_vault_id exists in vaults
            if not any(v.id == self.active_vault_id for v in self.vaults):
                self.active_vault_id = self.vaults[0].id if self.vaults else "default"
        except Exception as e:
            print(f"⚠️ Notice: Could not load vaults.json ({e}). Initializing defaults.")
            self.vaults = [VaultMetadata(**v) for v in DEFAULT_VAULTS]
            self.active_vault_id = "default"
            self._save_vaults(DEFAULT_VAULTS, active_id="default")

    def _save_vaults(self, vault_data: List[Dict[str, Any]], active_id: str) -> None:
        """Save vault list and active vault id to JSON file."""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "active_vault_id": active_id,
            "updated_at": time.time(),
            "vaults": vault_data,
        }
        self.storage_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def list_vaults(self) -> List[Dict[str, Any]]:
        """Return list of vaults with active status."""
        return [
            {
                **v.model_dump(),
                "is_active": (v.id == self.active_vault_id),
            }
            for v in self.vaults
        ]

    def get_vault(self, vault_id: str) -> Optional[VaultMetadata]:
        """Find a vault by ID."""
        for v in self.vaults:
            if v.id == vault_id:
                return v
        return None

    def get_active_vault(self) -> VaultMetadata:
        """Return the currently active vault."""
        active = self.get_vault(self.active_vault_id)
        if not active:
            active = self.vaults[0]
            self.active_vault_id = active.id
        return active

    def set_active_vault(self, vault_id: str) -> bool:
        """Switch active vault."""
        vault = self.get_vault(vault_id)
        if not vault:
            return False
        self.active_vault_id = vault.id
        self._save_vaults([v.model_dump() for v in self.vaults], active_id=self.active_vault_id)
        return True

    def create_vault(
        self,
        name: str,
        description: str = "",
        icon: str = "Folder",
        color: str = "#2E7D6A",
    ) -> VaultMetadata:
        """Create a new vault workspace with an isolated collection."""
        raw_slug = re.sub(r"[^\w\s-]", "", name.lower()).strip()
        slug = re.sub(r"[-\s]+", "-", raw_slug)
        if not slug:
            slug = f"vault-{int(time.time())}"

        # Ensure uniqueness
        base_slug = slug
        counter = 1
        while any(v.id == slug for v in self.vaults):
            slug = f"{base_slug}-{counter}"
            counter += 1

        collection_name = f"obsidian_vault_{slug.replace('-', '_')}"

        new_vault = VaultMetadata(
            id=slug,
            name=name.strip(),
            description=description.strip(),
            icon=icon,
            color=color,
            is_default=False,
            created_at=time.time(),
            collection_name=collection_name,
        )

        self.vaults.append(new_vault)
        self.active_vault_id = new_vault.id
        self._save_vaults([v.model_dump() for v in self.vaults], active_id=self.active_vault_id)
        return new_vault

    def delete_vault(self, vault_id: str) -> bool:
        """Delete a custom vault (cannot delete default vault)."""
        vault = self.get_vault(vault_id)
        if not vault or vault.is_default or len(self.vaults) <= 1:
            return False

        self.vaults = [v for v in self.vaults if v.id != vault_id]

        if self.active_vault_id == vault_id:
            self.active_vault_id = self.vaults[0].id

        self._save_vaults([v.model_dump() for v in self.vaults], active_id=self.active_vault_id)
        return True
