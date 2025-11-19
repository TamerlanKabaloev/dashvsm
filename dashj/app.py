from dataclasses import dataclass
from typing import Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Маршруты Москва ↔ Санкт-Петербург",
    page_icon="🛤️",
    layout="wide",
)


@dataclass(frozen=True)
class RouteClassInfo:
    name: str
    tariff_current: int
    tariff_model: int
    occupancy_factor: float


@dataclass(frozen=True)
class RouteScenario:
    display_name: str
    base_distance_km: int
    base_flow: int
    base_flow_model: int
    base_revenue: int
    base_revenue_model: int
    regions: List[str]
    path_nodes: List[Dict[str, float]]
    class_info: List[RouteClassInfo]
    loss_by_region: Dict[str, int]


ROUTE_LIBRARY: Dict[str, RouteScenario] = {
    "moscow_spb_m11": RouteScenario(
        display_name="Москва — Санкт-Петербург (М-11)",
        base_distance_km=684,
        base_flow=5_000_000,
        base_flow_model=5_600_000,
        base_revenue=12_000_000,
        base_revenue_model=22_000_000,
        regions=[
            "Москва",
            "Московская область",
            "Тверская область",
            "Новгородская область",
            "Ленинградская область",
            "Санкт-Петербург",
        ],
        path_nodes=[
            {"name": "Москва", "lat": 55.7558, "lon": 37.6176},
            {"name": "Клин", "lat": 56.3420, "lon": 36.7246},
            {"name": "Тверь", "lat": 56.8584, "lon": 35.9119},
            {"name": "Вышний Волочек", "lat": 57.6008, "lon": 34.5630},
            {"name": "Валдай", "lat": 57.9823, "lon": 33.2368},
            {"name": "Великий Новгород", "lat": 58.5256, "lon": 31.2742},
            {"name": "Тосно", "lat": 59.5403, "lon": 30.8776},
            {"name": "Санкт-Петербург", "lat": 59.9343, "lon": 30.3351},
        ],
        class_info=[
            RouteClassInfo("Стандарт", 4000, 4250, 0.94),
            RouteClassInfo("Комфорт", 5200, 5500, 0.89),
            RouteClassInfo("Бизнес", 12000, 12300, 0.74),
            RouteClassInfo("Первый", 32000, 31000, 0.52),
        ],
        loss_by_region={"Тверь": -500, "Великий Новгород": -180},
    ),
    "tver_novgorod": RouteScenario(
        display_name="Тверь — Великий Новгород (М-10)",
        base_distance_km=360,
        base_flow=1_800_000,
        base_flow_model=2_050_000,
        base_revenue=4_300_000,
        base_revenue_model=6_100_000,
        regions=[
            "Тверская область",
            "Новгородская область",
        ],
        path_nodes=[
            {"name": "Тверь", "lat": 56.8584, "lon": 35.9119},
            {"name": "Вышний Волочек", "lat": 57.6008, "lon": 34.5630},
            {"name": "Валдай", "lat": 57.9823, "lon": 33.2368},
            {"name": "Великий Новгород", "lat": 58.5256, "lon": 31.2742},
        ],
        class_info=[
            RouteClassInfo("Стандарт", 2100, 2350, 0.78),
            RouteClassInfo("Комфорт", 3100, 3350, 0.69),
            RouteClassInfo("Бизнес", 6400, 7000, 0.45),
            RouteClassInfo("Первый", 16000, 15000, 0.32),
        ],
        loss_by_region={"Вышний Волочек": -120, "Валдай": -90},
    ),
}


REGION_GEOMETRY = {
    "Москва": {
        "center": (55.7558, 37.6176),
        "polygon": [
            [37.45, 55.93],
            [37.82, 55.93],
            [37.82, 55.58],
            [37.45, 55.58],
        ],
    },
    "Московская область": {
        "center": (55.5, 37.3),
        "polygon": [
            [35.2, 56.2],
            [39.6, 56.2],
            [39.6, 54.7],
            [35.2, 54.7],
        ],
    },
    "Тверская область": {
        "center": (57.0, 35.3),
        "polygon": [
            [31.6, 58.2],
            [38.0, 58.2],
            [38.0, 55.2],
            [31.6, 55.2],
        ],
    },
    "Новгородская область": {
        "center": (58.1, 32.5),
        "polygon": [
            [28.4, 59.5],
            [35.0, 59.5],
            [35.0, 56.9],
            [28.4, 56.9],
        ],
    },
    "Ленинградская область": {
        "center": (59.9, 31.3),
        "polygon": [
            [27.0, 61.0],
            [34.8, 61.0],
            [34.8, 58.7],
            [27.0, 58.7],
        ],
    },
    "Санкт-Петербург": {
        "center": (59.9343, 30.3351),
        "polygon": [
            [30.1, 60.1],
            [30.55, 60.1],
            [30.55, 59.75],
            [30.1, 59.75],
        ],
    },
}


