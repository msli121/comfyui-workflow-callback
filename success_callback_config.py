import requests

from .workflow_callback import send_callback_req
import logging
import execution

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


class SuccessCallbackConfig:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enable": ("BOOLEAN", {"default": True}),
                "local_comfyui_url": ("STRING", {"multiline": False, "default": "http://localhost:8188"}),
                "callback_url": ("STRING", {"multiline": False, "default": ""}),
                "task_id": ("STRING", {"multiline": False, "default": ""}),
                "extra_info": ("STRING", {"multiline": False, "default": ""}),
            },
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "success_callback"
    CATEGORY = "utils/success_callbacks"

    def success_callback(self, enable=True, local_comfyui_url=None, callback_url="", task_id="", extra_info=None):
        try:
            prompt_id = self._get_prompt_id(local_comfyui_url)
            send_callback_req(enable=enable,
                              callback_url=callback_url,
                              status="success",
                              prompt_id=prompt_id,
                              task_id=task_id,
                              extra_info=extra_info)
        except Exception as e:
            logger.error(f"[Workflow Callback] send success callback failed. error: {e}")
            return (False,)
        return (True,)

    @staticmethod
    def _get_prompt_id(local_comfyui_url: str):
        try:
            response = requests.get(f"{local_comfyui_url}/queue")
            response.raise_for_status()
            data = response.json()
            if data and data.get("queue_running") and len(data["queue_running"]) > 0:
                return data.get("queue_running")[0][1]
            return None
        except Exception as e:
            logger.error(f"[Workflow Callback] get prompt id failed. error: {e}")
            raise e
