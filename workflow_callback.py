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
        prompt_id = None
        current_node_id = None
        first_node_id = None
        last_node_id = None

        # 打印日志信息
        # _print_args(*args, **kwargs)

        # 获取当前执行节点ID
        arg_3 = args[3]
        # arg_3 是一个字符串并且是数字
        if isinstance(arg_3, str) and arg_3.isdigit():
            current_node_id = int(arg_3)

        # 获取prompt信息
        arg_4 = args[4]
        if isinstance(arg_4, dict) and arg_4.get("extra_pnginfo"):
            prompt_id = arg_4.get("extra_pnginfo", {}).get("workflow", {}).get("id", None)
            nodes = arg_4.get("extra_pnginfo", {}).get("workflow", {}).get("nodes", [])
            if len(nodes) > 0:
                nodes = sorted(nodes, key=lambda x: x.get("order", 0))
                first_node_id = int(nodes[0].get("id"))
                last_node_id = int(nodes[-1].get("id"))

        logger.info(f"[wrapped_execute] prompt_id: {prompt_id}")
        logger.info(f"[wrapped_execute] current_node_id: {current_node_id}")

        outputs = original_execute(*args, **kwargs)

        exec_result = outputs[0]
        # exec_exception = outputs[1]
        exec_msg = outputs[2]

        logger.info(f"[wrapped_execute] output exec_result: {exec_result.value} {type(exec_result)}")
        logger.info(f"[wrapped_execute] output exec_msg: {exec_msg}")

        # 回调处理
        if int(exec_result.value) == 0:  # 节点执行成功
            if first_node_id is not None and last_node_id is not None:
                if current_node_id <= first_node_id:
                    _send("start", prompt_id)
                elif current_node_id >= last_node_id:
                    _send("success", prompt_id)
        elif int(exec_result.value) == 1:  # 节点执行失败
            _send("failed", prompt_id, exec_msg)

        return outputs

    execution.execute = wrapped_execute


def set_callback_settings(enable, url, extra_info):
    callback_config["enable"] = enable
    callback_config["url"] = url
    callback_config["extra_info"] = extra_info


def _send(event, prompt_id, error=None):
    if not callback_config["enable"]:
        logger.warning(f"[Workflow Callback] not enabled")
        return
    if not callback_config["url"] or len(callback_config["url"]) == 0:
        logger.warning(f"[Workflow Callback] url is empty")
        return
    payload = {
        "event": event,  # start, success, failed
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
        logger.info(f"[Workflow Monitor] Failed to send callback: {e}")

def _print_args(*args, **kwargs):
    logger.info("=== [START] print_args ===")
    for i, arg in enumerate(args):
        logger.info(f"  args[{i}]: {type(arg)} -> {repr(arg)}")
    logger.info("=== [END] print_args ===")

    logger.info("=== [START] print_kwargs ===")
    for key, value in kwargs.items():
        logger.info(f"  {key}: {type(value)} -> {repr(value)}")
    logger.info("=== [END] print_kwargs ===")