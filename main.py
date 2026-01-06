import yaml
import plotly.graph_objects as go
import math
from pydantic import BaseModel, field_validator
from typing import Optional

class Point(BaseModel):
    x: float
    y: float
    z: float

    def tooltip(self) -> str:
        return f"{int(self.x)}, {int(self.y)}, {int(self.z)}"

class Translocator(BaseModel):
    name: str
    desc: Optional[str] = ""
    origin: Point
    destination: Point
    color: str = "cyan"

    @field_validator('color', mode='before')
    @classmethod
    def validate_color(cls, v):
        return v if v else "cyan"

    def get_2d_dist(self) -> int:
        return int(math.sqrt((self.destination.x - self.origin.x)**2 + (self.destination.z - self.origin.z)**2))

class Landmark(BaseModel):
    name: str
    location: Point

    @property
    def location(self) -> Point: return Point.from_string(self.loc_str)


def load_data():
    with open('translocators.yaml', 'r') as f:
        tls = [Translocator(**item) for item in (yaml.safe_load(f) or [])]
    with open('landmarks.yaml', 'r') as f:
        lms = [Landmark(**item) for item in (yaml.safe_load(f) or [])]
    return tls, lms

tls, lms = load_data()

# Plot

fig = go.Figure()
dark_hover = dict(bgcolor="#1e1e1e", bordercolor="#555", font=dict(family="monospace", color="#e0e0e0"))

# Translocators
for tl in tls:
    fig.add_trace(go.Scatter(
        x=[tl.origin.x, tl.destination.x], 
        y=[tl.origin.z, tl.destination.z],
        mode='lines',
        name=tl.name, 
        line=dict(color=tl.color, width=3),
        hoverlabel=dark_hover,
        hovertemplate=f"<b>{tl.name}</b><br>Distance: {tl.get_2d_dist()} blocks<extra></extra>",
        legendgroup=tl.name
    ))
    
    fig.add_trace(go.Scatter(
        x=[tl.origin.x, tl.destination.x], 
        y=[tl.origin.z, tl.destination.z],
        mode='markers',
        marker=dict(size=12, color='white', symbol='circle-open', line=dict(width=2)),
        hoverlabel=dark_hover, 
        hoverinfo="text",
        text=[f"{tl.name} (Origin)<br>{tl.origin.tooltip()}", f"{tl.name} (Dest)<br>{tl.destination.tooltip()}"],
        showlegend=False, 
        legendgroup=tl.name
    ))

# Landmarks
for lm in lms:
    fig.add_trace(go.Scatter(
        x=[lm.location.x], y=[lm.location.z],
        mode='markers+text', 
        name="Landmarks",
        marker=dict(size=14, symbol='diamond', color='#fdcb6e'),
        text=[lm.name], 
        textposition="top center",
        hoverlabel=dark_hover, 
        hoverinfo="text",
        hovertext=[f"<b>{lm.name}</b><br>{lm.location.tooltip()}"],
        showlegend=(lm == lms[0])
    ))

fig.update_layout(
    title="ToF Translocator Map",
    template="plotly_dark", 
    paper_bgcolor="#111",
    plot_bgcolor="#111",
    dragmode='pan',
    hovermode='closest',
    hoverdistance=50,
    margin=dict(l=0, r=0, t=0, b=0),
    xaxis=dict(showgrid=True, gridcolor='#222', scaleanchor="y", scaleratio=1, constrain="domain"),
    yaxis=dict(showgrid=True, gridcolor='#222', autorange="reversed"),
    showlegend=False,
    height=None,
    width=None,
)

fig.write_html("index.html")