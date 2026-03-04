"""File analyzer skill - analyze code files and provide insights."""
import os
from pathlib import Path
from typing import Dict, Any
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.skill_base import Skill, SkillMetadata, SkillParameter

class FileAnalyzerSkill(Skill):
    """Analyze files and provide insights about code structure."""
    
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="file_analyzer",
            description="Analyze code files to count lines, detect language, and provide statistics",
            version="1.0.0",
            author="InceptionLabs",
            parameters=[
                SkillParameter(
                    name="path",
                    type="str",
                    description="Path to file or directory to analyze",
                    required=True
                ),
                SkillParameter(
                    name="recursive",
                    type="bool",
                    description="Recursively analyze directories",
                    required=False,
                    default=False
                )
            ],
            examples=[
                '{"skill": "file_analyzer", "params": {"path": "cli.py"}}',
                '{"skill": "file_analyzer", "params": {"path": "core", "recursive": true}}'
            ]
        )
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        path = kwargs.get("path")
        recursive = kwargs.get("recursive", False)
        
        path_obj = Path(path)
        
        if not path_obj.exists():
            return {
                "success": False,
                "error": f"Path '{path}' does not exist"
            }
        
        if path_obj.is_file():
            return self._analyze_file(path_obj)
        elif path_obj.is_dir():
            return self._analyze_directory(path_obj, recursive)
        else:
            return {
                "success": False,
                "error": f"Path '{path}' is neither a file nor directory"
            }
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            blank_lines = total_lines - code_lines - comment_lines
            
            # Detect language
            ext = file_path.suffix
            language_map = {
                '.py': 'Python',
                '.js': 'JavaScript',
                '.ts': 'TypeScript',
                '.java': 'Java',
                '.cpp': 'C++',
                '.c': 'C',
                '.go': 'Go',
                '.rs': 'Rust',
                '.rb': 'Ruby',
                '.php': 'PHP',
                '.swift': 'Swift',
                '.kt': 'Kotlin',
                '.md': 'Markdown',
                '.json': 'JSON',
                '.yaml': 'YAML',
                '.yml': 'YAML',
            }
            language = language_map.get(ext, 'Unknown')
            
            return {
                "success": True,
                "result": {
                    "file": str(file_path),
                    "language": language,
                    "total_lines": total_lines,
                    "code_lines": code_lines,
                    "comment_lines": comment_lines,
                    "blank_lines": blank_lines,
                    "size_bytes": file_path.stat().st_size
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to analyze file: {str(e)}"
            }
    
    def _analyze_directory(self, dir_path: Path, recursive: bool) -> Dict[str, Any]:
        """Analyze all files in a directory."""
        try:
            files_analyzed = []
            total_stats = {
                "total_files": 0,
                "total_lines": 0,
                "total_code_lines": 0,
                "languages": {}
            }
            
            pattern = "**/*" if recursive else "*"
            for file_path in dir_path.glob(pattern):
                if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.java', '.go', '.rs']:
                    result = self._analyze_file(file_path)
                    if result["success"]:
                        file_data = result["result"]
                        files_analyzed.append(file_data)
                        total_stats["total_files"] += 1
                        total_stats["total_lines"] += file_data["total_lines"]
                        total_stats["total_code_lines"] += file_data["code_lines"]
                        
                        lang = file_data["language"]
                        if lang not in total_stats["languages"]:
                            total_stats["languages"][lang] = 0
                        total_stats["languages"][lang] += 1
            
            return {
                "success": True,
                "result": {
                    "directory": str(dir_path),
                    "files": files_analyzed,
                    "summary": total_stats
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to analyze directory: {str(e)}"
            }
