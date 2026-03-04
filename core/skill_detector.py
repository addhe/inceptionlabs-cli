"""Detect and execute skills from AI responses."""
import json
import re
from typing import Optional, Tuple, Dict, Any
from .skill_manager import SkillManager
from .ui import UI

ui = UI()

class SkillDetector:
    """Detect and execute skills from AI responses."""
    
    def __init__(self, skill_manager: SkillManager):
        self.skill_manager = skill_manager
    
    def extract_skill_call(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract skill call from AI response.
        
        Expected format: {"skill": "skill_name", "params": {"param1": "value1"}}
        
        Returns:
            dict with 'skill' and 'params' keys if found, None otherwise
        """
        # Look for JSON skill call
        skill_pattern = r'\{"skill"\s*:\s*"[^"]+"\s*,\s*"params"\s*:\s*\{[^}]*\}\}'
        
        # Find all potential skill calls
        for match in re.finditer(skill_pattern, response, re.DOTALL):
            json_str = match.group(0)
            try:
                skill_data = json.loads(json_str)
                if 'skill' in skill_data and 'params' in skill_data:
                    return skill_data
            except json.JSONDecodeError:
                continue
        
        # Try more flexible pattern with bracket counting
        start_pattern = r'\{"skill"\s*:\s*"'
        for match in re.finditer(start_pattern, response):
            start_pos = match.start()
            brace_count = 0
            in_string = False
            escape_next = False
            
            for i in range(start_pos, len(response)):
                char = response[i]
                
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    continue
                
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_str = response[start_pos:i+1]
                            try:
                                skill_data = json.loads(json_str)
                                if 'skill' in skill_data and 'params' in skill_data:
                                    return skill_data
                            except json.JSONDecodeError:
                                break
        
        return None
    
    def execute_from_response(self, response: str) -> Tuple[str, bool, Optional[Dict]]:
        """
        Extract and execute skill from AI response.
        
        Returns:
            Tuple of (cleaned_response, skill_executed, skill_result)
        """
        skill_call = self.extract_skill_call(response)
        
        if not skill_call:
            return response, False, None
        
        skill_name = skill_call.get('skill')
        params = skill_call.get('params', {})
        
        # Show what skill will be executed
        ui.print_info(f"\n🔧 Executing skill: [bold cyan]{skill_name}[/bold cyan]")
        ui.print_info(f"   Parameters: {params}")
        
        # Execute the skill
        result = self.skill_manager.execute_skill(skill_name, **params)
        
        # Display result
        if result.get('success'):
            ui.print_success("\n✓ Skill executed successfully")
            self._display_skill_result(skill_name, result.get('result'))
        else:
            ui.print_error(f"\n✗ Skill execution failed: {result.get('error')}")
        
        # Remove skill JSON from response
        cleaned_response = re.sub(
            r'\{"skill"\s*:\s*"[^"]+"\s*,\s*"params"\s*:\s*\{.*?\}\}',
            '',
            response,
            flags=re.DOTALL
        ).strip()
        
        return cleaned_response, True, result
    
    def _display_skill_result(self, skill_name: str, result: Any) -> None:
        """Display skill execution result with formatting."""
        from rich.console import Console
        from rich.json import JSON
        from rich.table import Table
        
        console = Console()
        
        if skill_name == "file_analyzer":
            self._display_file_analyzer_result(result, console)
        elif skill_name == "git_helper":
            self._display_git_helper_result(result, console)
        elif skill_name == "web_search":
            self._display_web_search_result(result, console)
        elif skill_name == "rss_reader":
            self._display_rss_reader_result(result, console)
        else:
            # Generic JSON display
            console.print(JSON(json.dumps(result, indent=2)))
    
    def _display_file_analyzer_result(self, result: Dict, console) -> None:
        """Display file analyzer results."""
        if "files" in result:
            # Directory analysis
            from rich.table import Table
            table = Table(title="File Analysis Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            summary = result.get("summary", {})
            table.add_row("Total Files", str(summary.get("total_files", 0)))
            table.add_row("Total Lines", str(summary.get("total_lines", 0)))
            table.add_row("Code Lines", str(summary.get("total_code_lines", 0)))
            
            console.print(table)
            
            # Languages breakdown
            if summary.get("languages"):
                console.print("\n[bold]Languages:[/bold]")
                for lang, count in summary["languages"].items():
                    console.print(f"  • {lang}: {count} files")
        else:
            # Single file analysis
            console.print(f"\n[bold]File:[/bold] {result.get('file')}")
            console.print(f"[bold]Language:[/bold] {result.get('language')}")
            console.print(f"[bold]Total Lines:[/bold] {result.get('total_lines')}")
            console.print(f"[bold]Code Lines:[/bold] {result.get('code_lines')}")
            console.print(f"[bold]Comments:[/bold] {result.get('comment_lines')}")
            console.print(f"[bold]Blank Lines:[/bold] {result.get('blank_lines')}")
    
    def _display_git_helper_result(self, result: Dict, console) -> None:
        """Display git helper results."""
        if "commits" in result:
            from rich.table import Table
            table = Table(title="Recent Commits")
            table.add_column("Hash", style="yellow")
            table.add_column("Author", style="cyan")
            table.add_column("Date", style="green")
            table.add_column("Message", style="white")
            
            for commit in result["commits"]:
                table.add_row(
                    commit["hash"],
                    commit["author"],
                    commit["date"],
                    commit["message"][:50] + "..." if len(commit["message"]) > 50 else commit["message"]
                )
            console.print(table)
        elif "branches" in result:
            console.print("\n[bold]Branches:[/bold]")
            for branch in result["branches"]:
                console.print(f"  • {branch}")
        else:
            console.print(JSON(json.dumps(result, indent=2)))
    
    def _display_web_search_result(self, result: Dict, console) -> None:
        """Display web search results."""
        console.print(f"\n[bold]Query:[/bold] {result.get('query')}")
        
        abstract = result.get('abstract')
        source_url = result.get('source_url')
        topics = result.get('related_topics', [])
        
        # Check if we have any results
        has_results = bool(abstract or source_url or topics)
        
        if abstract:
            console.print(f"\n[bold]Summary:[/bold]\n{abstract}")
        
        if source_url:
            console.print(f"\n[bold]Source:[/bold] {source_url}")
        
        if topics:
            console.print("\n[bold]Related Topics:[/bold]")
            for topic in topics:
                console.print(f"  • {topic.get('text', '')}")
                if topic.get('url'):
                    console.print(f"    {topic['url']}")
        
        # Show message if no results found
        if not has_results:
            console.print("\n[yellow]⚠ No detailed results found from DuckDuckGo Instant Answer API.[/yellow]")
            console.print("[dim]Note: DuckDuckGo Instant Answer works best for factual queries (definitions, concepts).[/dim]")
            console.print("[dim]For news and current events, try more specific queries or use a news-specific API.[/dim]")
    
    def _display_rss_reader_result(self, result: Dict, console) -> None:
        """Display RSS feed reader results."""
        from rich.table import Table
        from rich.panel import Panel
        
        feed_title = result.get('feed_title', 'RSS Feed')
        source = result.get('source', '')
        articles = result.get('articles', [])
        
        # Display feed info
        console.print(f"\n[bold cyan]📰 {feed_title}[/bold cyan]")
        console.print(f"[dim]Source: {source}[/dim]\n")
        
        if not articles:
            console.print("[yellow]No articles found in feed[/yellow]")
            return
        
        # Display articles
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'No title')
            link = article.get('link', '')
            published = article.get('published', '')
            summary = article.get('summary', '')
            
            # Create panel for each article
            content = f"[bold]{title}[/bold]\n"
            if published:
                content += f"[dim]📅 {published}[/dim]\n"
            if summary:
                content += f"\n{summary}\n"
            if link:
                content += f"\n[blue]🔗 {link}[/blue]"
            
            panel = Panel(
                content,
                title=f"Article {i}",
                border_style="cyan",
                expand=False
            )
            console.print(panel)
