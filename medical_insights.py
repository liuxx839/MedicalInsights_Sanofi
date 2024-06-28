import streamlit as st
from zhipuai import ZhipuAI
import json
import os
import re

# 在主程序文件的开头
from config import (
    topics, 
    generate_tag_system_message, 
    rewrite_system_message, 
    prob_identy_system_message,
    institutions,
    departments,
    persons
)

# 设置页面配置
st.set_page_config(page_title="Medical Insights", layout="centered")

# 定义 topics 和 primary_topics_list
# topics = {
#   "获益/风险": ["治疗效果", "安全性评估", "副作用管理", "成本效益分析"],
#   "竞争产品": ["市场替代品", "竞品分析", "市场份额", "产品比较"],
#   "医疗器械与设备": ["医疗技术", "设备性能", "操作流程", "维护与校准"],
#   "疾病诊断与治疗": ["诊断标准", "治疗方案", "疗效评估", "并发症处理"],
#   "指南与共识": ["临床实践指南", "专家共识", "政策建议", "标准操作流程"],
#   "卫生政策与环境": ["卫生法规", "政策影响", "健康经济学", "医疗体系分析"],
#   "患者旅程、准入与支持": ["患者体验", "医疗准入", "患者支持计划", "健康教育资源"],
#   "证据生成(临床试验/研究/医学发表)": ["临床试验设计", "研究成果", "医学论文", "数据共享政策"],
#   "赛诺菲产品(疗效/安全性/其他)": ["产品特性", "临床试验结果", "患者反馈", "市场表现"],
#   "科学数据": ["数据收集", "数据分析", "结果解释", "数据保护"]
# }
primary_topics_list = list(topics.keys())

# 颜色映射，超过7个颜色的primary_topics_list都赋予粉色
color_list = [
    "#FF6347",  # 番茄红
    "#4682B4",  # 钢蓝色
    "#32CD32",  # 石灰绿色
    "#FFD700",  # 金色
    "#EE82EE",  # 紫罗兰
    "#8A2BE2",  # 蓝紫色
    "#FF4500"   # 橙红色
]

# 默认粉色用于超过7个颜色的主题
default_color = "#FF69B4"  # 粉色

# 按照顺序为 primary_topics_list 分配颜色
colors = {}
for i, topic in enumerate(primary_topics_list):
    colors[topic] = color_list[i] if i < len(color_list) else default_color

# 创建 ZhipuAI 客户端
api_key = os.environ.get("ZHIPU_API_KEY")
client = ZhipuAI(api_key=api_key)

# 修改generate_tag函数
def generate_tag(text):
    completion = client.chat.completions.create(
        model="glm-4-air",  # 填写需要调用的模型名称
        messages=[
            {"role": "system", "content": f'''
generate_tag_system_message.format(primary_topics_list=','.join(primary_topics_list))}
'''},       
            {"role": "user", "content": text}
        ],
        temperature=0.1,
        max_tokens=300,
    )
    summary = completion.choices[0].message.content.strip()
    return summary

def rewrite(text, institution, person):
    completion = client.chat.completions.create(
        model="glm-4-air",  # 填写需要调用的模型名称
        messages=[
       {"role": "system", "content": f'''
你的职责是改写文本，原则尽量使用原始文本内容
 
严格遵循下面的规范文本样式：
一名{institution}的{department}的{person}提出{{观点}},{{内容间的逻辑关系}},{{进一步的方案}}

执行逻辑：
1.如果判断原始文本缺失太多内容，请礼貌提醒，无需执行下面的任何步骤或者逻辑
2. 否则： ”一名{institution}的{department}的{person}提出“， 不需要修改
3。 原文如果存在的机构和人物，需要脱敏, 替换为“一名{institution}的{person}” 相应的部份
4.其中{{观点}},{{内容间的逻辑关系}},{{进一步的方案}} 要源于原始文本，尽量使用原文。不需要特别指出{{观点}},{{内容间的逻辑关系}},{{进一步的方案}}
5.只返回改写后的文本即可，无需解释。不要作额外推理
    '''},       
        {"role": "user", "content": text}
        ],
        temperature = .1,
        max_tokens = 300,
    )
    summary = completion.choices[0].message.content
    return summary

