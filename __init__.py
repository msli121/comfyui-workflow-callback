from .workflow_monitor import WorkflowMonitor
from .workflow_callback import init_patch

NODE_CLASS_MAPPINGS = {
    "WorkflowCallbackConfig": WorkflowMonitor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WorkflowCallbackConfig": "🔔 Workflow Callback Monitor",
}

# 初始化时执行 patch 注入监听器
init_patch()
