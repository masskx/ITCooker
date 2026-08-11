# ITCooker 🍳

> 为程序员准备的 AI 私厨智能体平台 —— 把文档"烹"成可直接下锅的知识库

基于 **LangChain + LangGraph** 构建的知识处理平台，将 PDF / Markdown 文档经解析、切片、向量化后导入向量数据库，为后续 RAG 问答与智能体应用提供食材。

## ✨ 特性

- **LangGraph 编排**：文档导入采用有向图流水线，节点可插拔、状态全程可追踪
- **PDF → Markdown**：基于 MinerU 云服务解析，保留版式与图片
- **图片语义化**：多模态模型理解文档图片并生成摘要，替换原文图片引用
- **智能切片 + 命名**：文档自动分块，并识别商品/产品名称（方便程序员检索定位）
- **向量化入库**：BGE Embedding + Milvus，天然支持 RAG 检索
- **FastAPI 服务**：为后续 Web 交互、任务实时日志预留接口

## 🧱 技术栈

| 分类 | 组件 |
| --- | --- |
| AI 编排 | LangChain / LangGraph |
| 文档解析 | MinerU API v4 |
| LLM / 多模态 | SiliconFlow（OpenAI 兼容接口，Qwen 系列） |
| 向量化 | BGE Embedding |
| 向量存储 | Milvus 2.5（docker-compose：etcd + MinIO + Milvus） |
| 对象存储 | MinIO |
| API 框架 | FastAPI |

## 📁 目录结构

```
itcooker/
├── config/                  # 全局配置
│   ├── mineru_config.py     #   MinerU 文档解析服务
│   ├── llm_config.py        #   LLM / 多模态模型
│   └── minio_config.py      #   MinIO 对象存储
├── processor/
│   ├── import_processor/    # 知识库导入流水线
│   │   ├── config.py        #   导入流程配置（Milvus / MinIO / 切片参数）
│   │   ├── state.py         #   图状态定义
│   │   ├── base.py          #   节点基类（统一日志、异常处理）
│   │   ├── exceptions.py    #   自定义异常体系
│   │   ├── main_graph.py    #   导入工作流主图
│   │   └── nodes/           # 图节点（a → g 顺序执行）
│   │       ├── a_node_entry.py                # 入口：路径校验 / 格式路由
│   │       ├── b_node_pdf_to_md.py            # PDF 解析（MinerU 上传/轮询/下载解压）
│   │       ├── c_node_md_img.py               # 图片扫描 + 多模态摘要 + MinIO 上传
│   │       ├── d_node_document_split.py       # 文档切片（待实现）
│   │       ├── e_node_item_name_recognition.py# 商品名称识别（待实现）
│   │       ├── f_node_bge_embedding.py        # BGE 向量化（待实现）
│   │       └── g_node_import_milvus.py        # 导入 Milvus（待实现）
│   └── query_processor/     # 检索问答流水线（规划中）
├── utils/                   # 通用工具
│   ├── llm_utils.py         #   LLM 客户端工厂（模型缓存、JSON 模式）
│   └── minio_utils.py       #   MinIO 客户端（自动建桶、公开读策略）
├── test/                    # 测试
└── docker-compose.yml       # etcd + MinIO + Milvus 本地环境
```

## 🚀 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 配置环境变量（复制 .env.example 为 .env 并填写）
#    MINERU_API_TOKEN：MinerU 文档解析服务
#    OPENAI_API_KEY：SiliconFlow 密钥（LLM / 视觉 / 命名识别）
#    MinIO / Milvus 连接信息（本地默认值可直接使用）

# 3. 启动本地基础设施（etcd + MinIO + Milvus）
docker compose up -d

# 4. 运行导入工作流（示例：D:\main.pdf）
python -m processor.import_processor.main_graph
```

## 🔄 核心流程

```
node_entry
  │  .pdf → node_pdf_to_md（MinerU 解析为 Markdown）
  │  .md  → 直接进入
  ▼
node_md_img（图片扫描 → VL 模型摘要 → MinIO 上传替换）
  ▼
node_document_split → node_item_name_recognition → node_bge_embedding → node_import_milvus
```

## 🗺️ 项目进度

- [x] 导入流水线骨架（LangGraph 主图 + 节点基类 + 状态管理 + 异常体系）
- [x] 配置模块（MinerU / MinIO / LLM / Milvus / 切片参数）
- [x] 本地基础设施（docker-compose：etcd + MinIO + Milvus）
- [x] 入口节点：路径校验与 PDF/MD 路由
- [x] PDF 解析节点：MinerU 上传 → 轮询 → 下载解压 → 重命名
- [ ] 图片处理节点：扫描 ✅，多模态摘要 / MinIO 上传替换待实现
- [ ] 文档切片节点（node_document_split）
- [ ] 商品名称识别节点（node_item_name_recognition）
- [ ] BGE 向量化节点（node_bge_embedding）
- [ ] Milvus 入库节点（node_import_milvus）
- [ ] 检索问答流水线（query_processor）
- [ ] 智能体工具集（tool）
- [ ] FastAPI 服务与 Web 交互