def compute_adjusted_values(
    scenario: RouteScenario,
    year: int,
    distance_km: float,
    direction: str,
    options: Dict[str, bool],
) -> Dict[str, float]:
    year_effect = 1 + 0.028 * (year - 2024)
    direction_effect = 1.0 if direction == "туда" else 0.965
    distance_effect = distance_km / scenario.base_distance_km

    flow_multiplier = year_effect * direction_effect * distance_effect
    revenue_multiplier = year_effect * distance_effect * (1.02 if options["Ажиотаж"] else 1.0)

    if options["Абонементы"]:
        flow_multiplier *= 1.05
        revenue_multiplier *= 0.97

    if options["Сборы"]:
        revenue_multiplier *= 1.04

    flow = scenario.base_flow * flow_multiplier
    model_flow = scenario.base_flow_model * flow_multiplier * (1.06 if options["Ажиотаж"] else 1.02)

    revenue = scenario.base_revenue * revenue_multiplier
    model_revenue = scenario.base_revenue_model * revenue_multiplier * 1.04

    return {
        "flow": flow,
        "model_flow": model_flow,
        "revenue": revenue,
        "model_revenue": model_revenue,
    }


def build_class_dataframe(
    scenario: RouteScenario,
    flow_ratio: float,
    options: Dict[str, bool],
) -> pd.DataFrame:
    rows = []
    for info in scenario.class_info:
        occupancy = info.occupancy_factor * flow_ratio
        if options["Абонементы"]:
            occupancy *= 1.05
        if options["Ажиотаж"]:
            occupancy *= 1.03

        delta_tariff = info.tariff_model - info.tariff_current
        delta_percent = (delta_tariff / info.tariff_current) * 100 if info.tariff_current else 0

        rows.append(
            {
                "Класс": info.name,
                "Тариф КС": info.tariff_current,
                "Тариф модель": info.tariff_model,
                "Отклонение, руб": delta_tariff,
                "Отклонение, %": delta_percent,
                "Заполняемость": min(round(occupancy * 100, 1), 120),
            }
        )

    return pd.DataFrame(rows)


def build_loss_dataframe(loss_by_region: Dict[str, int]) -> pd.DataFrame:
    data = [{"Регион": name, "Потеря выручки, млн руб.": value} for name, value in loss_by_region.items()]
    return pd.DataFrame(data)


def build_map_layers(active_regions: List[str], path_nodes: List[Dict[str, float]]):
    region_records = []
    for name, geometry in REGION_GEOMETRY.items():
        polygon = [[lon, lat] for lon, lat in geometry["polygon"]]
        if polygon and polygon[0] != polygon[-1]:
            polygon = polygon + [polygon[0]]
        is_active = name in active_regions
        fill_color = [28, 132, 198, 150] if is_active else [120, 120, 120, 40]
        line_color = [15, 76, 129, 180] if is_active else [90, 90, 90, 80]
        region_records.append(
            {
                "name": name,
                "polygon": polygon,
                "fill_color": fill_color,
                "line_color": line_color,
            }
        )

    path_coords = [[node["lon"], node["lat"]] for node in path_nodes]
    path_layer_data = [{"name": "Маршрут", "path": path_coords}] if path_coords else []

    node_records = [
        {"name": node["name"], "coordinates": [node["lon"], node["lat"]]}
        for node in path_nodes
    ]

    return region_records, path_layer_data, node_records


def render_map(active_regions: List[str], path_nodes: List[Dict[str, float]]):
    import pydeck as pdk

    polygons, path_data, node_data = build_map_layers(active_regions, path_nodes)

    polygon_layer = pdk.Layer(
        "PolygonLayer",
        polygons,
        get_polygon="polygon",
        get_fill_color="fill_color",
        get_line_color="line_color",
        line_width_min_pixels=1,
        stroked=True,
        filled=True,
        pickable=True,
    )

    path_layer = pdk.Layer(
        "PathLayer",
        path_data,
        get_path="path",
        get_color=[240, 84, 36],
        width_scale=10,
        width_min_pixels=4,
        rounded=True,
    )

    node_layer = pdk.Layer(
        "ScatterplotLayer",
        node_data,
        get_position="coordinates",
        get_fill_color=[255, 255, 255],
        get_line_color=[40, 40, 40],
        line_width_min_pixels=1,
        radius_scale=1500,
        radius_min_pixels=6,
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=58.0,
        longitude=34.0,
        zoom=5.2,
        bearing=0,
        pitch=30,
    )

    deck = pdk.Deck(
        layers=[polygon_layer, path_layer, node_layer],
        initial_view_state=view_state,
        tooltip={"text": "{name}"},
    )

    st.pydeck_chart(deck, use_container_width=True)


