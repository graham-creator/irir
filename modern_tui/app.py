from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Input, Button, Label, Markdown, Select
try:
    from textual.widgets import TextArea
except Exception:
    TextArea = None
try:
    from textual.widgets import Spinner
except Exception:
    Spinner = None
from textual import work
import ollama
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# Local package modules
from .utils import extract_youtube_id, sanitize_id
from . import workers, compare, conversations as convs, smoke
from .sidebar import Sidebar
from .welcome_screen import WelcomeScreen

import time
from pathlib import Path
import json
import uuid
import re
import tempfile
import subprocess
import os
import threading
import difflib
import sys
import asyncio
import logging

# Configure logging to file for unhandled exceptions and diagnostics
LOG_FILE = Path(__file__).resolve().parent / 'modern_tui_error.log'
LOG_LEVEL = os.environ.get("MODERN_TUI_LOG_LEVEL", "ERROR").upper()
logging.basicConfig(
    filename=str(LOG_FILE),
    level=getattr(logging, LOG_LEVEL, logging.ERROR),
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
)


def _log_unhandled_exception(exc_type, exc_value, exc_traceback):
    # Allow keyboard interrupts to exit normally
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def _log_exception(context: str, exc: Exception) -> None:
    logging.error("Error in %s: %s", context, exc, exc_info=exc)

# Register global exception hook
sys.excepthook = _log_unhandled_exception

# Threading exception hook (Python 3.8+)
def _thread_excepthook(args):
    try:
        logging.error("Uncaught thread exception", exc_info=(args.exc_type, args.exc_value, args.exc_traceback))
    except Exception:
        pass

try:
    threading.excepthook = _thread_excepthook
except Exception:
    pass

# asyncio loop exception handler
try:
    loop = asyncio.get_event_loop()
    def _async_exc_handler(loop, context):
        try:
            logging.error("Unhandled asyncio exception: %s", context)
        except Exception:
            pass
    loop.set_exception_handler(_async_exc_handler)
except Exception:
    pass


