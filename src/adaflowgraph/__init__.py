from . import visual
from .build import GraphBuilder

_builder = GraphBuilder()

build_from_source = _builder.build_from_source
build_from_file = _builder.build_from_file
build_from_tree = _builder.build_from_tree

export_graph_image = visual.export_graph_image
