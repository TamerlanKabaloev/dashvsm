"""
Дашборд для системы динамического ценообразования
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pricing_matrix import PricingMatrix, PricingConfig

# Настройка страницы
st.set_page_config(
    page_title="Система динамического ценообразования",
    page_icon="💰",
    layout="wide"
)

# Инициализация сессии
if 'pricing_matrix' not in st.session_state:
    st.session_state.pricing_matrix = None
if 'config' not in st.session_state:
    st.session_state.config = None

def initialize_system():
    """Инициализация системы ценообразования"""
    config = PricingConfig(
        target_price=st.session_state.get('target_price', 5000.0),
        base_platskart_share=st.session_state.get('platskart_share', 0.6),
        min_coefficient=st.session_state.get('min_coef', 0.3),
        max_coefficient=st.session_state.get('max_coef', 2.5),
        num_classes=4,
        max_days_before_departure=105,
        max_load_percentage=100
    )
    
    matrix = PricingMatrix(config)
    
    # Применяем сохраненные коэффициенты сезонности
    if 'seasonality_coefs' in st.session_state:
        for month, coef in enumerate(st.session_state.seasonality_coefs, 1):
            matrix.set_seasonality_coefficient(month, coef)
    
    # Применяем сохраненные коэффициенты классов
    if 'class_coefs' in st.session_state:
        for class_idx, coef in enumerate(st.session_state.class_coefs):
            matrix.set_class_coefficient(class_idx, coef)
    
    return matrix, config

try:
    st.title("💰 Система динамического ценообразования")
    st.markdown("---")
    
    # Боковая панель с настройками
    with st.sidebar:
        st.header("⚙️ Настройки системы")
        
        # Основные параметры
        st.subheader("Основные параметры")
        target_price = st.number_input(
            "Целевая цена (₽)",
            min_value=100.0,
            max_value=100000.0,
            value=st.session_state.get('target_price', 5000.0),
            step=100.0,
            key='target_price_input'
        )
        
        platskart_share = st.slider(
            "Доля плацкартной части",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get('platskart_share', 0.6),
            step=0.05,
            key='platskart_share_input'
        )
        
        col1, col2 = st.columns(2)
        with col1:
            min_coef = st.number_input(
                "Мин. коэффициент",
                min_value=0.1,
                max_value=1.0,
                value=st.session_state.get('min_coef', 0.3),
                step=0.1,
                key='min_coef_input'
            )
        with col2:
            max_coef = st.number_input(
                "Макс. коэффициент",
                min_value=1.0,
                max_value=5.0,
                value=st.session_state.get('max_coef', 2.5),
                step=0.1,
                key='max_coef_input'
            )
        
        # Сохраняем параметры
        st.session_state.target_price = target_price
        st.session_state.platskart_share = platskart_share
        st.session_state.min_coef = min_coef
        st.session_state.max_coef = max_coef
        
        # Коэффициенты сезонности
        st.subheader("📅 Коэффициенты сезонности")
        months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 
                 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
        
        if 'seasonality_coefs' not in st.session_state:
            st.session_state.seasonality_coefs = [1.0] * 12
        
        seasonality_cols = st.columns(4)
        for i, month in enumerate(months):
            col_idx = i % 4
            with seasonality_cols[col_idx]:
                st.session_state.seasonality_coefs[i] = st.number_input(
                    month,
                    min_value=0.1,
                    max_value=3.0,
                    value=st.session_state.seasonality_coefs[i],
                    step=0.1,
                    key=f'season_{i}'
                )
        
        # Коэффициенты классов
        st.subheader("🎫 Коэффициенты классов")
        class_names = ['Класс 1', 'Класс 2', 'Класс 3', 'Класс 4']
        
        if 'class_coefs' not in st.session_state:
            st.session_state.class_coefs = [1.0, 1.2, 1.5, 2.0]
        
        for i, class_name in enumerate(class_names):
            st.session_state.class_coefs[i] = st.number_input(
                class_name,
                min_value=0.5,
                max_value=5.0,
                value=st.session_state.class_coefs[i],
                step=0.1,
                key=f'class_{i}'
            )
        
        # Кнопка обновления
        if st.button("🔄 Обновить систему", type="primary"):
            st.session_state.pricing_matrix, st.session_state.config = initialize_system()
            st.rerun()
    
    # Инициализация системы
    if st.session_state.pricing_matrix is None:
        st.session_state.pricing_matrix, st.session_state.config = initialize_system()
    
    # Основной контент
    tabs = st.tabs(["📊 Матрица коэффициентов", "💵 Расчет цен", "📈 Оптимизация", "📋 История"])
    
    with tabs[0]:
        st.header("📊 Матрица коэффициентов")
        st.markdown("**Вертикаль:** Дни до отправления (0-105) | **Горизонталь:** Загрузка в % (0-100)")
        
        # Получаем матрицу
        matrix_df = st.session_state.pricing_matrix.get_matrix_dataframe()
        
        # Опции отображения
        col_view1, col_view2, col_view3 = st.columns(3)
        with col_view1:
            show_heatmap = st.checkbox("Показать тепловую карту", value=True)
        with col_view2:
            show_table = st.checkbox("Показать таблицу", value=True)
        with col_view3:
            detail_level = st.selectbox("Детализация таблицы", 
                                       ["Каждые 5%", "Каждые 10%", "Каждые 20%"],
                                       index=0)
        
        # Визуализация матрицы - тепловая карта
        if show_heatmap:
            st.subheader("🔥 Тепловая карта матрицы")
            fig = go.Figure(data=go.Heatmap(
                z=matrix_df.values,
                x=matrix_df.columns,
                y=matrix_df.index,
                colorscale='RdYlGn',
                colorbar=dict(title="Коэффициент"),
                hovertemplate='Дни: %{y}<br>Загрузка: %{x}%<br>Коэффициент: %{z:.2f}<extra></extra>',
                text=matrix_df.values.round(2),
                texttemplate='%{text}',
                textfont={"size": 8}
            ))
            
            fig.update_layout(
                title="Матрица коэффициентов ценообразования",
                xaxis_title="Загрузка (%)",
                yaxis_title="Дни до отправления",
                height=700,
                width=None
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Таблица матрицы
        if show_table:
            st.subheader("📋 Таблица коэффициентов")
            
            # Создаем детализированную таблицу в зависимости от выбора
            step_map = {"Каждые 5%": 5, "Каждые 10%": 10, "Каждые 20%": 20}
            step = step_map[detail_level]
            
            # Получаем полную матрицу и делаем выборку
            full_matrix = st.session_state.pricing_matrix.matrix
            days_range = range(0, full_matrix.shape[0], max(1, full_matrix.shape[0] // 50))  # Максимум 50 строк
            loads_range = range(0, full_matrix.shape[1], step)
            
            detailed_df = pd.DataFrame(
                full_matrix[np.ix_(list(days_range), list(loads_range))],
                index=days_range,
                columns=loads_range
            )
            
            # Стилизуем таблицу
            styled_df = detailed_df.style.background_gradient(
                cmap='RdYlGn', 
                axis=None,
                vmin=st.session_state.config.min_coefficient,
                vmax=st.session_state.config.max_coefficient
            ).format("{:.2f}")
            
            st.dataframe(styled_df, height=500, use_container_width=True)
            
            # Информация о матрице
            st.caption(f"📊 Размер полной матрицы: {full_matrix.shape[0]} × {full_matrix.shape[1]} ячеек | "
                      f"Диапазон коэффициентов: {full_matrix.min():.2f} - {full_matrix.max():.2f}")
            
            # Кнопка экспорта
            csv = detailed_df.to_csv(index=True)
            st.download_button(
                label="📥 Скачать матрицу (CSV)",
                data=csv,
                file_name=f"pricing_matrix_{detail_level.replace(' ', '_')}.csv",
                mime="text/csv"
            )
        
        # Ручная корректировка
        st.subheader("🔧 Ручная корректировка коэффициента")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            adjust_days = st.number_input("Дни до отправления", 
                                         min_value=0, 
                                         max_value=105, 
                                         value=50,
                                         key='adjust_days')
        with col2:
            adjust_load = st.number_input("Загрузка (%)", 
                                        min_value=0, 
                                        max_value=100, 
                                        value=50,
                                        key='adjust_load')
        
        # Показываем текущий коэффициент
        current_coef = st.session_state.pricing_matrix.get_coefficient(adjust_days, adjust_load)
        
        with col3:
            st.metric("Текущий коэффициент", f"{current_coef:.2f}")
        
        with col4:
            adjust_coef = st.number_input("Новый коэффициент", 
                                         min_value=float(min_coef), 
                                         max_value=float(max_coef), 
                                         value=float(current_coef),
                                         step=0.01,
                                         key='adjust_coef')
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("✅ Применить корректировку", type="primary"):
                st.session_state.pricing_matrix.manual_adjust_matrix(
                    adjust_days, adjust_load, adjust_coef
                )
                st.success(f"✅ Коэффициент обновлен: ({adjust_days} дней, {adjust_load}% загрузки) = {adjust_coef:.2f}")
                st.rerun()
        
        # Просмотр области матрицы
        st.subheader("🔍 Просмотр области матрицы")
        view_col1, view_col2 = st.columns(2)
        with view_col1:
            view_days_start = st.number_input("Начало диапазона дней", 
                                            min_value=0, 
                                            max_value=105, 
                                            value=0,
                                            key='view_days_start')
            view_days_end = st.number_input("Конец диапазона дней", 
                                          min_value=0, 
                                          max_value=105, 
                                          value=20,
                                          key='view_days_end')
        with view_col2:
            view_load_start = st.number_input("Начало диапазона загрузки (%)", 
                                            min_value=0, 
                                            max_value=100, 
                                            value=0,
                                            key='view_load_start')
            view_load_end = st.number_input("Конец диапазона загрузки (%)", 
                                          min_value=0, 
                                          max_value=100, 
                                          value=50,
                                          key='view_load_end')
        
        if st.button("👁️ Показать область"):
            # Создаем подматрицу для просмотра
            days_range = range(view_days_start, min(view_days_end + 1, 106))
            loads_range = range(view_load_start, min(view_load_end + 1, 101), 5)  # Каждые 5%
            
            if days_range and loads_range:
                view_matrix = st.session_state.pricing_matrix.matrix[
                    np.ix_(list(days_range), list(loads_range))
                ]
                
                view_df = pd.DataFrame(
                    view_matrix,
                    index=days_range,
                    columns=loads_range
                )
                
                styled_view = view_df.style.background_gradient(
                    cmap='RdYlGn',
                    axis=None,
                    vmin=st.session_state.config.min_coefficient,
                    vmax=st.session_state.config.max_coefficient
                ).format("{:.2f}")
                
                st.dataframe(styled_view, height=400, use_container_width=True)
    
    with tabs[1]:
        st.header("Расчет цен")
        
        # Параметры для расчета
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            calc_days = st.number_input("Дни до отправления", 
                                       min_value=0, 
                                       max_value=105, 
                                       value=30,
                                       key='calc_days')
        with col2:
            calc_load = st.slider("Загрузка (%)", 
                                min_value=0, 
                                max_value=100, 
                                value=50,
                                key='calc_load')
        with col3:
            calc_month = st.selectbox("Месяц", 
                                     range(1, 13),
                                     index=5,
                                     format_func=lambda x: ['Январь', 'Февраль', 'Март', 
                                                           'Апрель', 'Май', 'Июнь',
                                                           'Июль', 'Август', 'Сентябрь',
                                                           'Октябрь', 'Ноябрь', 'Декабрь'][x-1],
                                     key='calc_month')
        with col4:
            calc_class = st.selectbox("Класс", 
                                     range(4),
                                     format_func=lambda x: f"Класс {x+1}",
                                     key='calc_class')
        
        # Расчет цены
        price = st.session_state.pricing_matrix.calculate_price(
            calc_days, calc_load, calc_class, calc_month
        )
        
        # Детализация расчета
        base_coef = st.session_state.pricing_matrix.get_coefficient(calc_days, calc_load)
        seasonality_coef = st.session_state.pricing_matrix.seasonality_coefficients[calc_month - 1]
        class_coef = st.session_state.pricing_matrix.class_coefficients[calc_class]
        platskart_base = st.session_state.config.target_price * st.session_state.config.base_platskart_share
        
        st.markdown("---")
        st.metric("💰 Итоговая цена", f"{price:,.2f} ₽")
        
        st.subheader("Детализация расчета")
        detail_cols = st.columns(5)
        with detail_cols[0]:
            st.metric("Плацкартная база", f"{platskart_base:,.2f} ₽")
        with detail_cols[1]:
            st.metric("Коэф. матрицы", f"{base_coef:.2f}")
        with detail_cols[2]:
            st.metric("Коэф. сезонности", f"{seasonality_coef:.2f}")
        with detail_cols[3]:
            st.metric("Коэф. класса", f"{class_coef:.2f}")
        with detail_cols[4]:
            st.metric("Формула", f"{platskart_base:.0f} × {base_coef:.2f} × {seasonality_coef:.2f} × {class_coef:.2f}")
        
        # Сравнение цен по классам
        st.subheader("Сравнение цен по классам")
        prices_by_class = []
        for class_idx in range(4):
            class_price = st.session_state.pricing_matrix.calculate_price(
                calc_days, calc_load, class_idx, calc_month
            )
            prices_by_class.append({
                'Класс': f"Класс {class_idx + 1}",
                'Цена (₽)': class_price,
                'Коэффициент класса': st.session_state.pricing_matrix.class_coefficients[class_idx]
            })
        
        prices_df = pd.DataFrame(prices_by_class)
        st.dataframe(prices_df, use_container_width=True)
        
        # График цен по классам
        fig = px.bar(prices_df, x='Класс', y='Цена (₽)', 
                    title="Цены по классам",
                    color='Цена (₽)',
                    color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:
        st.header("Оптимизация матрицы")
        st.markdown("Введите данные о продажах для оптимизации коэффициентов")
        
        # Ввод продаж по классам
        st.subheader("Текущие продажи")
        sales_cols = st.columns(4)
        current_sales = {}
        for class_idx in range(4):
            with sales_cols[class_idx]:
                quantity = st.number_input(
                    f"Класс {class_idx + 1}",
                    min_value=0,
                    value=0,
                    key=f'sales_class_{class_idx}'
                )
                current_sales[class_idx] = quantity
        
        # Параметры текущей ситуации
        opt_cols = st.columns(3)
        with opt_cols[0]:
            opt_days = st.number_input("Дни до отправления", 
                                      min_value=0, 
                                      max_value=105, 
                                      value=30,
                                      key='opt_days')
        with opt_cols[1]:
            opt_load = st.slider("Загрузка (%)", 
                               min_value=0, 
                               max_value=100, 
                               value=50,
                               key='opt_load')
        with opt_cols[2]:
            learning_rate = st.slider("Скорость обучения", 
                                     min_value=0.001, 
                                     max_value=0.1, 
                                     value=0.01,
                                     step=0.001,
                                     key='learning_rate')
        
        # Расчет текущей средневзвешенной цены
        if sum(current_sales.values()) > 0:
            weighted_price = st.session_state.pricing_matrix.calculate_weighted_average_price(current_sales)
            target_price = st.session_state.config.target_price
            deviation = ((weighted_price - target_price) / target_price) * 100
            
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Средневзвешенная цена", f"{weighted_price:,.2f} ₽")
            with col2:
                st.metric("Целевая цена", f"{target_price:,.2f} ₽")
            with col3:
                st.metric("Отклонение", f"{deviation:+.2f}%", 
                         delta=f"{abs(deviation):.2f}%")
            
            # Кнопка оптимизации
            if st.button("🔧 Оптимизировать матрицу", type="primary"):
                st.session_state.pricing_matrix.optimize_matrix(
                    current_sales, opt_days, opt_load, learning_rate
                )
                st.success("Матрица оптимизирована!")
                st.rerun()
        else:
            st.info("Введите данные о продажах для расчета")
    
    with tabs[3]:
        st.header("История оптимизаций")
        
        if st.session_state.pricing_matrix.sales_history:
            history_df = pd.DataFrame(st.session_state.pricing_matrix.sales_history)
            
            # Отображаем последние записи
            st.subheader("Последние записи")
            display_df = history_df[['days', 'load', 'weighted_price', 'target_price', 'coefficient']].copy()
            display_df.columns = ['Дни', 'Загрузка (%)', 'Средняя цена', 'Целевая цена', 'Коэффициент']
            st.dataframe(display_df.tail(20), use_container_width=True)
            
            # График динамики цен
            if len(history_df) > 1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=history_df.index,
                    y=history_df['weighted_price'],
                    name='Средневзвешенная цена',
                    line=dict(color='blue')
                ))
                fig.add_trace(go.Scatter(
                    x=history_df.index,
                    y=history_df['target_price'],
                    name='Целевая цена',
                    line=dict(color='red', dash='dash')
                ))
                fig.update_layout(
                    title="Динамика цен",
                    xaxis_title="Итерация",
                    yaxis_title="Цена (₽)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("История оптимизаций пуста. Выполните оптимизацию для создания записей.")
        
except Exception as e:
    st.error(f"Ошибка: {e}")
    import traceback
    st.code(traceback.format_exc())
