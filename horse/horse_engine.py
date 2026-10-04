"""Horse: non-linear exploration of existing knowledge structures."""
from __future__ import annotations
from collections import defaultdict, deque
import hashlib
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from graph.knowledge_graph import KnowledgeGraph
from horse.models import HorseExploration, HorsePath
from parsi.models import PARSIResult
from starhouse.models import StarHouseMap

class HorseEngine:
    """Explore alternative graph paths without creating or validating knowledge."""
    VERSION = "1.0.0"

    def __init__(self, graph: Optional[KnowledgeGraph] = None) -> None:
        self.graph = graph or KnowledgeGraph()
        self._explorations = 0

    def explore(
        self,
        seeds: Optional[Sequence[str]] = None,
        parsi_result: Optional[PARSIResult] = None,
        starhouse_map: Optional[StarHouseMap] = None,
        max_hops: int = 3,
        max_paths: int = 8,
    ) -> HorseExploration:
        if max_hops < 1: raise ValueError("max_hops must be >= 1")
        if max_paths < 1: raise ValueError("max_paths must be >= 1")
        seed_ids = self._resolve_seeds(seeds, parsi_result)
        if not seed_ids:
            seed_ids = self._frontier_from_starhouse(starhouse_map)
        seed_ids = [sid for sid in seed_ids if sid in self.graph.nodes]
        paths = self._find_paths(seed_ids, max_hops, max_paths)
        frontier = sorted({p.node_ids[-1] for p in paths if p.node_ids})
        self._explorations += 1
        return HorseExploration(
            exploration_id=f"horse:{self._explorations}",
            seed_ids=seed_ids,
            paths=paths,
            frontier_node_ids=frontier,
            warnings=["Exploration candidates are not scientific conclusions or validated hypotheses."],
            provenance={
                "module": "Horse", "version": self.VERSION,
                "exploration": "non_linear_graph_paths",
                "parsi_used": parsi_result is not None,
                "starhouse_used": starhouse_map is not None,
                "graph_mutated": False,
                "scientific_validation": "not_performed",
            },
        )

    def health_check(self) -> Dict[str, Any]:
        return {"module":"Horse","version":self.VERSION,"status":"healthy","mutates_knowledge":False,"validates_truth":False}

    def stats(self) -> Dict[str, Any]:
        return {"version":self.VERSION,"explorations":self._explorations,"graph":self.graph.stats()}

    def _resolve_seeds(self, seeds: Optional[Sequence[str]], result: Optional[PARSIResult]) -> List[str]:
        if seeds: return list(dict.fromkeys(str(x) for x in seeds))
        if not result: return []
        terms = {e.normalized.lower() for e in result.entities if e.normalized}
        matches=[]
        for node_id,node in self.graph.nodes.items():
            text=" ".join(str(x or "") for x in [node_id,getattr(node,"label",None),getattr(node,"content",None),getattr(node,"statement",None)])
            normalized=re.sub(r"\s+"," ",text.lower()).strip()
            if any(term in normalized for term in terms): matches.append(node_id)
        return matches

    @staticmethod
    def _frontier_from_starhouse(mapping: Optional[StarHouseMap]) -> List[str]:
        if not mapping: return []
        return list(mapping.isolated_node_ids) or [r.node_ids[0] for r in mapping.regions if r.node_ids]

    def _find_paths(self, seeds: Sequence[str], max_hops: int, max_paths: int) -> List[HorsePath]:
        adjacency: Dict[str,List[Tuple[str,Dict[str,Any]]]] = defaultdict(list)
        for edge in self.graph.edges:
            if edge.get("source") in self.graph.nodes and edge.get("target") in self.graph.nodes:
                adjacency[edge["source"]].append((edge["target"],edge))
                adjacency[edge["target"]].append((edge["source"],edge))
        candidates=[]
        for seed in seeds:
            queue=deque([(seed,[seed],[],set([seed]))])
            while queue:
                current,path,relations,seen=queue.popleft()
                if len(path)>1:
                    score=self._score_path(path,relations)
                    if len({self._domain(n) for n in path})>1 or len(relations)>1:
                        pid="horse:path:"+hashlib.sha1("|".join(path).encode()).hexdigest()[:12]
                        candidates.append(HorsePath(pid,path,list(relations),score,"Alternative non-linear route through existing graph connections.",{"module":"Horse","validated":False}))
                if len(path)-1>=max_hops: continue
                for nxt,edge in adjacency[current]:
                    if nxt in seen: continue
                    queue.append((nxt,path+[nxt],relations+[str(edge.get("type","related"))],seen|{nxt}))
        candidates.sort(key=lambda p:(-p.score,len(p.node_ids),p.path_id))
        unique=[]; seen=set()
        for p in candidates:
            key=tuple(p.node_ids)
            if key not in seen:
                seen.add(key); unique.append(p)
            if len(unique)>=max_paths: break
        return unique

    def _score_path(self,path:Sequence[str],relations:Sequence[str])->float:
        confidences=[]
        for a,b in zip(path,path[1:]):
            for e in self.graph.edges:
                if {e.get("source"),e.get("target")}=={a,b}:
                    confidences.append(float(e.get("confidence",1.0))); break
        conf=sum(confidences)/len(confidences) if confidences else 0.0
        diversity=len({self._domain(n) for n in path})/max(1,len(path))
        relation_diversity=len(set(relations))/max(1,len(relations))
        return round(0.6*conf+0.25*diversity+0.15*relation_diversity,6)

    def _domain(self,node_id:str)->str:
        node=self.graph.nodes[node_id]
        return str(getattr(node,"domain",None) or getattr(node,"node_type",None) or "unknown")

Horse = HorseEngine
