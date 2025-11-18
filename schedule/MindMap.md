# MindMap

你需要完成 `MindMapPlugin` 插件。

## Function

当用户在菜单栏中选择“AI思维导图”时，调用大语言模型的 api，生成对整个文档的思维导图。

AI 只需生成指定格式的文本，Python 自有将这种格式的文本绘制成思维导图的扩展库（自行搜索）。

以弹窗的形式，思维导图反馈给用户，用户可以进行复制、保存等操作。

用户可以在菜单栏中配置生成的思维导图的深度等参数。

## Something Useful

- `ReaderAccess.get_selected_text()` ：获取目前选中的文本。
- `ReaderAccess.get_AI_configuration()` ：获取用户的 AI 配置参数。
- `Tab.doc` ：`fitz.Document` 对象，可视为 `Sequence[Page]` 和 `Iterable[Page]` 。
- `Page.get_text()` ：返回该页面上的文本。（详细信息自行搜索）