import os, random, json, boto3, requests

s3 = boto3.client("s3")
bucket = os.environ["BUCKET_NAME"]
predis_key   = os.environ["PREDIS_API_KEY"]
predis_brand = os.environ["PREDIS_BRAND_ID"]
openai_key   = os.environ["OPENAI_API_KEY"]

def lambda_handler(event, context):
    resp = s3.list_objects_v2(Bucket=bucket)
    items = resp.get("Contents", [])
    if not items:
        return {"statusCode":400, "body":"Empty bucket"}
    obj = random.choice(items)
    key = obj["Key"]
    image_url = s3.generate_presigned_url(
        "get_object", Params={"Bucket":bucket,"Key":key}, ExpiresIn=3600
    )
    # OpenAI
    oa = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization":f"Bearer {openai_key}"},
        json={
            "model":"gpt-4",
            "messages":[{"role":"user","content":f"Short caption for TikTok video, bg: {image_url}"}],
            "max_tokens":50, "temperature":0.7
        }
    )
    caption = oa.json()["choices"][0]["message"]["content"].strip()
    # Predis.ai
    pr = requests.post(
        "https://brain.predis.ai/predis_api/v1/create_content/",
        headers={"Authorization":predis_key,"Content-Type":"application/json"},
        json={
            "brand_id":predis_brand,
            "text":caption,
            "media_type":"video",
            "video_duration":"short",
            "media_urls":[image_url]
        }
    )
    return {"statusCode":pr.status_code, "body":json.dumps(pr.json())}