def render_route_dashboard():
    st.title("Маршруты Москва ↔ Санкт-Петербург")
    st.caption("Интерактивный дашборд с картой, KPI и тарифами по моделируемым маршрутам.")

    left, mid, right = st.columns([1.2, 1, 1])

    with left:
        route_key = st.selectbox(
            "Выбор маршрута",
            options=list(ROUTE_LIBRARY.keys()),
            format_func=lambda k: ROUTE_LIBRARY[k].display_name,
        )
        scenario = ROUTE_LIBRARY[route_key]

    with mid:
        year = st.slider("Выбор года", min_value=2023, max_value=2035, value=2031, step=1)
        direction = st.selectbox("Направление", options=["туда", "обратно"])

    with right:
        distance = st.number_input(
            "Длина маршрута, км",
            min_value=150,
            max_value=1500,
            value=scenario.base_distance_km,
            step=10,
            key=f"distance-{route_key}",
        )

    st.markdown("---")

    opt_col1, opt_col2, opt_col3 = st.columns(3)
    with opt_col1:
        opt_abonements = st.checkbox("Абонементы", value=True)
    with opt_col2:
        opt_hype = st.checkbox("Ажиотаж", value=False)
    with opt_col3:
        opt_fees = st.checkbox("Сборы", value=True)

    options = {"Абонементы": opt_abonements, "Ажиотаж": opt_hype, "Сборы": opt_fees}
    metrics = compute_adjusted_values(scenario, year, distance, direction, options)

    flow_delta = metrics["model_flow"] - metrics["flow"]
    revenue_delta = metrics["model_revenue"] - metrics["revenue"]

    metric_cols_top = st.columns(2)
    with metric_cols_top[0]:
        st.metric(
            "Поток КС, пасс.",
            f"{metrics['flow'] / 1_000_000:,.2f} млн",
            f"{flow_delta / 1_000_000:,.2f} млн",
        )
    with metric_cols_top[1]:
        st.metric(
            "Выручка КС, руб.",
            f"{metrics['revenue'] / 1_000_000:,.2f} млн",
            f"{revenue_delta / 1_000_000:,.2f} млн",
        )

    metric_cols_bottom = st.columns(2)
    with metric_cols_bottom[0]:
        st.metric(
            "Поток модель, пасс.",
            f"{metrics['model_flow'] / 1_000_000:,.2f} млн",
            help="Прогнозная модель учитывает выбранные параметры.",
        )
    with metric_cols_bottom[1]:
        st.metric(
            "Выручка модель, руб.",
            f"{metrics['model_revenue'] / 1_000_000:,.2f} млн",
            help="Прогнозная выручка после корректировок маршрута.",
        )

    st.markdown("### Сравнение потоков и выручки")
    chart_cols = st.columns(2)

    with chart_cols[0]:
        flow_chart_df = pd.DataFrame(
            {
                "Категория": ["Поток КС", "Поток модели"],
                "Пассажиры, млн": [
                    metrics["flow"] / 1_000_000,
                    metrics["model_flow"] / 1_000_000,
                ],
            }
        )
        st.plotly_chart(
            px.bar(
                flow_chart_df,
                x="Категория",
                y="Пассажиры, млн",
                color="Категория",
                text_auto=".2f",
                color_discrete_sequence=["#64b5f6", "#ef9a9a"],
            ),
            use_container_width=True,
        )

    with chart_cols[1]:
        revenue_chart_df = pd.DataFrame(
            {
                "Категория": ["Выручка КС", "Выручка модели"],
                "Выручка, млн руб": [
                    metrics["revenue"] / 1_000_000,
                    metrics["model_revenue"] / 1_000_000,
                ],
            }
        )
        st.plotly_chart(
            px.bar(
                revenue_chart_df,
                x="Категория",
                y="Выручка, млн руб",
                color="Категория",
                text_auto=".2f",
                color_discrete_sequence=["#64b5f6", "#ef9a9a"],
            ),
            use_container_width=True,
        )

    st.markdown("### Тарифная матрица")
    flow_ratio = metrics["flow"] / scenario.base_flow if scenario.base_flow else 1.0
    tariffs_df = build_class_dataframe(scenario, flow_ratio, options)
    st.dataframe(
        tariffs_df,
        use_container_width=True,
        height=220,
    )

    loss_df = build_loss_dataframe(scenario.loss_by_region)
    st.markdown("### Потеря выручки по точкам маршрута")
    st.dataframe(loss_df, use_container_width=True, height=160)

    st.markdown("### Карта маршрута и регионов")
    render_map(scenario.regions, scenario.path_nodes)


if __name__ == "__main__":
    render_route_dashboard()
