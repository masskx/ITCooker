import logging
from pathlib import Path

from processor.import_processor.base import BaseNode
from processor.import_processor.exceptions import StateFieldError, ValidationError
from processor.import_processor.state import ImportGraphState


class NodeEntry(BaseNode):
    """
    入口节点：任务分发
    """

    name = "node_entry"

    def process(self, state: ImportGraphState):
        logging.info(f"Processing {self.name}节点开始处理")
        # 获得输入路径
        import_file_path = state.get("import_file_path")
        # 校验路径存在
        if not import_file_path:
            raise StateFieldError(field_name="import_file_path",expected_type=str)
        # 校验文件
        import_file_path_obj = Path(import_file_path)
        # md还是pdf
        if not import_file_path_obj.exists():
            raise StateFieldError(message=f"文件不存在:{import_file_path}")
        # 检查文件后缀
        if import_file_path_obj.suffix == ".pdf":
            state["is_pdf_read_enabled"] = True
            state["pdf_path"] = import_file_path
        elif import_file_path_obj.suffix == ".md":
            state["is_md_read_enabled"] = True
            state["md_path"] = import_file_path
        else:
            raise ValidationError(message=f"该文件的后缀格式{import_file_path_obj.suffix}不支持")
        # 获取文件上传的标题更新到state中
        state["file_title"] = import_file_path_obj.stem
        print(f"state{state}")
        return state