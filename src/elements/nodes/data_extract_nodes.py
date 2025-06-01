import asyncio
import os
import time
from datetime import datetime
from src.elements.models.models import qwen_vl,client,llm,Author
from src.elements.states.data_extract_state import DataExtractState
from src.elements.utils.utils import *
def prepare_query_infos_node(state: DataExtractState):
    # TODO
    # 从excel中提取并准备好用于检索的信息，根据任务不同而不同
    # 论文检索信息
    import pandas as pd
    if state["mission_type"] == '论文抽取':
        df = pd.read_excel(state["excel_path"])
        # 这里假设论文名称在第一列
        article_names = df.loc[:, "论文名称"].tolist()
        author_lists = df.loc[:, "作者"].tolist()
        communication_authors = df.loc[:, "联系人"].tolist()
        first_authors = []

        for authors in author_lists:
            # 统一处理分隔符（中文顿号、逗号、换行符等）
            first = authors.split('、')[0].split(',')[0].split('，')[0].strip()
            first_authors.append(first)
        
        return {"query_infos": (article_names,first_authors,communication_authors)}    
      # # 专利检索信息
    
    if state["mission_type"] == '专利抽取':
        if 'info_images' not in state:
            state["info_images"] = []
        if not state["info_images"]:
            raise ValueError("专利抽取必须有图片上传")
        
        return {"query_infos": state["info_images"]}
    # else:
    #     article_names = []
    #     if "info_images" not in state:
    #         return {"info_images":[],"query_infos":article_names}
    #     return {"query_infos":article_names}

def extract_image_infos_node(state: DataExtractState):
    # TODO
    
    # 转换为Base64


    result_schema = {
                "申请年度": "",
                "授权年度": "",
                "专利名称": "",
                "申请类型": "",
                "申请日期": "",
                "申请号": "",
                "授权公告日": "",
                "专利号": ""
            }
            
    user_prompt=f"""你的任务是从图片中提取专利信息
1、如果图片标题是“专利申请受理通知书”，那么你需要提取的信息有：
申请号、申请日、申请年度（申请日的年份）、发明创造名称、申请人
你需要输出的信息格式如下：
{{  
    "申请号": "",
    "申请日": "",
    "申请年度": "",
    "发明创造名称": "",
    "申请人": ""
}}
2、如果图片标题是“专利发明证书”，那么你需要提取的信息有：
发明名称、发明人、专利号、专利申请日、申请年度（专利申请日的年份）、授权公告日、专利权人、授权年度（授权公告日的年份）、授权公共号
你需要输出的信息格式如下：
{{
    "发明名称": "",
    "发明人": "",
    "专利号": "",
    "专利申请日": "",
    "申请年度": "",
    "授权公告日": "",
    "专利权人": "",
    "授权年度": "",
    "授权公告号": ""
}}
注意：
1、如果有不确定的信息，或者无法提取的信息，请用'未知'代替；
2、你提取到的信息必须是百分百确定的，和图片中的文字保持完全一致，不要做任何更改；
3、你最终只输出一个字典，字典的键值对必须是以上两种格式之一；
最后，不要输出其他除了以上json外的其他任何文字"""
    
    # 4. 调用Qwen-VL模型（使用Base64图片数据）
    completion = client.chat.completions.create(
        model="qwen-vl-max",  # 模型名称
          
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},  # 文本提示
                    {
                        "type": "image_url",
                        "image_url": {
                            # 直接传递Base64数据（前缀 + 编码数据）
                            "url": f"data:image/jpeg;base64,{state['patent_data']}"
                        },
                        "min_pixels": 28 * 28 * 4,
                    # 输入图像的最大像素阈值，超过该值图像会按原比例缩小，直到总像素低于max_pixels
                        "max_pixels": 28 * 28 * 8192
                    }
                ]
            }
        ]
    )

    # 5. 输出结果
    # print(completion.choices[0].message.content)
    response = extract_json(completion.choices[0].message.content)
    # print(response)
    # print("``````````")
    
    # 6. 返回结果
    return {"extracted_image_infos":[response]}

def search_zhiwang_infos_node(state: DataExtractState):
    articles_finded = []
    for title, author,communication in zip(state["query_infos"][0], state["query_infos"][1],state["query_infos"][2]):
        
        article = asyncio.run(find_cnki_article_url(title,author,communication))
        if article:
            articles_finded.append(article)
 
        time.sleep(3)  
    return {"searched_zhiwang_infos": articles_finded}
    

def collect_infos_node(state: DataExtractState):
    
        
    
        data = integrate_patent_info(state["extracted_image_infos"])
        # print(state["extracted_image_infos"])
        return {"fully_filled_patent_infos": data}
   
def integrate_article_info_node(state: DataExtractState):
    if state["article"]["作者单位"] != "未提取到作者单位":
            model_with_structure = llm.with_structured_output(Author,include_raw=False,method="function_calling")
            # Invoke the model
            prompt = """以下是一篇文章的作者背景：
            {author_home}
            请从中提取出作者单位，例如institute, company等信息",把邮箱、地址等信息去掉"""
    
            structured_output = model_with_structure.invoke(prompt.format(author_home=state["article"]["作者单位"])) 
           
            author_home = ",".join(structured_output.author_unit)
            state["article"]["作者单位"] = author_home
        
    
    try:
        dt = datetime.strptime(state["article"]["发表时间"], "%Y-%m-%d %H:%M")
    except ValueError:
        dt = datetime.strptime(state["article"]["发表时间"], "%Y-%m-%d")
    state["article"]["发表时间"] = dt.strftime("%Y-%m-%d")
    state["article"]["发表年份"] = dt.strftime("%Y")
    state["article"]["发表期刊号卷号(会议名称"] = state["article"].pop("来源")
    state["article"]["论文名称"] = state["article"].pop("title")
    state["article"]["完成单位"] = state["article"].pop("作者单位")
    del state["article"]["数据库"]
    del state["article"]["被引"]
    del state["article"]["下载"]
    state["article"]["作者"] = state["article"].pop("作者")
    state["article"]["刊号"] = '-'
    state["article"]["状态"] = '录用'
    state["article"]["录用时间"] = '-'
    state["article"]["刊物级别"] = '核心期刊'
    state["article"]["检索号"] = '-'
    state["article"]["部门"] = '业务采集部'

    return {"fully_filled_article_infos":[state["article"]]}
   
   

