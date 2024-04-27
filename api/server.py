from app import app

def handler(request, response):
    if request.method == 'OPTIONS':
        # Handle preflight CORS requests
        response.status = 200
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization'
        return

    # Run the Flask app
    app(request, response)
