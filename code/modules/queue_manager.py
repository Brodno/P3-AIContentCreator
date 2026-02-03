"""
Queue Manager - Manage post queue with statuses
Statuses: draft, scheduled, published, archived
"""
import json
import os
from datetime import datetime
from pathlib import Path

QUEUE_FILE = "post_queue.json"

class QueueManager:
    """Manage post queue with statuses"""

    def __init__(self, queue_dir=None):
        if queue_dir is None:
            queue_dir = Path(__file__).parent.parent / "data"

        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(exist_ok=True, parents=True)
        self.queue_file = self.queue_dir / QUEUE_FILE

        self.queue = self._load_queue()

    def _load_queue(self):
        """Load queue from JSON file"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading queue: {e}")
                return []
        return []

    def _save_queue(self):
        """Save queue to JSON file"""
        try:
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(self.queue, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving queue: {e}")

    def add_post(self, topic, content, score, status="draft", scheduled_date=None):
        """
        Add new post to queue

        Args:
            topic: Post topic
            content: Post content
            score: Quality score
            status: draft/scheduled/published
            scheduled_date: Date for scheduled posts (YYYY-MM-DD)

        Returns:
            str: Post ID
        """
        post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        post = {
            'id': post_id,
            'topic': topic,
            'content': content,
            'score': score,
            'status': status,
            'created_at': datetime.now().isoformat(),
            'scheduled_date': scheduled_date,
            'published_date': None
        }

        self.queue.append(post)
        self._save_queue()

        return post_id

    def get_posts(self, status=None):
        """
        Get posts filtered by status

        Args:
            status: Filter by status (None = all)

        Returns:
            list: Filtered posts
        """
        if status is None:
            return self.queue

        return [p for p in self.queue if p['status'] == status]

    def get_post(self, post_id):
        """Get single post by ID"""
        for post in self.queue:
            if post['id'] == post_id:
                return post
        return None

    def update_status(self, post_id, new_status, scheduled_date=None):
        """
        Update post status

        Args:
            post_id: Post ID
            new_status: New status
            scheduled_date: Date for scheduled posts
        """
        for post in self.queue:
            if post['id'] == post_id:
                post['status'] = new_status

                if new_status == 'scheduled' and scheduled_date:
                    post['scheduled_date'] = scheduled_date

                if new_status == 'published':
                    post['published_date'] = datetime.now().isoformat()

                self._save_queue()
                return True

        return False

    def delete_post(self, post_id):
        """Delete post from queue"""
        self.queue = [p for p in self.queue if p['id'] != post_id]
        self._save_queue()

    def get_statistics(self):
        """Get queue statistics"""
        total = len(self.queue)
        draft = len([p for p in self.queue if p['status'] == 'draft'])
        scheduled = len([p for p in self.queue if p['status'] == 'scheduled'])
        published = len([p for p in self.queue if p['status'] == 'published'])

        scores = [p['score'] for p in self.queue if 'score' in p]
        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            'total': total,
            'draft': draft,
            'scheduled': scheduled,
            'published': published,
            'avg_score': round(avg_score, 1)
        }

    def get_scheduled_posts(self):
        """Get posts scheduled, sorted by date"""
        scheduled = [p for p in self.queue if p['status'] == 'scheduled']
        scheduled.sort(key=lambda x: x.get('scheduled_date', ''))
        return scheduled

    def get_recent_published(self, n=10):
        """Get N most recent published posts"""
        published = [p for p in self.queue if p['status'] == 'published']
        published.sort(key=lambda x: x.get('published_date', ''), reverse=True)
        return published[:n]


# Global instance
_manager = None

def get_queue_manager():
    """Get global QueueManager instance"""
    global _manager
    if _manager is None:
        _manager = QueueManager()
    return _manager


# Test
if __name__ == "__main__":
    manager = QueueManager()

    print("\n📊 Queue Statistics:")
    stats = manager.get_statistics()
    print(f"Total: {stats['total']}")
    print(f"Draft: {stats['draft']}")
    print(f"Scheduled: {stats['scheduled']}")
    print(f"Published: {stats['published']}")
    print(f"Avg Score: {stats['avg_score']}/100")
