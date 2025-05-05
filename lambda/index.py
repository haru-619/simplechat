# lambda/index.py
import json
import urllib.request

# Colab上で立ち上げたFastAPIのエンドポイントURLをここに貼る（後ろに /generate は付けない）
COLAB_API_BASE_URL = "https://dc75-35-202-210-226.ngrok-free.app"

def lambda_handler(event, context):
    try:
        # リクエストボディを読み取り
        body = json.loads(event["body"])
        prompt = body.get("message", "")
        conversation = body.get("conversationHistory", [])

        # 会話履歴からuserとassistantのメッセージを繋げてプロンプトを構築
        full_prompt = ""
        for msg in conversation:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                full_prompt += f"User: {content}\n"
            elif role == "assistant":
                full_prompt += f"Assistant: {content}\n"
        full_prompt += f"User: {prompt}\nAssistant: "

        # Colab API に送るデータ
        request_data = json.dumps({
            "prompt": full_prompt,
            "max_new_tokens": 256,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{COLAB_API_BASE_URL}/generate",
            data=request_data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode("utf-8"))
            assistant_response = response_data.get("generated_text", "No response")

        # 会話履歴を更新
        conversation.append({"role": "user", "content": prompt})
        conversation.append({"role": "assistant", "content": assistant_response})

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": conversation
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(e)
            })
        }
