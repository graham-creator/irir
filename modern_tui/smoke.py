from textual.widgets import Label

import asyncio
import time
import uuid

async def run_smoke_test(ai):
    try:
        chat_box = ai.query_one('#chat-history')
        await chat_box.mount(Label('Smoke test: Starting simulated multi-model send...', classes='system-msg'))
    except Exception:
        pass

    models = ['sim-alpha', 'sim-beta']
    ai._selected_models = set(models)
    user_text = 'This is a smoke test message.'

    try:
        if not ai._conversations:
            ai.create_conversation()
    except Exception:
        pass

    turn_id = 'smoke-' + str(uuid.uuid4())[:8]
    try:
        conv = next((c for c in ai._conversations if c['id'] == ai._current_conv_id), None)
        if conv is not None:
            conv.setdefault('messages', []).append({'role': 'user', 'content': user_text, 'turn_id': turn_id})
            conv['last_updated'] = time.time()
            ai.save_conversations()
            ai.render_conversation_list()
    except Exception:
        pass

    try:
        ai.create_response_group(turn_id, user_text, models)
    except Exception:
        pass

    for m in models:
        sid = ai._sanitize_id(m)
        try:
            md = ai.query_one(f'#resp-{turn_id}-{sid}')
        except Exception:
            md = None
        simulated = f"Simulated response from {m}.\n\n- Point A\n- Point B\n"
        cur = ''
        for token in simulated.split():
            cur += token + ' '
            try:
                if md is not None:
                    md.update(cur)
            except Exception:
                pass
            await asyncio.sleep(0.01)
        try:
            if conv is not None:
                conv.setdefault('messages', []).append({'role': 'assistant', 'content': simulated, 'model': m, 'turn_id': turn_id})
                conv['last_updated'] = time.time()
                ai.save_conversations()
        except Exception:
            pass

    await asyncio.sleep(0.2)
    try:
        ai.handle_compare(turn_id)
    except Exception:
        pass

    try:
        await chat_box.mount(Label('Smoke test: Completed; exiting.', classes='system-msg'))
    except Exception:
        pass
    await asyncio.sleep(0.4)
    try:
        ai.exit()
    except Exception:
        pass