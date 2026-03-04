"""Base class for skills system."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class SkillParameter:
    """Parameter definition for a skill."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None

@dataclass
class SkillMetadata:
    """Metadata for a skill."""
    name: str
    description: str
    version: str
    author: str
    parameters: List[SkillParameter]
    examples: List[str]

class Skill(ABC):
    """Base class for all skills."""
    
    @abstractmethod
    def get_metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the skill with given parameters.
        
        Returns:
            Dict with 'success', 'result', and optional 'error' keys
        """
        pass
    
    def validate_parameters(self, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate input parameters against skill metadata."""
        metadata = self.get_metadata()
        
        for param in metadata.parameters:
            if param.required and param.name not in kwargs:
                return False, f"Missing required parameter: {param.name}"
            
            if param.name in kwargs:
                value = kwargs[param.name]
                expected_type = param.type
                
                # Basic type checking
                if expected_type == "str" and not isinstance(value, str):
                    return False, f"Parameter {param.name} must be a string"
                elif expected_type == "int" and not isinstance(value, int):
                    return False, f"Parameter {param.name} must be an integer"
                elif expected_type == "bool" and not isinstance(value, bool):
                    return False, f"Parameter {param.name} must be a boolean"
                elif expected_type == "list" and not isinstance(value, list):
                    return False, f"Parameter {param.name} must be a list"
        
        return True, None
