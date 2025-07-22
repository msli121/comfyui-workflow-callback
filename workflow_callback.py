import requests
import sys
import traceback
from server import prompt_queue
from server import PromptServer

registered_callbacks = {
    "enable": False,
    "url": "",
    "extra_info": ""
}

def init_patch():
    """在 ComfyUI 启动时注入监听器"""
    def on_prompt_start(prompt):
        if registered_callbacks["enable"] and registered_callbacks["url"]:
            prompt_id = prompt.get("prompt_id", "")
            _send_callback("start", prompt_id)

    def on_prompt_end(prompt):
        if registered_callbacks["enable"] and registered_callbacks["url"]:
            prompt_id = prompt.get("prompt_id", "")
            _send_callback("success", prompt_id)

    def on_prompt_error(prompt, error):
        if registered_callbacks["enable"] and registered_callbacks["url"]:
            prompt_id = prompt.get("prompt_id", "")
            error_msg = _get_last_error_message()
            _send_callback("fail", prompt_id, error_msg)

    # 注册监听
    prompt_queue.on_prompt_start(on_prompt_start)
    prompt_queue.on_prompt_end(on_prompt_end)
    prompt_queue.on_prompt_error(on_prompt_error)


def register_callback_settings(enable, url, extra_info):
    registered_callbacks["enable"] = enable
    registered_callbacks["url"] = url
    registered_callbacks["extra_info"] = str(extra_info) if extra_info else ""


def _send_callback(event, prompt_id, error=None):
    data = {
        "event": event,
        "prompt_id": prompt_id,
        "extra_info": registered_callbacks.get("extra_info", "")
    }
    if error:
        data["error"] = error

    try:
        requests.post(registered_callbacks["url"], json=data, timeout=10)
    except Exception as e:
        print(f"[Monitor] Callback error: {e}")


def _get_last_error_message():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if exc_type:
        return ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    return "Unknown error"
