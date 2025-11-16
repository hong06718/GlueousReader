"""
Ctrl+鼠标拖动选中文字插件
"""

from typing import override
from types import MethodType
import tkinter as tk
from tkinter import messagebox

import fitz

from glueous import ReaderAccess
from glueous_plugin import Plugin


class SelectPlugin(Plugin):
    """
    绑定 Ctrl+鼠标拖动 事件，在画布上绘制选择区域。
    为 ReaderAccess 添加 get_selected_text 方法。
    """

    name = "SelectPlugin"
    description = """
# SelectPlugin

- name: SelectPlugin
- author: Little Liu
- hotkeys: `Ctrl+拖动`
- menu entrance: None

## Function

绑定 Ctrl+鼠标拖动 事件到当前活跃 canvas。
当发生该事件时，在画布上绘制一个半透明的选择区域（矩形）。
当接近窗口边缘时，还要滚动。

## Api

- `context.get_selected_text(format=None, **kwargs)` - 获得选中区域内的文字

## Depend

Python extension library:
- fitz (PyMuPDF)

Other plugins:
- TabPlugin
"""

    hotkeys = []

    @staticmethod
    def get_selected_text(access: ReaderAccess, format=None, **kwargs) -> str:
        """
        获取选中区域的文字
        """
        current_tab = access.get_current_tab()
        if current_tab is None or not hasattr(current_tab, '_selection_rect'):
            return ""
        
        selection_rect = current_tab._selection_rect
        if not selection_rect:
            return ""
        
        if format is None:
            format = "text"
        
        # 转换画布坐标到 PDF 坐标（考虑滚动）
        x_view_start, _ = current_tab.canvas.xview()
        y_view_start, _ = current_tab.canvas.yview()
        
        page_rect = current_tab.page.rect
        pdf_x1 = (selection_rect[0] / current_tab.zoom) + page_rect.width * x_view_start
        pdf_y1 = (selection_rect[1] / current_tab.zoom) + page_rect.height * y_view_start
        pdf_x2 = (selection_rect[2] / current_tab.zoom) + page_rect.width * x_view_start
        pdf_y2 = (selection_rect[3] / current_tab.zoom) + page_rect.height * y_view_start
        
        pdf_rect = fitz.Rect(pdf_x1, pdf_y1, pdf_x2, pdf_y2)
        
        return current_tab.page.get_text(format, clip=pdf_rect, **kwargs)

    @staticmethod
    def setup_select_event(access: ReaderAccess) -> None:
        """
        为当前 tab 的 canvas 绑定 Ctrl+鼠标拖动 事件
        """
        current_tab = access.get_current_tab()
        if current_tab is None:
            return
        
        canvas = current_tab.canvas
        
        # 初始化选择状态
        if not hasattr(current_tab, '_selection_state'):
            current_tab._selection_state = {
                "ctrl_start": None,
                "rect": None,
                "canvas_id": None,
            }
            current_tab._selection_rect = None
        
        state = current_tab._selection_state
        
        def on_button_press(event):
            """处理普通左键按下 - 清除选框"""
            if not (event.state & 0x4):  # 不是 Ctrl+左键
                if state["canvas_id"] is not None:
                    canvas.delete(state["canvas_id"])
                    state["canvas_id"] = None
                    state["rect"] = None
                    current_tab._selection_rect = None
                    state["ctrl_start"] = None
        
        def on_ctrl_button_press(event):
            """Ctrl+左键按下 - 开始选择"""
            # 清除之前的选框
            if state["canvas_id"] is not None:
                canvas.delete(state["canvas_id"])
                state["canvas_id"] = None
                state["rect"] = None
                current_tab._selection_rect = None
            
            state["ctrl_start"] = (event.x, event.y)
        
        def on_ctrl_button_drag(event):
            """Ctrl+拖动 - 绘制选框"""
            if state["ctrl_start"] is None:
                return
            
            x1, y1 = state["ctrl_start"]
            x2, y2 = event.x, event.y
            
            # 删除旧选框
            if state["canvas_id"] is not None:
                canvas.delete(state["canvas_id"])
            
            # 绘制新选框
            state["canvas_id"] = canvas.create_rectangle(
                x1, y1, x2, y2,
                outline="blue",
                width=2,
                fill="lightblue",
                stipple="gray50"
            )
            
            state["rect"] = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
            current_tab._selection_rect = state["rect"]
            
            # 检查边缘滚动
            _check_edge_scroll(canvas, event.x, event.y, current_tab)
        
        def on_ctrl_button_release(event):
            """Ctrl+释放 - 保存文字"""
            if state["ctrl_start"] is None:
                return
            
            state["ctrl_start"] = None
            
            # 只保存选中文字，不清除选框
            if state["canvas_id"] is not None and state["rect"] is not None:
                text = SelectPlugin.get_selected_text(access)
                
                if text.strip():
                    current_tab._selected_text = text
        
        # 【修改】绑定专用的 Ctrl 组合键事件
        canvas.bind("<Button-1>", on_button_press)
        canvas.bind("<Control-Button-1>", on_ctrl_button_press)
        canvas.bind("<Control-B1-Motion>", on_ctrl_button_drag)
        canvas.bind("<Control-ButtonRelease-1>", on_ctrl_button_release)
    
    @override
    def loaded(self) -> None:
        """
        插件加载时：为 ReaderAccess 扩展 get_selected_text 方法
        """
        self.context.get_selected_text = MethodType(
            self.get_selected_text,
            self.context
        )
        
        # 在标签页切换时重新绑定事件
        self.context.add_at_notebook_tab_changed_function(
            lambda event=None: self.setup_select_event(self.context)
        )
        
        # 为当前 tab 绑定事件
        if self.context.get_current_tab() is not None:
            self.setup_select_event(self.context)
    
    @override
    def run(self) -> None:
        pass
    
    @override
    def unloaded(self) -> None:
        pass


def _check_edge_scroll(canvas, x, y, tab):
    """检查是否接近窗口边缘，如果是则滚动"""
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    edge_threshold = 30
    
    if x < edge_threshold and tab.canvas_width > width:
        canvas.xview_scroll(-3, "units")
    elif x > width - edge_threshold and tab.canvas_width > width:
        canvas.xview_scroll(3, "units")
    
    if y < edge_threshold and tab.canvas_height > height:
        canvas.yview_scroll(-3, "units")
    elif y > height - edge_threshold and tab.canvas_height > height:
        canvas.yview_scroll(3, "units")