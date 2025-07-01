"""
Core data objects for KG-Eval framework.

This module defines the fundamental data structures used in the evaluation process:
- Entity: Represents a node in the knowledge graph
- Relationship: Represents a directed edge between two entities
- SourceText: Represents the original text snippet from which knowledge is extracted
"""

from typing import List, Optional, Tuple
from pydantic import BaseModel, Field


class Entity(BaseModel):
    """
    Represents a node in the knowledge graph.
    
    Attributes:
        entity_name: The unique, canonical, human-readable name of the entity
        entity_type: The category of the entity (optional)
        description: A text description of the entity (optional)
    """
    entity_name: str = Field(
        description="The unique, canonical, human-readable name of the entity"
    )
    entity_type: Optional[str] = Field(
        None, description="The category of the entity (e.g., 'Person', 'Location')"
    )
    description: Optional[str] = Field(
        None, description="A text description of the entity"
    )

    def __hash__(self) -> int:
        return hash(self.entity_name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.entity_name == other.entity_name

    def __str__(self) -> str:
        return self.entity_name


class Relationship(BaseModel):
    """
    Represents a directed edge between two entities.
    
    Attributes:
        source_entity_name: The entity_name of the source entity
        target_entity_name: The entity_name of the target entity
        description: A text description of the relationship
        keywords: A list of keywords or tags summarizing the type of relationship
        weight: A numerical value representing the confidence or importance
    """
    source_entity_name: str = Field(
        description="The entity_name of the source entity"
    )
    target_entity_name: str = Field(
        description="The entity_name of the target entity"
    )
    description: str = Field(
        description="A text description of the relationship"
    )
    keywords: Optional[List[str]] = Field(
        None, description="A list of keywords or tags summarizing the relationship type"
    )
    weight: Optional[float] = Field(
        None, description="A numerical value representing confidence or importance"
    )

    def __hash__(self) -> int:
        return hash((self.source_entity_name, self.target_entity_name, self.description))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Relationship):
            return False
        return (
            self.source_entity_name == other.source_entity_name
            and self.target_entity_name == other.target_entity_name
            and self.description == other.description
        )

    def __str__(self) -> str:
        return f"{self.source_entity_name} -> {self.target_entity_name}: {self.description}"


class SourceText(BaseModel):
    """
    Represents the original text snippet from which knowledge is extracted.
    
    Attributes:
        content: The raw content of the text block
        linked_entity_names: A list of entity_names extracted from this text block
        linked_edges: A list of relationships extracted from this text block
    """
    content: str = Field(
        description="The raw content of the text block"
    )
    linked_entity_names: List[str] = Field(
        description="A list of entity_names extracted from this text block"
    )
    linked_edges: List[Tuple[str, str]] = Field(
        description="A list of relationships extracted from this text block, "
                   "where each relationship is represented by a tuple of "
                   "(source_entity_name, target_entity_name)"
    )

    def __str__(self) -> str:
        return f"SourceText({len(self.content)} chars, {len(self.linked_entity_names)} entities, {len(self.linked_edges)} edges)"


class KnowledgeGraph(BaseModel):
    """
    Represents a complete knowledge graph with entities, relationships, and source texts.
    
    This is the main container for all evaluation data.
    """
    entities: List[Entity] = Field(description="List of all entities in the graph")
    relationships: List[Relationship] = Field(description="List of all relationships in the graph")
    source_texts: List[SourceText] = Field(description="List of all source texts")

    def get_entity_names(self) -> List[str]:
        """Get all unique entity names in the graph."""
        return [entity.entity_name for entity in self.entities]

    def get_entity_by_name(self, name: str) -> Optional[Entity]:
        """Get an entity by its name."""
        for entity in self.entities:
            if entity.entity_name == name:
                return entity
        return None

    def get_relationships_for_entity(self, entity_name: str) -> List[Relationship]:
        """Get all relationships where the entity is involved (as source or target)."""
        return [
            rel for rel in self.relationships
            if rel.source_entity_name == entity_name or rel.target_entity_name == entity_name
        ]

    def __str__(self) -> str:
        return f"KnowledgeGraph({len(self.entities)} entities, {len(self.relationships)} relationships, {len(self.source_texts)} source texts)" 