import streamlit as st
from zhipuai import ZhipuAI
import json
import os

# 设置页面配置
st.set_page_config(page_title="UI Demo", layout="centered")

# 定义 topics 和 primary_topics_list
topics = {
    "药品": ["新药", "抗生素", "抗病毒药物", "降压药", "降脂药", "抗凝剂", "生物制剂", "靶向药物", "免疫调节剂", "疫苗", "治疗剂", "药物A", "药物B"],
    "竞品": ["竞争产品", "替代品", "对比药品", "市场上的其他选项", "竞争剂"],
    "疾病": ["心血管疾病", "癌症", "糖尿病", "高血压", "高血脂", "肺炎", "病毒感染", "风湿性疾病", "自身免疫性疾病", "神经退行性疾病", "疾病X", "疾病Y"],
    "医疗器械": ["诊断设备", "治疗设备", "手术器械", "监测设备", "辅助设备", "假体", "植入物"],
    "检查/诊断": ["影像学检查", "实验室检测", "病理诊断", "临床评估", "体检", "健康筛查"],
    "治疗方法": ["外科手术", "药物治疗", "介入治疗", "物理治疗", "心理治疗", "替代疗法", "综合治疗方案"],
    "研究领域": ["生物医学研究", "药理学研究", "临床试验", "基础研究", "应用研究", "转化研究"],
    "健康与保健": ["健康生活方式", "营养补充", "运动健身", "心理健康", "养生保健", "预防措施", "个人卫生"]
}

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
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
            {"role": "system", "content": f'''
你的职责是给文本打标签，标签只能在下面的类别里,最多最多选三个最接近的,不需要解释，直接返回结果即可,不需要任何其他文字,如果判断内容不符合任何标签，返回out of label
{','.join(primary_topics_list)}
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
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
       {"role": "system", "content": f'''
你的职责是改写文本，原则尽量使用原始文本内容
 
严格遵循下面的规范文本样式：
一名{institution}的{person}提出{{观点}},{{内容间的逻辑关系}},{{进一步的方案}}

执行逻辑：
1.如果判断原始文本缺失太多内容，请礼貌提醒，无需执行下面的任何步骤或者逻辑
2. 否则： ”一名{institution}的{person}提出“， 不需要修改
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
    st.header("Select Options")
    
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
st.write(f"**Person:** {person}")

# 替换默认标签，按逗号分词
if 'tags' in st.session_state:
    user_generated_tags = st.session_state.tags.split(",")  # 按逗号分词
    tag_html = " ".join([f'<span class="tag" style="background-color: {match_color(tag.strip())};">{tag.strip()}</span>' for tag in user_generated_tags])
    st.markdown(f"**AutoTags:** {tag_html}", unsafe_allow_html=True)

# 创建按钮和可编辑文本区域
if st.button("ReWrite"):
    rewrite_text = rewrite(user_input, institution, person)
    st.session_state.rewrite_text = rewrite_text  # 将改写后的文本存储到会话状态

if 'rewrite_text' in st.session_state:
    user_editable_text = st.text_area("Editable Rewritten Text:", st.session_state.rewrite_text)
    st.session_state.rewrite_text = user_editable_text  # 更新会话状态中的文本
    # st.write(user_editable_text)

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
