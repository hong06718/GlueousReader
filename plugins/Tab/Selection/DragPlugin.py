"""
鼠标拖动：划词或拖动页面
"""

from typing import override
from types import MethodType
import tkinter as tk
from tkinter import messagebox

import fitz

from glueous import ReaderAccess
from glueous_plugin import Plugin


class DragPlugin(Plugin):
    """
    绑定鼠标拖动事件。
    判断拖动起点是否落在文字上：
    - 若是，视为划词
    - 否则，视为拖动页面
    """

    name = "DragPlugin"
    description = """
# DragPlugin

- name: DragPlugin
- author: Little Liu
- hotkeys: `鼠标拖动`
- menu entrance: None

## Function

绑定鼠标拖动事件到当前活跃 canvas。
判断拖动起点是否落在文字上：
- 若是，视为划词，绘制选择区域
- 否则，视为拖动页面

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
        if current_tab is None or not hasattr(current_tab, '_drag_selection_rect'):
            return ""
        
        selection_rect = current_tab._drag_selection_rect
        if not selection_rect:
            return ""
        
        # 【修改】设置默认格式为 "text"
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
        
        # 获取文字
        return current_tab.page.get_text(format, clip=pdf_rect, **kwargs)

    @staticmethod
    def _is_on_text(tab, canvas_x, canvas_y) -> bool:
        """
        判断画布坐标 (canvas_x, canvas_y) 是否落在文字上
        """
        try:
            text_dict = tab.page.get_text("dict")
            blocks = text_dict.get("blocks", [])
            
            # 获取滚动偏移
            x_view_start, _ = tab.canvas.xview()
            y_view_start, _ = tab.canvas.yview()
            
            page_rect = tab.page.rect
            
            # 转换画布坐标到 PDF 坐标（考虑滚动）
            pdf_x = (canvas_x / tab.zoom) + page_rect.width * x_view_start
            pdf_y = (canvas_y / tab.zoom) + page_rect.height * y_view_start
            
            for block in blocks:
                if block.get("type") == 0:  # 文本块
                    bbox = block.get("bbox")
                    if bbox:
                        x0, y0, x1, y1 = bbox
                        if x0 <= pdf_x <= x1 and y0 <= pdf_y <= y1:
                            return True
            
            return False
        except Exception:
            return False

    @staticmethod
    def setup_drag_event(access: ReaderAccess) -> None:
        """
        为当前 tab 的 canvas 绑定鼠标拖动事件
        """
        current_tab = access.get_current_tab()
        if current_tab is None:
            return
        
        canvas = current_tab.canvas
        
        # 初始化拖动状态
        if not hasattr(current_tab, '_drag_state'):
            current_tab._drag_state = {
                "start": None,
                "is_text_selection": False,
                "selection_rect": None,
                "canvas_id": None,
            }
            current_tab._drag_selection_rect = None
        
        state = current_tab._drag_state
        
        def on_mouse_down(event):
            # 【修改】检查是否有 Ctrl 键，有则忽略（由 SelectPlugin 处理）
            if event.state & 0x4:
                return
            
            # 【新增】左键按下时清除之前的划词选框
            if state["is_text_selection"] and state["canvas_id"] is not None:
                canvas.delete(state["canvas_id"])
                state["canvas_id"] = None
                state["selection_rect"] = None
                current_tab._drag_selection_rect = None
            
            state["start"] = (event.x, event.y)
            # 判断是否在文字上
            state["is_text_selection"] = DragPlugin._is_on_text(current_tab, event.x, event.y)
        
        def on_mouse_drag(event):
            # 【修改】检查是否有 Ctrl 键，有则忽略
            if event.state & 0x4:
                return
            
            if state["start"] is None:
                return
            
            x1, y1 = state["start"]
            x2, y2 = event.x, event.y
            
            if state["is_text_selection"]:
                # 划词模式：绘制选择区域
                if state["canvas_id"] is not None:
                    canvas.delete(state["canvas_id"])
                
                state["canvas_id"] = canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline="green",
                    width=2,
                    fill="lightgreen",
                    stipple="gray50"
                )
                
                state["selection_rect"] = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                current_tab._drag_selection_rect = state["selection_rect"]
                
                # 检查边缘滚动
                _check_edge_scroll(canvas, event.x, event.y, current_tab)
            else:
                # 页面拖动模式：滚动页面
                dx = x1 - x2
                dy = y1 - y2
                
                if dx != 0:
                    canvas.xview_scroll(dx // 10, "units")
                if dy != 0:
                    canvas.yview_scroll(dy // 10, "units")
        
        def on_mouse_up(event):
            # 【修改】检查是否有 Ctrl 键，有则忽略
            if event.state & 0x4:
                return
            
            if state["start"] is None:
                return
            
            state["start"] = None
            
            # 【修改】如果是划词模式，只保存文字，不清除选框
            if state["is_text_selection"] and state["canvas_id"] is not None and state["selection_rect"] is not None:
                # 获取选中的文字
                text = DragPlugin.get_selected_text(access)
                
                if text.strip():
                    # 保存选中文字供其他插件使用
                    current_tab._selected_text = text
        
        # 绑定事件
        canvas.bind("<Button-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)
    
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
            lambda event=None: self.setup_drag_event(self.context)
        )
        
        # 为当前 tab 绑定事件
        if self.context.get_current_tab() is not None:
            self.setup_drag_event(self.context)
    
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
    
    # 检查水平滚动
    if x < edge_threshold and tab.canvas_width > width:
        canvas.xview_scroll(-3, "units")
    elif x > width - edge_threshold and tab.canvas_width > width:
        canvas.xview_scroll(3, "units")
    
    # 检查垂直滚动
    if y < edge_threshold and tab.canvas_height > height:
        canvas.yview_scroll(-3, "units")
    elif y > height - edge_threshold and tab.canvas_height > height:
        canvas.yview_scroll(3, "units")