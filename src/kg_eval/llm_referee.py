"""
LLM Referee for KG-Eval framework.

This module provides an interface for using LLMs as "referees" to evaluate
factual precision and contextual relevance of extracted knowledge.
"""

from typing import Union, Literal, Any, Optional
from abc import ABC, abstractmethod
import json

from .data_objects import Relationship, SourceText, Entity


class LLMReferee(ABC):
    """Abstract base class for LLM referees."""

    @abstractmethod
    def evaluate_factual_precision(self, relationship: Relationship, source_text: SourceText) -> Literal["correct", "partially_correct", "incorrect"]:
        """
        Evaluate if a relationship is factually correct according to the source text.
        
        Args:
            relationship: The relationship to evaluate
            source_text: The source text from which the relationship was extracted
            
        Returns:
            "correct", "partially_correct", or "incorrect"
        """
        pass

    @abstractmethod
    def evaluate_contextual_relevance(self, knowledge_item: Union[Entity, Relationship], 
                                    source_text: SourceText, item_type: str) -> bool:
        """
        Evaluate if a knowledge item represents core or marginal information.
        
        Args:
            knowledge_item: The entity or relationship to evaluate
            source_text: The source text from which the item was extracted
            item_type: "entity" or "relationship"
            
        Returns:
            True if core fact, False if marginal fact
        """
        pass


class OpenAIReferee(LLMReferee):
    """OpenAI-based LLM referee implementation."""

    def __init__(self, api_key: str, model: str = "gpt-4", temperature: float = 0.1, base_url: Optional[str] = None):
        """
        Initialize OpenAI referee.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4)
            temperature: Temperature for generation (default: 0.1 for consistency)
            base_url: Custom base URL for API endpoint (optional, for proxies or custom deployments)
        """
        try:
            import openai
            
            # Configure client with optional base_url
            client_kwargs = {"api_key": api_key}
            if base_url:
                client_kwargs["base_url"] = base_url
                
            self.client = openai.OpenAI(**client_kwargs)
            self.model = model
            self.temperature = temperature
            self.base_url = base_url
        except ImportError:
            raise ImportError("OpenAI package is required. Install with: pip install openai")

    def evaluate_factual_precision(self, relationship: Relationship, source_text: SourceText) -> Literal["correct", "partially_correct", "incorrect"]:
        """Evaluate factual precision using OpenAI."""
        prompt = self._create_factual_precision_prompt(relationship, source_text)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=50
            )
            
            result = response.choices[0].message.content.strip().lower()
            
            if "correct" in result and "partially" not in result:
                return "correct"
            elif "partially" in result or "partial" in result:
                return "partially_correct"
            else:
                return "incorrect"
                
        except Exception as e:
            print(f"Error in factual precision evaluation: {e}")
            return "incorrect"

    def evaluate_contextual_relevance(self, knowledge_item: Union[Entity, Relationship], 
                                    source_text: SourceText, item_type: str) -> bool:
        """Evaluate contextual relevance using OpenAI."""
        prompt = self._create_contextual_relevance_prompt(knowledge_item, source_text, item_type)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=50
            )
            
            result = response.choices[0].message.content.strip().lower()
            return "core" in result or "important" in result
            
        except Exception as e:
            print(f"Error in contextual relevance evaluation: {e}")
            return False

    def _create_factual_precision_prompt(self, relationship: Relationship, source_text: SourceText) -> str:
        """Create prompt for factual precision evaluation."""
        return f"""You are evaluating the factual accuracy of extracted knowledge from text.

Source Text:
"{source_text.content}"

Extracted Relationship:
- Source Entity: {relationship.source_entity_name}
- Target Entity: {relationship.target_entity_name}
- Relationship: {relationship.description}

Question: Is this relationship factually correct according to the source text?

Please respond with exactly one of:
- "CORRECT" if the relationship is fully supported by the source text
- "PARTIALLY_CORRECT" if the relationship is somewhat supported but has inaccuracies
- "INCORRECT" if the relationship is not supported or contradicted by the source text

Response:"""

    def _create_contextual_relevance_prompt(self, knowledge_item: Union[Entity, Relationship], 
                                          source_text: SourceText, item_type: str) -> str:
        """Create prompt for contextual relevance evaluation."""
        if item_type == "entity":
            item_desc = f"Entity: {knowledge_item.entity_name}"
            if knowledge_item.entity_type:
                item_desc += f" (Type: {knowledge_item.entity_type})"
        else:  # relationship
            item_desc = f"Relationship: {knowledge_item.source_entity_name} -> {knowledge_item.target_entity_name}: {knowledge_item.description}"

        return f"""You are evaluating the importance of extracted knowledge from text.

Source Text:
"{source_text.content}"

Extracted Knowledge:
{item_desc}

Question: Is this extracted knowledge a CORE FACT or MARGINAL information from the source text?

Core facts are central, important information that represents the main content or key details.
Marginal information is peripheral, trivial, or secondary details.

Please respond with exactly one of:
- "CORE" if this is important, central information
- "MARGINAL" if this is peripheral or trivial information

Response:"""


