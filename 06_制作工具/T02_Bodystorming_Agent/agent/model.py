import json
import os
import re
import threading
import urllib.error
import urllib.parse
import urllib.request


class AgentError(Exception):
    pass


class ModelClient:
    def __init__(self):
        self.lock = threading.Lock()
        self.base_url = os.environ.get('BODYSTORM_BASE_URL', 'https://api.deepseek.com')
        self.model = os.environ.get('BODYSTORM_MODEL', 'deepseek-flash')
        self.key = os.environ.get('BODYSTORM_API_KEY', '')
        self.json_mode = True

    def public(self):
        with self.lock:
            return dict(base_url=self.base_url, model=self.model, configured=bool(self.key), json_mode=self.json_mode)

    def configure(self, data):
        base = str(data.get('base_url', '')).strip().rstrip('/')
        parsed = urllib.parse.urlsplit(base)
        if not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise AgentError('请填写不含账号、查询参数的模型 API Base URL。')
        if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('localhost', '127.0.0.1', '::1')):
            raise AgentError('远程接口需使用 HTTPS；本机模型可用 HTTP。')
        model = str(data.get('model', '')).strip()
        if not model or len(model) > 180:
            raise AgentError('请填写模型名称或服务商提供的模型接入点 ID。')
        with self.lock:
            if data.get('clear_key'):
                self.key = ''
            elif data.get('api_key'):
                self.key = str(data['api_key']).strip()
            self.base_url, self.model = base, model
            self.json_mode = bool(data.get('json_mode', True))
        return self.public()

    def complete(self, system, payload, image=None):
        with self.lock:
            base, model, key, use_json = self.base_url, self.model, self.key, self.json_mode
        if not key:
            raise AgentError('尚未配置模型 API。请打开“模型设置”，在本机填写密钥，或明确切换到演示模式。')
        content = json.dumps(payload, ensure_ascii=False)
        if image:
            content = [{'type': 'text', 'text': content}, {'type': 'image_url', 'image_url': {'url': image}}]
        body = dict(model=model, messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': content}], stream=False)
        if use_json:
            body['response_format'] = {'type': 'json_object'}
        endpoint = base if base.endswith('/chat/completions') else base + '/chat/completions'
        request = urllib.request.Request(endpoint, data=json.dumps(body).encode('utf-8'), headers={
            'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key,
        })
        try:
            with urllib.request.urlopen(request, timeout=100) as response:
                result = json.loads(response.read(4_000_000))
            text = result['choices'][0]['message']['content']
            if not isinstance(text, str) or not text.strip():
                raise AgentError('模型没有返回可用文本，请确认所选模型支持当前接口。')
            cleaned = re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip(), flags=re.I)
            answer = json.loads(cleaned)
            if not isinstance(answer, dict):
                raise ValueError('not an object')
            return answer
        except urllib.error.HTTPError as exc:
            labels = {401: '密钥未通过认证', 403: '账号没有此模型权限', 404: '模型或接口地址不存在',
                      429: '额度不足或请求过于频繁', 400: '请求格式或模型参数不被支持，可尝试关闭 JSON 模式'}
            raise AgentError(f'模型 API 返回 HTTP {exc.code}：{labels.get(exc.code, "服务商暂时无法处理请求")}。') from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise AgentError('模型连接失败或超时，请检查地址、网络和本机代理。') from None
        except AgentError:
            raise
        except (ValueError, KeyError, IndexError, TypeError):
            raise AgentError('模型输出不符合节点要求的 JSON 格式。本次运行已保留错误记录，没有替换成演示数据。') from None

