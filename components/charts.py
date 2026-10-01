import plotly.express as px
import pandas as pd

COLOR_SEQUENCE = ["#2563EB", "#14B8A6", "#64748B", "#F59E0B", "#EF4444", "#8B5CF6"]


def type_distribution_chart(type_counts):
    if not type_counts:
        return None
    df = pd.DataFrame(type_counts, columns=["Asset Type", "Count"])
    fig = px.bar(
        df, x="Asset Type", y="Count",
        title="Assets by Type",
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=350)
    return fig


def status_distribution_chart(status_counts):
    if not status_counts:
        return None
    df = pd.DataFrame(status_counts, columns=["Status", "Count"])
    df = df[df["Count"] > 0]
    if df.empty:
        return None
    fig = px.pie(
        df, names="Status", values="Count",
        title="Asset Status Distribution",
        color_discrete_sequence=COLOR_SEQUENCE,
        hole=0.4,
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=350)
    return fig


def department_distribution_chart(dept_counts):
    if not dept_counts:
        return None
    df = pd.DataFrame(dept_counts, columns=["Department", "Count"])
    fig = px.bar(
        df, x="Count", y="Department",
        orientation="h",
        title="Assets by Department",
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=350)
    return fig