# custom_nodes/comfyui_workflow_monitor/workflow_callback.py
import requests
import sys
import traceback
from server import PromptExecutor

registered_callbacks = {
    "enable": False,
    "url": "",
    "extra_info": ""
}


def init_patch():
    original_execute = PromptExecutor.execute

    def wrapped_execute(self, prompt):
        prompt_id = prompt.get("prompt_id", "")
        if registered_callbacks["enable"] and registered_callbacks["url"]:
            _send_callback("start", prompt_id)

        try:
            result = original_execute(self, prompt)
            if registered_callbacks["enable"] and registered_callbacks["url"]:
                _send_callback("success", prompt_id)
            return result
        except Exception:
            if registered_callbacks["enable"] and registered_callbacks["url"]:
                error_msg = _get_last_error_message()
                _send_callback("fail", prompt_id, error_msg)
            raise

    PromptExecutor.execute = wrapped_execute


def register_callback_settings(enable, url, extra_info):
    registered_callbacks["enable"] = enable
    registered_callbacks["url"] = url
    registered_callbacks["extra_info"] = str(extra_info) if extra_info is not None else ""


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
