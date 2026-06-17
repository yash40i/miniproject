"""
Vector-Gap Extraction & Node Activation Engine for Resume-Insight AI.

Phase: ML Pipeline Bridge
- Computes per-skill cosine similarity between resume and job skill embeddings
- Applies a threshold (< 0.70) to isolate Skill Gaps
- Maps each skill to a 3-state machine node using the SkillDAG:
    * Mastered  : similarity >= threshold  (skill well-represented in resume)
    * Unlocked  : similarity <  threshold  AND all prerequisites are Mastered
    * Locked    : similarity <  threshold  AND one or more prerequisites are NOT Mastered

The resulting SkillNodeMap is a list of NodeActivation objects that can be
serialised to JSON and stored/returned by the API.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional

import numpy as np

from src.pipeline.embeddings import EmbeddingGenerator
from src.pipeline.knowledge_graph import ProbabilisticCluster, SkillDAG

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Node state enum
# ─────────────────────────────────────────────
class NodeState(str, Enum):
    MASTERED = "Mastered"      # High similarity — present in resume
    UNLOCKED = "Unlocked"      # Gap, but all prerequisites are satisfied (study NOW)
    LOCKED   = "Locked"        # Gap, prerequisites missing (blocked)


# ─────────────────────────────────────────────
# Data containers
# ─────────────────────────────────────────────
@dataclass
class NodeActivation:
    """Activated state of a single skill node in the knowledge graph."""
    skill: str
    similarity_score: float          # cosine similarity to resume  (0–1)
    state: NodeState
    prerequisites: List[str]         # all direct DAG prerequisites
    unmet_prerequisites: List[str]   # prerequisites that are NOT yet Mastered
    companion_skills: List[Dict]     # probabilistic market-cluster companions
    is_gap: bool                     # True when similarity < threshold

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["state"] = self.state.value
        return d


@dataclass
class SkillNodeMap:
    """Complete output of the GapAnalysisEngine for one analysis run."""
    threshold: float
    nodes: List[NodeActivation] = field(default_factory=list)

    # ── Convenience accessors ──────────────────────────────────────────
    @property
    def mastered(self) -> List[NodeActivation]:
        return [n for n in self.nodes if n.state == NodeState.MASTERED]

    @property
    def unlocked(self) -> List[NodeActivation]:
        return [n for n in self.nodes if n.state == NodeState.UNLOCKED]

    @property
    def locked(self) -> List[NodeActivation]:
        return [n for n in self.nodes if n.state == NodeState.LOCKED]

    def to_dict(self) -> Dict:
        return {
            "threshold": self.threshold,
            "summary": {
                "total":    len(self.nodes),
                "mastered": len(self.mastered),
                "unlocked": len(self.unlocked),
                "locked":   len(self.locked),
            },
            "nodes": [n.to_dict() for n in self.nodes],
        }


# ─────────────────────────────────────────────
# Engine
# ─────────────────────────────────────────────
class GapAnalysisEngine:
    """
    Bridges the Sentence Transformers embedding pipeline with the SkillDAG
    to produce a full skill-node activation map for a given resume / JD pair.
    """

    # Default cosine-similarity threshold below which a skill is a "gap"
    DEFAULT_THRESHOLD: float = 0.70

    def __init__(
        self,
        threshold: float = DEFAULT_THRESHOLD,
        embedding_gen: Optional[EmbeddingGenerator] = None,
        skill_dag: Optional[SkillDAG] = None,
        market_cluster: Optional[ProbabilisticCluster] = None,
    ):
        self.threshold      = threshold
        self.embedding_gen  = embedding_gen  or EmbeddingGenerator()
        self.skill_dag      = skill_dag      or SkillDAG()
        self.market_cluster = market_cluster or ProbabilisticCluster()

    # ─────────────────────────────────────────
    # Public entry point
    # ─────────────────────────────────────────
    def analyse(
        self,
        resume_text: str,
        job_skills: List[str],
    ) -> SkillNodeMap:
        """
        Run the full Vector-Gap Extraction & Node Activation pipeline.

        Args:
            resume_text : Cleaned resume text (used to build a single
                          representative resume embedding).
            job_skills  : List of skill tokens extracted from the job description.

        Returns:
            SkillNodeMap with every job skill classified as Mastered / Unlocked / Locked.
        """
        if not job_skills:
            logger.warning("GapAnalysisEngine.analyse: job_skills is empty, returning empty map.")
            return SkillNodeMap(threshold=self.threshold)

        # ── Step 1: embed resume and each individual job skill ──────────
        logger.info("[GapEngine] Embedding resume text …")
        resume_emb = self._embed_text(resume_text)

        logger.info(f"[GapEngine] Embedding {len(job_skills)} job skills …")
        skill_embs = self._embed_skills(job_skills)

        # ── Step 2: compute per-skill similarity to resume ───────────────
        similarity_scores = self._compute_similarities(resume_emb, skill_embs)

        # ── Step 3: classify mastered vs gap ────────────────────────────
        mastered_skills: set[str] = set()
        for skill, score in zip(job_skills, similarity_scores):
            if score >= self.threshold:
                canonical = self.skill_dag.find_canonical_name(skill) or skill
                mastered_skills.add(canonical)
                mastered_skills.add(skill)   # keep raw form too for matching

        logger.info(
            f"[GapEngine] Mastered: {len(mastered_skills)} skills "
            f"(threshold={self.threshold})"
        )

        # ── Step 4: build NodeActivation objects with DAG state ──────────
        nodes: List[NodeActivation] = []
        for skill, score in zip(job_skills, similarity_scores):
            node = self._build_node(skill, score, mastered_skills)
            nodes.append(node)

        skill_node_map = SkillNodeMap(threshold=self.threshold, nodes=nodes)
        logger.info(
            f"[GapEngine] Summary → Mastered={len(skill_node_map.mastered)}, "
            f"Unlocked={len(skill_node_map.unlocked)}, "
            f"Locked={len(skill_node_map.locked)}"
        )
        return skill_node_map

    # ─────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────
    def _embed_text(self, text: str) -> np.ndarray:
        """Embed a full text block and return a 1-D normalised vector."""
        emb = self.embedding_gen.embed(text)
        if emb is None or emb.size == 0:
            raise ValueError("GapEngine: could not generate embedding for resume text.")
        # Ensure 1-D
        emb = np.array(emb).flatten()
        norm = np.linalg.norm(emb)
        return emb / (norm + 1e-8)

    def _embed_skills(self, skills: List[str]) -> List[np.ndarray]:
        """Embed each skill individually and return a list of normalised 1-D vectors."""
        embeddings: List[np.ndarray] = []
        for skill in skills:
            try:
                emb = self.embedding_gen.embed(skill)
                emb = np.array(emb).flatten()
                norm = np.linalg.norm(emb)
                embeddings.append(emb / (norm + 1e-8))
            except Exception as e:
                logger.warning(f"GapEngine: could not embed skill '{skill}': {e}")
                # Fallback: zero vector (will score 0 similarity → gap)
                embeddings.append(np.zeros(self.embedding_gen.embedding_dim))
        return embeddings

    def _compute_similarities(
        self,
        resume_emb: np.ndarray,
        skill_embs: List[np.ndarray],
    ) -> List[float]:
        """
        Cosine similarity between the resume vector and each skill vector.
        Since both vectors are already L2-normalised, similarity = dot product.
        """
        scores: List[float] = []
        for emb in skill_embs:
            score = float(np.dot(resume_emb, emb))
            # Clamp to [0, 1]  (normalised embeddings may give tiny negatives)
            scores.append(max(0.0, min(1.0, score)))
        return scores

    def _build_node(
        self,
        skill: str,
        score: float,
        mastered_skills: set,
    ) -> NodeActivation:
        """
        Classify a single skill node using the state-machine rules and
        annotate it with DAG prerequisites and probabilistic companions.
        """
        is_gap = score < self.threshold

        # Canonical DAG name (may be None for dynamic LLM-extracted skills)
        canonical = self.skill_dag.find_canonical_name(skill) or skill

        # Direct prerequisites from the DAG
        prereqs = self.skill_dag.get_direct_dependencies(canonical)

        # Which prerequisites are NOT mastered?
        unmet = [
            p for p in prereqs
            if not self._is_mastered(p, mastered_skills)
        ]

        # ── State machine ─────────────────────────────────────────────
        if not is_gap:
            state = NodeState.MASTERED
        elif len(unmet) == 0:
            state = NodeState.UNLOCKED   # All prerequisites satisfied → study now
        else:
            state = NodeState.LOCKED     # Blocked by unmet prerequisites

        # Probabilistic companion skills
        try:
            companions = self.market_cluster.get_companion_skills([skill], threshold=0.65)
        except Exception:
            companions = []

        return NodeActivation(
            skill=skill,
            similarity_score=round(score, 4),
            state=state,
            prerequisites=prereqs,
            unmet_prerequisites=unmet,
            companion_skills=companions,
            is_gap=is_gap,
        )

    def _is_mastered(self, skill: str, mastered_skills: set) -> bool:
        """Check if a skill appears in the mastered set (case-insensitive)."""
        if skill in mastered_skills:
            return True
        skill_lower = skill.lower()
        return any(s.lower() == skill_lower for s in mastered_skills)
