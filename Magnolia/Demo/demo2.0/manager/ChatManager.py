# ChatManager.py
from flask import request, jsonify
from funct.gtp import gpt

class ChatManager:
    @staticmethod
    def initialize_gpt_instance(user_info):
        """Initialize GPT instance with database configuration."""
        server_name = user_info['server'].replace("\\\\", "\\")
        db_config = {
            'server_name': server_name,
            'db_name': user_info['db_name']
        }
        return gpt(**db_config)

    @staticmethod
    def process_post_request(gpt_instance):
        """Process POST request for chat."""
        data = request.get_json()
        if data:
            user_query = data.get('user_query')
            db_mode = data.get('db_mode') == 'si'
            response = gpt_instance.web_run(user_query, db_mode)
            return jsonify({'response': response})
        return jsonify({'error': 'Invalid data'}), 400
