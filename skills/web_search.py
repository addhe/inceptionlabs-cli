"""Web search skill - search the web for information."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.skill_base import Skill, SkillMetadata, SkillParameter
from typing import Dict, Any
import subprocess

class WebSearchSkill(Skill):
    """Search the web using curl and return results."""
    
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="web_search",
            description="Search the web for information using DuckDuckGo Instant Answer API",
            version="1.0.0",
            author="InceptionLabs",
            parameters=[
                SkillParameter(
                    name="query",
                    type="str",
                    description="Search query",
                    required=True
                )
            ],
            examples=[
                '{"skill": "web_search", "params": {"query": "Python programming"}}',
                '{"skill": "web_search", "params": {"query": "what is clean code"}}'
            ]
        )
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        query = kwargs.get("query", "")
        
        if not query:
            return {
                "success": False,
                "error": "Query parameter is required"
            }
        
        try:
            # Use DuckDuckGo Instant Answer API
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json"
            
            result = subprocess.run(
                ["curl", "-s", url],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                # Extract relevant information
                abstract = data.get("Abstract", "")
                abstract_text = data.get("AbstractText", "")
                abstract_url = data.get("AbstractURL", "")
                related_topics = data.get("RelatedTopics", [])
                
                # Get first few related topics
                topics = []
                for topic in related_topics[:5]:
                    if isinstance(topic, dict) and "Text" in topic:
                        topics.append({
                            "text": topic.get("Text", ""),
                            "url": topic.get("FirstURL", "")
                        })
                
                return {
                    "success": True,
                    "result": {
                        "query": query,
                        "abstract": abstract_text or abstract,
                        "source_url": abstract_url,
                        "related_topics": topics
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Search failed: {result.stderr}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Search error: {str(e)}"
            }
