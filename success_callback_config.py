from .workflow_callback import send_callback_req
import logging
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
                "callback_url": ("STRING", {"multiline": False, "default": ""}),
                "task_id": ("STRING", {"multiline": False, "default": ""}),
                "extra_info": ("STRING", {"multiline": False, "default": ""}),
            },
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "success_callback"
    CATEGORY = "utils/success_callbacks"

    def success_callback(self, enable=True, callback_url="", task_id="", extra_info=None):
        try:
            send_callback_req(enable=enable, callback_url=callback_url, status="success", task_id=task_id,
                              extra_info=extra_info)
        except Exception as e:
            logger.error(f"[Workflow Callback] send success callback failed. error: {e}")
            return (False,)
        return (True,)
