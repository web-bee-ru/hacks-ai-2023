# from datetime import datetime as dt
import streamlit as st
# import streamlit.components.v1 as components
import pandas as pd
import altair as alt
import numpy as np
# import geopandas as gpd
# import folium
# from folium.plugins import MarkerCluster
import plotly.express as px
import datetime
import re
from datetime import timedelta

from utils.query import *

st.set_page_config(layout="wide", page_title="WebBee")

st.markdown('<div><a href="/" alt="Web-bee"><img src="https://drive.moskit.pro/f/f224bceb243b47a6b8f7/?dl=1" width="140"></a></h3>', unsafe_allow_html=True)

col_header, col_links = st.columns([7, 1])

with col_header:
    st.header("Цифровой Прорыв 2023: Кейс ЦБ РФ")
with col_links:
    st.write("")
    st.download_button(label="Презентация", data="https://drive.moskit.pro/f/2eac6a0db66c45df87bc/?dl=1", file_name="presentation.pptx")

st.subheader("Отфильтруйте обращения")
st.markdown("Выберите только те данные, которые вам нужны. Можете обновлять страницу, ваш фильтр сохранится.", unsafe_allow_html=False)

csv_train = './train_dataset_cb/train.csv'
csv_test = './train_dataset_cb/test.csv'
cols_DATE = ['Крайний срок', 'Дата обращения', 'Дата восстановления', 'Дата закрытия обращения']
df_train = pd.read_csv(csv_train, parse_dates=cols_DATE)
df_test = pd.read_csv(csv_test, parse_dates=cols_DATE).drop('id', axis=1)

col11, col12, col13 = st.columns([2, 2, 2])
col21, col22, col23 = st.columns([2, 2, 2])
col31, col32, col33, col34 = st.columns([4, 4, 2, 2])


with col11:
    selected_IMPACT = multiselect_impact()
with col12:
    selected_QUAL = multiselect_qual()
with col13:
    opts_DATASET = ['train', 'test']
    selected_DATASET = multiselect_query_wrapper('dataset', "Датасет", opts_DATASET, default=opts_DATASET)
    df = pd.DataFrame()
    if 'train' in selected_DATASET:
        df = pd.concat([df, df_train], ignore_index=True)
    if 'test' in selected_DATASET:
        df = pd.concat([df, df_test], ignore_index=True)
    df = df.reindex()
    df_full = df.copy()
    # st.write(len(df))

with col21:
    selected_PRIORITY = multiselect_priority()
with col22:
    selected_TYPE = multiselect_type()
# with col23:
    # тут (ниже) добавляется еще 1 комбик

with col31:
    selected_CRIT = multiselect_crit()
with col32:
    selected_COL_DATE = select_query_wrapper('date-type', 'Тип даты', cols_DATE, default_index=1)
    min_date = df[selected_COL_DATE].min()
    max_date = df[selected_COL_DATE].max()
with col33:
    date_FROM = st.date_input("Дата начала", min_date, min_value=min_date, max_value=max_date)
with col34:
    date_TO = st.date_input("Дата окончания", max_date, min_value=min_date, max_value=max_date)

if selected_TYPE:
    arr = list(df[selected_TYPE].unique())
    arr.sort()
    opts_for_selected_type = arr.copy()
    with col23:
        selected_TYPE_ITEM = multiselect_query_wrapper(selected_TYPE, selected_TYPE, opts_for_selected_type)

qs = [
    f'`{selected_COL_DATE}` > @date_FROM',
    f'`{selected_COL_DATE}` < @date_TO'
]
if selected_TYPE and len(selected_TYPE_ITEM) != 0:
    qs.append(f'`{selected_TYPE}` in @selected_TYPE_ITEM')

if len(selected_IMPACT) != 0:
    qs.append(f'`Влияние` in @selected_IMPACT')
if len(selected_PRIORITY) != 0:
    qs.append(f'`Приоритет` in @selected_PRIORITY')
if len(selected_CRIT) != 0:
    qs.append(f'`Критичность` in @selected_CRIT')

if len(qs) != 0:
    df = df.query(' and '.join(qs))
# st.write(len(df))
# st.write(' and '.join(qs))

if len(selected_QUAL) != 0:
    qs = []
    if 'Запрос' in selected_QUAL:
        qs.append(f'`Тип обращения на момент подачи` == "Запрос"')
    if 'Инцидент' in selected_QUAL:
        qs.append(f'`Тип обращения на момент подачи` == "Инцидент"')
    if 'Запрос->Инцидент' in selected_QUAL:
        qs.append(f'`Тип переклассификации` == 1')
    if 'Инцидент->Запрос' in selected_QUAL:
        qs.append(f'`Тип переклассификации` == 2')

    if len(qs) != 0:
        df = df.query(' or '.join(qs))

COLUMNS = df.columns.tolist()

st.write("---")
st.subheader("Проанализируйте отфильтрованные обращения")

