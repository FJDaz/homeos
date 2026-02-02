"""Workflows for AETHERFLOW 2.0."""
from .proto import ProtoWorkflow
from .prod import ProdWorkflow

__all__ = ["ProtoWorkflow", "ProdWorkflow"]
