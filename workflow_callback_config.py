class WorkflowCallbackConfig:
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
    FUNCTION = "set_callback_config"
    CATEGORY = "utils/monitor_callbacks"

    def set_callback_config(self, enable=True, callback_url="", task_id=None, extra_info=None):
        from .workflow_callback import set_callback_settings
        set_callback_settings(enable=enable, url=callback_url, task_id=task_id, extra_info=extra_info)
        return (True,)
