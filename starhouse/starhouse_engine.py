"""StarHouse: observation and cartography of the KALATRACE knowledge graph."""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional

from graph.knowledge_graph import KnowledgeGraph
from starhouse.models import KnowledgeConnection, KnowledgeGap, KnowledgeRegion, StarHouseMap


class StarHouseEngine:
    """Observe and map existing knowledge without changing scientific state.

    StarHouse is intentionally descriptive. It does not create hypotheses,
    validate evidence, or mutate the supplied graph.
    """

    VERSION = "1.0.0"

    def __init__(self, graph: Optional[KnowledgeGraph] = None) -> None:
        self.graph = graph or KnowledgeGraph()
        self._observations = 0

    def observe(self, graph: Optional[KnowledgeGraph] = None) -> StarHouseMap:
        """Create a point-in-time cartographic observation."""
        target = graph or self.graph
        regions = self._build_regions(target)
        connections = self._build_connections(target)
        isolated = [node.id for node in target.isolated_nodes()]
        low_confidence = target.low_confidence_edges()
        gaps = self._build_gaps(target, isolated, low_confidence)
        self._observations += 1

        return StarHouseMap(
            version=self.VERSION,
            node_count=len(target.nodes),
            edge_count=len(target.edges),
            regions=regions,
            connections=connections,
            gaps=gaps,
            isolated_node_ids=isolated,
            low_confidence_edge_count=len(low_confidence),
            provenance={
                "module": "StarHouse",
                "observation": "cartography_only",
                "scientific_truth_evaluation": "not_performed",
                "graph_mutated": False,
                "observation_number": self._observations,
            },
        )

    def map(self, graph: Optional[KnowledgeGraph] = None) -> StarHouseMap:
        """Alias for :meth:`observe`, matching the cartographic role."""
        return self.observe(graph)

    def regions(self, graph: Optional[KnowledgeGraph] = None) -> List[KnowledgeRegion]:
        return self._build_regions(graph or self.graph)

    def gaps(self, graph: Optional[KnowledgeGraph] = None) -> List[KnowledgeGap]:
        target = graph or self.graph
        isolated = [node.id for node in target.isolated_nodes()]
        return self._build_gaps(target, isolated, target.low_confidence_edges())

    def stats(self) -> Dict[str, Any]:
        graph_stats = self.graph.stats()
        return {
            "version": self.VERSION,
            "observations": self._observations,
            "graph": graph_stats,
        }

    def health_check(self) -> Dict[str, Any]:
        return {
            "module": "StarHouse",
            "version": self.VERSION,
            "status": "healthy",
            "role": "observation_and_cartography",
            "mutates_knowledge": False,
            "validates_truth": False,
        }

    @staticmethod
    def _node_domain(node: Any) -> str:
        return str(
            getattr(node, "domain", None)
            or getattr(node, "node_type", None)
            or getattr(node, "metadata", {}).get("domain", None)
            or "unknown"
        )

    def _build_regions(self, graph: KnowledgeGraph) -> List[KnowledgeRegion]:
        groups: Dict[str, List[Any]] = defaultdict(list)
        for node in graph.nodes.values():
            groups[self._node_domain(node)].append(node)

        edge_counts: Dict[str, int] = defaultdict(int)
        for edge in graph.edges:
            source = graph.get_node(edge["source"])
            target = graph.get_node(edge["target"])
            if source is not None and self._node_domain(source) == self._node_domain(target):
                edge_counts[self._node_domain(source)] += 1

        regions: List[KnowledgeRegion] = []
        for label, nodes in sorted(groups.items()):
            count = len(nodes)
            possible = count * (count - 1)
            density = edge_counts[label] / possible if possible else 0.0
            regions.append(
                KnowledgeRegion(
                    region_id=f"region:{label.lower().replace(' ', '_')}",
                    label=label,
                    node_ids=sorted(node.id for node in nodes),
                    node_count=count,
                    edge_count=edge_counts[label],
                    density=round(density, 6),
                )
            )
        return regions

    @staticmethod
    def _build_connections(graph: KnowledgeGraph) -> List[KnowledgeConnection]:
        return [
            KnowledgeConnection(
                source_id=edge["source"],
                target_id=edge["target"],
                relation_type=edge.get("type", "related"),
                confidence=float(edge.get("confidence", 1.0)),
                weight=float(edge.get("weight", 1.0)),
            )
            for edge in graph.edges
        ]

    @staticmethod
    def _build_gaps(
        graph: KnowledgeGraph,
        isolated: Iterable[str],
        low_confidence_edges: Iterable[Dict[str, Any]],
    ) -> List[KnowledgeGap]:
        gaps: List[KnowledgeGap] = []
        isolated_ids = list(isolated)
        if isolated_ids:
            gaps.append(
                KnowledgeGap(
                    gap_type="isolated_region",
                    node_ids=isolated_ids,
                    severity=1.0,
                    rationale="Nodes exist without observed graph connections.",
                )
            )

        weak_edges = list(low_confidence_edges)
        if weak_edges:
            weak_ids = sorted({e["source"] for e in weak_edges} | {e["target"] for e in weak_edges})
            average = sum(float(e.get("confidence", 0.0)) for e in weak_edges) / len(weak_edges)
            gaps.append(
                KnowledgeGap(
                    gap_type="weak_connection",
                    node_ids=weak_ids,
                    severity=round(1.0 - average, 6),
                    rationale="Observed connections fall below the configured confidence threshold.",
                )
            )

        return gaps


# Public alias consistent with the naming convention used by the other modules.
StarHouse = StarHouseEngine
