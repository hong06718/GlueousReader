# View

你需要完成 `ViewPlugin` 插件。

## Function

`Tab.display_mode` 属性提供了视图模式。

视图模式有 `"single"`, `"continuous"`, `"facing"`, `"book"` 。

其中 `("single", "continuous")` 可与 `("", "facing", "book")` 两两组合，一共产生六种视图模式：

- `"single"` ：单页不连续。
- `"continuous"` ：单页连续。
- `"single facing"` ：双页不连续。
- `"continuous facing"` ：双页连续。
- `"single book"` ：书本形式不连续。
- `"continuous book"` ：书本形式连续。

其中（具体可参考 SumatraPDF）：

- “连续”指的是垂直滚动时，当滚到一页底部时，会继续显示下一页内容。
- 双页视图：从文档第一页开始就以**左右两页并排**的方式显示。例如，第1页在左，第2页在右，第3页在左，第4页在右，以此类推。
- 书本视图：**第一页单独显示**（通常作为封面），位于视图右侧；从第二页开始才以双页并排方式显示：第2页在左，第3页在右，第4页在左，第5页在右...

你需要在你的插件加载（`loaded`）时动态重载 `Tab` 类的 `canvas_width` 、`canvas_height` 、`canvas_rect` 、`visible_page_positions` 、`selectable_page_positions` 属性以及 `coord2real` 方法，以实现在不同视图模式下的页面布局。

对齐方式、坐标变换见 [关于页面矩形与画布矩形的讨论.md](关于页面矩形与画布矩形的讨论.md) 。

> [!TIP]
>
> 你无需考虑 `Tab.rotation` 属性。

## API

以下是你需要为 `Tab` 类重载的属性：

- `canvas_width` ：`int` ，整块画布的宽度，向上取整。
- `canvas_height` ：`int` ，整块画布的高度，向上取整。
- `canvas_rect` ：`fitz.Rect` ，`(0, 0, canvas_width, canvas_height)` 。
- `visible_page_positions` ：`List[Tuple[fitz.Page, fitz.Rect, fitz.Rect]]` ，每个元素是 (能见页面, 该页面上的能见区域, 该区域显示在整块 canvas 上的位置矩形) ，将用于渲染页面。
- `selectable_page_positions` ：`List[Tuple[fitz.Page, fitz.Rect]]` ，每个元素是 (可被选择的页面, 该页面的在整块 canvas 上的位置矩形) ，将用于 `SelectPlugin` 和 `DragPlugin` 。

你可以通过 `ReaderAccess.Tab` 来访问 `Tab` 类，并通过使用 `property` 来修改该类的所有实例的属性行为。

以下是你需要为 `Tab` 类重载的方法：

- `coord2real(pos)` ：
    - 输入：
        - `pos` ：`Tuple[float, float]` ，在“用户视界”上的坐标。
    - 输出：`Tuple[float, float]` ，对应在画布上的坐标。

你可以通过 `Tab.method = new_method` 来重载原有方法，这会改变该类的所有实例（包括已创建和将要创建的）的行为。

## Something Useful

- `pymupdf.Page` ：页面类，下面简记为 `Page` ，具体细节自行搜索。
- `Page.rect` ：页面矩形。

## Future

之后可以添加小部件来实现视图的切换。