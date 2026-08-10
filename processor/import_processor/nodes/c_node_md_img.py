import json
from mimetypes import init
from pathlib import Path
import os

from processor.import_processor.base import BaseNode, setup_logging
from processor.import_processor.exceptions import StateFieldError
from processor.import_processor.state import ImportGraphState


class NodeMDImg(BaseNode):
    """
    MarkDown图片处理节点：多模态图片理解
    """

    name = "node_md_img"

    def process(self, state: ImportGraphState):
        # 参数处理
        md_content,md_path_obj,images_dir = self._step_1_get_content(state)
        print(md_content,md_path_obj,images_dir)
        # 图片扫描
        target_images = self._step_2_scan_images(md_content,images_dir)
        # 视觉模型摘要
        summaries = self._step_3_generate_summaries(md_path_obj.stem,target_images)
        #上传MinIO，替换md内容
        new_md_content = self._step_4_upload_and_replace(md_path_obj.stem,target_images,summaries,md_content)
        #对处理好的md保存备份
        new_md_file_name = self._step_5_backup_new_md_file(state['md_path'],new_md_content)
        
        state['md_path'] = new_md_file_name
        state['md_content'] = new_md_content
        return state

    def _step_1_get_content(self, state):
        # 校验参数
        md_path = state.get('md_path')
        if not md_path:
            raise StateFieldError(field_name="md_path",expected_type=str)
        md_path_obj = Path(md_path)
        if not md_path_obj.exists():
            raise StateFieldError(field_name="输入不存在",expected_type=str)
        md_content = state.get('md_content')
        # 图片路径,和md文档所在目录同级别的图片路径
        images_dir = md_path_obj.parent / "images"
        return md_content,md_path_obj,images_dir



    def _step_2_scan_images(self, md_content, images_dir):
        # 返回结果
        target_res = []
        # 循环刚才的路径，找image所有图片
        for image_file in os.listdir(images_dir):
            file_ext = os.path.splitext(image_file)[1].lower()#切分扩展名
            if file_ext not in self.config.image_extensions:
                self.logger.warning(f"图片格式不支持：{image_file}")
                continue
            img_path = images_dir / image_file # 图片路径
            context = self._find_image_in_md(md_content, image_file) # 图片上下文

            target_res.append((image_file,img_path,context))

        return target_res
    def _step_3_generate_summaries(self, stem, target_images):
        pass

    def _step_4_upload_and_replace(self, stem, target_images, summaries, md_content):
        pass

    def _step_5_backup_new_md_file(self, param, new_md_content):
        pass

    def _find_image_in_md(self, md_content, image_file):
        pass


if __name__ == '__main__':
    setup_logging()
    init_state = {
        'md_path':r"D:\output\main\main.md",
        "md_content": ""
    }
    node = NodeMDImg(init_state)
    result = node(init_state)

    dumps = json.dumps(result)
    print(dumps)