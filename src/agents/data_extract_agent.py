from langgraph.graph import StateGraph, START, END
import os
import sys
sys.path.append(os.getcwd())
from src.elements.nodes.data_extract_nodes import prepare_query_infos_node,extract_image_infos_node,search_zhiwang_infos_node,collect_infos_node,integrate_article_info_node
from src.elements.edges.conditional_edges import data_extract_conditional_edge, parallel_conditional_edge
from src.elements.states.data_extract_state import DataExtractState

data_extract_work_flow_builder = StateGraph(DataExtractState)

data_extract_work_flow_builder.add_node("prepare_query_infos_node",prepare_query_infos_node)
data_extract_work_flow_builder.add_node("extract_image_infos_node",extract_image_infos_node)
data_extract_work_flow_builder.add_node("search_zhiwang_infos_node",search_zhiwang_infos_node)
data_extract_work_flow_builder.add_node("collect_infos_node",collect_infos_node)
data_extract_work_flow_builder.add_node(integrate_article_info_node)
data_extract_work_flow_builder.add_edge(START,"prepare_query_infos_node")
data_extract_work_flow_builder.add_conditional_edges("prepare_query_infos_node",data_extract_conditional_edge,["extract_image_infos_node","search_zhiwang_infos_node"])
data_extract_work_flow_builder.add_conditional_edges("search_zhiwang_infos_node",parallel_conditional_edge,["integrate_article_info_node"])
data_extract_work_flow_builder.add_edge("extract_image_infos_node","collect_infos_node")
data_extract_work_flow_builder.add_edge("collect_infos_node",END)
data_extract_work_flow_builder.add_edge("integrate_article_info_node",END)

data_extract_work_flow = data_extract_work_flow_builder.compile()

if __name__ == "__main__":
    
    s = data_extract_work_flow.invoke({"mission_type":"论文抽取","excel_path":"工作簿2.xlsx"})

    print(s['fully_filled_article_infos'])
        