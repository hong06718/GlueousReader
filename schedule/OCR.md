# OCR

你需要完成 ` OCRPlugin` 插件。

## Function

调用 Python 的 OCR 拓展库（自行搜索），对文档中的图像进行 OCR ，得到图像中的文本及其位置。

> [!TIP]
>
> 不用自己去训练一个模型来识别文字，用 Python 现有的扩展库！

用户可以在菜单栏中关闭/打开自动OCR；可以要求重新识别。

### 优先级

若用户打开了自动 OCR ：

- 用 `current_tab.visible_page_positions` 获得所有可见页面。
- 用 `current_tab.selectable_page_positions` 获得所有可选择页面。
- 用 `current_tab.page_no` 获取当前页面编号

优先识别当前页面及其周围的页面，当 `visible_page_positions` 中的页面全部识别完成后，再对 `selectable_page_positions` 中的页面进行识别。

### 性能

建议将识别一页的内容（以 A4 的教科书为标准）控制在2秒内，需要在准确度与速度之间进行权衡。

### 缓存

为避免重复 OCR 带来的开销，每个页面只识别一次，可以将识别到的内容进行 JSON 化，通过 `ReaderAccess` 的 `data` 属性，存储在本地的 `config/data.json` 文件中，实现数据持久化，下次再打开时可直接读取，无需再次识别。（参见 `Tab.py` 中的 `Tab.__init__` ）

## API

重载 `pymupdf.Page` 类的 `get_text` 方法，在原本的返回值中再加入 OCR 识别出的结果，注意输入和输出类型与原 `get_text` 方法相同。

下面是一个在已有方法上添加新功能的示例：

```python
import fitz

# 创建 Page 对象
doc = fitz.open(r"path/to/a/pdf")
page = doc[0]
page.get_text()

# 重载 Page 类已有的 get_text 方法
origin_get_text = fitz.Page.get_text
def new_get_text(*args, **kwargs):
    print("This is a modified method.")
    return origin_get_text(*args, **kwargs)

fitz.Page.get_text = new_get_text
```

## Something Useful

- `Tab.doc` ：`fitz.Document` 对象，可视为 `Sequence[Page]` 和 `Iterable[Page]` 。
- `Tab.visible_page_positions` 
- `Tab.selectable_page_positions` 
- `Tab.page_no` 
- `Page.get_images()` ：返回一个**列表**，列表中的每个元素都是一个元组，代表页面上的一张图像信息。（详细信息自行搜索）
- `Page.get_image_bbox()` ：获取页面中指定图像所占用的矩形区域。（详细信息自行搜索）用于计算识别出的文字在整个页面上的坐标。

## Attention

当 `OCRPlugin` 插件已完成时， `DragPlugin` 却未完成，你们的调试将遇到困难。
