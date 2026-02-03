import difflib


def get_response_text(ai, turn_id: str, model_name: str) -> str:
    """Retrieve response text for a model in a turn from conversation storage or UI."""
    try:
        conv = next((c for c in ai._conversations if c['id'] == ai._current_conv_id), None)
        if conv:
            for m in conv.get('messages', []):
                if m.get('role') == 'assistant' and m.get('model') == model_name and m.get('turn_id') == turn_id:
                    return m.get('content', '')
    except Exception:
        pass
    try:
        sid = ai._sanitize_id(model_name)
        md = ai.query_one(f"#resp-{turn_id}-{sid}")
        return getattr(md, 'renderable', '') or getattr(md, 'text', '') or ''
    except Exception:
        return ''


def handle_compare(ai, turn_id: str, m1: str = None, m2: str = None):
    """Handle compare action: if two models specified, show diff; otherwise show metrics and pair buttons."""
    try:
        group = ai._groups.get(turn_id, {})
        models = group.get('models', [])
        if not models:
            try:
                ai.query_one('#chat-history').mount(ai.Label('No models found for this turn.', classes='error-msg'))
            except Exception:
                pass
            return

        if m1 and m2:
            a = next((x for x in models if ai._sanitize_id(x) == m1), None)
            b = next((x for x in models if ai._sanitize_id(x) == m2), None)
            if not a or not b:
                try:
                    ai.query_one('#chat-history').mount(ai.Label('Error: models not found for comparison.', classes='error-msg'))
                except Exception:
                    pass
                return
            ta = get_response_text(ai, turn_id, a).splitlines()
            tb = get_response_text(ai, turn_id, b).splitlines()
            diff = list(difflib.unified_diff(ta, tb, fromfile=a, tofile=b, lineterm=''))
            text = '```\n' + '\n'.join(diff) + '\n```'
            try:
                ai.query_one('#chat-history').mount(ai.Markdown(f"**Diff {a} vs {b}**\n\n{text}"))
            except Exception:
                pass
            return

        if len(models) == 2:
            a, b = models[0], models[1]
            ta = get_response_text(ai, turn_id, a).splitlines()
            tb = get_response_text(ai, turn_id, b).splitlines()
            diff = list(difflib.unified_diff(ta, tb, fromfile=a, tofile=b, lineterm=''))
            text = '```\n' + '\n'.join(diff) + '\n```'
            try:
                ai.query_one('#chat-history').mount(ai.Markdown(f"**Diff {a} vs {b}**\n\n{text}"))
            except Exception:
                pass
            return

        rows = []
        for i in range(len(models)):
            for j in range(i+1, len(models)):
                x = models[i]
                y = models[j]
                tx = set(get_response_text(ai, turn_id, x).split())
                ty = set(get_response_text(ai, turn_id, y).split())
                overlap = len(tx & ty)
                total = max(1, len(tx | ty))
                pct = int(100.0 * overlap / total)
                rows.append((x, y, overlap, total, pct))
        try:
            box = ai.Vertical()
            box.mount(ai.Label('Comparison pairs:'))
            for r in rows:
                a, b, overlap, total, pct = r
                h = ai.Horizontal()
                h.mount(ai.Label(f"{a} vs {b} — overlap {overlap}/{total} ({pct}%)"))
                h.mount(ai.Button('Compare', id=f'comparepair-{turn_id}-{ai._sanitize_id(a)}-{ai._sanitize_id(b)}'))
                box.mount(h)
            ai.query_one('#chat-history').mount(box)
        except Exception:
            pass
    except Exception:
        pass