class AnthropicReferee(LLMReferee):
    """Anthropic Claude-based LLM referee implementation."""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", max_tokens: int = 50, base_url: Optional[str] = None):
        """
        Initialize Anthropic referee.
        
        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-3-sonnet)
            max_tokens: Maximum tokens for response
            base_url: Custom base URL for API endpoint (optional, for proxies or custom deployments)
        """
        try:
            import anthropic
            
            # Configure client with optional base_url
            client_kwargs = {"api_key": api_key}
            if base_url:
                client_kwargs["base_url"] = base_url
                
            self.client = anthropic.Anthropic(**client_kwargs)
            self.model = model
            self.max_tokens = max_tokens
            self.base_url = base_url
        except ImportError:
            raise ImportError("Anthropic package is required. Install with: pip install anthropic")

    def evaluate_factual_precision(self, relationship: Relationship, source_text: SourceText) -> Literal["correct", "partially_correct", "incorrect"]:
        """Evaluate factual precision using Anthropic."""
        prompt = self._create_factual_precision_prompt(relationship, source_text)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text.strip().lower()
            
            if "correct" in result and "partially" not in result:
                return "correct"
            elif "partially" in result or "partial" in result:
                return "partially_correct"
            else:
                return "incorrect"
                
        except Exception as e:
            print(f"Error in factual precision evaluation: {e}")
            return "incorrect"

    def evaluate_contextual_relevance(self, knowledge_item: Union[Entity, Relationship], 
                                    source_text: SourceText, item_type: str) -> bool:
        """Evaluate contextual relevance using Anthropic."""
        prompt = self._create_contextual_relevance_prompt(knowledge_item, source_text, item_type)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text.strip().lower()
            return "core" in result or "important" in result
            
        except Exception as e:
            print(f"Error in contextual relevance evaluation: {e}")
            return False

    def _create_factual_precision_prompt(self, relationship: Relationship, source_text: SourceText) -> str:
        """Create prompt for factual precision evaluation."""
        return f"""You are evaluating the factual accuracy of extracted knowledge from text.

Source Text:
"{source_text.content}"

Extracted Relationship:
- Source Entity: {relationship.source_entity_name}
- Target Entity: {relationship.target_entity_name}
- Relationship: {relationship.description}

Question: Is this relationship factually correct according to the source text?

Please respond with exactly one of:
- "CORRECT" if the relationship is fully supported by the source text
- "PARTIALLY_CORRECT" if the relationship is somewhat supported but has inaccuracies
- "INCORRECT" if the relationship is not supported or contradicted by the source text

Response:"""

    def _create_contextual_relevance_prompt(self, knowledge_item: Union[Entity, Relationship], 
                                          source_text: SourceText, item_type: str) -> str:
        """Create prompt for contextual relevance evaluation."""
        if item_type == "entity":
            item_desc = f"Entity: {knowledge_item.entity_name}"
            if knowledge_item.entity_type:
                item_desc += f" (Type: {knowledge_item.entity_type})"
        else:  # relationship
            item_desc = f"Relationship: {knowledge_item.source_entity_name} -> {knowledge_item.target_entity_name}: {knowledge_item.description}"

        return f"""You are evaluating the importance of extracted knowledge from text.

Source Text:
"{source_text.content}"

Extracted Knowledge:
{item_desc}

Question: Is this extracted knowledge a CORE FACT or MARGINAL information from the source text?

Core facts are central, important information that represents the main content or key details.
Marginal information is peripheral, trivial, or secondary details.

Please respond with exactly one of:
- "CORE" if this is important, central information
- "MARGINAL" if this is peripheral or trivial information

Response:""" 