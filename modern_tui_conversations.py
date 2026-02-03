import time
import json
from pathlib import Path


def conversations_file_path():
    return Path(__file__).resolve().parent / 'conversations.json'


def load_conversations():
    p = conversations_file_path()
    try:
        if p.exists():
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('conversations', [])
    except Exception:
        pass
    return []


def save_conversations(conv_list):
    p = conversations_file_path()
    try:
        with open(p, 'w', encoding='utf-8') as f:
            json.dump({'conversations': conv_list}, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def create_conversation(conv_list, title: str = 'New Conversation'):
    new = {'id': str(uuid.uuid4())[:8], 'title': title, 'messages': [], 'last_updated': time.time()}
    conv_list.insert(0, new)
    save_conversations(conv_list)
    return new
