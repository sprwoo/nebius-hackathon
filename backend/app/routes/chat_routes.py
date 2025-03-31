from flask import Blueprint, jsonify, request
from app.services.supabase import post_message, get_chat_histories
from app.controllers import Chunky, build_graph
import os
import base64
from .blawb import SupabaseStorage

chat_bp = Blueprint("chat", __name__)
# @chat_bp.route("/send_message", methods=["POST"])
# def route_send_message():
#     data = request.json
#     chat_session_id = data.get('chat_session_id')
#     sender = data.get('sender')
#     message = data.get('message')

#     if not all([chat_session_id, sender, message]):
#         return jsonify({"error": "chat_session_id, sender, and message are required"}), 400

#     result = post_message(sender, message)
#     return jsonify(result), 200

@chat_bp.route("/get_chat_histories", methods=["GET"])
def route_chat_histories():
    chat_session_id = request.args.get("chat_session_id")
    if not chat_session_id:
        return jsonify({"error": "Missing chat_session_id parameter"}), 400

    try:
        result = get_chat_histories(chat_session_id)
        for row in result:
            print(row)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route("/chat", methods=["POST"])
def handle_chat():
    sender = request.form.get("sender")
    user_input = request.form.get("user_input")
    chat_session_id = request.form.get("session_id")

    print("session_id", chat_session_id)
    print("user_input", user_input)

    image_summary = None
    image_url = None

    if "image" in request.files:
        image_file = request.files["image"]
        if image_file.filename != "":
            # Process the image summary
            chunky = Chunky()
            file_bytes = image_file.read()
            encoded_image = base64.b64encode(file_bytes).decode('utf-8')
            image_summary = chunky.advanced_image_handling(user_input, encoded_image)
            user_input += f" The user also uploaded an image with these being the contents of the image: \n\n {image_summary}"

            # Save the image to a temporary location
            temp_dir = "/tmp"
            temp_path = os.path.join(temp_dir, image_file.filename)
            with open(temp_path, "wb") as temp_file:
                temp_file.write(file_bytes)

            # Upload the image to Supabase
            storage = SupabaseStorage()
            try:
                image_url = storage.upload_file(temp_path)
            except Exception as e:
                print("Error uploading image:", e)
                image_url = None

    # Build the graph and get the AI response
    graph = build_graph()
    state = {
        "user_input": user_input,
        "session_id": chat_session_id,
    }
    result = graph.invoke(state)
    
    # Save the user message
    post_status = post_message("user", user_input, chat_session_id, image_url=image_url)
    
    # Save the AI message along with any code, image summary, and image_url
    ai_message = result.get("chat_response")
    manim_code = "\n".join(result.get("code_chunks", [])) or None
    post_status = post_message(
        "ai", 
        ai_message, 
        chat_session_id, 
        manim_code=manim_code, 
        image_summary=image_summary,
    )
    
    return jsonify(post_status), 200