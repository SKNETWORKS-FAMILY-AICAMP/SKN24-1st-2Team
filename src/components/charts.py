"""
차트 컴포넌트
- 등록 추이 차트
- 유지비 비교 차트
"""
import plotly.graph_objects as go

# 공통 색상 정의
CHART_COLORS = {
    "electric": "#3b82f6",  # 전기
    "combustion": "#9ca3af",  # 내연
    "grid": "rgba(75, 85, 99, 0.15)",
    "text": "#6b7280",
    "legend": "#9ca3af"
}


def render_registration_trend_chart(data):
    """
    화물차 등록 추이 차트 (전기 vs 내연기관)
    """
    years = [d["year"] for d in data]
    electric = [d["electric"] for d in data]
    combustion = [d["combustion"] for d in data]
    
    fig = go.Figure()
    
    # 내연 화물차
    fig.add_trace(go.Scatter(
        x=years,
        y=combustion,
        name="내연 화물차",
        mode="lines+markers",
        line=dict(color=CHART_COLORS["combustion"], width=2),
        marker=dict(size=7, color=CHART_COLORS["combustion"]),
        hovertemplate="%{y:,.0f}대<extra></extra>"
    ))
    
    # 전기 화물차
    fig.add_trace(go.Scatter(
        x=years,
        y=electric,
        name="전기 화물차",
        mode="lines+markers",
        line=dict(color=CHART_COLORS["electric"], width=2.5),
        marker=dict(size=7, color=CHART_COLORS["electric"]),
        hovertemplate="%{y:,.0f}대<extra></extra>"
    ))
    
    # Y축 눈금 계산 최적화
    max_val = max(max(electric), max(combustion)) if electric and combustion else 100000
    
    # 눈금이 최대 5~6개만 나오도록 step 조절
    if max_val > 1000000:
        tick_step = 10000000 # 10M 단위
    elif max_val > 100000:
        tick_step = 500000   # 500k 단위
    else:
        tick_step = 15000    # 기존 유지
        
    max_tick = ((max_val // tick_step) + 1) * tick_step
    tickvals = list(range(0, int(max_tick) + 1, int(tick_step)))
    
    # 단위 표시 (k: 천, M: 백만)
    def format_tick(v):
        if v >= 1000000: return f"{v/1000000:.1f}M"
        if v >= 1000: return f"{int(v/1000)}k"
        return str(v)
    
    ticktext = [format_tick(v) for v in tickvals]
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=50, r=20, t=20, b=60),
        height=300,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.12,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color=CHART_COLORS["legend"]),
            bgcolor="rgba(0,0,0,0)",
            itemsizing="constant"
        ),
        xaxis=dict(
            showgrid=False,
            showline=False,
            tickfont=dict(size=11, color=CHART_COLORS["text"]),
            tickmode="array",
            tickvals=years,
            fixedrange=True
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=CHART_COLORS["grid"],
            gridwidth=1,
            showline=False,
            tickfont=dict(size=11, color=CHART_COLORS["text"]),
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            zeroline=False,
            fixedrange=True
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1f2937",
            font_size=12,
            font_color="#ffffff"
        )
    )
    
    return fig


def render_maintenance_cost_chart(data):
    """
    연간 유지비 비교 차트 (전기 vs 내연기관)
    - 항목별 breakdown이 아니라, 총합 기준으로 막대 2개만 표시
    """
    total_electric = sum(d.get("electric", 0) for d in data)
    total_combustion = sum(d.get("combustion", 0) for d in data)

    fig = go.Figure()

    x = ["전기 화물차", "내연 화물차"]
    y = [total_electric, total_combustion]

    fig.add_trace(
        go.Bar(
            x=x,
            y=y,
            marker=dict(
                color=[CHART_COLORS["electric"], CHART_COLORS["combustion"]],
                cornerradius=3,
            ),
            text=[f"{v:,}만원" for v in y],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y:,}만원<extra></extra>",
            name="",
        )
    )

    # Y축 최댓값 계산
    max_val = max(y) if y else 0
    tick_step = 200
    max_tick = ((max_val // tick_step) + 1) * tick_step if max_val > 0 else tick_step
    tickvals = list(range(0, int(max_tick) + 1, tick_step))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=20, b=60),
        height=300,
        showlegend=False,
        bargap=0.775,
        xaxis=dict(
            showgrid=False,
            showline=False,
            tickfont=dict(size=11, color=CHART_COLORS["text"]),
            fixedrange=True
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=CHART_COLORS["grid"],
            gridwidth=1,
            showline=False,
            tickfont=dict(size=11, color=CHART_COLORS["text"]),
            tickmode="array",
            tickvals=tickvals,
            zeroline=False,
            fixedrange=True
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1f2937",
            font_size=12,
            font_color="#ffffff"
        )
    )
    
    return fig

