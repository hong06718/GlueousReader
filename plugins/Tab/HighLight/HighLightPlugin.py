"""
PDF 高亮和标记插件 - 支持关键词搜索和高亮
"""

import fitz
from tkinter import messagebox, simpledialog

from glueous_plugin import Plugin


class HighLightPlugin(Plugin):
    """
    高亮插件：在 PDF 上高亮和标记关键词
    """

    name = "HighLightPlugin"
    description = """
# HighLightPlugin

- name: HighLightPlugin
- author: Zhenghongbo
- hotkeys: `Ctrl+H`
- menu entrance: `工具 → 高亮关键词`

## Function

在 PDF 中搜索并高亮关键词。支持以下功能：
- 输入关键词进行搜索
- 用矩形框标记找到的所有匹配
- 保存带高亮的 PDF 文件
- 清除已有的高亮标记

## Api

None

## Depend

Python extension library:
- fitz (PyMuPDF)

Other plugins:
- TabPlugin
"""

    hotkeys = ["<Control-h>"]

    def loaded(self) -> None:
        """
        插件加载时：注册菜单项和快捷键
        """
        self.context.add_menu_command(
            path=["工具"],
            label="高亮关键词",
            command=self.run,
            accelerator="Ctrl+H"
        )

    def run(self) -> None:
        """
        执行高亮操作
        """
        current_tab = self.context.get_current_tab()
        if current_tab is None:
            messagebox.showwarning("提示", "请先打开一个 PDF 文件")
            return

        # 弹出输入框，让用户输入关键词
        keywords_input = simpledialog.askstring(
            "高亮关键词",
            "输入要高亮的关键词（多个关键词用逗号分隔）：",
            parent=current_tab.canvas
        )

        if not keywords_input:
            return

        # 解析关键词
        keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]

        if not keywords:
            messagebox.showwarning("提示", "请输入至少一个关键词")
            return

        # 执行高亮操作
        try:
            self._highlight_keywords(current_tab, keywords)
            messagebox.showinfo("成功", f"已在全部页面高亮 {len(keywords)} 个关键词")
        except Exception as e:
            messagebox.showerror("错误", f"高亮失败: {str(e)}")

    def _highlight_keywords(self, tab, keywords: list) -> None:
        """
        在 PDF 的所有页面中高亮关键词
        """
        if not tab.doc:
            return

        total_highlights = 0

        # 遍历所有页面
        for page_num in range(len(tab.doc)):
            page = tab.doc[page_num]

            # 为每个关键词进行搜索和高亮
            for keyword in keywords:
                # 搜索关键词的所有位置
                text_instances = page.search_for(keyword)

                for rect in text_instances:
                    # 添加矩形注释（高亮框）
                    highlight_rect = page.add_rect_annot(rect)
                    
                    # 设置边框
                    highlight_rect.set_border(width=2)
                    
                    # 设置颜色（蓝色边框，黄色填充）
                    highlight_rect.set_colors(
                        stroke=[0, 0, 1],      # 蓝色边框 RGB
                        fill=[1, 1, 0]         # 黄色填充 RGB
                    )
                    
                    # 设置透明度
                    highlight_rect.set_opacity(0.3)
                    
                    # 更新注释
                    highlight_rect.update()
                    
                    total_highlights += 1

        # 【修改】刷新显示：调用 Tab 的 render 方法
        tab.render()

    def unloaded(self) -> None:
        """
        插件卸载时清理
        """
        pass
