from .workflow_callback_config import WorkflowCallbackConfig
from .workflow_callback import int_patch

NODE_CLASS_MAPPINGS = {
    "WorkflowCallbackConfig": WorkflowCallbackConfig,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WorkflowCallbackConfig": "🔔 Workflow Callback 配置",
}

# 初始化时执行 patch 注入监听器
int_patch()
