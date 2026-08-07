import logging

from langgraph.constants import END
from langgraph.graph import StateGraph

from processor.import_processor.nodes.a_node_entry import NodeEntry
from processor.import_processor.nodes.b_node_pdf_to_md import NodePDFToMD
from processor.import_processor.nodes.c_node_md_img import NodeMDImg
from processor.import_processor.nodes.d_node_document_split import NodeDocumentSplit
from processor.import_processor.nodes.e_node_item_name_recognition import NodeItemNameRecognition
from processor.import_processor.nodes.f_node_bge_embedding import NodeBGEEmbedding
from processor.import_processor.nodes.g_node_import_milvus import NodeImportMilvus
from processor.import_processor.state import ImportGraphState


class KBImportWorkflow:
    """

    """
    def __init__(self,config=None):
        self._compiled_graph = None #实例属性

    @property # 伪装成属性的方法
    def graph(self):
        """

        :return:返回图实例
        """
        logging.info("获取图实例")
        if self._compiled_graph is None:
            self._compiled_graph = self.build_graph() #创建图
        return self._compiled_graph
    @staticmethod
    def route_after_entry(state:ImportGraphState):
        if state.get("is_pdf_read_enabled"):
            return "node_pdf_to_md"
        elif state.get("is_md_read_enabled"):
            return "node_md_img"
        else:
            return END



    def build_graph(self):
        """
        创建主图
        :return:
        """
        graph = StateGraph(ImportGraphState)
        # 注册节点
        graph.add_node("node_entry",NodeEntry())
        graph.add_node("node_pdf_to_md",NodePDFToMD())
        graph.add_node("node_md_img",NodeMDImg())
        graph.add_node("node_document_split",NodeDocumentSplit())
        graph.add_node("node_item_name_recognition",NodeItemNameRecognition())
        graph.add_node("node_bge_embedding",NodeBGEEmbedding())
        graph.add_node("node_import_milvus",NodeImportMilvus())

        # 连接节点
        graph.set_entry_point("node_entry")
        graph.add_conditional_edges(
            "node_entry",
            self.route_after_entry,
            {
                "node_md_img":"node_md_img",
                "node_pdf_to_md":"node_pdf_to_md",
                END:END
            }
        )
        graph.add_edge("node_pdf_to_md","node_md_img")
        graph.add_edge("node_md_img","node_document_split")
        graph.add_edge("node_document_split","node_item_name_recognition")
        graph.add_edge("node_item_name_recognition","node_bge_embedding")
        graph.add_edge("node_bge_embedding","node_import_milvus")
        # 编译图

        return graph.compile()

if __name__ == "__main__":
    workflow = KBImportWorkflow()
    graph = workflow.graph
    print(graph)