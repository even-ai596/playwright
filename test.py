from bs4 import BeautifulSoup

def extract_author_institutions(html):
    """
    从HTML中提取作者单位信息
    
    参数:
        html (str): 包含作者单位信息的HTML片段
        
    返回:
        list: 作者单位列表
    """
    soup = BeautifulSoup(html, 'html.parser')
    institutions = []
    
    # 查找所有class为'author'的h3标签
    for author_section in soup.find_all('h3', class_='author'):
        # 跳过包含作者姓名的部分（通常有id="authorpart"）
        if 'id' in author_section.attrs and 'authorpart' in author_section['id']:
            continue
            
        # 提取单位信息
        for span in author_section.find_all('span'):
            a_tag = span.find('a')
            if a_tag:
                # 获取纯文本并去除首尾空白
                institution = a_tag.get_text(strip=True)
                if institution:  # 确保不是空字符串
                    institutions.append(institution)
                    
    return institutions

# 示例使用
html = """[<h3 class="author" id="authorpart"> <span> <a href="https://kns.cnki.net/kcms2/author/detail?v=qQX4xeHgc6tnffUvggAfhGvOJxQsJq-MZLDKUF4Mmug_90YOlB8_PI8YCJstxSLshfwFd5ZTlhzRqpSJlQsczXdV83iQSxIqKbyDBmdcdkgi5qj8dARSnw==&amp;uniplatform=NZKPT&amp;language=CHS" target="_blank">高帅<sup>1,2</sup></a> <input class="authorcode" type="hidden" value="000028143267"/> </span><span> <a href="https://kns.cnki.net/kcms2/author/detail?v=qQX4xeHgc6tnffUvggAfhGvOJxQsJq-M1eZ7AG1Ok1woIxjm227o6d8PpU5EOx9HVIPcMh2oMCjxuPHDI9ix3Eg4bwoRfGJTUxhifDdYQRFv764bY_RJpw==&amp;uniplatform=NZKPT&amp;language=CHS" target="_blank">赵林<sup>1,2</sup></a> <input class="authorcode" type="hidden" value="000033461281"/> </span><span> <a href="https://kns.cnki.net/kcms2/author/detail?v=qQX4xeHgc6tnffUvggAfhGvOJxQsJq-MKpKpL1ERgP510mhjomkUhzTkQNVHE7Hv237H7oghdye5XTrr-ivHOmCtaqUm_NvX0ZoE_qk4NW6N3u7xvClK-UAgyWbCYldh&amp;uniplatform=NZKPT&amp;language=CHS" target="_blank">徐占河<sup>1,2</sup></a> <input class="authorcode" type="hidden" value="000023949292"/> </span><span> <a href="https://kns.cnki.net/kcms2/author/detail?v=qQX4xeHgc6tnffUvggAfhGvOJxQsJq-M1EVDYhDE6c8EdCvbh82t5KlwqijAMmDSbNGg1qNd9L9GVI6gOxxJ7B2q9-fibsIFkBSr-R36Y9epByoDdLTZnKNhkWpC0REU&amp;uniplatform=NZKPT&amp;language=CHS" target="_blank">袁瑞铭<sup>1,2</sup></a> <input class="authorcode" type="hidden" value="000025709579"/> </span><span> <a href="https://kns.cnki.net/kcms2/author/detail?v=qQX4xeHgc6tnffUvggAfhGvOJxQsJq-M9yEMgmUleaFzfg0PmBhhAmycI7inB1I3H_oLzFokcok2ELtheLm11YlCB7TQjbBZ0v4JcsfXqOzaL7KPo5SZqzlaPkuJJeMT&amp;uniplatform=NZKPT&amp;language=CHS" target="_blank">周丽霞<sup>1,2</sup></a> <input class="authorcode" type="hidden" value="000065320938"/> </span> </h3>, <h3 class="author"> <span> <a href="https://kns.cnki.net/kcms2/organ/detail?v=qQX4xeHgc6sE2S3UH3HSKX-VAL9ml5yamHD3L8HcFJyu5-_U1pigj6eLWdGxeyfaJEeQ0b8PitgENwqE2xXFFmmZkgnqk0HiANSouyiE9fbV4EH8E6VY7ndZbr9TyxdHmo_8T36iND_bI8x9g50RRRs2yGjGD6gm3FDE-mIcg4HxsYxNnnUpcvDtg99JUjHNIrkYUJ5MNgLlOpfqOq9OZocWD8FQcML2VWAOitmsWRb2Zo27eMHuq_b7tbeE3rqQOqN-82aFD3Vam2pBGl8uof6GdbfP8FsL&amp;uniplatform=NZKPT&amp;language=CHS" target="_blank">                    1.国网冀北电力有限公司电力科学研究院</a> </span><span> <a href="https://kns.cnki.net/kcms2/organ/detail?v=qQX4xeHgc6sE2S3UH3HSKWLwg-zR0_Nk54Alm_gy966AFKb914uPjnjdrs-G0stmotZU0INwIirt6OcSymMcvUsciK-N2BpugHD1e28OZrox2RqcZ8FsIxsDBHubxDFbPQiwvwuwFIOiHdXXMLUyHmGWxUsJTDfHgPz3aT1RIw9zku9ZVvtWZS0RJU5SuoU17P_ADoBl7gD4gZbJ8Zk5bJUVZ6v2pHF0p_MfiTzZlU3NQI_3vfjR4C10_LM8nNqdQl0Ua7snPPMX2PDblsr_x_kDl-wlcCr-TKXV6rSsjycVka8x5nEHr_vViVnyP088LcGhc8ukaubvvJmKq3aHoN8fEnZiv5fbDUvRsehoy0syi1MW3kzHCQ==&amp;uniplatform=NZKPT&amp;language=CHS" target="_blank">                    2.华北电力科学研究院有限责任公司电气测量技术研究所</a> </span> </h3>]"""
institutions = extract_author_institutions(html)
print(institutions)

