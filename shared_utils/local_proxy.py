'''gptac环境里的uvicorn无法局域网访问，只能自己再转发'''

from fastapi import FastAPI, Request, Response
import httpx
import uvicorn

PORT= 48854
TARGET_PORT = 48853
app = FastAPI()


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"])
async def proxy_request(request: Request):
  # 构建目标URL
  target_url = f"http://localhost:{TARGET_PORT}{request.url.path}"
  # 创建一个httpx客户端
  async with httpx.AsyncClient() as client:
    # 转发请求
    response = await client.request(
      method=request.method,
      url=target_url,
      headers=request.headers,
      content=await request.body()
    )
    # response = await client.request(method=request.method, url=target_url, headers=dict(**request.headers), content=await request.body())
    # 构建FastAPI响应
    return Response(content=response.content, status_code=response.status_code, headers=response.headers)


if __name__ == "__main__":
  print(f"Proxy server running on port {PORT}")
  uvicorn.run(app, host="0.0.0.0", port=PORT, log_level='warning')
