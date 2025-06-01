import operator
from typing import Annotated, List, Dict
from typing_extensions import TypedDict

class DataExtractState(TypedDict):
    mission_type: str # 任务类型，按需替换成自定义枚举型
    excel_path: str
    info_images: list # 图片
    
    query_infos: tuple # 用于检索知网或者图片抽取出来的信息的信息，按需替换成自定义pydantic model
    
    extracted_image_infos: Annotated[list, operator.add] # 图片抽取出来的信息，从这里按需检索取用，按需替换成自定义pydantic model
    searched_zhiwang_infos: List # 遍历excel里论文名抓下来的知网论文信息，按需替换成自定义pydantic model
    
    fully_filled_patent_infos: List[dict] # 最终汇总信息，按需替换成自定义pydantic model
    fully_filled_article_infos: Annotated[list, operator.add]
    article_name: str # 论文名称
    patent_data: str # 专利图片base64数据
    
