"""A/B provenance tool: projections only, never an independent native verifier."""
from .model import ProvenanceError, load_document, build_graph, graph_summary

__all__ = ["ProvenanceError", "load_document", "build_graph", "graph_summary"]
__version__ = "0.1.0"
