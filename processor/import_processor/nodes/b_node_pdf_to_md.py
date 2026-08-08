import json
import logging
from pathlib import Path

from numpy.distutils.core import setup

from processor.import_processor.base import BaseNode, setup_logging
from processor.import_processor.exceptions import StateFieldError, FileProcessingError
from processor.import_processor.state import ImportGraphState


class NodePDFToMD(BaseNode):
    """
    PDF 转 Markdown 节点：PDF结构化解析
    """

    name = "node_pdf_to_md"

    def process(self, state: ImportGraphState):
        # 检查获取相关参数
        pdf_path_obj,output_dir_obj = self._step_1_validate_paths(state)
        # 获取上传链接并上传到MinerU服务器
        zip_url = self._step_2_upload_and_poll(pdf_path_obj)
        # 下载zip文件并解压
        md_path = self._step_3_download_and_extract(zip_url,output_dir_obj,pdf_path_obj.stem)
        # 读取文件
        try:
            with open(md_path,"r",encoding="utf-8") as md_file:
                md_content = md_file.read()
        except:
            print("其实已经成功了")
        finally:
            print("over================")
        # 返回结果
        state["md_content"] = md_content
        state["md_path"] = md_path

        return state

    def _step_1_validate_paths(self, state:ImportGraphState):
        #校验路径
        pdf_path = state.get("pdf_path")
        if not pdf_path:
            raise StateFieldError(field_name="pdf_path",expected_type=str)

        file_dir = state.get("file_dir")
        if not file_dir:
            raise StateFieldError(field_name="file_dir",expected_type=str)

        pdf_path_obj = Path(pdf_path)
        output_dir_obj = Path(file_dir)

        # 文档是否存在
        if not output_dir_obj.exists():
            raise FileProcessingError(message=f"输出文件不存在：{output_dir_obj}")
        if not pdf_path_obj.exists():
            raise FileProcessingError(message=f"输入文件不存在：{pdf_path_obj}")

        return pdf_path_obj,output_dir_obj

    def _step_2_upload_and_poll(self, pdf_path_obj):
        logging.info("上传文件到服务器")
        return "上传url"

    def _step_3_download_and_extract(self, zip_url, output_dir_obj, stem):
        logging.info("下载并解压改名")
        return "md_path"

if __name__ == '__main__':
    setup_logging()
    init_state={
        "pdf_path": r"D:\main.pdf",
        "file_dir": r"D:\output",
    }
    node = NodePDFToMD(init_state)
    result = node(init_state)
    dumps = json.dumps(result, ensure_ascii=False,indent=4)
    print(result)