"""
向上滚动。
"""

from tkinter import ttk
from typing import override

from glueous_plugin import Plugin


class VerticalScrollUpPlugin(Plugin):
    """
    向上滚动插件：允许用户通过快捷键或菜单项向上滚动页面。
    """

    # 插件信息
    name = "VerticalScrollUpPlugin"
    description = """
# VerticalScrollUpPlugin

- name: VerticalScrollUpPlugin
- author: Jerry
- hotkeys: `<Up>`
- menu entrance: `前往 → 向上滚动`

## Function

Scroll up the page.

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
    hotkeys = ["<Up>"]


    @override
    def loaded(self) -> None:
        """
        注册菜单项。
        """
        self.context.add_menu_command(
            path = ["前往"],
            label = "向上滚动",
            command = self.run,
            accelerator = self.hotkey
        )


    @override
    def run(self) -> None:
        """
        执行向上滚动操作。
        """
        current_tab = self.context.get_current_tab()
        if current_tab is None:
            return

        # 向上滚动画布
        current_tab.canvas.yview_scroll(-1, "units")


    @override
    def unloaded(self) -> None:
        pass
