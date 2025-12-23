import json

def handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Netlify Functions are working!", "path": event.get("path")})
    }