with st.container():
    st.markdown("##### 1. Группируйте обращения по любым столбцам")
    col1, col2 = st.columns([2, 1])
    with col2:
        selected_GR1 = st.selectbox('grouper 1', COLUMNS, index=0)
        selected_GR2 = st.selectbox('grouper 2', COLUMNS, index=9)
        selected_GR3 = st.selectbox('grouper 3', COLUMNS, index=1)
    with col1:
        df_gr = df.copy()
        df_gr['counter'] = 1
        df_gr = df_gr.groupby(
            np.unique([selected_GR1, selected_GR2, selected_GR3]).tolist()
        ).counter.count().reset_index()
        st.write(df_gr)
    st.write("---")



with st.container():
    st.markdown("##### 2. Анализируйте обращения в разрезах по времени")
    col1, col2 = st.columns([2, 1])
    with col2:
        selected_BARCHART_X = st.selectbox('Ось X', cols_DATE, index=1, key='selected_BARCHART_X')
        selected_BARCHART_COLOR = st.selectbox('Цвет', COLUMNS, index=1, key='selected_BARCHART_COLOR')
        selected_BARCHART_BINS = st.radio('Столбцы', [
            'По дням',
            'По часам',
            'По часу в дне',
            'По дню в неделе',
            'По дню в месяце',
        ])
        # st.write(selected_BARCHART_BINS)
    with col1:
        df_barchart = df.copy()
        nbins = None
        if selected_BARCHART_BINS == 'По дням':
           nbins = int((max_date - min_date) / timedelta(days=1))
        if selected_BARCHART_BINS == 'По часам':
            nbins = int((max_date - min_date) / timedelta(hours=1))
        if selected_BARCHART_BINS == 'По часу в дне':
           df_barchart[selected_BARCHART_X] = df_barchart[selected_BARCHART_X].dt.hour
        if selected_BARCHART_BINS == 'По дню в неделе':
           df_barchart[selected_BARCHART_X] = df_barchart[selected_BARCHART_X].dt.dayofweek
        if selected_BARCHART_BINS == 'По дню в месяце':
           df_barchart[selected_BARCHART_X] = df_barchart[selected_BARCHART_X].dt.day
        bar = px.histogram(df_barchart, x=selected_BARCHART_X, color=selected_BARCHART_COLOR, nbins=nbins)
        st.plotly_chart(bar, use_container_width=True)
    st.write("---")


with st.container():
    st.markdown("##### 3. Сравнивайте обращения между собой")
    col1, col2 = st.columns([2, 1])
    with col2:
        selected_LINE_X = st.selectbox('Ось X', cols_DATE, index=1, key='selected_LINE_X')
        selected_LINE_COLOR = st.selectbox('Цвет', COLUMNS, index=1, key='selected_LINE_COLOR')
        selected_LINE_CUMULATIVE = st.checkbox('Накопительный', key='selected_LINE_CUMULATIVE')
    with col1:
        df_line = df.copy()
        df_line['counter'] = 1
        df_line = df_line.groupby(
            # [selected_LINE_COLOR, selected_LINE_X]
            [selected_LINE_COLOR, pd.Grouper(key=selected_LINE_X, freq="1d")]
            # np.unique([selected_LINE_X, selected_LINE_COLOR]).tolist()
        )['counter'].count().reset_index()
        df_line['counter_cumsum'] = df_line.groupby(
            [selected_LINE_COLOR]
        )['counter'].cumsum()
        line = px.line(df_line, x=selected_LINE_X, y='counter_cumsum' if selected_LINE_CUMULATIVE else 'counter', color=selected_LINE_COLOR)
        st.plotly_chart(line, use_container_width=True)
        # st.write(df_line)
    st.write("---")


with st.container():
    st.markdown("##### 4. Оценивайте распределение обращений по любым полям")
    col1, col2 = st.columns([2, 1])
    with col2:
        selected_PIE_GROUP = st.selectbox('Группировка', COLUMNS, index=13, key='selected_PIE_COUNT')
        # selected_PIE_COLOR = st.selectbox('Цвет', COLUMNS, index=1, key='selected_PIE_COLOR')
    with col1:
        df_pie = df.copy()
        df_pie['counter'] = 1
        df_pie = df_pie.groupby(
            np.unique([selected_PIE_GROUP]).tolist()
        ).counter.count().reset_index()
        pie = px.pie(df_pie, values='counter', color=selected_PIE_GROUP, labels=False)
        st.plotly_chart(pie, use_container_width=True)
    st.write("---")



