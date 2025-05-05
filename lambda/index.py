# lambda/index.py
import json
import urllib.request

# Colab で起動した FastAPI のエンドポイント
COLAB_API_URL = "https://dc75-35-202-210-226.ngrok-free.app/generate"

def lambda_handler(event, context):
    try:
        # リクエストボディの取得と解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])

        print("受信したメッセージ:", message)

        # 単純なプロンプト生成形式に変換
        prompt = message

        # Colab 側に送るペイロード
        payload = {
            "prompt": prompt,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }

        # HTTP POSTリクエスト送信
        req = urllib.request.Request(
            COLAB_API_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req) as res:
            res_body = res.read()
            res_data = json.loads(res_body)

        assistant_response = res_data['generated_text']

        # 会話履歴にアシスタントの返答を追加
        conversation_history.append({
            "role": "user", "content": message
        })
        conversation_history.append({
            "role": "assistant", "content": assistant_response
        })

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": conversation_history
            })
        }

    except Exception as e:
        print("エラー:", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(e)
            })
        }
