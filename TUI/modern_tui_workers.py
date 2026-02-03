import time
import threading

from youtube_transcript_api import YouTubeTranscriptApi


def summarize_text(ai, text: str, model_name: str) -> str:
    """Hierarchical summarization: chunk -> summarize -> combine -> summarize again.

    `ai` is passed for potential logging or progress callbacks.
    """
    chunk_size = 3000
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    summaries = []
    for chunk in chunks:
        try:
            resp = ai.ollama.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': f"Summarize the following text in concise bullet points:\n\n{chunk}"}],
                stream=False,
            )
            content = ""
            if isinstance(resp, dict):
                content = (resp.get('message') or {}).get('content', '')
                if not content:
                    choices = resp.get('choices') or []
                    if choices:
                        content = (choices[0].get('message') or {}).get('content', '')
            if not content:
                content = str(resp)
            summaries.append(content)
        except Exception as e:
            summaries.append(f"(Error summarizing chunk: {e})")

    combined = "\n\n".join(summaries)
    if len(summaries) > 1:
        try:
            resp2 = ai.ollama.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': f"Summarize the following text in concise bullet points:\n\n{combined}"}],
                stream=False,
            )
            final = (resp2.get('message') or {}).get('content', '') if isinstance(resp2, dict) else str(resp2)
            if not final:
                final = str(resp2)
            return final
        except Exception:
            return combined
    return summaries[0] if summaries else "(No summary generated)"


def fetch_transcript(vid_id: str):
    """Return full transcript text for a YouTube video id or raise."""
    transcript = YouTubeTranscriptApi.get_transcript(vid_id)
    full_text = " ".join([i.get('text', '') for i in transcript])
    return full_text


def spinner_worker(ai, message: str, spinner_id: str = "summarize-spinner"):
    """Spinner worker that runs in a thread - updates small label while long tasks run."""
    ai._spinner_running = True
    frames = ["|", "/", "-", "\\"]

    def mount():
        try:
            chat_box = ai.query_one("#chat-history")
            try:
                existing = ai.query_one(f"#{spinner_id}")
                existing.remove()
            except Exception:
                pass
            chat_box.mount(ai.Label(f"{message}", id=spinner_id, classes='system-msg'))
        except Exception:
            pass

    try:
        ai.call_from_thread(mount)
    except Exception:
        mount()

    idx = 0
    while ai._spinner_running:
        ch = frames[idx % len(frames)]
        def upd(ch=ch):
            try:
                lbl = ai.query_one(f"#{spinner_id}")
                lbl.update(f"{message} {ch}")
            except Exception:
                pass
        try:
            ai.call_from_thread(upd)
        except Exception:
            upd()
        time.sleep(0.12)
        idx += 1

    def remove():
        try:
            node = ai.query_one(f"#{spinner_id}")
            node.remove()
        except Exception:
            pass
    try:
        ai.call_from_thread(remove)
    except Exception:
        remove()
