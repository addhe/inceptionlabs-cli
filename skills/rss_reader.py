"""RSS Feed Reader skill - read news from RSS feeds."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.skill_base import Skill, SkillMetadata, SkillParameter
from typing import Dict, Any
import subprocess

class RSSReaderSkill(Skill):
    """Read and parse RSS feeds from news sources."""
    
    # Popular news RSS feeds
    FEED_SOURCES = {
        "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
        "cnn": "http://rss.cnn.com/rss/edition.rss",
        "reuters": "https://www.reutersagency.com/feed/?best-topics=tech&post_type=best",
        "techcrunch": "https://techcrunch.com/feed/",
        "hackernews": "https://news.ycombinator.com/rss",
        "nytimes": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "guardian": "https://www.theguardian.com/world/rss",
        "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "verge": "https://www.theverge.com/rss/index.xml",
        "wired": "https://www.wired.com/feed/rss",
    }
    
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="rss_reader",
            description="Read news articles from RSS feeds (BBC, CNN, Reuters, TechCrunch, etc.)",
            version="1.0.0",
            author="InceptionLabs",
            parameters=[
                SkillParameter(
                    name="source",
                    type="str",
                    description=f"News source: {', '.join(self.FEED_SOURCES.keys())}, or custom RSS URL",
                    required=True
                ),
                SkillParameter(
                    name="limit",
                    type="int",
                    description="Number of articles to return (default: 5)",
                    required=False,
                    default=5
                )
            ],
            examples=[
                '{"skill": "rss_reader", "params": {"source": "bbc", "limit": 5}}',
                '{"skill": "rss_reader", "params": {"source": "techcrunch", "limit": 3}}',
                '{"skill": "rss_reader", "params": {"source": "https://example.com/feed.xml"}}'
            ]
        )
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        source = kwargs.get("source", "")
        limit = kwargs.get("limit", 5)
        
        if not source:
            return {
                "success": False,
                "error": "Source parameter is required"
            }
        
        # Get feed URL
        feed_url = self.FEED_SOURCES.get(source.lower(), source)
        
        try:
            # Use feedparser directly (more reliable than subprocess)
            import feedparser
            
            feed = feedparser.parse(feed_url)
            
            if feed.bozo and not feed.entries:
                # If parsing failed and no entries, try fallback
                return self._fallback_parse(feed_url, limit, source)
            
            # Extract articles
            articles = []
            for entry in feed.entries[:limit]:
                summary = entry.get("summary", "") or entry.get("description", "")
                # Clean HTML tags from summary
                import re
                summary = re.sub(r'<[^>]+>', '', summary).strip()
                if len(summary) > 200:
                    summary = summary[:200] + "..."
                
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", "") or entry.get("updated", ""),
                    "summary": summary
                })
            
            if not articles:
                return {
                    "success": False,
                    "error": "No articles found in feed"
                }
            
            return {
                "success": True,
                "result": {
                    "source": source,
                    "feed_url": feed_url,
                    "feed_title": feed.feed.get("title", f"{source.upper()} News"),
                    "articles": articles
                }
            }
                
        except Exception as e:
            # Try fallback parsing
            try:
                return self._fallback_parse(feed_url, limit, source)
            except:
                return {
                    "success": False,
                    "error": f"RSS read error: {str(e)}"
                }
    
    def _fallback_parse(self, feed_url: str, limit: int, source: str) -> Dict[str, Any]:
        """Fallback parsing using curl and basic XML parsing."""
        try:
            result = subprocess.run(
                ["curl", "-s", "-L", feed_url],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "Failed to fetch RSS feed"
                }
            
            # Basic XML parsing
            import re
            xml_content = result.stdout
            
            # Extract items
            items = re.findall(r'<item>(.*?)</item>', xml_content, re.DOTALL)
            if not items:
                items = re.findall(r'<entry>(.*?)</entry>', xml_content, re.DOTALL)
            
            articles = []
            for item in items[:limit]:
                title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
                link_match = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
                desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
                if not desc_match:
                    desc_match = re.search(r'<summary>(.*?)</summary>', item, re.DOTALL)
                pub_match = re.search(r'<pubDate>(.*?)</pubDate>', item, re.DOTALL)
                if not pub_match:
                    pub_match = re.search(r'<published>(.*?)</published>', item, re.DOTALL)
                
                if title_match:
                    # Clean HTML tags from description
                    desc = desc_match.group(1) if desc_match else ""
                    desc = re.sub(r'<[^>]+>', '', desc).strip()
                    desc = desc[:200] + "..." if len(desc) > 200 else desc
                    
                    articles.append({
                        "title": title_match.group(1).strip(),
                        "link": link_match.group(1).strip() if link_match else "",
                        "published": pub_match.group(1).strip() if pub_match else "",
                        "summary": desc
                    })
            
            if not articles:
                return {
                    "success": False,
                    "error": "No articles found in feed"
                }
            
            return {
                "success": True,
                "result": {
                    "source": source,
                    "feed_url": feed_url,
                    "feed_title": f"{source.upper()} News",
                    "articles": articles
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Fallback parse error: {str(e)}"
            }
