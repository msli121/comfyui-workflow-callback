import sys
import traceback
import requests
import logging
import execution

# 配置日志
logger = logging.getLogger("comfyui-textin-watermark")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

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
        logger.info(f"[Workflow Callback] Sending callback. url {callback_config['url']}, payload: {payload}")
        response = requests.post(callback_config["url"], json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"[Workflow Callback] Response: {response.text}")
    except Exception as e:
        print(f"[Workflow Monitor] Failed to send callback: {e}")


def _get_error():
    etype, evalue, tb = sys.exc_info()
    return ''.join(traceback.format_exception(etype, evalue, tb))