class AIClient(App):
    CSS = """
#main { height: 1fr; }
#home { height: 1fr; }

Screen {
    background: #000;
    color: #fff;
}

#conversations {
    width: 28%;
    min-width: 16;
    background: #0a0a0a;
    border-right: solid #222;
    opacity: 1;
}

#conv-list {
    height: 1fr;
    overflow-y: auto;
}

#chat-history {
    height: 1fr;
    overflow-y: auto;
    padding: 1;
}

#input-area {
    height: 3;
}

.user-msg { color: #fff; }
.ai-msg { color: #fff; }

.system-msg { color: #f33; }
.error-msg { color: #f66; }

#tab-bar {
    background: #0b0b0b;
    overflow-x: auto;
    border-bottom: solid #300;
    height: 3;
    opacity: 1;
}

.tab-btn {
    background: #111;
    color: #fff;
    border: solid #500;
    margin: 0 1;
}

.tab-btn.active {
    background: #300;
    color: #fff;
}

#home {
    align: center middle;
    background: #000;
}

#home-card {
    background: #0b0b0b;
    border: solid #500;
    padding: 1 2;
    width: 90%;
    max-width: 80;
}

#home-title {
    color: #fff;
    text-style: bold;
}

#home-subtitle {
    color: #f33;
    padding-top: 1;
}

#home-copy {
    color: #ddd;
    padding-top: 1;
}

#home-hints {
    color: #aaa;
    padding-top: 1;
}

/* Start hidden */
#controls,
#main,
#input-area {
    display: none;
}

#controls {
    overflow-x: auto;
}

#sidebar {
    width: 40;
    min-width: 24;
}

"""

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="tab-bar"):
            yield Button("Home", id="tab-home", classes="tab-btn active")
            yield Button("Chat", id="tab-chat", classes="tab-btn")

        with Vertical(id="home"):
            with Vertical(id="home-card"):
                yield Label("Home", id="home-title")
                yield Label("Black · Red · White", id="home-subtitle")
                yield Label(
                    "Open your workspace, review conversations, or jump into chat.",
                    id="home-copy",
                )
                yield Label(
                    "Use the tabs above to switch views.",
                    id="home-hints",
                )

        # === EXISTING UI (UNCHANGED) ===

        # Top Bar
        with Horizontal(id="controls"):
            yield Select([], prompt="Select Model", id="model-selector")
            yield Select(
                [
                    ("Summarize & Append", "summarize_append"),
                    ("Append Full", "append_full"),
                    ("Summarize Only", "summarize_only"),
                    ("Replace Input", "replace_summary"),
                ],
                prompt="YT Action",
                id="yt-action",
            )
            yield Button("Pull Transcript", id="btn-yt")

        # Main area
        with Horizontal(id="main"):
            with Vertical(id="conversations"):
                yield Label("Conversations", id="conv-title-label")
                yield Input(placeholder="Search...", id="conv-search")
                yield ScrollableContainer(id="conv-list")
                with Horizontal():
                    yield Button("New", id="create-conv")
                    yield Button("Rename", id="rename-conv")
                    yield Button("Delete", id="delete-conv")
                    yield Button("Export", id="export-conv")
                    yield Button("Import", id="import-conv")

            yield ScrollableContainer(id="chat-history")
            yield Sidebar(id="sidebar")

        # Input area
        with Vertical(id="input-area"):
            yield Input(
                placeholder="Type a message (or YouTube URL)...",
                id="user-input",
            )
            with Horizontal():
                yield Button("Send", id="send-btn", variant="primary")
                yield Button("Send to Selected", id="send-selected")

        yield Footer()

    def _set_active_tab(self, tab_id: str):
        for btn_id in ("tab-home", "tab-chat"):
            try:
                btn = self.query_one(f"#{btn_id}")
                if btn_id == tab_id:
                    btn.add_class("active")
                else:
                    btn.remove_class("active")
            except Exception:
                pass

    def show_home(self, user_action: bool = False):
        if user_action:
            self._tab_override = True
        self._active_tab = "home"
        try:
            self.query_one("#home").display = True
        except Exception:
            pass
        for id_ in ("controls", "main", "input-area"):
            try:
                self.query_one(f"#{id_}").display = False
            except Exception:
                pass
        self._set_active_tab("tab-home")

    def show_chat(self, user_action: bool = False):
        if user_action:
            self._tab_override = True
        self._active_tab = "chat"
        try:
            self.query_one("#home").display = False
        except Exception:
            pass
        for id_ in ("controls", "main", "input-area"):
            try:
                self.query_one(f"#{id_}").display = True
            except Exception:
                pass
        if not getattr(self, "_chat_reveal_done", False):
            self._chat_reveal_done = True
            try:
                asyncio.create_task(self._animate_chat_reveal())
            except Exception:
                pass
        self._set_active_tab("tab-chat")
        self._update_welcome_screen()
        try:
            self.query_one("#user-input").focus()
        except Exception:
            pass



    def extract_youtube_id(self, url: str):
        """Delegate to utils.extract_youtube_id for clarity and testability."""
        try:
            return extract_youtube_id(url)
        except Exception:
            return None

    async def _animate_chat_reveal(self):
        try:
            tab_bar = self.query_one("#tab-bar")
            conversations = self.query_one("#conversations")
        except Exception:
            return
        try:
            tab_bar.opacity = 0
            conversations.opacity = 0
            await tab_bar.animate("opacity", 1.0, duration=0.25)
            await conversations.animate("opacity", 1.0, duration=0.35)
        except Exception:
            pass

    @work(thread=True)
    def populate_models(self):
        """Background worker to fetch available models from Ollama and update the Select."""
        try:
            models = workers.list_models()
        except Exception as e:
            _log_exception("populate_models", e)
            models = []

        def _replace():
            try:
                parent = self.query_one("#controls")
                old = self.query_one("#model-selector")
                old.remove()
                options = [(m['name'], m['name']) for m in models] or [("llama3", "llama3")]
                parent.mount(Select(options, prompt="Select Model", id="model-selector"))
            except Exception:
                pass

        # Update UI in main thread
        try:
            self.call_from_thread(_replace)
        except Exception:
            # Fallback: ignore if call_from_thread unavailable
            _replace()

    async def on_mount(self):
        # populate models without blocking UI
        self.populate_models()
        # state for summary preview/interaction
        self._last_summary = None
        self._last_summary_widgets = []
        # spinner control flag
        self._spinner_running = False
        # Conversations state
        self._conversations = []
        self._current_conv_id = None
        self._show_agents = False
        self._awaiting_editor_key = False
        # multi-model send state
        self._selected_models = set()
        self._send_multi_mode = False
        self.load_conversations()
        self.render_conversation_list()
        # ensure there is at least one conversation selected
        if not self._current_conv_id and self._conversations:
            self.select_conversation(self._conversations[0]['id'])
        self._active_tab = None
        self._tab_override = False
        self._chat_reveal_done = False
        self.update_splash_visibility()

        # Support smoke test mode (non-network): run a simulated multi-model send then exit
        try:
            if '--smoke' in sys.argv or os.environ.get('SMOKE_TEST'):
                # schedule the smoke test to run in the event loop after mount
                asyncio.create_task(self.run_smoke_test())
        except Exception:
            pass

    @work(thread=True)
    def _spinner_worker(self, message: str):
        """Background spinner that updates a small spinner+label in the chat area while long tasks run."""
        self._spinner_running = True
        chat_box = self.query_one("#chat-history")
        spinner_id = "summarize-spinner"
        frames = ["|", "/", "-", "\\"]

        def _mount():
            try:
                existing = self.query_one(f"#{spinner_id}")
                existing.remove()
            except Exception:
                pass
            # Use native Spinner if available for better visuals
            if 'Spinner' in globals() and Spinner:
                container = Horizontal(id=spinner_id)
                try:
                    container.mount(Spinner())
                except Exception:
                    # If Spinner fails to mount, fall back to a label inside container
                    container.mount(Label(message, id=f"{spinner_id}-label", classes="system-msg"))
                else:
                    container.mount(Label(message, id=f"{spinner_id}-label", classes="system-msg"))
                chat_box.mount(container)
            else:
                chat_box.mount(Label(f"{message}", id=spinner_id, classes="system-msg"))

        try:
            self.call_from_thread(_mount)
        except Exception:
            _mount()

        idx = 0
        while self._spinner_running:
            ch = frames[idx % len(frames)]
            def _upd(ch=ch):
                try:
                    if 'Spinner' in globals() and Spinner:
                        lbl = self.query_one(f"#{spinner_id}-label")
                        lbl.update(f"{message} {ch}")
                    else:
                        lbl = self.query_one(f"#{spinner_id}")
                        lbl.update(f"{message} {ch}")
                except Exception:
                    pass
            try:
                self.call_from_thread(_upd)
            except Exception:
                _upd()
            time.sleep(0.12)
            idx += 1

        def _remove():
            try:
                node = self.query_one(f"#{spinner_id}")
                node.remove()
            except Exception:
                pass
        try:
            self.call_from_thread(_remove)
        except Exception:
            _remove()

    @work
    async def get_ai_response(self, user_text, model_name, turn_id: str = None):
        """Background worker to fetch AI response without freezing UI. Supports being called concurrently for different models."""
        chat_box = self.query_one("#chat-history")
        # Show model label so responses are clearly attributable
        try:
            await chat_box.mount(Label(f"{model_name}:", classes="system-msg"))
        except Exception:
            pass
        
        # Check for a YouTube link and extract video id safely
        vid_id = self.extract_youtube_id(user_text)
        if vid_id:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(vid_id)
                full_text = " ".join([i.get('text', '') for i in transcript])
                user_text = f"Analyze this YouTube video transcript: {full_text[:3000]}..."  # limit length
                await chat_box.mount(Label(f"System: Fetched YouTube Transcript!", classes="system-msg"))
            except Exception as e:
                await chat_box.mount(Label(f"Error fetching transcript: {e}", classes="error-msg"))

        # Send to Ollama (guard API errors)
        try:
            stream = ollama.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': user_text}],
                stream=True,
            )
        except Exception as e:
            _log_exception("ollama.chat", e)
            await chat_box.mount(Label(f"Error contacting model {model_name}: {e}", classes="error-msg"))
            return

        # Stream the response into a Markdown widget. If part of a grouped turn, update the group-specific widget.
        sanitized = self._sanitize_id(model_name)
        if turn_id:
            placeholder_id = f"resp-{turn_id}-{sanitized}"
            try:
                new_msg = self.query_one(f"#{placeholder_id}")
            except Exception:
                new_msg = Markdown("")
                try:
                    await chat_box.mount(new_msg)
                except Exception:
                    pass
        else:
            new_msg = Markdown("")
            await chat_box.mount(new_msg)

        chunked_text = ""
        last_update = time.monotonic()
        last_len = 0
        try:
            # Try sync iterator first
            try:
                iterator = iter(stream)
                for chunk in iterator:
                    part = (chunk.get('message') or {}).get('content', '')
                    if not part:
                        continue
                    chunked_text += part
                    if time.monotonic() - last_update > 0.15 or len(chunked_text) - last_len > 200:
                        new_msg.update(chunked_text)
                        last_update = time.monotonic()
                        last_len = len(chunked_text)
                new_msg.update(chunked_text)
            except TypeError:
                # async iterable
                async for chunk in stream:
                    part = (chunk.get('message') or {}).get('content', '')
                    if not part:
                        continue
                    chunked_text += part
                    if time.monotonic() - last_update > 0.15 or len(chunked_text) - last_len > 200:
                        new_msg.update(chunked_text)
                        last_update = time.monotonic()
                        last_len = len(chunked_text)
                new_msg.update(chunked_text)
        except Exception as e:
            await chat_box.mount(Label(f"Error streaming response: {e}", classes="error-msg"))

        # Save assistant response to conversation (include model metadata and turn id)
        try:
            conv = next((c for c in self._conversations if c['id'] == self._current_conv_id), None)
            if conv is not None:
                msg = {'role': 'assistant', 'content': chunked_text, 'model': model_name}
                if turn_id:
                    msg['turn_id'] = turn_id
                conv.setdefault('messages', []).append(msg)
                conv['last_updated'] = time.time()
                self.save_conversations()
                self.render_conversation_list()
        except Exception:
            pass

    def summarize_text(self, text: str, model_name: str) -> str:
        """Delegate summarization to helpers for easier testing and navigation."""
        try:
            return workers.summarize_text(self, text, model_name)
        except Exception:
            return "(Error summarizing)"

    # ---- Conversation persistence and UI helpers ----
    def _conversations_file_path(self):
        p = Path(__file__).resolve().parent / 'conversations.json'
        return p

    def load_conversations(self):
        p = self._conversations_file_path()
        try:
            if p.exists():
                with open(p, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._conversations = data.get('conversations', [])
                    self._current_conv_id = data.get('current')
            else:
                self._conversations = []
                self._current_conv_id = None
        except Exception:
            self._conversations = []
            self._current_conv_id = None

    def save_conversations(self):
        p = self._conversations_file_path()
        data = {'conversations': self._conversations, 'current': self._current_conv_id}
        try:
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def render_conversation_list(self):
        try:
            conv_list = self.query_one('#conv-list')
            # clear
            for child in list(getattr(conv_list, 'children', [])):
                try:
                    child.remove()
                except Exception:
                    pass
            # mount buttons (show last-updated if present), apply search filter
            q = getattr(self, '_conv_search', '') or ''
            for conv in sorted(self._conversations, key=lambda c: c.get('last_updated', 0), reverse=True):
                title = conv.get('title', 'Untitled')
                if q and q.lower() not in title.lower():
                    continue
                ts = conv.get('last_updated')
                if ts:
                    try:
                        s = time.strftime('%Y-%m-%d %H:%M', time.localtime(ts))
                        label = f"{title}  ({s})"
                    except Exception:
                        label = title
                else:
                    label = title
                btn = Button(label, id=f"conv-{conv['id']}", classes="conv-btn")
                conv_list.mount(btn)
            # remove any lingering context menu
            try:
                self.query_one('#conv-context').remove()
            except Exception:
                pass
        except Exception:
            pass

    def _create_conversation_obj(self, title=None):
        cid = str(uuid.uuid4())[:8]
        return {
            'id': cid,
            'title': title or f"Conversation {len(self._conversations)+1}",
            'messages': [],
            'last_updated': time.time(),
            'model': 'llama3'
        }

    def create_conversation(self):
        conv = self._create_conversation_obj()
        self._conversations.append(conv)
        self.save_conversations()
        self.render_conversation_list()
        self.select_conversation(conv['id'])
        self.update_splash_visibility()

    def select_conversation(self, conv_id: str):
        conv = next((c for c in self._conversations if c['id'] == conv_id), None)
        if not conv:
            return
        self._current_conv_id = conv_id
        # update chat title label
        try:
            title_lbl = self.query_one('#conv-title')
            title_lbl.update(conv.get('title', ''))
        except Exception:
            # not mounted yet; mount at top of chat
            try:
                ch = self.query_one('#chat-history')
                ch.mount(Label(conv.get('title', ''), id='conv-title'))
            except Exception:
                pass
        # load messages
        try:
            chat_box = self.query_one('#chat-history')
            # remove previous message widgets
            for child in list(getattr(chat_box, 'children', [])):
                try:
                    child.remove()
                except Exception:
                    pass
            for msg in conv.get('messages', []):
                    role = msg.get('role')
                    content = msg.get('content')
                    if role == 'user':
                        chat_box.mount(Label(f"You: {content}", classes='user-msg'))
                    else:
                        chat_box.mount(Markdown(content))
        except Exception:
            pass
        # Update splash visibility depending on messages
        try:
            self.update_splash_visibility()
            self._update_welcome_screen()
        except Exception:
            pass

    def delete_conversation(self, conv_id: str):
        self._conversations = [c for c in self._conversations if c['id'] != conv_id]
        if self._current_conv_id == conv_id:
            self._current_conv_id = self._conversations[0]['id'] if self._conversations else None
        self.save_conversations()
        self.render_conversation_list()
        if self._current_conv_id:
            self.select_conversation(self._current_conv_id)
        else:
            # clear chat
            try:
                chat_box = self.query_one('#chat-history')
                for child in list(getattr(chat_box, 'children', [])):
                    try:
                        child.remove()
                    except Exception:
                        pass
            except Exception:
                pass

    def start_rename(self):
        # mount an input in the conversations sidebar for renaming
        try:
            conv = next((c for c in self._conversations if c['id'] == self._current_conv_id), None)
            if not conv:
                return
            conv_list = self.query_one('#conversations')
            # remove existing rename widget if any
            try:
                existing = self.query_one('#rename-input')
                existing.remove()
            except Exception:
                pass
            inp = Input(value=conv.get('title',''), id='rename-input')
            btns = Horizontal()
            btns.mount(Button('Save', id='save-rename'))
            btns.mount(Button('Cancel', id='cancel-rename'))
            conv_list.mount(inp)
            conv_list.mount(btns)
        except Exception:
            pass

    def finish_rename(self, new_title: str):
        conv = next((c for c in self._conversations if c['id'] == self._current_conv_id), None)
        if not conv:
            return
        conv['title'] = new_title
        self.save_conversations()
        self.render_conversation_list()
        # update title label if present
        try:
            title_lbl = self.query_one('#conv-title')
            title_lbl.update(new_title)
        except Exception:
            pass

    def export_conversation(self, conv_id: str):
        conv = next((c for c in self._conversations if c['id'] == conv_id), None)
        if not conv:
            return
        p = Path(__file__).resolve().parent / f"conv_{conv_id}.json"
        try:
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(conv, f, indent=2)
            chat_box = self.query_one('#chat-history')
            chat_box.mount(Label(f"Exported conversation to {p.name}", classes='system-msg'))
        except Exception as e:
            try:
                chat_box = self.query_one('#chat-history')
                chat_box.mount(Label(f"Error exporting: {e}", classes='error-msg'))
            except Exception:
                pass
        finally:
            self.render_conversation_list()
    def import_conversation(self, file_path: str):
        p = Path(file_path)
        try:
            with open(p, 'r', encoding='utf-8') as f:
                conv = json.load(f)
            if 'id' not in conv:
                conv['id'] = str(uuid.uuid4())[:8]
            conv['last_updated'] = time.time()
            conv.setdefault('messages', [])
            if 'model' not in conv:
                conv['model'] = 'llama3'
            self._conversations.append(conv)
            self.save_conversations()
            self.render_conversation_list()
            self.select_conversation(conv['id'])
            chat_box = self.query_one('#chat-history')
            chat_box.mount(Label(f"Imported conversation from {p.name}", classes='system-msg'))
        except Exception as e:
            try:
                chat_box = self.query_one('#chat-history')
                chat_box.mount(Label(f"Error importing: {e}", classes='error-msg'))
            except Exception:
                pass

    # ---- Helpers: sanitizers, model listing, agents UI ----
    def _sanitize_id(self, name: str) -> str:
        try:
            return sanitize_id(name)
        except Exception:
            return re.sub(r"[^0-9a-zA-Z_-]", "_", name)

    def list_models(self):
        try:
            return workers.list_models()
        except Exception as e:
            _log_exception("list_models", e)
            return []

    def show_import_picker(self):
        """Show a simple file picker listing JSON files in program folder for importing."""
        try:
            p = Path(__file__).resolve().parent
            files = sorted([x.name for x in p.glob('*.json')])
            picker = Vertical(id='import-picker')
            picker.mount(Label('Import conversation from file:', classes='system-msg'))
            for fn in files:
                btn = Button(fn, id=f"pick-{self._sanitize_id(fn)}")
                picker.mount(btn)
            picker.mount(Button('Cancel', id='cancel-import'))
            # mount modal-like in main area
            try:
                self.query_one('#main').mount(picker)
            except Exception:
                try:
                    self.query_one('#chat-history').mount(picker)
                except Exception:
                    pass
        except Exception:
            try:
                self.query_one('#chat-history').mount(Label('Error showing import picker.', classes='error-msg'))
            except Exception:
                pass

    def _render_models_in_agents(self, panel):
        try:
            # clear existing model rows
            for child in list(getattr(panel, 'children', [])):
                try:
                    if getattr(child, 'id', '') and child.id.startswith('model-row-'):
                        child.remove()
                except Exception:
                    pass
            models = self.list_models()
            for m in models:
                name = m.get('name') or str(m)
                sid = self._sanitize_id(name)
                row = Horizontal(id=f"model-row-{sid}")
                row.mount(Label(name))
                row.mount(Button('Pull', id=f"pull-{sid}"))
                row.mount(Button('Delete', id=f"delete-{sid}"))
                row.mount(Button('Use', id=f"use-{sid}"))
                # Include / exclude for multi-send
                sel_label = 'Included' if name in self._selected_models else 'Include'
                row.mount(Button(sel_label, id=f"select-{sid}"))
                panel.mount(row)
        except Exception:
            pass

    def show_delete_confirm(self, kind: str, name: str):
        """Show a confirmation box for deleting a model or conversation.
        kind: 'model' or 'conv'
        name: model name (for model) or conv id (for conv)
        """
        try:
            # remove existing confirm
            try:
                self.query_one('#delete-confirm').remove()
            except Exception:
                pass
            box = Vertical(id='delete-confirm')
            if kind == 'model':
                box.mount(Label(f"Confirm delete model: {name}?"))
            else:
                # conv id to title lookup
                conv = next((c for c in self._conversations if c['id'] == name), None)
                box.mount(Label(f"Confirm delete conversation: {conv.get('title','?')}?"))
            btns = Horizontal()
            btns.mount(Button('Confirm Delete', id=f'confirm-delete-{kind}-{self._sanitize_id(str(name))}'))
            btns.mount(Button('Cancel', id='cancel-delete'))
            box.mount(btns)
            # mount near conversations area
            try:
                self.query_one('#conversations').mount(box)
            except Exception:
                try:
                    self.query_one('#chat-history').mount(box)
                except Exception:
                    pass
            self._pending_delete = {'kind': kind, 'name': name}
        except Exception:
            pass

    def cancel_delete_confirm(self):
        try:
            self._pending_delete = None
            try:
                self.query_one('#delete-confirm').remove()
            except Exception:
                pass
        except Exception:
            pass

    def perform_confirm_delete(self):
        try:
            if not getattr(self, '_pending_delete', None):
                return
            kind = self._pending_delete.get('kind')
            name = self._pending_delete.get('name')
            if kind == 'model':
                # map sanitized name back to model name
                models = self.list_models()
                for m in models:
                    nm = m.get('name') or str(m)
                    if self._sanitize_id(nm) == self._sanitize_id(str(name)):
                        self.delete_model(nm)
                        break
            else:
                # conversation delete
                self.delete_conversation(name)
            self.cancel_delete_confirm()
        except Exception:
            pass

    def show_conv_context(self, conv_id: str):
        try:
            # remove existing
            try:
                self.query_one('#conv-context').remove()
            except Exception:
                pass
            ctx = Vertical(id='conv-context')
            ctx.mount(Button('Rename', id=f'ctx-rename-{conv_id}', classes='ctx-btn'))
            ctx.mount(Button('Delete', id=f'ctx-delete-{conv_id}', classes='ctx-btn'))
            ctx.mount(Button('Export', id=f'ctx-export-{conv_id}', classes='ctx-btn'))
            ctx.mount(Button('Cancel', id=f'ctx-cancel', classes='ctx-btn'))
            try:
                self.query_one('#conversations').mount(ctx)
            except Exception:
                try:
                    self.query_one('#chat-history').mount(ctx)
                except Exception:
                    pass
        except Exception:
            pass

    def hide_conv_context(self):
        try:
            try:
                self.query_one('#conv-context').remove()
            except Exception:
                pass
        except Exception:
            pass

    def refresh_models_panel(self):
        try:
            panel = self.query_one('#agents-panel')
            # add a refresh indicator
            try:
                panel.query_one('#models-refresh-msg').remove()
            except Exception:
                pass
            panel.mount(Label('Refreshing models...', id='models-refresh-msg', classes='system-msg'))
            try:
                self._render_models_in_agents(panel)
            finally:
                try:
                    panel.query_one('#models-refresh-msg').remove()
                except Exception:
                    pass
        except Exception:
            pass

    @work(thread=True)
    def pull_model(self, model_name: str):
        chat_box = self.query_one('#chat-history')
        sid = self._sanitize_id(model_name)
        # show per-model op indicator
        try:
            panel = self.query_one('#agents-panel')
            try:
                panel.mount(Label(f"Pulling {model_name}...", id=f"model-op-{sid}", classes='system-msg'))
            except Exception:
                pass
        except Exception:
            pass
        try:
            # best effort call - may vary by ollama client
            try:
                ollama.pull(model_name)
                chat_box.mount(Label(f"Pulled model {model_name}", classes='system-msg'))
            except Exception as e:
                chat_box.mount(Label(f"Error pulling model {model_name}: {e}", classes='error-msg'))
        except Exception:
            pass
        finally:
            try:
                if panel:
                    try:
                        panel.query_one(f"#model-op-{sid}").remove()
                    except Exception:
                        pass
            except Exception:
                pass

    @work(thread=True)
    def delete_model(self, model_name: str):
        chat_box = self.query_one('#chat-history')
        sid = self._sanitize_id(model_name)
        try:
            panel = self.query_one('#agents-panel')
            try:
                panel.mount(Label(f"Deleting {model_name}...", id=f"model-op-{sid}", classes='system-msg'))
            except Exception:
                pass
        except Exception:
            pass
        try:
            try:
                ollama.delete(model_name)
                chat_box.mount(Label(f"Deleted model {model_name}", classes='system-msg'))
            except Exception as e:
                chat_box.mount(Label(f"Error deleting model {model_name}: {e}", classes='error-msg'))
        except Exception:
            pass
        finally:
            try:
                if panel:
                    try:
                        panel.query_one(f"#model-op-{sid}").remove()
                    except Exception:
                        pass
            except Exception:
                pass

    # (duplicate delete_model removed; use the earlier threaded implementation that reports per-panel progress)
    def set_conversation_model(self, model_name: str):
        try:
            conv = next((c for c in self._conversations if c['id'] == self._current_conv_id), None)
            if conv is None:
                return
            conv['model'] = model_name
            self.save_conversations()
            self.render_conversation_list()
            self.query_one('#chat-history').mount(Label(f"System: Set conversation model to {model_name}", classes='system-msg'))
        except Exception:
            pass

    @work(thread=True)
    def fetch_and_process_transcript(self, url: str, action: str, model_name: str):
        """Delegate transcript fetch and summary workflow to helper functions."""
        chat_box = self.query_one("#chat-history")
        vid_id = self.extract_youtube_id(url)
        if not vid_id:
            def _err():
                chat_box.mount(Label("Error: No YouTube URL found in input.", classes="error-msg"))
            try:
                self.call_from_thread(_err)
            except Exception:
                _err()
            return

        try:
            full_text = workers.fetch_transcript(vid_id)
        except Exception as e:
            def _err():
                chat_box.mount(Label(f"Error fetching transcript: {e}", classes="error-msg"))
            try:
                self.call_from_thread(_err)
            except Exception:
                _err()
            return

        if action == "append_full":
            excerpt = full_text[:3000]
            append_text = f"\n\n[YouTube Transcript excerpt]\n{excerpt}\n"

            def _update():
                inp = self.query_one("#user-input")
                inp.value = (inp.value or "") + append_text
                chat_box.mount(Label("System: Appended transcript to input.", classes="system-msg"))
                try:
                    conv = next((c for c in self._conversations if c['id'] == self._current_conv_id), None)
                    if conv is not None:
                        conv['last_updated'] = time.time()
                        self.save_conversations()
                        self.render_conversation_list()
                except Exception:
                    pass

            try:
                self.call_from_thread(_update)
            except Exception:
                _update()
            return

        if action in ("summarize_append", "summarize_only", "replace_summary"):
            # Produce hierarchical summary via workers.summarize_text and show preview
            try:
                threading.Thread(target=lambda: workers.spinner_worker(self, "Summarizing transcript"), daemon=True).start()
                final_summary = workers.summarize_text(self, full_text, model_name)
            except Exception as e:
                self._spinner_running = False
                def _err():
                    chat_box.mount(Label(f"Error summarizing transcript: {e}", classes="error-msg"))
                try:
                    self.call_from_thread(_err)
                except Exception:
                    _err()
                return
            finally:
                self._spinner_running = False

            self._last_summary = final_summary

            def _preview():
                md = Markdown(f"**Summary preview**\n\n{final_summary}")
                btns = Horizontal()
                btns.mount(Button("Edit Summary", id="edit-summary"))
                btns.mount(Button("Append Summary", id="append-summary"))
                btns.mount(Button("Replace Input", id="replace-summary"))
                btns.mount(Button("Cancel", id="cancel-summary"))
                chat_box.mount(md)
                chat_box.mount(btns)
                self._last_summary_widgets = [md, btns]
                chat_box.mount(Label("System: Summary ready. Choose an action.", classes="system-msg"))
                try:
                    conv = next((c for c in self._conversations if c['id'] == self._current_conv_id), None)
                    if conv is not None:
                        conv['last_updated'] = time.time()
                        self.save_conversations()
                        self.render_conversation_list()
                except Exception:
                    pass

            try:
                self.call_from_thread(_preview)
            except Exception:
                _preview()
            return

        # Unknown action
        def _err():
            chat_box.mount(Label("Error: Unknown action for transcript.", classes="error-msg"))
        try:
            self.call_from_thread(_err)
        except Exception:
            _err()

    # ---- Splash and UI helpers ----
    def create_response_group(self, turn_id: str, user_text: str, models: list):
        """Create an aggregated UI container for multi-model responses."""
        try:
            chat_box = self.query_one('#chat-history')
            group = Vertical(id=f'group-{turn_id}')
            header = Horizontal()
            header.mount(Label(f"You: {user_text}", classes='user-msg'))
            header.mount(Button('Compare', id=f'compare-{turn_id}'))
            group.mount(header)
            # mount placeholders for each model
            for m in models:
                sid = self._sanitize_id(m)
                row = Vertical(id=f'row-{turn_id}-{sid}')
                row.mount(Label(m, classes='system-msg'))
                md = Markdown('', id=f'resp-{turn_id}-{sid}')
                row.mount(md)
                group.mount(row)
            chat_box.mount(group)
            # track group
            self._groups = getattr(self, '_groups', {})
            self._groups[turn_id] = {'models': list(models)}
        except Exception:
            pass

    def update_splash_visibility(self):
        try:
            if getattr(self, "_tab_override", False):
                return
            conv = next((c for c in self._conversations if c['id'] == self._current_conv_id), None)
            has_msgs = bool(conv and conv.get('messages'))
            if has_msgs:
                self.show_chat()
            else:
                self.show_home()
        except Exception:
            pass

    def _update_welcome_screen(self):
        try:
            conv = next((c for c in self._conversations if c['id'] == self._current_conv_id), None)
            has_msgs = bool(conv and conv.get('messages'))
            chat_box = self.query_one("#chat-history")
            try:
                welcome = self.query_one("#welcome-screen")
            except Exception:
                welcome = None
            if has_msgs:
                if welcome is not None:
                    try:
                        welcome.remove()
                    except Exception:
                        pass
                return
            if welcome is None:
                try:
                    chat_box.mount(WelcomeScreen(id="welcome-screen"))
                except Exception:
                    pass
        except Exception:
            pass

    def toggle_agents(self):
        try:
            panel_exists = False
            try:
                self.query_one('#agents-panel')
                panel_exists = True
            except Exception:
                panel_exists = False
            if panel_exists:
                try:
                    self.query_one('#agents-panel').remove()
                except Exception:
                    pass
                self._show_agents = False
                return
            # create an agents panel with model management
            ap = Vertical(id='agents-panel')
            ap.mount(Label('Agents / Models', id='agents-title'))
            ap.mount(Button('Refresh Models', id='refresh-models'))
            ap.mount(Button('Select All Models', id='select-all-models'))
            # model list will be loaded dynamically
            self._render_models_in_agents(ap)
            try:
                self.query_one('#main').mount(ap)
            except Exception:
                # fallback: mount in chat
                try:
                    self.query_one('#chat-history').mount(ap)
                except Exception:
                    pass
            self._show_agents = True
        except Exception:
            pass

    async def run_smoke_test(self):
        """Delegate smoke test to modular helper (headless-friendly)."""
        try:
            return await smoke.run_smoke_test(self)
        except Exception:
            try:
                logging.exception("Smoke test failed")
            except Exception:
                pass
            return

    def show_commands_overlay(self):
        try:
            # if present remove and re-add to refresh
            try:
                self.query_one('#commands-overlay').remove()
            except Exception:
                pass
            co = Vertical(id='commands-overlay')
            co.mount(Label('Commands:'))
            co.mount(Label('Ctrl+X E  -> Open external editor'))
            co.mount(Label('Tab       -> Toggle agents'))
            co.mount(Label('Ctrl+P    -> This commands list'))
            try:
                self.query_one('#main').mount(co)
            except Exception:
                try:
                    self.query_one('#chat-history').mount(co)
                except Exception:
                    pass
            # auto-dismiss after 3s
            def _dismiss():
                time.sleep(3)
                try:
                    self.call_from_thread(lambda: self.query_one('#commands-overlay').remove())
                except Exception:
                    try:
                        self.query_one('#commands-overlay').remove()
                    except Exception:
                        pass
            threading.Thread(target=_dismiss, daemon=True).start()
        except Exception:
            pass

    @work(thread=True)
    def open_external_editor(self):
        try:
            inp = self.query_one('#user-input')
            initial = getattr(inp, 'value', '') or ''
            editor = os.environ.get('EDITOR', 'vi')
            with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.tmp') as tf:
                tf.write(initial)
                tf.flush()
                tfname = tf.name
            subprocess.run([editor, tfname])
            # read back
            with open(tfname, 'r', encoding='utf-8') as f:
                new_content = f.read()
            def _update():
                try:
                    inp = self.query_one('#user-input')
                    inp.value = new_content
                    self.query_one('#chat-history').mount(Label('System: Imported edits from external editor.', classes='system-msg'))
                except Exception:
                    pass
            try:
                self.call_from_thread(_update)
            except Exception:
                _update()
        except Exception as e:
            try:
                self.query_one('#chat-history').mount(Label(f'Error opening editor: {e}', classes='error-msg'))
            except Exception:
                pass

    # ---- Comparison & diff helpers ----
    def _get_response_text(self, turn_id: str, model_name: str) -> str:
        """Delegate to compare.get_response_text for clarity."""
        try:
            return compare.get_response_text(self, turn_id, model_name)
        except Exception:
            return ''

    def handle_compare(self, turn_id: str, m1: str = None, m2: str = None):
        """Delegate compare/diff handling to modular helper."""
        try:
            return compare.handle_compare(self, turn_id, m1=m1, m2=m2)
        except Exception:
            try:
                self.query_one('#chat-history').mount(Label('Error running comparison.', classes='error-msg'))
            except Exception:
                pass
            return

    def on_button_pressed(self, event):
        if event.button.id == "tab-home":
            self.show_home(user_action=True)
        elif event.button.id == "tab-chat":
            self.show_chat(user_action=True)
        elif event.button.id == "send-btn":
            inp = self.query_one("#user-input")
            user_text = inp.value
            selector = self.query_one("#model-selector")
            model = getattr(selector, "value", None) or "llama3" # Default fallback
            
            if user_text:
                # Append to UI
                self.query_one("#chat-history").mount(Label(f"You: {user_text}", classes="user-msg"))
                # Save to current conversation
                try:
                    conv = next((c for c in self._conversations if c['id'] == self._current_conv_id), None)
                    if conv is not None:
                        conv.setdefault('messages', []).append({'role': 'user', 'content': user_text})
                        conv['last_updated'] = time.time()
                        self.save_conversations()
                        self.render_conversation_list()
                except Exception:
                    pass
                # Ask AI
                self.get_ai_response(user_text, model)
                inp.value = ""
        elif event.button.id == "btn-yt":
            inp = self.query_one("#user-input")
            user_text = inp.value or ""
            if not user_text:
                self.query_one("#chat-history").mount(Label("Please paste a YouTube URL into the input first.", classes="error-msg"))
            else:
                # Determine desired action from selector and kick off background worker
                action_selector = self.query_one("#yt-action")
                action = getattr(action_selector, "value", None) or "summarize_append"
                selector = self.query_one("#model-selector")
                model = getattr(selector, "value", None) or "llama3"
                self.fetch_and_process_transcript(user_text, action, model)
        elif event.button.id == "send-selected":
            inp = self.query_one("#user-input")
            user_text = inp.value or ""
            if not user_text:
                self.query_one('#chat-history').mount(Label('Please enter a message to send.', classes='error-msg'))
            elif not self._selected_models:
                self.query_one('#chat-history').mount(Label('No models selected. Use the Agents panel to include models.', classes='error-msg'))
            else:
                # Show user message once
                self.query_one('#chat-history').mount(Label(f"You: {user_text}", classes='user-msg'))
                # Save to conversation
                try:
                    conv = next((c for c in self._conversations if c['id'] == self._current_conv_id), None)
                    if conv is not None:
                        conv.setdefault('messages', []).append({'role': 'user', 'content': user_text})
                        conv['last_updated'] = time.time()
                        self.save_conversations()
                        self.render_conversation_list()
                except Exception:
                    pass
                # Create a turn id and group UI for aggregated responses
                turn_id = str(uuid.uuid4())[:8]
                # attach turn id to user message
                try:
                    conv = next((c for c in self._conversations if c['id'] == self._current_conv_id), None)
                    if conv is not None:
                        conv.setdefault('messages', []).append({'role': 'user', 'content': user_text, 'turn_id': turn_id})
                        conv['last_updated'] = time.time()
                        self.save_conversations()
                        self.render_conversation_list()
                except Exception:
                    pass

                models_to_send = list(self._selected_models)
                # mount grouped UI
                try:
                    self.create_response_group(turn_id, user_text, models_to_send)
                except Exception:
                    pass

                # Send to each selected model (concurrently via work) and pass turn_id
                for mod in models_to_send:
                    try:
                        self.get_ai_response(user_text, mod, turn_id=turn_id)
                    except Exception:
                        try:
                            self.query_one('#chat-history').mount(Label(f'Error scheduling send to {mod}', classes='error-msg'))
                        except Exception:
                            pass
                inp.value = ""
        elif event.button.id == "create-conv":
            self.create_conversation()
        elif event.button.id == "delete-conv":
            if self._current_conv_id:
                # show confirmation first
                self.show_delete_confirm('conv', self._current_conv_id)
        elif event.button.id == "rename-conv":
            self.start_rename()
        elif event.button.id == "save-rename":
            try:
                inp = self.query_one('#rename-input')
                new_title = inp.value
                # cleanup rename widgets
                for child in list(getattr(self.query_one('#conversations'), 'children', [])):
                    try:
                        if getattr(child, 'id', '') in ('rename-input',):
                            child.remove()
                    except Exception:
                        pass
                for child in list(getattr(self.query_one('#conversations'), 'children', [])):
                    try:
                        # remove the Horizontal buttons group too if present
                        if isinstance(child, type(self.query_one('#conversations'))):
                            pass
                    except Exception:
                        pass
            except Exception:
                new_title = None
            if new_title:
                self.finish_rename(new_title)
        elif event.button.id == 'agent-build':
            try:
                self.query_one('#chat-history').mount(Label('System: Build agent triggered (mock).', classes='system-msg'))
            except Exception:
                pass
        elif event.button.id == 'agent-test':
            try:
                self.query_one('#chat-history').mount(Label('System: Test agent triggered (mock).', classes='system-msg'))
            except Exception:
                pass
        elif event.button.id == 'refresh-models':
            self.refresh_models_panel()
        elif event.button.id.startswith('pull-'):
            s = event.button.id.split('pull-')[1]
            # find model by sanitized name
            models = self.list_models()
            for m in models:
                name = m.get('name') or str(m)
                if self._sanitize_id(name) == s:
                    self.pull_model(name)
                    # refresh the panel after some delay
                    threading.Thread(target=lambda: (time.sleep(0.5), self.refresh_models_panel()), daemon=True).start()
                    break
        elif event.button.id.startswith('select-'):
            s = event.button.id.split('select-')[1]
            models = self.list_models()
            for m in models:
                name = m.get('name') or str(m)
                if self._sanitize_id(name) == s:
                    if name in self._selected_models:
                        self._selected_models.remove(name)
                        try:
                            btn = self.query_one(f"#select-{s}")
                            btn.update('Include')
                        except Exception:
                            pass
                    else:
                        self._selected_models.add(name)
                        try:
                            btn = self.query_one(f"#select-{s}")
                            btn.update('Included')
                        except Exception:
                            pass
                    break
        elif event.button.id == 'select-all-models':
            # select all available models
            try:
                models = self.list_models()
                for m in models:
                    name = m.get('name') or str(m)
                    self._selected_models.add(name)
                self.refresh_models_panel()
            except Exception:
                pass
        elif event.button.id.startswith('delete-'):
            s = event.button.id.split('delete-')[1]
            models = self.list_models()
            for m in models:
                name = m.get('name') or str(m)
                if self._sanitize_id(name) == s:
                    self.show_delete_confirm('model', name)
                    break
        elif event.button.id.startswith('use-'):
            s = event.button.id.split('use-')[1]
            models = self.list_models()
            for m in models:
                name = m.get('name') or str(m)
                if self._sanitize_id(name) == s:
                    self.set_conversation_model(name)
                    break
        elif event.button.id == 'cancel-delete':
            self.cancel_delete_confirm()
        elif event.button.id.startswith('confirm-delete-'):
            self.perform_confirm_delete()
        elif event.button.id.startswith('ctx-'):
            # context menu actions
            parts = event.button.id.split('-')
            action = parts[1]
            cid = '-'.join(parts[2:])
            if action == 'rename':
                self.hide_conv_context()
                self.select_conversation(cid)
                self.start_rename()
            elif action == 'delete':
                self.hide_conv_context()
                self.show_delete_confirm('conv', cid)
            elif action == 'export':
                self.hide_conv_context()
                self.export_conversation(cid)
            elif action == 'cancel':
                self.hide_conv_context()
        elif event.button.id.startswith('compare-'):
            # Compare button pressed for a grouped turn
            turn_id = event.button.id.split('compare-')[1]
            threading.Thread(target=lambda: self.handle_compare(turn_id), daemon=True).start()
        elif event.button.id.startswith('comparepair-'):
            # Compare pair request: comparepair-<turn>-<m1>-<m2>
            parts = event.button.id.split('-')
            turn_id = parts[1]
            m1 = parts[2]
            m2 = parts[3]
            threading.Thread(target=lambda: self.handle_compare(turn_id, m1, m2), daemon=True).start()
        elif event.button.id == "cancel-rename":
            # remove rename input if present
            try:
                for child in list(getattr(self.query_one('#conversations'), 'children', [])):
                    try:
                        if getattr(child, 'id', '') in ('rename-input',):
                            child.remove()
                    except Exception:
                        pass
            except Exception:
                pass
        elif event.button.id == "export-conv":
            if self._current_conv_id:
                self.export_conversation(self._current_conv_id)
        elif event.button.id == "import-conv":
            # show a simple in-app file picker to import conversation JSONs
            self.show_import_picker()
        elif event.button.id == 'cancel-import':
            try:
                self.query_one('#import-picker').remove()
            except Exception:
                pass
        elif event.button.id.startswith('pick-'):
            # figure out original filename from sanitized id
            sid = event.button.id.split('pick-')[1]
            try:
                p = Path(__file__).resolve().parent
                files = [x for x in p.glob('*.json')]
                target = None
                for f in files:
                    if self._sanitize_id(f.name) == sid:
                        target = f
                        break
                if target:
                    self.import_conversation(str(target))
                else:
                    self.query_one('#chat-history').mount(Label('Error: file not found.', classes='error-msg'))
            except Exception as e:
                try:
                    self.query_one('#chat-history').mount(Label(f'Import error: {e}', classes='error-msg'))
                except Exception:
                    pass
            try:
                self.query_one('#import-picker').remove()
            except Exception:
                pass
        elif event.button.id.startswith('conv-'):
            cid = event.button.id.split('conv-')[1]
            self.select_conversation(cid)
        elif event.button.id == "append-summary":
            # Append the last generated summary to input
            inp = self.query_one("#user-input")
            inp.value = (inp.value or "") + "\n\n" + (getattr(self, "_last_summary", "") or "")
            for w in getattr(self, "_last_summary_widgets", []):
                try:
                    w.remove()
                except Exception:
                    pass
            self._last_summary_widgets = []
            self.query_one("#chat-history").mount(Label("System: Appended summary to input.", classes="system-msg"))
        elif event.button.id == "replace-summary":
            inp = self.query_one("#user-input")
            inp.value = getattr(self, "_last_summary", "") or ""
            for w in getattr(self, "_last_summary_widgets", []):
                try:
                    w.remove()
                except Exception:
                    pass
            self._last_summary_widgets = []
            self.query_one("#chat-history").mount(Label("System: Replaced input with summary.", classes="system-msg"))
        elif event.button.id == "cancel-summary":
            for w in getattr(self, "_last_summary_widgets", []):
                try:
                    w.remove()
                except Exception:
                    pass
            self._last_summary_widgets = []
            self.query_one("#chat-history").mount(Label("System: Summary preview canceled.", classes="system-msg"))
        elif event.button.id == "edit-summary":
            chat_box = self.query_one("#chat-history")
            summary = getattr(self, "_last_summary", "") or ""
            if TextArea:
                editor = TextArea(value=summary, id="summary-editor")
            else:
                editor = Input(value=summary, id="summary-editor")
                chat_box.mount(Label("Note: editor is single-line fallback.", classes="system-msg"))
            edit_btns = Horizontal()
            edit_btns.mount(Button("Save Edits", id="save-summary-edit"))
            edit_btns.mount(Button("Cancel Edit", id="cancel-edit"))
            chat_box.mount(editor)
            chat_box.mount(edit_btns)
            self._last_summary_widgets.extend([editor, edit_btns])
            chat_box.mount(Label("System: Edit the summary and click Save.", classes="system-msg"))
        elif event.button.id == "save-summary-edit":
            # Save edited summary and update preview
            try:
                editor = self.query_one("#summary-editor")
                new_summary = getattr(editor, "value", None) or ""
                if hasattr(editor, "get_value"):
                    try:
                        new_summary = editor.get_value()
                    except Exception:
                        pass
            except Exception:
                new_summary = getattr(self, "_last_summary", "") or ""
            self._last_summary = new_summary
            # Update the preview Markdown widget
            for w in list(getattr(self, "_last_summary_widgets", [])):
                if isinstance(w, Markdown):
                    try:
                        w.update(f"**Summary preview**\n\n{new_summary}")
                    except Exception:
                        pass
            # Remove editor widgets
            for w in list(self._last_summary_widgets):
                try:
                    if getattr(w, "id", "") == "summary-editor":
                        w.remove()
                        self._last_summary_widgets.remove(w)
                    if isinstance(w, Horizontal):
                        # Check its children button ids
                        wids = []
                        try:
                            for child in getattr(w, "children", []):
                                wids.append(getattr(child, "id", None))
                        except Exception:
                            pass
                        if "save-summary-edit" in wids or "cancel-edit" in wids:
                            try:
                                w.remove()
                                self._last_summary_widgets.remove(w)
                            except Exception:
                                pass
                except Exception:
                    pass
            self.query_one("#chat-history").mount(Label("System: Saved edited summary.", classes="system-msg"))
        elif event.button.id == "cancel-edit":
            for w in list(getattr(self, "_last_summary_widgets", [])):
                try:
                    if getattr(w, "id", "") == "summary-editor":
                        w.remove()
                        self._last_summary_widgets.remove(w)
                    if isinstance(w, Horizontal):
                        # maybe it's edit btns
                        wids=[]
                        try:
                            for child in getattr(w, "children", []):
                                wids.append(getattr(child, "id", None))
                        except Exception:
                            pass
                        if "save-summary-edit" in wids or "cancel-edit" in wids:
                            try:
                                w.remove()
                                self._last_summary_widgets.remove(w)
                            except Exception:
                                pass
                except Exception:
                    pass
            self.query_one("#chat-history").mount(Label("System: Edit canceled.", classes="system-msg"))

    def _set_compact_labels(self, compact: bool):
        labels = {
            'tab-home': ('Home', 'H'),
            'tab-chat': ('Chat', 'C'),
            'create-conv': ('New', 'N'),
            'rename-conv': ('Rename', 'Ren'),
            'delete-conv': ('Delete', 'Del'),
            'export-conv': ('Export', 'Exp'),
            'import-conv': ('Import', 'Imp'),
            'send-btn': ('Send', 'Go'),
            'send-selected': ('Send to Selected', 'Multi'),
            'btn-yt': ('Pull Transcript', 'Transcript'),
        }
        for wid, (full, short) in labels.items():
            try:
                self.query_one(f'#{wid}').label = short if compact else full
            except Exception:
                pass

    def on_resize(self, event):
        try:
            width = getattr(event, 'width', None) or getattr(self.size, 'width', 120)
            self._set_compact_labels(width < 110)
        except Exception:
            pass

    def on_key(self, event):
        """Global key handler for quick actions: Tab (agents), Ctrl+P (commands), Ctrl+X then E (external editor)."""
        k = event.key
        if k == 'tab':
            self.toggle_agents()
            return
        if k == 'ctrl+p':
            self.show_commands_overlay()
            return
        if k == 'ctrl+x':
            self._awaiting_editor_key = True
            try:
                self.query_one('#chat-history').mount(Label('System: Press E to open external editor...', classes='system-msg'))
            except Exception:
                pass
            # clear after timeout
            def _clear():
                time.sleep(4)
                self._awaiting_editor_key = False
            threading.Thread(target=_clear, daemon=True).start()
            return
        if self._awaiting_editor_key and k and k.lower() == 'e':
            self._awaiting_editor_key = False
            self.open_external_editor()
            return
