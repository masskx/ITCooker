import json
import logging
import time
from collections import deque

from pathlib import Path
import os
from typing import Tuple, Dict, List, Deque
import re


from processor.import_processor.base import BaseNode, setup_logging
from processor.import_processor.exceptions import StateFieldError
from processor.import_processor.state import ImportGraphState
from utils import llm_utils


class NodeMDImg(BaseNode):
    """
    MarkDown图片处理节点：多模态图片理解
    """

    name = "node_md_img"

    def process(self, state: ImportGraphState):
        # 参数处理
        md_content,md_path_obj,images_dir = self._step_1_get_content(state)
        # print(md_content,md_path_obj,images_dir)
        # 图片扫描
        target_images = self._step_2_scan_images(md_content,images_dir)
        print(target_images)
        # 视觉模型摘要
        summaries = self._step_3_generate_summaries(md_path_obj.stem,target_images)
        #上传MinIO，替换md内容
        new_md_content = self._step_4_upload_and_replace(md_path_obj.stem,target_images,summaries,md_content)
        #对处理好的md保存备份
        new_md_file_name = self._step_5_backup_new_md_file(state['md_path'],new_md_content)
        
        state['md_path'] = new_md_file_name
        state['md_content'] = new_md_content
        return state
    # 步骤一
    def _step_1_get_content(self, state):
        # 校验参数
        md_path = state.get('md_path')
        if not md_path:
            raise StateFieldError(field_name="md_path",expected_type=str)
        md_path_obj = Path(md_path)
        if not md_path_obj.exists():
            raise StateFieldError(field_name="输入不存在",expected_type=str)
        md_content = state.get('md_content')
        if not md_content:
            with open(md_path, "r", encoding="utf-8") as md_file:
                md_content = md_file.read()
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
    def _step_3_generate_summaries(self, dict_stem:str, target_images:List[Tuple[str,str,Tuple[str,str]]])->Dict[str,str]:
        summaries = {}
        request_deque = deque()
        for image_file, img_path, context in target_images:
            self._apply_api_rate_limit(request_deque,max_requests = 10)
            summaries[image_file] = self._summarize_image(img_path, root_folder=dict_stem, image_content=context)




    def _step_4_upload_and_replace(self, stem, target_images, summaries, md_content):
        pass

    def _step_5_backup_new_md_file(self, param, new_md_content):
        pass

    def _find_image_in_md(self, md_content:str, image_file:str,context_len:int = 100)->Tuple[str,str]:

        pattern = re.compile(rf'!\[[^\]]*\]\([^)]*{re.escape(image_file)}\)')

        match = pattern.search(md_content)
        if not match:
            return "", ""
        start,end = match.span()
        pre_text = md_content[max(0, start-context_len):start] # 文件上文
        post_text = md_content[end:min(len(md_content), end+context_len)] #文件下文
        return pre_text,post_text

    def _apply_api_rate_limit(
            self,
            request_times: Deque[float],
            max_requests: int,
            window_seconds: int = 60
    ) -> None:
        """
        通用滑动窗口API速率限制器（抽离为公共工具）
        核心逻辑：维护请求时间戳双端队列，窗口内请求数超上限则自动等待，防止触发第三方API限流
        :param request_times: 存储请求时间戳的双端队列，需外部初始化（全局/单例），跨调用复用
        :param max_requests: 速率限制窗口内的最大允许请求次数
        :param window_seconds: 速率限制滑动窗口时长，默认60秒（1分钟）
        :return: None，超出限制时会阻塞等待
        """
        current_time = time.time()

        # 1. 清理滑动窗口外的过期请求时间戳，保证队列仅存窗口内的请求
        while request_times and current_time - request_times[0] >= window_seconds:
            request_times.popleft()

        # 2. 窗口内请求数达上限，计算并阻塞等待剩余时间
        if len(request_times) >= max_requests:
            # 计算需要等待的时长（窗口总时长 - 最早请求已存在的时长）
            sleep_duration = window_seconds - (current_time - request_times[0])
            if sleep_duration > 0:
                logging.getLogger().info(
                    f"触发API速率限制，窗口{window_seconds}秒内最多{max_requests}次，需等待：{sleep_duration:.2f} 秒")
                time.sleep(sleep_duration)
                # 等待后更新当前时间，重新清理过期请求（避免等待期间有请求过期）
                current_time = time.time()
                while request_times and current_time - request_times[0] >= window_seconds:
                    request_times.popleft()

        # 3. 记录当前请求时间戳，加入滑动窗口队列
        request_times.append(current_time)
        logging.getLogger().info(f"API请求时间戳已记录，当前{window_seconds}秒窗口内请求数：{len(request_times)}")

    def _summarize_image(self, img_path:str, root_folder:str, image_content:Tuple[str,str])->str:
        #  llm工具

        #  调用模型

        # 返回信息

        return "图片摘要"


if __name__ == '__main__':
    setup_logging()
    init_state = {
        'md_path':r"D:\output\main\main.md",
        'md_content': None
    }
    node = NodeMDImg()
    result = node(init_state)

    dumps = json.dumps(result)
    print(dumps)