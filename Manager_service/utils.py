from flask import jsonify

def setup_return_format(jid, type, content, code):
    return jsonify({
        'jid':str(jid),
        type : content
    }), code