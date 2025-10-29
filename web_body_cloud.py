# web_body_cloud.py
import json, urllib.request, datetime, os, streamlit as st

st.set_page_config(page_title="AI体质评估", page_icon="🌿")
st.title("🌿 AI中医体质评估 · 云端版")

@st.cache_data(show_spinner=False)
def ask_gpt(age, sex, scores):
    url = "https://api.openai.com/v1/chat/completions"
    prompt = f"""你是一位中医健康管理师，请根据以下问卷得分（满分45）给出：1. 体质类型（单选：平和质/气虚质/阳虚质/阴虚质/痰湿质/湿热质/血瘀质/气郁质/特禀质）2. 一句话解释（≤50字）3. 三条可执行养生建议（食疗/运动/作息）输出 JSON 格式：{{"体质":"","解释":"","建议":{{"食疗":"","运动":"","作息":""}}}} 年龄：{age} 性别：{sex} 问卷得分：{scores} 总分：{sum(scores)}"""
    data = {"model":"gpt-3.5-turbo","temperature":0.3,"messages":[{"role":"user","content":prompt}]}
    headers = {"Content-Type":"application/json","Authorization":f"Bearer {os.getenv('OPENAI_API_KEY')}"}
    req = urllib.request.Request(url,data=json.dumps(data).encode(),headers=headers)
    raw = urllib.request.urlopen(req).read().decode()
    content = json.loads(raw)["choices"][0]["message"]["content"].strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(content)

QUESTIONS = ["您容易疲乏吗？","您容易气短吗？","您心慌心悸吗？","您头晕或站起晕眩吗？","您喜欢安静懒得说话吗？","您说话声音低弱无力吗？","您怕冷、手脚发凉吗？","您容易失眠多梦吗？","您容易便秘或大便稀溏吗？"]

with st.form("form"):
    age = st.number_input("年龄",1,120,30)
    sex = st.radio("性别",["男","女"])
    scores = [st.slider(q,1,5,3) for q in QUESTIONS]
    submitted = st.form_submit_button("生成报告")

if submitted:
    if not os.getenv("OPENAI_API_KEY"):
        st.error("管理员未配置 OPENAI_API_KEY，暂不可用"); st.stop()
    with st.spinner("正在生成报告..."):
        r = ask_gpt(age, sex, scores)
    st.success("完成！")
    st.subheader(f"体质：{r['体质']}")
    st.write("**解释：**", r["解释"])
    for k,v in r["建议"].items():
        st.write(f"**{k}：**{v}")
    txt = f"体质：{r['体质']}\n解释：{r['解释']}\n建议：\n"
    for k,v in r["建议"].items(): txt += f"  {k}：{v}\n"
    txt += "\n仅供养生参考，不能替代诊疗！\n"
    file_name = f"体质报告_{age}岁_{sex}_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt"
    st.download_button("📥 下载报告", txt, file_name=file_name)