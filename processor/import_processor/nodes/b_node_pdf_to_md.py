import json
import logging
import time
import zipfile

from pathlib import Path
import requests
from config.mineru_config import mineru_config
from processor.import_processor.base import BaseNode, setup_logging
from processor.import_processor.exceptions import StateFieldError, FileProcessingError, PdfConversionError
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
        print(f"获取下载地址{zip_url}")
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
        """
        上传
        :param pdf_path_obj:
        :return:
        """
        logging.info("上传文件到服务器")
        # 校验api_token
        api_token = mineru_config.api_token
        base_url = mineru_config.base_url
        if not api_token:
            raise FileProcessingError(message="api_token未配置")
        if not base_url:
            raise FileProcessingError(message="base_url未配置")
        # 申请上传链接post
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
        data = {
            "files": [
                {
                    "name": pdf_path_obj.name,
                }
            ],
            "model_version": "vlm"
        }
        url = f"{base_url}/file-urls/batch"
        print(f"申请上传链接接口：{url}")
        response = requests.post(url, headers=header, json=data)
        if response.status_code != 200:
            raise FileProcessingError(message=f"申请文件上传失败：{response.text}")

        result = response.json()
        print('response success. result:{}'.format(result))
        if result["code"] != 0:
            raise FileProcessingError(message=f"申请文件上传失败{result.get('message')}")
        batch_id = result["data"]["batch_id"]
        signed_url = result["data"]["file_urls"]

        print('batch_id:{},urls:{}'.format(batch_id, signed_url))
        #上传文件put
        with open(pdf_path_obj, 'rb') as f:
            res_upload = requests.put(signed_url[0], data=f)
            if res_upload.status_code == 200:
                self.logger.info(f"文件上传成功！")
            else:
                raise PdfConversionError(f"文件上传失败，状态码：{res_upload.status_code},响应结果：{res_upload}")
        # 获取下载链接get
        poll_url = f"{base_url}/extract-results/batch/{batch_id}" # 检查转化结果的接口
        start_time = time.time() # 记录开始时间
        timeout_seconds = 600 #最大超时时间
        poll_interval = 3 #轮询间隔时间

        while True:
            end_time = time.time() - start_time
            if end_time > timeout_seconds:
                raise FileProcessingError(message="获得下载地址超时")
            try:
                res_poll = requests.get(url=poll_url,headers=header,timeout=10) # 获得下载链接
            except Exception as e:
                self.logger.error(f"轮询接口异常：{e}")
                time.sleep(poll_interval)
                continue
            if res_poll.status_code != 200:
                raise FileProcessingError(message=f"轮询失败,HTTP状态码：{res_poll.status_code}，响应内容：{res_poll}")
            poll_data = res_poll.json() # 请求成功，不代表任务成功
            if poll_data.get("code") != 0:
                raise FileProcessingError(message=f"轮询失败,错误信息：{poll_data.get('message')}")
            print(f"轮询成功，响应内容：{poll_data}")
            extract_results = poll_data['data']['extract_result'] # 任务结果
            extract_result = extract_results[0] # 下载链接
            extract_state = extract_result["state"] # 下载链接对象
            if extract_state == "done":
                full_zip_url = extract_result["full_zip_url"] # 获取下载链接
                return full_zip_url
            elif extract_state == "failed":
                pass
            else:
                self.logger.info(f"任务处理中，已耗时{end_time}秒，轮询状态：{extract_state}，batch_id：{batch_id}")
                time.sleep(poll_interval)

        return "上传url"

    def _step_3_download_and_extract(self, zip_url, output_dir_obj, pdf_stem):
        logging.info("下载并解压改名")
        # 下载
        response = requests.get(zip_url)
        if response.status_code != 200:
            raise FileProcessingError(message=f"获得下载文件失败：{response.text}")
        zip_save_path = output_dir_obj / (f"{pdf_stem}_result.zip")
        with open(zip_save_path, "wb") as f:
            f.write(response.content)
        # 创建目录
        extract_target_dir = output_dir_obj / pdf_stem
        extract_target_dir.mkdir(parents=True, exist_ok=True)
        # 解压
        with zipfile.ZipFile(zip_save_path, 'r') as zip_file_obj:
            zip_file_obj.extractall(extract_target_dir)
        self.logger.info(f"文件压包成功！")
        # 改名
        self.logger.info(f"文件重命名")
        target_md_file = extract_target_dir / f"full.md"
        new_md_path = target_md_file.with_name(f"{pdf_stem}.md")
        target_md_file.rename(new_md_path)
        self.logger.info(f"文件重命名成功！{new_md_path}")

        return str(new_md_path.absolute()) # 返回绝对路径

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