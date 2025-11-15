"""
向右滚动。
"""

from tkinter import ttk
from typing import override

from glueous_plugin import Plugin


class HorizontalScrollRightPlugin(Plugin):
    """
    向右滚动插件：允许用户通过快捷键或菜单项向右滚动页面。
    """

    # 插件信息
    name = "HorizontalScrollRightPlugin"
    description = """
# HorizontalScrollRightPlugin

- name: HorizontalScrollRightPlugin
- author: Jerry
- hotkeys: `<Right>`
- menu entrance: `前往 → 向右滚动`

## Function

Scroll right the page.

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
    hotkeys = ["<Right>"]


    @override
    def loaded(self) -> None:
        """
        注册菜单项。
        """
        self.context.add_menu_command(
            path = ["前往"],
            label = "向右滚动",
            command = self.run,
            accelerator = self.hotkey
        )


    @override
    def run(self) -> None:
        """
        执行向右滚动操作。
        """
        current_tab = self.context.get_current_tab()
        if current_tab is None:
            return

        # 向右滚动画布
        current_tab.canvas.xview_scroll(1, "units")


    @override
    def unloaded(self) -> None:
        pass
