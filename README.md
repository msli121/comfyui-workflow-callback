# ComfyUI Workflow Callback Monitor

这个插件用于监听 ComfyUI 工作流执行状态（开始、成功、失败），并向指定的 HTTP 回调地址发送通知。

## Tip

当前实现基于 ComfyUI version: 0.3.43，其他版本的ComfyUI可能会有差异，可自行参考解决


## 📦 安装方式

将整个文件夹放入 `ComfyUI/custom_nodes/comfyui-workflow-callback/`

## 📘 使用方法

1. 添加 `WorkflowCallbackConfig` 节点到工作流中。
2. 设置 `callback_enable=True`，并填写 `callback_url`
3. 每次执行工作流都会在开始 / 成功 / 失败时发送如下回调：

```json
{
  "status": "start" | "success" | "fail",
  "id": "...",
  "extra_info": "...",
  "error": "..."
}
