"""
Vault & Workspace Manager for ObsidianMind.
Handles creation, listing, switching, and deletion of isolated knowledge workspaces,
with strict multi-user partitioning.
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


def get_default_vaults_for_user(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return isolated default workspace templates for a user."""
    prefix = f"user_{re.sub(r'[^a-zA-Z0-9_]', '_', user_id)}_" if user_id else "obsidian_vault_"
    return [
        {
            "id": "default",
            "name": "Primary Vault",
            "description": "Personal knowledge vault with general notes, journals, and docs",
            "icon": "Folder",
            "color": "#2E7D6A",
            "is_default": True,
            "collection_name": f"{prefix}default" if user_id else "obsidian_vault",
        },
        {
            "id": "academics",
            "name": "College & Academics",
            "description": "Courses, identity documents, grade records, and syllabus notes",
            "icon": "GraduationCap",
            "color": "#3B82F6",
            "is_default": False,
            "collection_name": f"{prefix}academics",
        },
        {
            "id": "ai-research",
            "name": "AI & Research",
            "description": "Machine learning papers, Transformer architectures, and RAG guides",
            "icon": "Cpu",
            "color": "#8B5CF6",
            "is_default": False,
            "collection_name": f"{prefix}research",
        },
    ]


class VaultManager:
    """Manages workspace vaults and persists configuration scoped per user."""

    def __init__(self, user_id: Optional[str] = None, storage_path: Optional[Path] = None):
        self.user_id = user_id
        if storage_path:
            self.storage_file = storage_path
        elif user_id:
            self.storage_file = settings.USERS_DIR / user_id / "vaults.json"
        else:
            self.storage_file = settings.DATA_DIR / "vaults.json"

        self.active_vault_id: str = "default"
        self._load_vaults()

    def _get_default_vaults(self) -> List[Dict[str, Any]]:
        return get_default_vaults_for_user(self.user_id)

    def _load_vaults(self) -> None:
        """Load vault list from disk, initializing defaults if file does not exist."""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        default_vaults = self._get_default_vaults()

        if not self.storage_file.exists():
            self._save_vaults(default_vaults, active_id="default")
            self.vaults = [VaultMetadata(**v) for v in default_vaults]
            self.active_vault_id = "default"
            return

        try:
            data = json.loads(self.storage_file.read_text(encoding="utf-8"))
            vault_list = data.get("vaults", [])
            if not vault_list:
                vault_list = default_vaults
            self.vaults = [VaultMetadata(**v) for v in vault_list]
            self.active_vault_id = data.get("active_vault_id", "default")

            # Ensure active_vault_id exists in vaults
            if not any(v.id == self.active_vault_id for v in self.vaults):
                self.active_vault_id = self.vaults[0].id if self.vaults else "default"
        except Exception as e:
            print(f"⚠️ Notice: Could not load vaults ({e}). Initializing defaults.")
            self.vaults = [VaultMetadata(**v) for v in default_vaults]
            self.active_vault_id = "default"
            self._save_vaults(default_vaults, active_id="default")

    def _save_vaults(self, vault_data: List[Dict[str, Any]], active_id: str) -> None:
        """Save vault list and active vault id to JSON file."""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "user_id": self.user_id,
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

        clean_slug = slug.replace("-", "_")
        if self.user_id:
            clean_uid = re.sub(r"[^a-zA-Z0-9_]", "_", self.user_id)
            collection_name = f"user_{clean_uid}_{clean_slug}"[:63]
        else:
            collection_name = f"obsidian_vault_{clean_slug}"[:63]

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
