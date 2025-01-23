# 通义千问不如 deepseekv3一根 ，回去通马桶吧

import asyncio
import aiohttp
from aiohttp import web


PORT = 48854
TARGET_PORT = 48853


async def handle_http(request):
  # 构造目标URL
  url = f'http://127.0.0.1:{TARGET_PORT}{request.path}'

  # 转发请求
  async with aiohttp.ClientSession() as session:
    async with session.request(method=request.method, url=url, headers=request.headers, data=await request.read()) as response:
      # 将响应返回给客户端
      return web.Response(status=response.status, headers=response.headers, body=await response.read())


async def handle_websocket(request):
  # 构造目标URL
  url = f'ws://127.0.0.1:{TARGET_PORT}{request.path}'

  # 创建WebSocket连接
  ws = web.WebSocketResponse()
  await ws.prepare(request)

  # 连接到目标WebSocket服务器
  async with aiohttp.ClientSession() as session:
    async with session.ws_connect(url) as client_ws:
      # 双向转发消息
      async def forward_to_client():
        async for msg in client_ws:
          if msg.type == aiohttp.WSMsgType.TEXT:
            await ws.send_str(msg.data)
          elif msg.type == aiohttp.WSMsgType.BINARY:
            await ws.send_bytes(msg.data)
          elif msg.type == aiohttp.WSMsgType.ERROR:
            await ws.close()
            break

      async def forward_to_server():
        async for msg in ws:
          if msg.type == aiohttp.WSMsgType.TEXT:
            await client_ws.send_str(msg.data)
          elif msg.type == aiohttp.WSMsgType.BINARY:
            await client_ws.send_bytes(msg.data)
          elif msg.type == aiohttp.WSMsgType.ERROR:
            await client_ws.close()
            break

      # 等待任意一个任务完成
      await asyncio.gather(forward_to_client(), forward_to_server())

  return ws


async def handle_request(request):
  if request.headers.get('Upgrade', '').lower() == 'websocket':
    return await handle_websocket(request)
  else:
    return await handle_http(request)


async def start_proxy():
  app = web.Application()
  app.router.add_route('*', '/{path:.*}', handle_request)

  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, '0.0.0.0', PORT)
  await site.start()

  print(f'Proxy server started at http://0.0.0.0:{PORT}')

  # 保持服务器运行
  while True:
    await asyncio.sleep(3600)


if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(start_proxy())
