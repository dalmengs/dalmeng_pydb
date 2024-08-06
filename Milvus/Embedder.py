import aiohttp
import json as j

class Embedder:

    def __init__(self, embedding_ip, embedding_port):
        self.__embedding_endpoint = "http://{ip}:{port}/api/v1/embedding".format(
            ip=embedding_ip,
            port=embedding_port
        )

    async def encode(self, message):
        embedding_result = await Request.post(
            url=self.__embedding_endpoint,
            headers={
                "Content-type": "application/json"
            },
            data={
                "text": message
            }
        )
        
        return embedding_result.json()["data"]

class Request:
    session = None

    class Response:
        def __init__(self, status_code, msg="succeed", data=None, content=None):
            self.status_code = status_code
            self.msg = msg
            self.data = data
            self.content = content

        def json(self):
            try:
                return j.loads(self.data)
            except:
                return j.loads(self.content)

    @staticmethod
    async def post(url, headers: dict = {}, data: dict = {}, timeout=60):
        if not Request.session:
            timeout = aiohttp.ClientTimeout(total=timeout)
            Request.session = aiohttp.ClientSession(timeout=timeout)

        try:
            res = await Request.session.post(url, headers=headers, json=data)

            data = None
            content = None

            if "Content-Type" in headers and ('text' in headers["Content-Type"] or 'json' in headers["Content-Type"]):
                data = await res.text()
            else:
                content = await res.read()
            return Request.Response(
                status_code=res.status,
                data=data,
                content=content
            )
        except aiohttp.ClientError as e:
            return Request.Response(
                status_code=400,
                msg=str(e)
            )
        except Exception as e:
            return Request.Response(
                status_code=500,
                msg=str(e)
            )
