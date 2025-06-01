import fitz  # PyMuPDF
import streamlit as st
from src.elements.utils.utils import *
from src.elements.models.models import client
from src.agents.data_extract_agent import data_extract_work_flow
import pandas as pd
from io import BytesIO
def pantent():
    if st.button("返回选择"):
        del st.session_state.mission_type
        st.rerun()
    st.title("文档信息抽取系统")
    if "action" not in st.session_state:
        st.session_state.action = "处理"
    

    # # 2. Excel File Upload
    # excel_file = st.file_uploader(
    #     "上传Excel模板文件",
    #     type=["xlsx", "xls"]
    # )

    # 3. PDF Files Upload
    uploaded_files = st.file_uploader(
        "上传PDF文件",
        accept_multiple_files=True,
        type=["pdf"]
    )
    if st.session_state.action =="处理":
        if st.button("开始处理"):
            
                # Run the workflow
                with st.spinner("正在处理文档..."):
                        # if not excel_file or not uploaded_files:
                        #     st.warning("请上传Excel模板和PDF文件")
                        # else:
                        # Save excel file temporarily
                        # excel_path = f"temp_{excel_file.name}"
                        # with open(excel_path, "wb") as f:
                        #     f.write(excel_file.getbuffer())
                        # import os
                        # if os.path.exists(excel_path):
                        #     os.remove(excel_path)
                        # Convert PDFs to base64 images
                        base64_images = pdf_to_base64_images(uploaded_files)
                        
                        # Create input dictionary
                        input_dict = {
                            "mission_type": st.session_state.mission_type,
                            
                            "info_images": base64_images
                        }
                            # try:
                        result = data_extract_work_flow.invoke(input_dict)
                        
                        if not result["fully_filled_patent_infos"]:
                            st.warning("请重试一次，或者检查图片是否清晰")
                        else:
                            df = pd.DataFrame(result["fully_filled_patent_infos"])
                            column_order = [
                                "申请年度", "授权年度", "专利名称", "申请类型", "状态", "申请日期", 
                                "申请号", "授权公告日", "专利号", "联系人", "部门", "专利权人", "发明人"
                            ]

                            # 确保DataFrame只包含指定的列，并按指定顺序排列
                            df = df[column_order]

                            # 按专利号排序：非空值在上，空值在下
                            df_sorted = df.sort_values(by="专利号", na_position='last')

                            # 处理重复专利名称的情况
                            # 1. 找出所有重复的专利名称
                            duplicate_names = df_sorted[df_sorted.duplicated('专利名称', keep=False)]['专利名称'].unique()
                
                            # 2. 对每个重复专利名称进行处理
                            for name in duplicate_names:
                                # 获取该专利名称的所有行
                                duplicates = df_sorted[df_sorted['专利名称'] == name]
            
                                # 检查是否有受理和授权两种状态
                                if {'受理', '授权'}.issubset(set(duplicates['状态'])):
                                    # 获取授权行和受理行
                                    authorized_row = duplicates[duplicates['状态'] == '授权'].iloc[0]
                                    accepted_row = duplicates[duplicates['状态'] == '受理'].iloc[0]
                                    
                                    # 如果授权行的申请号为空，而受理行有申请号，则进行合并
                                    if pd.isna(authorized_row['申请号']) and not pd.isna(accepted_row['申请号']):
                                        # 更新授权行的申请号
                                        df_sorted.loc[authorized_row.name, '申请号'] = accepted_row['申请号']
                                        
                                        # 删除受理行
                                        df_sorted = df_sorted.drop(accepted_row.name)

                            # 导出Excel
                            output = BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                df_sorted.to_excel(writer, index=False, sheet_name='专利信息')

                            st.session_state.action = "下载"
                            st.session_state.excel_file = output
                            st.success("处理完成！请点击下方按钮下载结果。")
                            st.rerun()
    if st.session_state.action == "下载":

        # Create download button
        st.download_button(
            label="下载Excel文件",
            data=st.session_state.excel_file.getvalue(),
            file_name="专利信息提取结果.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        if st.button("重新处理"):
            st.session_state.action = "处理"
            st.rerun()
def article():
    if st.button("返回选择"):
        del st.session_state.mission_type
        st.rerun()
    st.title("文档信息抽取系统")
    if "action" not in st.session_state:
        st.session_state.action = "处理"
    

    # 2. Excel File Upload
    excel_file = st.file_uploader(
        "上传Excel模板文件",
        type=["xlsx", "xls"]
    )

    
    if st.session_state.action =="处理":
        if st.button("开始处理"):
            
            # Run the workflow
            with st.spinner("正在处理文档..."):
                    if not excel_file :
                        st.warning("请上传Excel模板和PDF文件")
                    else:
                        # Save excel file temporarily
                        excel_path = f"temp_{excel_file.name}"
                        with open(excel_path, "wb") as f:
                            f.write(excel_file.getbuffer())
                        
                        
                        # Create input dictionary
                        input_dict = {
                            "mission_type": st.session_state.mission_type,
                            "excel_path": excel_path,
                        }
                            # try:
                        result = data_extract_work_flow.invoke(input_dict)
                    
                    if not result["fully_filled_article_infos"]:
                        st.warning("请重试一次")
                    else:
                        df = pd.DataFrame(result["fully_filled_article_infos"])


                        # df['完成单位'] = df['完成单位'].str.replace('\n', '; ')

                        # # 处理作者分隔符（统一用分号+空格）
                        # df['作者'] = df['作者'].str.replace(';', '; ').str.replace(' ', '')
                        
                        # 3. 列顺序调整（将重要信息靠前）
                        column_order = [
                            '发表年份', '论文名称', '发表期刊号卷号(会议名称', 
                            '刊号', '状态', '录用时间',
                            '发表时间', '刊物级别', '检索号',
                            '联系人', '部门', '完成单位', '作者'
                        ]
                        df = df[column_order]
                        # 4. 导出Excel到内存
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(
                                writer, 
                                index=False, 
                                sheet_name='论文信息'
                                
                            )

                        st.session_state.action = "下载"
                        st.session_state.excel_file = output
                        st.success("处理完成！请点击下方按钮下载结果。")
                        st.rerun()
            import os
            if os.path.exists(excel_path):
                os.remove(excel_path)
    if st.session_state.action == "下载":

        # Create download button
        st.download_button(
            label="下载Excel文件",
            data=st.session_state.excel_file.getvalue(),
            file_name="论文信息提取结果.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        if st.button("重新处理"):
            
            st.session_state.action = "处理"
            st.rerun()
def article_or_patent():
    st.title("文档信息抽取系统")
    col = st.columns(2)
    with col[0]:
        if st.button("论文抽取"):
            st.session_state.clear()
            mission_type = "论文抽取"
            st.session_state.mission_type = mission_type
            st.rerun()
    with col[1]:
        if st.button("专利抽取"):
            st.session_state.clear()
            mission_type = "专利抽取"
    
            st.session_state.mission_type = mission_type
            st.rerun()
    
             
if __name__ == "__main__":
    if "mission_type" not in st.session_state:
        article_or_patent()
    else:
        if st.session_state.mission_type == "专利抽取":
            pantent()
        elif st.session_state.mission_type == "论文抽取":
            article()
         