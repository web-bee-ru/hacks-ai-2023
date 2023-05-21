import streamlit as st
import pandas as pd

csv_train = './train_dataset_cb/train.csv'
csv_test = './train_dataset_cb/test.csv'
df_train = pd.read_csv(csv_train, parse_dates=['Крайний срок', 'Дата обращения', 'Дата восстановления', 'Дата закрытия обращения'])


# services = st.multiselect("Query", query)

# мне кажется, что надо аналитический дашборд делать, в котором пользователь может (как в икселе) выбрать (отфильтровать, везде возможен мультивыбор):
# - тип (сервис/ФГ/система/место)
# - квалификацию (запрос, инцидент, r2i, i2r)
# - время (обращ/восстано/закрытия)
# - критичность (1234)
# - влияние (1234)
# - приоритет (1234)

ALL = 'Все'



# ['1-Особая', '2-Повышенная', '3-Базовая', '4-Нет']
arr = list(df_train['Критичность'].unique())
arr.sort()
opts_CRIT = arr.copy()

# ['1-Всеохватывающее', '2-Значительное', '3-Малое', '4-Нет влияния']
arr = list(df_train['Влияние'].unique())
arr.sort()
opts_IMPACT = arr.copy()

# ['0-Критический', '1-Высокий', '2-Средний', '3-Низкий']
arr = list(df_train['Приоритет'].unique())
arr.sort()
opts_PRIORITY = arr.copy()

def multiselect_query_wrapper(name, *args, **kwargs):
    query = st.experimental_get_query_params()
    selected = st.multiselect(*args, default=query[name] if name in query else None, **kwargs)
    query[name] = selected
    st.experimental_set_query_params(**query)
    return selected

def select_query_wrapper(name, *args, **kwargs):
    query = st.experimental_get_query_params()
    params = args[1]
    selected = st.selectbox(*args, **kwargs, index= params.index(query[name][0]) if name in query else 0 )
    query[name] = selected
    st.experimental_set_query_params(**query)
    return selected


def multiselect_type(**kwargs):
    opts_TYPE = ['Сервис', 'Функциональная группа', 'Система', 'Место']
    return select_query_wrapper('ms_type',"Тип", opts_TYPE, **kwargs)

def multiselect_qual(**kwargs):
    opts_QUAL = ['Запрос', 'Инцидент', 'Запрос->Инцидент', 'Инцидент->Запрос']
    return multiselect_query_wrapper('ms_qual',"Квалифицировано", opts_QUAL, **kwargs)

def multiselect_time(**kwargs):
    opts_TIME = ['Крайний срок', 'Дата обращения', 'Дата восстановления', 'Дата закрытия обращения']
    return multiselect_query_wrapper('ms_time',"Время", opts_TIME, **kwargs)

def multiselect_crit(**kwargs):
    return multiselect_query_wrapper('ms_crit',"Критичность", opts_CRIT, **kwargs)

def multiselect_impact(**kwargs):
    return multiselect_query_wrapper('ms_impact',"Влияние", opts_IMPACT, **kwargs)

def multiselect_priority(**kwargs):
    return multiselect_query_wrapper('ms_priority',"Приоритет", opts_PRIORITY, **kwargs)


selected_TYPE = multiselect_type()
selected_QUAL = multiselect_qual()
selected_TIME = multiselect_time()
selected_CRIT = multiselect_crit()
selected_IMPACT = multiselect_impact()
selected_PRIORITY = multiselect_priority()


