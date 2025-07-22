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

    def print_args(*args, **kwargs):
        logger.info("=== [START] print_args ===")
        for i, arg in enumerate(args):
            logger.info(f"  args[{i}]: {type(arg)} -> {repr(arg)}")
        logger.info("=== [END] print_args ===")

        logger.info("=== [START] print_kwargs ===")
        for key, value in kwargs.items():
            logger.info(f"  {key}: {type(value)} -> {repr(value)}")
        logger.info("=== [END] print_kwargs ===")

    def wrapped_execute(*args, **kwargs):
        prompt_id = None
        current_node_id = None
        nodes = []

        # 打印日志信息
        # print_args(*args, **kwargs)

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
            # nodes 中对象按order排序
            nodes = sorted(nodes, key=lambda x: x.get("order", 0))

        logger.info(f"[wrapped_execute] prompt_id: {prompt_id}")
        logger.info(f"[wrapped_execute] current_node_id: {current_node_id}")
        logger.info(f"[wrapped_execute] last order node: {nodes[-1]}")

        outputs = original_execute(*args, **kwargs)

        exec_result = outputs[0]
        exec_msg = outputs[1]
        exec_exception = outputs[2]

        logger.info(f"[wrapped_execute] output exec_result: {exec_result}")
        logger.info(f"[wrapped_execute] output exec_msg: {exec_msg}")
        logger.info(f"[wrapped_execute] outputs exec_exception: {exec_exception}")


        # if outputs.get("system", {}).get("execution_error"):
        #     _send("fail", prompt_id, error=_get_error_msg(outputs))
        # else:
        #     _send("success", prompt_id)

        return outputs

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
        logger.info(f"[Workflow Callback] Request. url {callback_config['url']}, payload: {payload}")
        response = requests.post(callback_config["url"], json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"[Workflow Callback] Response: {response.text}")
    except Exception as e:
        logger.info(f"[Workflow Monitor] Failed to send callback: {e}")


def _get_error():
    etype, evalue, tb = sys.exc_info()
    return "".join(traceback.format_exception(etype, evalue, tb))


def _get_error_msg(outputs):
    err = outputs.get("system", {}).get("execution_error", None)
    if err:
        return str(err)
    return "Unknown error"