with st.container():
    st.markdown("##### 5. Визуализируйте отклонения от общей массы")
    col1, col2 = st.columns([2, 1])
    with col2:
        selected_SC_1 = st.selectbox('Ось X', COLUMNS, key='selected_SC_1', index=6)
        selected_SC_2 = st.selectbox('Ось Y', COLUMNS, key='selected_SC_2', index=5)
        selected_SC_3 = st.selectbox('Цвет', COLUMNS, key='selected_SC_4', index=1)
    with col1:
        df_sc = df.copy()
        df_sc['counter'] = 1
        df_sc = df_sc.groupby(
            np.unique([selected_SC_1, selected_SC_2, selected_SC_3]).tolist()
        ).counter.count().reset_index()
        scatter = px.scatter(df_sc, x=selected_SC_1, y=selected_SC_2, color=selected_SC_3)
        st.plotly_chart(scatter, use_container_width=True)
    st.write("---")


with st.container():
    st.markdown("##### 6. Оцените зависимость систем")

    sys_graph_df = df_full[df_full['Содержание'].str.contains('Система') == True]
    sys_graph_df['Система в содержании'] = [str(a) in str(b) for a, b in zip(sys_graph_df['Система'], sys_graph_df['Содержание'])]
    sys_graph_df = sys_graph_df[sys_graph_df['Система в содержании'] == False]
    sys_graph_df['Обращение к системе'] = [re.findall(r"((Система|База)\d*)", line)[0][0] for line in list(sys_graph_df['Содержание'])]
    sys_graph_df['Кол-во'] = 1
    sys_graph_df = sys_graph_df.groupby(['Система', 'Обращение к системе']).count().reset_index()
    sys_graph_df = sys_graph_df[['Система', 'Обращение к системе', 'Кол-во']]
    sys_graph_lst = list(zip(sys_graph_df['Система'], sys_graph_df['Обращение к системе'], sys_graph_df['Кол-во']))

    graph_squads_res = []
    graph_used_biba = []

    graph_max_weight = max(list(sys_graph_df['Кол-во']))

    def get_graph_deps(main_biba, arr):
        finds = []
        for biba, boba, _ in sys_graph_lst:
            if biba == main_biba and boba not in graph_used_biba:
                finds.append(boba)
            if boba == main_biba and biba not in graph_used_biba:
                finds.append(biba)
        return finds

    def append_graph_nodes(biba, arr):
        if biba in graph_used_biba:
            return
        graph_used_biba.append(biba)
        all_bobs = get_graph_deps(biba, arr)
        for boba in list(set(all_bobs)):
            count = 0
            for b in all_bobs:
                if b == boba:
                    count += 1
            if count > 1:
                arr.append([boba,biba])
            arr.append([biba,boba])
            append_graph_nodes(boba, arr)

    for (biba,_, _) in sys_graph_lst:
        if biba in graph_used_biba:
            continue
        n_arr = []
        append_graph_nodes(biba, n_arr)
        graph_squads_res.append(n_arr)

    graph_not_base_squads = []
    graph_base_squad = None

    for squad in graph_squads_res:
        is_base_squad = False
        for pair in squad:
            if 'База' in pair:
                is_base_squad = True
        if is_base_squad:
            graph_base_squad = squad
        else:
            graph_not_base_squads.append(squad)

    def get_graph_weight(biba, boba):
        for c_biba, c_boba, weight in sys_graph_lst:
            if biba == c_biba and boba == c_boba:
                return weight
        return 0

    def draw_graph(squads, graph_type):
        str_g = '''
        digraph G {
            layout=''' + graph_type + ''';
            fontsize="20";
            bgcolor="#252525";
    
            graph [ fontname=Arial, fontcolor=blue ]; 
            node [ fontname="sans-serif", fillcolor="#5a5857", style=filled, fontcolor="#FAFAFA", fixedsize=true ]; 
            edge [ fontname=Helvetica, color="#FAFAFA", fontcolor=red ]; 
        '''

        if selected_TYPE == 'Система':
            for service in selected_TYPE_ITEM:
                f = False
                for squad in squads:
                    for pair in squad:
                        f = f or service in pair
                if f:
                    str_g += service + ' [fillcolor="#cb9700", style=filled];'

        for i, squad in enumerate(squads):
            for biba, boba in squad:
                weight = get_graph_weight(biba, boba)
                str_g += '"' + biba  + '" -> "' + boba + '" [dir=forward, penwidth=' + str(weight / graph_max_weight * 3 + .5) + '];'

        str_g += '''
        } 
        '''

        st.graphviz_chart(str_g)

    graph_type = st.selectbox("Тип графа", ['dot', 'twopi', 'neato'])
    if graph_base_squad:
        draw_graph([graph_base_squad],graph_type)
    draw_graph(graph_not_base_squads, graph_type)

    st.write("---")
    ##### Конец пункта с графами #####



with st.container():
    st.markdown("##### 7. Или просто посмотрите все данные, которые мы можем предоставить по отфильтрованным обращениям")
    st.write(df)
    # st.write(len(df))

    st.write("---")
st.markdown('<div style="text-align: center;"><a href="https://web-bee.ru/" alt="Web-bee"><img src="https://drive.moskit.pro/f/dc718d4d56e5452288a7/?dl=1" width="140"></a></h3>', unsafe_allow_html=True)
