import threading
import time

import uvicorn
import fastapi
from fastapi import FastAPI

from toolbox import get_conf


class Server(uvicorn.Server):
    # A server that runs in a separate thread
    def install_signal_handlers(self):
        pass

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        while not self.started:
            time.sleep(5e-2)

    def close(self):
        self.should_exit = True
        self.thread.join()

# 没用
# 用gptac环境里的uvicorn无法局域网访问，但py3.10自己安装的就可以
def init_uvicorn(app, host, port, ssl_keyfile, ssl_certfile):
  CUSTOM_PATH = get_conf('CUSTOM_PATH')
  config = uvicorn.Config(
      app,
      host=host,
      port=port,
      reload=False,
      log_level="warning",
      ssl_keyfile=ssl_keyfile,
      ssl_certfile=ssl_certfile,
  )
  server = Server(config)
  url_host_name = "localhost" if host == "0.0.0.0" else host
  if ssl_keyfile is not None:
      if ssl_certfile is None:
          raise ValueError(
            "ssl_certfile must be provided if ssl_keyfile is provided."
          )
      path_to_local_server = f"https://{url_host_name}:{port}/"
  else:
      path_to_local_server = f"http://{url_host_name}:{port}/"
  if CUSTOM_PATH != '/':
      path_to_local_server += CUSTOM_PATH.lstrip('/').rstrip('/') + '/'
  return server, path_to_local_server
