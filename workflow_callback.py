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

def int_patch():
    original_execute = execution.execute

    def wrapped_execute(*args, **kwargs):
        print("=== [DEBUG] wrapped_execute called ===")
        print("args:")
        for i, arg in enumerate(args):
            print(f"  args[{i}]: {type(arg)} -> {repr(arg)}")
        print("kwargs:")
        for key, value in kwargs.items():
            print(f"  {key}: {type(value)} -> {repr(value)}")
        print("=== [END DEBUG] ===")

        # # 判断 prompt_id 和 prompt 的位置
        # if len(args) >= 2 and isinstance(args[1], dict):
        #     prompt_id = args[0] if isinstance(args[0], str) else None
        #     prompt = args[1]
        # elif len(args) >= 3 and isinstance(args[2], dict):
        #     # 第一个是 self
        #     prompt_id = args[1] if isinstance(args[1], str) else None
        #     prompt = args[2]
        # else:
        #     prompt_id = "unknown"
        #     prompt = {}
        #
        # if callback_config["enable"]:
        #     _send("start", prompt_id)

        outputs = original_execute(*args, **kwargs)
        # 打印结果
        print("=== [DEBUG] outputs ===")
        print(outputs)
        print("=== [END DEBUG] ===")

        # if outputs.get("system", {}).get("execution_error"):
        #     _send("fail", prompt_id, error=_get_error_msg(outputs))
        # else:
        #     _send("success", prompt_id)

        return outputs

    execution.execute = wrapped_execute

# def patch_prompt_queue():
#     original_execute = execution.execute
#
#     def wrapped_execute(prompt_id, prompt, *args, **kwargs):
#         real_prompt_id = prompt.get("prompt_id", "")
#         if callback_config["enable"]:
#             _send("start", prompt_id)
#         try:
#             result = original_execute(prompt_id, prompt, *args, **kwargs)
#             if callback_config["enable"]:
#                 _send("success", prompt_id)
#             return result
#         except Exception:
#             if callback_config["enable"]:
#                 _send("fail", prompt_id, _get_error())
#             raise
#
#     execution.execute = wrapped_execute


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
        logger.info(f"[Workflow Callback] Request. url {callback_config['url']}, payload: {payload}")
        response = requests.post(callback_config["url"], json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"[Workflow Callback] Response: {response.text}")
    except Exception as e:
        print(f"[Workflow Monitor] Failed to send callback: {e}")


def _get_error():
    etype, evalue, tb = sys.exc_info()
    return ''.join(traceback.format_exception(etype, evalue, tb))

def _get_error_msg(outputs):
    err = outputs.get("system", {}).get("execution_error", None)
    if err:
        return str(err)
    return "Unknown error"
