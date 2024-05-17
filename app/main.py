from fastapi import FastAPI, Form, HTTPException
import uvicorn
import aiomysql
import re
import base64
from typing import List, Tuple
from io import BytesIO
from PIL import Image
import os
from model.clip import load, tokenize
import numpy as np
from typing import Optional
import torch
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["http://localhost:8080"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许访问的源列表
    allow_credentials=True,
    allow_methods=["*"],  # 允许的HTTP方法
    allow_headers=["*"],  # 允许的HTTP头
)

# 加载CLIP模型
model, preprocess = load("ViT-B/32", device="cpu")


async def create_db_pool():
    # 创建数据库连接池
    return await aiomysql.create_pool(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        port=int(os.getenv('DB_PORT', 3307)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '96196'),
        db=os.getenv('DB_NAME', 'Test'),
        charset='utf8mb4',
        autocommit=True,
    )


@app.on_event("startup")
async def startup_event():
    app.state.db_pool = await create_db_pool()


@app.on_event("shutdown")
async def shutdown_event():
    app.state.db_pool.close()
    await app.state.db_pool.wait_closed()


async def get_similar_images(pool, input_feature: torch.Tensor) -> List[str]:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT image_url, features, shape FROM image")
            results = await cursor.fetchall()

            # 计算每个图片特征与输入特征的相似度
            similarities = []
            for row in results:
                shape = np.frombuffer(row['shape'], dtype=int)
                shape_tuple = tuple(shape)
                # 直接将二进制数据转换为张量，并使用reshape恢复原始形状
                db_feature = torch.tensor(np.frombuffer(row['features'], dtype=np.float32)).reshape(shape_tuple)
                input_feature_tensor = input_feature if input_feature.ndim == 2 else input_feature.unsqueeze(0)

                similarity = torch.nn.functional.cosine_similarity(db_feature, input_feature_tensor)
                similarities.append((row['image_url'], similarity.item()))

            similarities.sort(key=lambda x: x[1], reverse=True)
            top_4_similar = similarities[:4]

    # 返回相似度最高的10个图片URL
    return [url for url, _ in top_4_similar]


def base64_to_image(base64_str):
    padding_needed = len(base64_str) % 4
    if padding_needed:  # 如果不是4的倍数
        missing_padding = 4 - padding_needed
        base64_str += '=' * missing_padding  # 添加缺失的填充字符

    base64_str = re.sub('^data:image/.+;base64,', '', base64_str)

    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data))
    return image


def image_to_base64(image_path):
    with Image.open(image_path) as image:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')


def get_image_features(image):
    image_preprocessed = preprocess(image).unsqueeze(0)
    with torch.no_grad():
        image_features = model.encode_image(image_preprocessed)
        image_features /= image_features.norm(dim=-1, keepdim=True)
    return image_features


def get_text_features(text):
    text_tokens = tokenize([text])
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)
    return text_features


@app.post("/search")
async def search(image_base64: Optional[str] = Form(None), text: Optional[str] = Form(None)):
    img_results = []

    if image_base64 and text:
        img = base64_to_image(image_base64)
        input_img_feature = get_image_features(img)
        text_feature = get_text_features(text)
        input_feature = (text_feature + input_img_feature) / 2
        urls = await get_similar_images(app.state.db_pool, input_feature)
        img_results = [image_to_base64(url) for url in urls]
    elif image_base64:
        img = base64_to_image(image_base64)
        input_img_feature = get_image_features(img)
        urls = await get_similar_images(app.state.db_pool, input_img_feature)
        img_results = [image_to_base64(url) for url in urls]
    elif text:
        text_feature = get_text_features(text)
        urls = await get_similar_images(app.state.db_pool, text_feature)
        img_results = [image_to_base64(url) for url in urls]
    else:
        raise HTTPException(status_code=400, detail="No search input provided")

    return {
        "images": img_results
    }


if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=11451)