def prob_identy(text):
    completion = client.chat.completions.create(
        model="glm-4",
        messages=[
            {"role": "system", "content": '''
你是医学insight检测员指令
检查给定文本是否符合以下规则:

脱敏信息: 检查是否存在未脱敏的机构名或人名(包括仅姓氏),**但是具体的人物职务或者职称，并非敏感信息，算为已脱敏**
观点表述: 评估是否包含明确观点
逻辑关系: 分析内容逻辑性
解决方案: 判断是否提供进一步方案
字数要求: 确保字数>20

响应规则

综合判断：首先综合判断整体规则服从情况，只能从：“满足所有条件”，“基本满足”，“需要修改”三个词中选择
违反规则: 如果有违反情况，请简明指出问题,解释原因，不要罗嗦
            '''},       
            {"role": "user", "content": text}
        ],
        temperature=0.1,
        max_tokens=300,
    )
    summary = completion.choices[0].message.content
    return summary
  
# 修改match_color函数
def match_color(tag):
    tag = tag.strip()
    # 直接匹配一级分类
    if tag in primary_topics_list:
        return colors[tag]
    # 二级分类匹配
    for topic, keywords in topics.items():
        if tag in keywords:
            return colors[topic]
    return "#696969"  # 默认为灰色

# 标题
st.title("Medical Insights Tagging&Rewrite")

# 多选框和下拉菜单
with st.sidebar:
    st.markdown("""
    <div style="font-size:18px; font-weight:bold;">
    - Insight应涵盖4W要素（Who-谁、What-什么、Why-为什么、Wayfoward-未来方向）。<br>
    以下是一个合格样式的示例："一位{脱敏机构}的{科室}的{脱敏人物}指出{观点}，并阐述了{内容间的逻辑联系}，进而提出了{后续方案}"。<br>
    - Insight Copilot：您可以在下面提交您的初稿，然后使用此工具对内容进行打标或者重写。您还可以直接修改重写后的结果。
    </div>
    """, unsafe_allow_html=True)
  
    # st.header("Select Options")
    
    # 用户输入框
    user_input = st.text_area("Enter Medical Insights: ")

    # 生成标签
    if st.button("Generate Tags"):
        # 直接将用户输入的文本传递给 generate_tag 函数
        tags = generate_tag(user_input)
        # 去重复并存储生成的标签到会话状态
        unique_tags = list(set(tags.split(",")))  # 将标签按逗号分隔后转换为集合去重，再转换为列表
        st.session_state.tags = ",".join(unique_tags)  # 将去重后的标签列表转换为逗号分隔的字符串并存储到会话状态

    # # 显示生成的标签
    # if 'tags' in st.session_state:
    #     st.write("Generated Tags:", st.session_state.tags)

    # 一级主题选择
    primary_topics = st.multiselect("Select Primary Topics", primary_topics_list)
    
    # 二级主题选择
    secondary_topics = {}
    if primary_topics:
        for topic in primary_topics:
            secondary_topics[topic] = st.multiselect(f"Select Secondary Topics for {topic}", topics[topic])

    # 使用 selectbox 创建一个下拉菜单
    institution = st.selectbox(
        "Select Institution",
        [
            "大型医疗机构",
            "综合性医院",
            "专科医院",
            "三甲医院",
            "二甲医院",
            "城市医院",
            "省立医院",
            "地区医院",
            "医疗中心",
            "教学医院",
            "医疗集团",
            "医疗机构",
            "临床医院",
            "医疗服务中心"
        ]
    )

  # 使用 selectbox 创建一个下拉菜单
    department = st.selectbox(
        "Select Dsepartment",
        [
              "内分泌科",
              "肾移植科",
              "妇产科",
              "儿科",
              "急诊科",
              "心血管内科",
              "神经内科",
              "消化内科",
              "呼吸内科",
              "骨科",
              "泌尿外科",
              "心胸外科",
              "整形外科",
              "眼科",
              "耳鼻喉科",
              "口腔科",
              "皮肤科",
              "中医科",
              "康复科",
              "肿瘤科",
              "放射科",
              "检验科",
              "病理科",
              "药剂科",
              "麻醉科",
              "重症医学科",
              "感染性疾病科",
              "老年病科",
              "精神心理科",
              "肾内科",
              "血液科",
              "风湿免疫科",
              "营养科",
              "介入科",
              "核医学科",
              "超声科",
              "体检中心",
              "医学美容科"
       ]
    )

    # 使用另一个 selectbox 创建一个下拉菜单
    person = st.selectbox(
        "Select Person",
        [
            "专家",
            "医生",
            "主任医师",
            "副主任医师",
            "主治医师",
            "医疗团队成员",
            "研究人员",
            "学者",
            "顾问",
            "分析师",
            "工作人员",
            "主任",
            "副主任",
            "教授",
            "副教授",
            "讲师",
            "医疗保健提供者",
            "护士长",
            "护士",
            "研究员"
        ]
    )

