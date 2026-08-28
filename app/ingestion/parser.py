"""
Markdown and Obsidian Note parser.
Extracts YAML frontmatter, cleans Obsidian Wikilinks, extracts headings,
and packages rich metadata.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml


@dataclass
class ObsidianDocument:
    """Represents a parsed Obsidian Markdown note."""
    content: str
    raw_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    headings: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def source(self) -> str:
        return self.metadata.get("source", "")

    @property
    def title(self) -> str:
        return self.metadata.get("title", "")

    @property
    def folder(self) -> str:
        return self.metadata.get("folder", "")

    @property
    def tags(self) -> List[str]:
        return self.metadata.get("tags", [])


class ObsidianParser:
    """Parser for Obsidian Markdown files."""

    # Frontmatter regex: starts at beginning of file with --- ... ---
    FRONTMATTER_REGEX = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    
    # Obsidian Wikilinks regex: [[Note Name|Alias]] or [[Note Name]]
    WIKILINK_ALIAS_REGEX = re.compile(r"\[\[([^\]|]+)\|([^\]]+)\]\]")
    WIKILINK_SIMPLE_REGEX = re.compile(r"\[\[([^\]]+)\]\]")
    
    # Obsidian Embeds: ![[image.png]] or ![[note#section]]
    EMBED_REGEX = re.compile(r"!\[\[(.*?)\]\]")
    
    # Obsidian comments: %% comment %%
    COMMENT_REGEX = re.compile(r"%%.*?%%", re.DOTALL)
    
    # Headings regex: # Heading
    HEADING_REGEX = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    
    # Inline tags regex: #tag_name (not preceded by non-space or inside code)
    INLINE_TAG_REGEX = re.compile(r"(?:^|\s)#([a-zA-Z0-9_\-\/]+)(?=\s|$|[.,;:!?])")

    def parse_file(
        self,
        file_path: Path,
        vault_root: Optional[Path] = None,
        override_filename: Optional[str] = None,
    ) -> ObsidianDocument:
        """
        Parse a markdown or text file from the vault.

        Args:
            file_path: Absolute or relative path to the file.
            vault_root: Optional path to the root of the vault.
            override_filename: Optional display/original filename.

        Returns:
            ObsidianDocument instance.
        """
        file_path = Path(file_path).resolve()
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                raw_content = f.read()
        except Exception as e:
            raise IOError(f"Could not read file {file_path}: {e}")

        actual_name = override_filename or file_path.name
        vault_root = vault_root or file_path.parent

        # Compute relative paths
        try:
            rel_path = str(file_path.relative_to(vault_root)) if not override_filename else actual_name
        except ValueError:
            rel_path = actual_name

        folder = str(Path(rel_path).parent)
        if folder == ".":
            folder = "Root"

        filename = actual_name
        stem = Path(actual_name).stem.replace("_", " ").replace("-", " ").title()

        # Extract frontmatter
        frontmatter_data, body_content = self._extract_frontmatter(raw_content)

        # Extract headings from body content
        headings = self._extract_headings(body_content)

        # Extract inline tags
        inline_tags = self._extract_inline_tags(body_content)

        # Merge tags from frontmatter and inline
        tags = self._normalize_tags(frontmatter_data.get("tags", []), inline_tags)

        # Determine title
        title = self._determine_title(frontmatter_data, headings, stem)

        # Clean content for vector embedding and retrieval
        cleaned_content = self._clean_markdown(body_content)

        # Metadata dictionary
        metadata: Dict[str, Any] = {
            "source": rel_path,
            "filename": filename,
            "title": title,
            "folder": folder,
            "tags": tags,
            "aliases": frontmatter_data.get("aliases", []),
            "created": str(frontmatter_data.get("created", "")),
            "total_headings": len(headings),
        }

        # Include custom frontmatter keys if any
        for k, v in frontmatter_data.items():
            if k not in metadata and isinstance(v, (str, int, float, bool, list)):
                metadata[k] = v

        return ObsidianDocument(
            content=cleaned_content,
            raw_content=raw_content,
            metadata=metadata,
            headings=headings,
        )

    def _extract_frontmatter(self, text: str) -> tuple[Dict[str, Any], str]:
        """Extract YAML frontmatter if present and return (dict, remaining_text)."""
        match = self.FRONTMATTER_REGEX.match(text)
        if not match:
            return {}, text

        yaml_text = match.group(1)
        remaining_text = text[match.end():]

        try:
            parsed = yaml.safe_load(yaml_text)
            if isinstance(parsed, dict):
                return parsed, remaining_text
        except Exception:
            # Fallback if invalid YAML syntax
            pass

        return {}, remaining_text

    def _extract_headings(self, text: str) -> List[Dict[str, Any]]:
        """Extract markdown headings with level and line position."""
        headings = []
        for match in self.HEADING_REGEX.finditer(text):
            level = len(match.group(1))
            heading_text = match.group(2).strip()
            headings.append({
                "level": level,
                "text": heading_text,
                "start": match.start(),
            })
        return headings

    def _extract_inline_tags(self, text: str) -> List[str]:
        """Extract inline hashtags like #ai #machine-learning from text."""
        # Avoid extracting inside markdown code blocks
        text_no_code = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text_no_code = re.sub(r"`.*?`", "", text_no_code)
        matches = self.INLINE_TAG_REGEX.findall(text_no_code)
        return [tag.strip() for tag in matches if not tag.startswith("#")]

    def _normalize_tags(self, frontmatter_tags: Any, inline_tags: List[str]) -> List[str]:
        """Consolidate tags into a clean list of unique lowercase strings."""
        all_tags = set()

        if isinstance(frontmatter_tags, list):
            for t in frontmatter_tags:
                if isinstance(t, str):
                    all_tags.add(t.strip().lstrip("#").lower())
        elif isinstance(frontmatter_tags, str):
            # Comma-separated or space-separated
            for t in re.split(r"[, ]+", frontmatter_tags):
                if t.strip():
                    all_tags.add(t.strip().lstrip("#").lower())

        for t in inline_tags:
            all_tags.add(t.strip().lstrip("#").lower())

        return sorted(list(all_tags))

    def _determine_title(
        self,
        frontmatter_data: Dict[str, Any],
        headings: List[Dict[str, Any]],
        filename_stem: str
    ) -> str:
        """Derive the most descriptive note title."""
        if "title" in frontmatter_data and isinstance(frontmatter_data["title"], str):
            return frontmatter_data["title"].strip()

        # Look for the first Level 1 heading
        for h in headings:
            if h["level"] == 1:
                return h["text"]

        # If no H1, use first heading of any level
        if headings:
            return headings[0]["text"]

        # Fallback to file name stem (e.g. "RAG" from "RAG.md")
        return filename_stem.replace("_", " ").replace("-", " ").title()

    def _clean_markdown(self, text: str) -> str:
        """
        Clean and normalize markdown for vector search.
        Transforms Obsidian wikilinks into plain text, strips comments and image embeds.
        """
        # Remove Obsidian comments: %% ... %%
        text = self.COMMENT_REGEX.sub("", text)

        # Replace image/media embeds: ![[image.png]] -> ""
        text = self.EMBED_REGEX.sub("", text)

        # Replace aliased wikilinks: [[Note Name|Alias]] -> Alias
        text = self.WIKILINK_ALIAS_REGEX.sub(r"\2", text)

        # Replace simple wikilinks: [[Note Name]] -> Note Name
        text = self.WIKILINK_SIMPLE_REGEX.sub(r"\1", text)

        # Normalize excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()
