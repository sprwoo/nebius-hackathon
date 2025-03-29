from app.controllers import Chunky
import json

def should_generate_video(state):
    user_input = state.get("user_input")
    chat_summary = state.get("chat_summary", "")
    
    prompt = (
        "Given the chat so far and the user's latest message, decide whether a visual explanation "
        "like a short educational video would help clarify the concept.\n\n"
        f"Chat Summary:\n{chat_summary}\n\n"
        f"User Message:\n{user_input}\n\n"
        "Respond in a json format like this: {'generate_video': boolean}"
    )
    
    chunky = Chunky()
    result = chunky.basic_response(prompt)
    
    try:
        parsed = json.loads(result)
        make_video = parsed.get("generate_video", False)
    except Exception:
        make_video = "true" in result.lower()

    return {
        "make_video": make_video,
    }