# 主页面内容
st.write("### Selected Options")
primary_topic_tags = [f'<span class="tag" style="background-color: {colors[topic]};">{topic}</span>' for topic in primary_topics]
st.markdown(f"**Primary Topics:** {' '.join(primary_topic_tags)}", unsafe_allow_html=True)

secondary_topic_tags = []
for topic, subtopics in secondary_topics.items():
    for subtopic in subtopics:
        secondary_topic_tags.append(f'<span class="tag" style="background-color: {colors[topic]};">{subtopic}</span>')
st.markdown(f"**Secondary Topics:** {' '.join(secondary_topic_tags)}", unsafe_allow_html=True)

st.write(f"**Institution:** {institution}")
st.write(f"**Department:** {department}")
st.write(f"**Person:** {person}")

# 替换默认标签，按逗号分词
if 'tags' in st.session_state:
    # 使用正则表达式同时匹配逗号和空白作为分隔符
    user_generated_tags = re.split(r'[,\s]+', st.session_state.tags.strip())
    # 移除空字符串
    user_generated_tags = [tag for tag in user_generated_tags if tag]
    tag_html = " ".join([f'<span class="tag" style="background-color: {match_color(tag)};">{tag}</span>' for tag in user_generated_tags])
    st.markdown(f"**AutoTags:** {tag_html}", unsafe_allow_html=True)

# 创建按钮和可编辑文本区域
if st.button("ReWrite"):
    rewrite_text = rewrite(user_input, institution, person)
    potential_issues = prob_identy(user_input)
    st.session_state.rewrite_text = rewrite_text
    st.session_state.potential_issues = potential_issues

def determine_issue_severity(issues_text):
    if "满足所有条件" in issues_text or "文本符合要求" in issues_text:
        return "green"
    elif any(word in issues_text.lower() for word in ["需要修改"]):
        return "red"
    elif any(word in issues_text.lower() for word in ["基本满足"]):
        return "yellow"
    else:
        return "white"

if 'rewrite_text' in st.session_state:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Potential Issues:")
        background_color = determine_issue_severity(st.session_state.potential_issues)
        st.markdown(
            f"""
            <div style="background-color: {background_color}; color: black; padding: 10px; border-radius: 5px; font-family: sans-serif;">
                {st.session_state.potential_issues}
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.subheader("Editable Rewritten Text:")
        user_editable_text = st.text_area("", st.session_state.rewrite_text, height=300)
        st.session_state.rewrite_text = user_editable_text

# if 'rewrite_text' in st.session_state:
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Potential Issues:")
#         st.write(st.session_state.potential_issues)
    
#     with col2:
#         st.subheader("Editable Rewritten Text:")
#         user_editable_text = st.text_area("", st.session_state.rewrite_text, height=300)
#         st.session_state.rewrite_text = user_editable_text

# # 添加更多选项
# if st.checkbox("More"):
#     st.write("More options are selected.")

# 添加其他标签
st.markdown(
    """
    <style>
    .tag {
        display: inline-block;
        color: white;
        border-radius: 5px;
        padding: 5px;
        margin: 2px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 复选框选项
use_generated_text_and_tags = st.checkbox("Use Editable Rewritten Text and AutoTags", value=True)

# 生成并下载 JSON 文件
def create_json_data():
    if use_generated_text_and_tags and 'rewrite_text' in st.session_state and 'tags' in st.session_state:
        data = {
            "Medical_Insights": st.session_state.rewrite_text,
            "Tags": st.session_state.tags.split(",")
        }
    else:
        data = {
            "Medical_Insights": user_input,
            "Tags": primary_topics
        }
    return json.dumps(data, ensure_ascii=False, indent=4)

# 下载 JSON 文件
st.download_button(
    label="Download JSON",
    data=create_json_data(),
    file_name="medical_insights.json",
    mime="application/json"
)
