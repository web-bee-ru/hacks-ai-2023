import streamlit as st
import pandas as pd
from datetime import datetime

_csv_train = './train_dataset_cb/train.csv'
_df_train = pd.read_csv(_csv_train, parse_dates=['Крайний срок', 'Дата обращения', 'Дата восстановления', 'Дата закрытия обращения'])


# services = st.multiselect("Query", query)

# мне кажется, что надо аналитический дашборд делать, в котором пользователь может (как в икселе) выбрать (отфильтровать, везде возможен мультивыбор):
# - тип (сервис/ФГ/система/место)
# - квалификацию (запрос, инцидент, r2i, i2r)
# - время (обращ/восстано/закрытия)
# - критичность (1234)
# - влияние (1234)
# - приоритет (1234)

# ALL = 'Все'


# ['1-Особая', '2-Повышенная', '3-Базовая', '4-Нет']
_arr = list(_df_train['Критичность'].unique())
_arr.sort()
_opts_CRIT = _arr.copy()

# ['1-Всеохватывающее', '2-Значительное', '3-Малое', '4-Нет влияния']
_arr = list(_df_train['Влияние'].unique())
_arr.sort()
_opts_IMPACT = _arr.copy()

# ['0-Критический', '1-Высокий', '2-Средний', '3-Низкий']
_arr = list(_df_train['Приоритет'].unique())
_arr.sort()
_opts_PRIORITY = _arr.copy()

def date_query_wrapper(name, *args, **kwargs):
    def change_url_query():
        query = st.experimental_get_query_params()
        current_value = st.session_state[name] 
        query[name] = current_value
        st.experimental_set_query_params(**query)

    label = args[0]
    default = args[1]

    query = st.experimental_get_query_params()
    return st.date_input(label, datetime.strptime(query[name][0], '%Y-%m-%d').date() if name in query else default, on_change=change_url_query, key=name, **kwargs)

def multiselect_query_wrapper(name, *args, **kwargs):
    def change_url_query():
        query = st.experimental_get_query_params()
        current_value = st.session_state[name] 
        query[name] = current_value
        st.experimental_set_query_params(**query)

    
    default_index = kwargs['default'] if 'default' in kwargs else None
    if 'default' in kwargs:
        del kwargs['default']

    query = st.experimental_get_query_params()
    selected = st.multiselect(*args, default=query[name] if name in query else default_index, on_change=change_url_query, key=name, **kwargs)
    query[name] = selected
    return selected

def select_query_wrapper(name, *args, **kwargs):
    
    def change_url_query():
        query = st.experimental_get_query_params()
        current_value = st.session_state[name] 
        query[name] = current_value
        st.experimental_set_query_params(**query)
        
    default_index = kwargs['default_index'] if 'default_index' in kwargs else 0
    if 'default_index' in kwargs:
        del kwargs['default_index']

    query = st.experimental_get_query_params()
    params = args[1]
    selected = st.selectbox(*args, index= params.index(query[name][0]) if name in query else default_index, on_change=change_url_query, key=name, **kwargs)
    return selected


def multiselect_type(**kwargs):
    opts_TYPE = ['Сервис', 'Функциональная группа', 'Система', 'Место']
    return select_query_wrapper('ms_type', "Тип", opts_TYPE, **kwargs)

def multiselect_qual(**kwargs):
    opts_QUAL = ['Запрос', 'Инцидент', 'Запрос->Инцидент', 'Инцидент->Запрос']
    return multiselect_query_wrapper('ms_qual', "Квалифицировано", opts_QUAL, **kwargs)

# def multiselect_dataset(**kwargs):
#     opts_DATASET = ['train', 'test']
#     return multiselect_query_wrapper('ms_dataset', "Датасет", opts_DATASET, **kwargs)

def multiselect_time(**kwargs):
    opts_TIME = ['Крайний срок', 'Дата обращения', 'Дата восстановления', 'Дата закрытия обращения']
    return multiselect_query_wrapper('ms_time', "Время", opts_TIME, **kwargs)

def multiselect_crit(**kwargs):
    return multiselect_query_wrapper('ms_crit', "Критичность", _opts_CRIT, **kwargs)

def multiselect_impact(**kwargs):
    return multiselect_query_wrapper('ms_impact', "Влияние", _opts_IMPACT, **kwargs)

def multiselect_priority(**kwargs):
    return multiselect_query_wrapper('ms_priority', "Приоритет", _opts_PRIORITY, **kwargs)


# selected_TYPE = multiselect_type()
# selected_QUAL = multiselect_qual()
# selected_TIME = multiselect_time()
# selected_CRIT = multiselect_crit()
# selected_IMPACT = multiselect_impact()
# selected_PRIORITY = multiselect_priority()


