import sys
import tempfile
import json
import os
from pathlib import Path
import pytest

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.knowledge_graph import SkillDAG, ProbabilisticCluster


class TestKnowledgeGraph:
    """Test suite for the SkillDAG and ProbabilisticCluster."""

    def test_dag_loading_and_cycle_checking(self):
        """Test loading and cycle checking on a valid graph."""
        dag = SkillDAG()
        assert len(dag.skills) > 0
        assert "Python" in dag.skills
        # No error raised means valid acyclic check succeeded on init.

    def test_cycle_detection_invalid_graph(self):
        """Test that a cycle in the graph correctly throws ValueError."""
        # Create a temp JSON file with a cycle
        cyclic_data = {
            "skills": {
                "A": {"type": "terminal", "prerequisites": ["B"]},
                "B": {"type": "terminal", "prerequisites": ["C"]},
                "C": {"type": "terminal", "prerequisites": ["A"]}
            }
        }
        
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as temp_file:
            json.dump(cyclic_data, temp_file)
            temp_path = temp_file.name

        try:
            with pytest.raises(ValueError, match="Cycle detected"):
                SkillDAG(config_path=temp_path)
        finally:
            os.remove(temp_path)

    def test_formal_grammar_rule_parsing_and_evaluation(self):
        """Test recursive rule parsing and evaluation using the parse_and_evaluate engine."""
        dag = SkillDAG()

        # Rule evaluation directly
        # React requires JavaScript and CSS (which requires HTML) to be satisfied
        assert dag.evaluate_rule("React ^ HTML ^ CSS", {"React", "HTML", "CSS", "JavaScript"}) is True
        assert dag.evaluate_rule("React ^ HTML ^ CSS", {"React", "HTML", "CSS"}) is False
        assert dag.evaluate_rule("FastAPI | Django", {"FastAPI", "Python"}) is True
        assert dag.evaluate_rule("FastAPI | Django", {"Django", "Python"}) is True
        assert dag.evaluate_rule("FastAPI | Django", {"Python"}) is False
        assert dag.evaluate_rule("(FastAPI | Django) ^ PostgreSQL", {"FastAPI", "PostgreSQL", "Python", "RelationalDB"}) is True
        assert dag.evaluate_rule("(FastAPI | Django) ^ PostgreSQL", {"Django", "Python", "RelationalDB"}) is False

    def test_is_satisfied_recursive(self):
        """Test whether competencies are satisfy recursive sub-skills requirements."""
        dag = SkillDAG()

        # "Frontend" requires "React ^ HTML ^ CSS".
        # "React" requires "JavaScript" and "CSS" (which requires "HTML")
        # So satisfies: Frontend is satisfied when React, HTML, CSS are satisfied.
        # But React is terminal and requires its own prerequisites to be satisfied.
        # Let's check:
        # If we have JavaScript, HTML, CSS, React:
        # Is React satisfied?
        # - React is present.
        # - React prerequisites are JavaScript and CSS.
        # - JavaScript is present.
        # - CSS is present and its prerequisite HTML is present.
        # So React is satisfied. And Frontend is satisfied.
        terminals = {"JavaScript", "HTML", "CSS", "React"}
        assert dag.is_satisfied("React", terminals) is True
        assert dag.is_satisfied("Frontend", terminals) is True

        # If we omit JavaScript:
        terminals_missing_js = {"HTML", "CSS", "React"}
        assert dag.is_satisfied("React", terminals_missing_js) is False
        assert dag.is_satisfied("Frontend", terminals_missing_js) is False

    def test_topological_sorting(self):
        """Test that get_all_required_skills expands and topologically sorts dependencies."""
        dag = SkillDAG()

        # FullStack expands to: FullStack, Frontend, Backend, React, HTML, CSS, FastAPI, RelationalDB, plus their prerequisites (JavaScript, Python)
        all_skills = dag.get_all_required_skills(["FullStack"])
        
        # Verify all elements are present
        expected_subset = {"FullStack", "Frontend", "Backend", "React", "HTML", "CSS", "FastAPI", "RelationalDB", "JavaScript", "Python"}
        for s in expected_subset:
            assert s in all_skills

        # Verify topological ordering constraint:
        # Prerequisite must appear before dependent
        def assert_before(pre, dep):
            assert all_skills.index(pre) < all_skills.index(dep), f"Expected {pre} to be before {dep}"

        assert_before("JavaScript", "React")
        assert_before("HTML", "CSS")
        assert_before("CSS", "React")
        assert_before("React", "Frontend")
        assert_before("HTML", "Frontend")
        assert_before("CSS", "Frontend")
        assert_before("Python", "FastAPI")
        assert_before("FastAPI", "Backend")
        assert_before("RelationalDB", "Backend")
        assert_before("Frontend", "FullStack")
        assert_before("Backend", "FullStack")

    def test_conditional_probability_companion_skills(self):
        """Test that ProbabilisticCluster fetches companion skills correctly."""
        cluster = ProbabilisticCluster()
        
        # Let's query Kubernetes
        companions = cluster.get_companion_skills(["Kubernetes"], threshold=0.6)
        # Kubernetes maps to Docker: 0.95, Helm: 0.80, AWS: 0.70, Terraform: 0.65
        companion_names = [c["skill"] for c in companions]
        assert "Docker" in companion_names
        assert "Helm" in companion_names
        assert "AWS" in companion_names
        assert "Terraform" in companion_names

        # Docker should be the highest probability companion for Kubernetes
        assert companions[0]["skill"] == "Docker"
        assert companions[0]["probability"] == 0.95

        # Check thresholding: if threshold is 0.9, Helm (0.8), AWS (0.7) should be excluded
        high_threshold_companions = cluster.get_companion_skills(["Kubernetes"], threshold=0.9)
        high_companion_names = [c["skill"] for c in high_threshold_companions]
        assert "Docker" in high_companion_names
        assert "Helm" not in high_companion_names
        assert "AWS" not in high_companion_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
