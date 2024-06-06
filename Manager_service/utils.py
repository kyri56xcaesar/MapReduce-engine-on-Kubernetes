from flask import jsonify

def jid_json_formatted_message(jid, type, content, code):
    return jsonify({
        'jid':str(jid),
        type : content
    }), code