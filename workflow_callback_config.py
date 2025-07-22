class WorkflowCallbackConfig:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "callback_enable": ("BOOLEAN", {"default": True}),
                "callback_url": ("STRING", {"multiline": False, "default": ""}),
            },
            "optional": {
                "extra_info": ("ANY", {"multiline": False, "default": ""}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "set_callback_config"
    OUTPUT_NODE = True
    CATEGORY = "utils/monitor_callbacks"

    def set_callback_config(self, callback_enable=True, callback_url="", extra_info=None):
        from .workflow_callback import set_callback_settings
        set_callback_settings(callback_enable, callback_url, extra_info)
        # print(f"[Monitor] Callback enabled: {callback_enable}, URL: {callback_url}, extra_info: {extra_info}")
        return ()
