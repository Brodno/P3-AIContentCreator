"""
Notion Queue Manager - Store post queue in Notion Database
Compatible with Streamlit Cloud (stateless)
"""
import os
from datetime import datetime
from notion_client import Client

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


class NotionQueueManager:
    """Manage post queue using Notion Database"""

    def __init__(self, api_key=None, database_id=None):
        """
        Initialize Notion client

        Args:
            api_key: Notion Integration Token
            database_id: Notion Database ID
        """
        # Get credentials from Streamlit secrets or env
        if STREAMLIT_AVAILABLE and hasattr(st, 'secrets'):
            try:
                self.api_key = st.secrets['NOTION_API_KEY']
                self.database_id = st.secrets['NOTION_DATABASE_ID']
            except KeyError:
                self.api_key = api_key or os.getenv('NOTION_API_KEY')
                self.database_id = database_id or os.getenv('NOTION_DATABASE_ID')
        else:
            self.api_key = api_key or os.getenv('NOTION_API_KEY')
            self.database_id = database_id or os.getenv('NOTION_DATABASE_ID')

        if not self.api_key:
            raise ValueError("❌ NOTION_API_KEY not found!")

        if not self.database_id:
            raise ValueError("❌ NOTION_DATABASE_ID not found!")

        self.client = Client(auth=self.api_key)

    def add_post(self, topic, content, score, status="draft", scheduled_date=None):
        """
        Add new post to Notion database

        Args:
            topic: Post topic
            content: Post content
            score: Quality score
            status: draft/scheduled/published
            scheduled_date: Date for scheduled posts (YYYY-MM-DD)

        Returns:
            str: Notion Page ID
        """
        properties = {
            "Temat": {
                "title": [
                    {
                        "text": {
                            "content": topic[:100]  # Notion title limit
                        }
                    }
                ]
            },
            "Score": {
                "number": score
            },
            "Status": {
                "select": {
                    "name": status.capitalize()
                }
            },
            "Data utworzenia": {
                "date": {
                    "start": datetime.now().isoformat()
                }
            }
        }

        if scheduled_date:
            properties["Data publikacji"] = {
                "date": {
                    "start": scheduled_date
                }
            }

        # Store content in page body
        children = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content[:2000]  # Notion block limit
                            }
                        }
                    ]
                }
            }
        ]

        try:
            page = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=children
            )
            return page["id"]
        except Exception as e:
            print(f"❌ Error adding post to Notion: {e}")
            raise

    def get_posts(self, status=None):
        """
        Get posts filtered by status

        Args:
            status: Filter by status (None = all)

        Returns:
            list: Posts as dicts
        """
        try:
            # Build filter
            filter_params = {}
            if status:
                filter_params = {
                    "property": "Status",
                    "select": {
                        "equals": status.capitalize()
                    }
                }

            # Query database
            if filter_params:
                results = self.client.databases.query(
                    database_id=self.database_id,
                    filter=filter_params
                )
            else:
                results = self.client.databases.query(
                    database_id=self.database_id
                )

            # Parse results
            posts = []
            for page in results.get("results", []):
                props = page["properties"]

                # Extract title
                title_prop = props.get("Temat", {})
                title = ""
                if title_prop.get("title"):
                    title = title_prop["title"][0]["text"]["content"]

                # Extract status
                status_prop = props.get("Status", {})
                status_val = status_prop.get("select", {}).get("name", "").lower()

                # Extract score
                score_prop = props.get("Score", {})
                score_val = score_prop.get("number", 0)

                # Extract dates
                created_prop = props.get("Data utworzenia", {})
                created_date = created_prop.get("date", {}).get("start", "")

                published_prop = props.get("Data publikacji", {})
                published_date = published_prop.get("date", {}).get("start", "")

                posts.append({
                    'id': page["id"],
                    'topic': title,
                    'content': "",  # Content is in blocks, would need separate call
                    'score': score_val,
                    'status': status_val,
                    'created_at': created_date,
                    'scheduled_date': published_date if status_val == 'scheduled' else None,
                    'published_date': published_date if status_val == 'published' else None
                })

            return posts

        except Exception as e:
            print(f"❌ Error fetching posts from Notion: {e}")
            return []

    def update_status(self, post_id, new_status, scheduled_date=None):
        """
        Update post status

        Args:
            post_id: Notion Page ID
            new_status: New status
            scheduled_date: Date for scheduled posts
        """
        try:
            properties = {
                "Status": {
                    "select": {
                        "name": new_status.capitalize()
                    }
                }
            }

            if new_status == 'scheduled' and scheduled_date:
                properties["Data publikacji"] = {
                    "date": {
                        "start": scheduled_date
                    }
                }

            if new_status == 'published':
                properties["Data publikacji"] = {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                }

            self.client.pages.update(
                page_id=post_id,
                properties=properties
            )
            return True

        except Exception as e:
            print(f"❌ Error updating post status: {e}")
            return False

    def delete_post(self, post_id):
        """Archive post (Notion doesn't allow deleting)"""
        try:
            self.client.pages.update(
                page_id=post_id,
                archived=True
            )
        except Exception as e:
            print(f"❌ Error archiving post: {e}")

    def get_statistics(self):
        """Get queue statistics"""
        try:
            posts = self.get_posts()

            total = len(posts)
            draft = len([p for p in posts if p['status'] == 'draft'])
            scheduled = len([p for p in posts if p['status'] == 'scheduled'])
            published = len([p for p in posts if p['status'] == 'published'])

            scores = [p['score'] for p in posts if p['score'] > 0]
            avg_score = sum(scores) / len(scores) if scores else 0

            return {
                'total': total,
                'draft': draft,
                'scheduled': scheduled,
                'published': published,
                'avg_score': round(avg_score, 1)
            }
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {
                'total': 0,
                'draft': 0,
                'scheduled': 0,
                'published': 0,
                'avg_score': 0
            }

    def get_recent_published(self, n=10):
        """Get N most recent published posts"""
        try:
            published = self.get_posts(status='published')
            # Sort by published_date (descending)
            published.sort(key=lambda x: x.get('published_date', ''), reverse=True)
            return published[:n]
        except Exception as e:
            print(f"❌ Error getting recent published: {e}")
            return []


# Global instance
_manager = None

def get_queue_manager():
    """Get global NotionQueueManager instance"""
    global _manager
    if _manager is None:
        _manager = NotionQueueManager()
    return _manager


# Test
if __name__ == "__main__":
    import sys

    print("\n🧪 Testing Notion Queue Manager...")

    api_key = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")

    if not api_key or not database_id:
        print("❌ Set NOTION_API_KEY and NOTION_DATABASE_ID in .env")
        sys.exit(1)

    manager = NotionQueueManager(api_key, database_id)

    print("\n📊 Queue Statistics:")
    stats = manager.get_statistics()
    print(f"Total: {stats['total']}")
    print(f"Draft: {stats['draft']}")
    print(f"Scheduled: {stats['scheduled']}")
    print(f"Published: {stats['published']}")
    print(f"Avg Score: {stats['avg_score']}/100")

    print("\n✅ Notion Queue Manager works!")
