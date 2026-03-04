"""Git helper skill - perform git operations."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.skill_base import Skill, SkillMetadata, SkillParameter
from typing import Dict, Any
import subprocess

class GitHelperSkill(Skill):
    """Helper skill for common git operations."""
    
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="git_helper",
            description="Perform common git operations like status, log, diff, and branch info",
            version="1.0.0",
            author="InceptionLabs",
            parameters=[
                SkillParameter(
                    name="operation",
                    type="str",
                    description="Git operation: status, log, diff, branches, current_branch",
                    required=True
                ),
                SkillParameter(
                    name="path",
                    type="str",
                    description="Repository path (defaults to current directory)",
                    required=False,
                    default="."
                ),
                SkillParameter(
                    name="limit",
                    type="int",
                    description="Limit number of results (for log operation)",
                    required=False,
                    default=10
                )
            ],
            examples=[
                '{"skill": "git_helper", "params": {"operation": "status"}}',
                '{"skill": "git_helper", "params": {"operation": "log", "limit": 5}}',
                '{"skill": "git_helper", "params": {"operation": "branches"}}'
            ]
        )
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        operation = kwargs.get("operation", "")
        path = kwargs.get("path", ".")
        limit = kwargs.get("limit", 10)
        
        operations = {
            "status": self._git_status,
            "log": lambda p: self._git_log(p, limit),
            "diff": self._git_diff,
            "branches": self._git_branches,
            "current_branch": self._git_current_branch
        }
        
        if operation not in operations:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}. Available: {', '.join(operations.keys())}"
            }
        
        try:
            return operations[operation](path)
        except Exception as e:
            return {
                "success": False,
                "error": f"Git operation failed: {str(e)}"
            }
    
    def _run_git_command(self, args: list, cwd: str = ".") -> tuple[bool, str, str]:
        """Run a git command and return success, stdout, stderr."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def _git_status(self, path: str) -> Dict[str, Any]:
        """Get git status."""
        success, stdout, stderr = self._run_git_command(["status", "--short"], path)
        if success:
            return {
                "success": True,
                "result": {
                    "status": stdout.strip(),
                    "clean": len(stdout.strip()) == 0
                }
            }
        return {"success": False, "error": stderr}
    
    def _git_log(self, path: str, limit: int) -> Dict[str, Any]:
        """Get git log."""
        success, stdout, stderr = self._run_git_command(
            ["log", f"-{limit}", "--pretty=format:%h|%an|%ar|%s"],
            path
        )
        if success:
            commits = []
            for line in stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3]
                        })
            return {
                "success": True,
                "result": {"commits": commits}
            }
        return {"success": False, "error": stderr}
    
    def _git_diff(self, path: str) -> Dict[str, Any]:
        """Get git diff."""
        success, stdout, stderr = self._run_git_command(["diff", "--stat"], path)
        if success:
            return {
                "success": True,
                "result": {"diff": stdout.strip()}
            }
        return {"success": False, "error": stderr}
    
    def _git_branches(self, path: str) -> Dict[str, Any]:
        """Get git branches."""
        success, stdout, stderr = self._run_git_command(["branch", "-a"], path)
        if success:
            branches = [b.strip().replace('* ', '') for b in stdout.strip().split('\n')]
            return {
                "success": True,
                "result": {"branches": branches}
            }
        return {"success": False, "error": stderr}
    
    def _git_current_branch(self, path: str) -> Dict[str, Any]:
        """Get current git branch."""
        success, stdout, stderr = self._run_git_command(["branch", "--show-current"], path)
        if success:
            return {
                "success": True,
                "result": {"branch": stdout.strip()}
            }
        return {"success": False, "error": stderr}
