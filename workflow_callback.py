import sys
import traceback
import requests
import execution

callback_config = {
    "enable": False,
    "url": "",
    "extra_info": ""
}


def patch_prompt_queue():
    original_execute = execution.execute

    def wrapped_execute(prompt_id, prompt, *args, **kwargs):
        if callback_config["enable"]:
            _send("start", prompt_id)
        try:
            result = original_execute(prompt_id, prompt, *args, **kwargs)
            if callback_config["enable"]:
                _send("success", prompt_id)
            return result
        except Exception:
            if callback_config["enable"]:
                _send("fail", prompt_id, _get_error())
            raise

    execution.execute = wrapped_execute


def set_callback_settings(enable, url, extra_info):
    callback_config["enable"] = enable
    callback_config["url"] = url
    callback_config["extra_info"] = extra_info


def _send(event, prompt_id, error=None):
    payload = {
        "event": event,
        "prompt_id": prompt_id,
        "extra_info": callback_config["extra_info"]
    }
    if error:
        payload["error"] = error
    try:
        requests.post(callback_config["url"], json=payload, timeout=5)
    except Exception as e:
        print(f"[Workflow Monitor] Failed to send callback: {e}")


def _get_error():
    etype, evalue, tb = sys.exc_info()
    return ''.join(traceback.format_exception(etype, evalue, tb))
