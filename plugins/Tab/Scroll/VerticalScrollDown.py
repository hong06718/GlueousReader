"""
向下滚动。
"""

from tkinter import ttk
from typing import override

from glueous_plugin import Plugin


class VerticalScrollDownPlugin(Plugin):
    """
    向下滚动插件：允许用户通过快捷键或菜单项向下滚动页面。
    """

    # 插件信息
    name = "VerticalScrollDownPlugin"
    description = """
# VerticalScrollDownPlugin

- name: VerticalScrollDownPlugin
- author: Jerry
- hotkeys: `<Down>`
- menu entrance: `前往 → 向下滚动`

## Function

Scroll down the page.

## Api

None.

## Depend

Python extension library: None

Other plugins:
- TabPlugin

## Others

None.
"""

    # 快捷键设置
    hotkeys = ["<Down>"]


    @override
    def loaded(self) -> None:
        """
        注册菜单项。
        """
        self.context.add_menu_command(
            path = ["前往"],
            label = "向下滚动",
            command = self.run,
            accelerator = self.hotkey
        )


    @override
    def run(self) -> None:
        """
        执行向下滚动操作。
        """
        current_tab = self.context.get_current_tab()
        if current_tab is None:
            return

        # 检查是否到达边界
        arrive_boundary = False

        if current_tab.display_mode == "single":
            pass

        # 向下滚动画布
        current_tab.canvas.yview_scroll(1, "units")


    @override
    def unloaded(self) -> None:
        pass
