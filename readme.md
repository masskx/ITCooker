# ITCooker 🍳

> 为程序员准备的 AI 私厨智能体平台 —— 把文档"烹"成可直接下锅的知识库

基于 **LangChain + LangGraph** 构建的知识处理平台，将 PDF / Markdown 文档经解析、切片、向量化后导入向量数据库，为后续 RAG 问答与智能体应用提供食材。

## ✨ 特性

- **LangGraph 编排**：文档导入采用有向图流水线，节点可插拔、状态全程可追踪
- **PDF → Markdown**：基于 MinerU 解析，保留版式与图片
- **智能切片 + 命名**：文档自动分块，并识别商品/产品名称（方便程序员检索定位）
- **向量化入库**：BGE Embedding + Milvus，天然支持 RAG 检索
- **FastAPI 服务**：为后续 Web 交互、任务实时日志预留接口

## 🧱 技术栈

| 分类 | 组件 |
| --- | --- |
| AI 编排 | LangChain / LangGraph |
| 文档解析 | MinerU |
| 向量化 | BGE Embedding |
| 向量存储 | Milvus |
| 对象存储 | MinIO |
| API 框架 | FastAPI |

## 📁 目录结构

```
itcooker/
├── config/              # 全局配置（如 MinerU）
├── processor/
│   ├── import_processor/   # 知识库导入流水线
│   │   ├── nodes/          # 图节点（解析/切片/向量化/入库）
│   │   ├── base.py         # 节点基类（统一日志、异常处理）
│   │   ├── state.py        # 图状态定义
│   │   └── main_graph.py   # 导入工作流主图
│   └── query_processor/    # 检索问答流水线（规划中）
├── tool/                # 智能体工具集（规划中）
├── utils/               # 通用工具（规划中）
└── test/                # 测试
```

## 🚀 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 配置环境变量（复制 .env.example 为 .env，填入以下项）
#    MINERU_BASE_URL / MINERU_API_TOKEN：MinerU 文档解析服务
#    Milvus / MinIO 等连接信息（待补充）

# 3. 运行导入工作流
python -m processor.import_processor.main_graph
```

## 🔄 核心流程

```
文档入口
  │  is_pdf_read_enabled → PDF 解析 (MinerU → Markdown)
  │  is_md_read_enabled  → 直接读 Markdown
  ▼
图片处理 → 文档切片 → 名称识别 → BGE 向量化 → 导入 Milvus
```

## 🗺️ 项目进度

- [x] 导入流水线骨架（LangGraph 主图 + 节点基类 + 状态管理）
- [x] MinerU 配置模块
- [ ] 各节点实现完善（PDF 解析 / 切片 / 名称识别 / 向量化 / 入库）
- [ ] 检索问答流水线（query_processor）
- [ ] 智能体工具集（tool）
- [ ] FastAPI 服务与 Web 交互
