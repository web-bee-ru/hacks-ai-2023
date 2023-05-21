# Main

import re

import graphviz
# Mine
import pandas as pd
import plotly.express as px
import streamlit as st

df = pd.read_csv('./train_dataset_cb/train.csv', parse_dates=['Дата обращения', 'Дата закрытия обращения', 'Дата восстановления', 'Крайний срок'])



clist = df["Сервис"].unique().tolist()

services = st.multiselect("Сервис", clist)
request_type = st.selectbox("Тип", ['Все', 'Инцидент', 'Запрос'])

tt_df = df.copy()
tt_df['День даты обращения'] = df['Дата обращения'].dt.date
tt_df = tt_df.sort_values('День даты обращения').groupby(['Сервис', 'День даты обращения', 'Тип обращения итоговый']).count().reset_index()
tt_df['Кол-во обращения'] = tt_df['Содержание']
tt_df = tt_df[['Сервис', 'Кол-во обращения','День даты обращения', 'Тип обращения итоговый']]

if (len(services) != 0):
    tt_df = tt_df[tt_df['Сервис'].isin(services)]

if request_type != 'Все':
    tt_df = tt_df[tt_df['Тип обращения итоговый'] == request_type]

tt_df = tt_df[['Сервис', 'Кол-во обращения','День даты обращения']]

# st.dataframe(tt_df)
# st.dataframe(tt_df.groupby('Сервис').sum().reset_index())

c = px.line(tt_df, x='День даты обращения', y='Кол-во обращения', color='Сервис')
bar = px.bar(tt_df, x='День даты обращения', y='Кол-во обращения', color='Сервис')
scatter = px.scatter(df, x='Дата закрытия обращения', y='Крайний срок')
pie = px.pie(tt_df.groupby('Сервис').sum().reset_index(), values='Кол-во обращения', color='Сервис')

sys_df = df[df['Содержание'].str.contains('Система') == True]

sys_df['Система в содержании'] = [str(a) in str(b) for a, b in zip(sys_df['Система'], sys_df['Содержание'])]

sys_df = sys_df[sys_df['Система в содержании'] == False]

sys_df['Обращение к системе'] = [re.findall(r"((Система|База)\d+)", line)[0][0] for line in list(sys_df['Содержание'])]
sys_df = sys_df.drop_duplicates(subset=["Система", "Обращение к системе"], keep=False)

sys_gph_res = list(zip(sys_df['Система'], sys_df['Обращение к системе']))

n_res = []

used_biba = []



def get_deps(main_biba, arr):
    finds = []
    for biba, boba in sys_gph_res:
        if biba == main_biba and biba not in used_biba:
            finds.append(boba)
        if boba == main_biba:
            append_nodes(boba, arr)
    used_biba.append(main_biba)

    return finds

def append_nodes(biba, arr):
    if biba in used_biba:
        return

    all_bobs = get_deps(biba, arr)
    for boba in all_bobs:
        arr.append([biba,boba])
        append_nodes(boba, arr)

for (biba,_) in sys_gph_res:
    if biba in used_biba:
        continue
    n_arr = []
    append_nodes(biba, n_arr)
    n_res.append(n_arr)

graph = graphviz.Digraph()

with graph.subgraph() as s:
    s.attr(rank='same')
    for squad in n_res:
        for biba, boba in squad[:1]:
            s.node(biba)

for biba, boba in sys_gph_res:
    graph.edge(biba, boba)

st.plotly_chart(c)
st.plotly_chart(bar)
st.plotly_chart(scatter)
st.plotly_chart(pie)
st.graphviz_chart(graph)
