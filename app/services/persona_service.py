"""Persona management for AI assistant.

This module loads and manages customer-specific personas that define
the AI assistant's personality, tone, capabilities, and conversation flow.
"""
import os
from pathlib import Path
from typing import Optional

from app.core.config import settings


class PersonaManager:
    """Loads and manages AI assistant personas."""

    def __init__(self, personas_dir: Optional[Path] = None):
        """Initialize persona manager.

        Parameters
        ----------
        personas_dir : Path, optional
            Directory containing persona text files. Defaults to app/personas/
        """
        if personas_dir is None:
            personas_dir = Path(__file__).parent.parent / "personas"
        self.personas_dir = personas_dir

    def load_persona(self, persona_name: str = "default") -> str:
        """Load a persona by name.

        Parameters
        ----------
        persona_name : str
            Name of the persona file (without .txt extension).
            Examples: "default", "medical_clinic", "salon_spa"

        Returns
        -------
        str
            The full persona text with instructions for the AI.

        Raises
        ------
        FileNotFoundError
            If the persona file doesn't exist.
        """
        persona_file = self.personas_dir / f"{persona_name}.txt"

        if not persona_file.exists():
            # Fall back to default if specified persona doesn't exist
            if persona_name != "default":
                print(f"Warning: Persona '{persona_name}' not found. Using default.")
                persona_file = self.personas_dir / "default.txt"

        if not persona_file.exists():
            raise FileNotFoundError(
                f"Persona file not found: {persona_file}. "
                "Please create at least a default.txt persona."
            )

        return persona_file.read_text(encoding="utf-8")

    def inject_business_context(
        self,
        persona_text: str,
        business_name: Optional[str] = None,
        business_info: Optional[dict] = None,
    ) -> str:
        """Inject business-specific information into persona template.

        Parameters
        ----------
        persona_text : str
            The base persona text with placeholders.
        business_name : str, optional
            Name of the business to inject.
        business_info : dict, optional
            Additional business information (hours, services, address, etc.)

        Returns
        -------
        str
            Persona text with business context injected.
        """
        result = persona_text

        # Replace business name placeholder
        if business_name:
            result = result.replace("[Business Name]", business_name)

        # Inject additional business context if provided
        if business_info:
            context_section = "\n\n## Business Context (Current Session)\n"
            for key, value in business_info.items():
                context_section += f"- **{key.replace('_', ' ').title()}**: {value}\n"
            result += context_section

        return result

    def get_system_prompt(
        self,
        persona_name: str = "default",
        business_name: Optional[str] = None,
        business_info: Optional[dict] = None,
    ) -> str:
        """Get complete system prompt with persona and business context.

        This is the main method to use when setting up the AI assistant.

        Parameters
        ----------
        persona_name : str
            Name of the persona to load.
        business_name : str, optional
            Name of the business.
        business_info : dict, optional
            Additional business context.

        Returns
        -------
        str
            Complete system prompt ready for OpenAI.
        """
        persona = self.load_persona(persona_name)
        return self.inject_business_context(persona, business_name, business_info)

    def list_available_personas(self) -> list[str]:
        """List all available persona names.

        Returns
        -------
        list[str]
            List of persona names (without .txt extension).
        """
        if not self.personas_dir.exists():
            return []

        return [
            f.stem for f in self.personas_dir.glob("*.txt") if f.is_file()
        ]


# Singleton instance
persona_manager = PersonaManager()
