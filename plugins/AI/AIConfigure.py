"""
AI 配置插件：允许用户配置 AI 模型参数
"""

import json
import tkinter as tk
from tkinter import simpledialog, messagebox
from typing import Dict, Any, override

from glueous_plugin import Plugin


class AIConfigurePlugin(Plugin):
    """
    AI 配置插件：允许用户设置大语言模型的参数
    """

    name = "AIConfigurePlugin"
    description = """
# AIConfigurePlugin

- name: AIConfigurePlugin
- author: Jerry
- hotkeys: None
- menu entrance: `工具 → AI配置`

## Function

Allow users to configure parameters for calling large language models, such as `url`, `model`, `token`, etc.

The configuration information will be saved in `ReaderAccess.data` and can be restored after program restart.

## Api

- `context.get_AI_configuration()`: Obtain the user's AI configuration parameters.

## Depend

Python extension library: None

Other plugins: None

## Others

The configuration parameters are saved in JSON format in config/data.json.
"""

    hotkeys = []

    # 默认配置
    DEFAULT_CONFIGURATION: Dict[str, Any] = {
        "url": "",
        "token": "",
        "model": "",
        "stream": True,
    }

    # 存在 ReaderAccess.data 中的键名
    _CONFIG_KEY: str = "ai_configuration"


    def get_AI_configuration(self) -> Dict[str, Any]:
        """
        获取用户的AI配置参数

        Returns:
            Dict[str, Any]: AI配置参数，例如：
            {
                "url": "https://api-inference.modelscope.cn/v1/chat/completions",
                "token": "12345678",
                "model": "Qwen/Qwen3-Coder-30B-A3B-Instruct",
                "stream": True,
            }
        """
        # 从数据中获取配置，如果没有则返回默认配置
        return self.context.data.get(self._CONFIG_KEY, self.DEFAULT_CONFIGURATION)


    def loaded(self) -> None:
        """
        插件加载时：注册菜单项，从数据文件恢复配置
        """
        # 注册菜单项
        self.context.add_menu_command(
            path = ["工具"],
            label = "AI配置",
            command = self.run
        )

        # 提供获取配置的方法
        self.context.get_AI_configuration = self.get_AI_configuration


    def run(self) -> None:
        try:
            # 获取当前配置
            current_configuration = self.get_AI_configuration()

            # 创建配置对话框
            config_str = json.dumps(current_configuration, indent=2, ensure_ascii=False)
            new_config_str = simpledialog.askstring(
                "AI配置",
                "请输入AI配置参数（JSON格式）：",
                initialvalue=config_str,
                parent=None
            )

            if new_config_str:
                # 验证并保存配置
                new_config = json.loads(new_config_str)
                self._save_configuration(new_config)
                messagebox.showinfo("成功", "AI配置已保存")

        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON格式错误: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"配置失败: {str(e)}")


    def _save_configuration(self, config: Dict[str, Any]) -> None:
        """
        保存配置到数据文件

        Args:
            config: 要保存的配置字典
        """
        self.context.data[self._CONFIG_KEY] = config


    def unloaded(self) -> None:
        """
        插件卸载时清理
        """
        pass
