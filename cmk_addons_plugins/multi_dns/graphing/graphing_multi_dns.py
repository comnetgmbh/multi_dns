#!/usr/bin/env python3
#2024 Comnet GmbH, Andreas Decker

from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.metrics import Color, DecimalNotation, Metric, Unit
from cmk.graphing.v1.perfometers import Closed, FocusRange, Perfometer

metric_average_resolution_time = Metric(
    name="avg_dns_resolution_time",
    title=Title("Average resolution time of checked domains"),
    unit=Unit(DecimalNotation("")),
    color=Color.PINK,
)

graph_average_resolution_time = Graph(
    name="avg_dns_resolution_time_graph",
    title=Title("Average resolution time of checked domains"),
    simple_lines=["avg_dns_resolution_time"],
    minimal_range=MinimalRange(0, 500),
)

perfometer_average_resolution_time = Perfometer(
    name="avg_dns_resolution_time_perfometer",
    focus_range=FocusRange(Closed(0), Closed(1000)),
    segments=["avg_dns_resolution_time"],
)
