"""Skills manager for loading and executing skills."""
import os
import importlib.util
from typing import Dict, List, Optional
from pathlib import Path
from .skill_base import Skill, SkillMetadata
from .ui import UI

ui = UI()

class SkillManager:
    """Manage skills loading and execution."""
    
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Skill] = {}
        self.load_skills()
    
    def load_skills(self) -> None:
        """Load all skills from the skills directory."""
        if not self.skills_dir.exists():
            self.skills_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for skill_file in self.skills_dir.glob("*.py"):
            if skill_file.name.startswith("_"):
                continue
            
            try:
                self._load_skill_from_file(skill_file)
            except Exception as e:
                ui.print_warning(f"Failed to load skill from {skill_file.name}: {e}")
    
    def _load_skill_from_file(self, file_path: Path) -> None:
        """Load a skill from a Python file."""
        module_name = file_path.stem
        
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find Skill subclasses in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Skill) and 
                    attr != Skill):
                    skill_instance = attr()
                    metadata = skill_instance.get_metadata()
                    self.skills[metadata.name] = skill_instance
                    ui.print_success(f"✓ Loaded skill: {metadata.name} v{metadata.version}")
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name."""
        return self.skills.get(name)
    
    def list_skills(self) -> List[SkillMetadata]:
        """List all available skills."""
        return [skill.get_metadata() for skill in self.skills.values()]
    
    def execute_skill(self, name: str, **kwargs) -> Dict:
        """Execute a skill with given parameters."""
        skill = self.get_skill(name)
        if not skill:
            return {
                "success": False,
                "error": f"Skill '{name}' not found"
            }
        
        # Validate parameters
        valid, error = skill.validate_parameters(**kwargs)
        if not valid:
            return {
                "success": False,
                "error": error
            }
        
        # Execute skill
        try:
            result = skill.execute(**kwargs)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Skill execution failed: {str(e)}"
            }
    
    def get_skills_for_ai_prompt(self) -> str:
        """Generate skills description for AI system prompt."""
        if not self.skills:
            return ""
        
        skills_desc = "\n\nAvailable Skills:\n"
        for metadata in self.list_skills():
            skills_desc += f"\n- **{metadata.name}**: {metadata.description}\n"
            skills_desc += "  Parameters:\n"
            for param in metadata.parameters:
                req = "required" if param.required else "optional"
                skills_desc += f"    - {param.name} ({param.type}, {req}): {param.description}\n"
            if metadata.examples:
                skills_desc += "  Examples:\n"
                for example in metadata.examples:
                    skills_desc += f"    - {example}\n"
        
        skills_desc += "\nTo use a skill, respond with JSON format:\n"
        skills_desc += '{"skill": "skill_name", "params": {"param1": "value1", "param2": "value2"}}\n'
        
        return skills_desc
