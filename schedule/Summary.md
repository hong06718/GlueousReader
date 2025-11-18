# Summary

你需要完成 `SummaryPlugin` 插件。

## Function

当用户在菜单栏中选择“AI总结”时，调用大语言模型的 api ，生成选中区域/整个文档的总结。

- 若有选中文字，则生成选中区域的总结。
- 若没有选中文字，则生成对整个文档的总结。

以弹窗的形式，将 AI 生成的总结反馈给用户，用户可以进行复制、保存等操作。

用户可以在菜单栏中配置生成总结的长度。

## Something Useful

- `ReaderAccess.get_selected_text()` ：获取目前选中的文本。
- `ReaderAccess.get_AI_configuration()` ：获取用户的 AI 配置参数。
- `Tab.doc` ：`fitz.Document` 对象，可视为 `Sequence[Page]` 和 `Iterable[Page]` 。
- `Page.get_text()` ：返回该页面上的文本。（详细信息自行搜索）