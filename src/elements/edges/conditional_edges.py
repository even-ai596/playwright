from langgraph.types import Send
from src.elements.states.data_extract_state import DataExtractState

def data_extract_conditional_edge(state: DataExtractState):
    
    # 此边从prepare_query_infos_node开始，根据不同任务类型不同条件前往不同节点,到collect_infos_node为止，设置多条条件跳转边
    # 如果任务类型为论文抽取，那么前往search_zhiwang_infos_node
    if state["mission_type"] == '论文抽取':
        return "search_zhiwang_infos_node"    # 如果同时有图片上传，那么在prepare_query_infos_node后并行前往search_zhiwang_infos_node和extract_image_infos_node
    
    
    # 如果任务类型为专利抽取，且无图片上传，那么前往END并返回错误信息提示专利抽取必须有图片上传
    
    
    # 如果任务类型为专利抽取，且有图片上传，那么prepare_query_infos_node后前往extract_image_infos_node
    if state["mission_type"] == '专利抽取' and state["info_images"]:
        return [Send("extract_image_infos_node", {"patent_data": base64}) for base64 in state["query_infos"]]
    
def parallel_conditional_edge(state: DataExtractState):
    
    
   
    if state["mission_type"] == '论文抽取':
        return [Send("integrate_article_info_node", {"article": article}) for article in state["searched_zhiwang_infos"]]