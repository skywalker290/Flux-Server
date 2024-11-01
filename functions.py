from flask import jsonify

def check_credentials(request):
    MY_KEY = "7865"
    data = request.get_json()

    if not data:
        return "Invalid request: No JSON payload found", 400

    KEY = data.get('KEY')

    if(KEY):
        if(KEY != MY_KEY):
            return "Authorization Failed [Incorrect Credentials]!", 401
    else:
        return "Authorization Failed [Key Not Found]!", 401
    
    return True

def gen_json(Data):
    response = {
        "data": Data
    }
    return jsonify(response)