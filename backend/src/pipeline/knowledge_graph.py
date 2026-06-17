"""
Knowledge Graph & Dependency Modeling module for Resume-Insight AI.
Implements Directed Acyclic Graph (DAG) for skills, formal grammar production rules,
and probabilistic skill grouping based on market clusters.
"""

import os
import json
import re
from typing import List, Dict, Any, Set, Optional, Tuple

class SkillDAG:
    """
    Manages the skill dependency graph, resolves competency production rules,
    and performs topological sorting.
    """
    def __init__(self, config_path: Optional[str] = None):
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "config", "skill_dag.json"
            )
        
        self.config_path = config_path
        self.skills: Dict[str, Dict[str, Any]] = {}
        self.load_graph()
        self.check_acyclic()

    def load_graph(self):
        """Loads the skill graph from skill_dag.json."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Skill DAG config not found at: {self.config_path}")
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.skills = data.get("skills", {})

    def find_canonical_name(self, skill_name: str) -> Optional[str]:
        """Finds the canonical skill name in the graph (case-insensitive & substring match)."""
        skill_lower = skill_name.strip().lower()
        
        # Exact match
        for s in self.skills:
            if s.lower() == skill_lower:
                return s
                
        # Substring match (e.g. "ReactJS" matches "React")
        for s in self.skills:
            s_lower = s.lower()
            if s_lower in skill_lower or skill_lower in s_lower:
                return s
                
        return None

    def get_direct_dependencies(self, skill_name: str) -> List[str]:
        """Returns direct dependencies / prerequisites for a given skill."""
        canonical = self.find_canonical_name(skill_name)
        if not canonical:
            return []
            
        node = self.skills[canonical]
        if node["type"] == "terminal":
            return node.get("prerequisites", [])
        elif node["type"] == "competency":
            rule = node.get("rule", "")
            # Extract all alphanumeric words as operands
            operands = re.findall(r'[a-zA-Z0-9_\-]+', rule)
            deps = []
            for op in operands:
                op_canonical = self.find_canonical_name(op)
                if op_canonical:
                    deps.append(op_canonical)
            return deps
        return []

    def check_acyclic(self):
        """Verifies that the loaded skills DAG contains no cycles using DFS."""
        visited = {}  # name -> state: 0=unvisited, 1=visiting, 2=visited
        
        def dfs(node: str):
            visited[node] = 1
            for dep in self.get_direct_dependencies(node):
                dep_canonical = self.find_canonical_name(dep)
                if not dep_canonical:
                    continue
                if visited.get(dep_canonical, 0) == 1:
                    raise ValueError(f"Cycle detected in Skill DAG: {node} -> {dep_canonical}")
                if visited.get(dep_canonical, 0) == 0:
                    dfs(dep_canonical)
            visited[node] = 2

        for skill in self.skills:
            if visited.get(skill, 0) == 0:
                dfs(skill)

    def evaluate_rule(self, rule: str, satisfied_skills: Set[str]) -> bool:
        """
        Parses and evaluates a production rule using a recursive descent parser.
        Supports operator ^ (AND), | (OR), and parentheses.
        """
        tokens = re.findall(r'\(|\)|\^|\||[a-zA-Z0-9_\-]+', rule)
        index = 0
        
        satisfied_lower = {self.find_canonical_name(s) or s.lower() for s in satisfied_skills}
        satisfied_lower = {s.lower() for s in satisfied_lower if s}

        def parse_expression() -> bool:
            nonlocal index
            val = parse_term()
            while index < len(tokens) and tokens[index] == '|':
                index += 1
                next_val = parse_term()
                val = val or next_val
            return val
            
        def parse_term() -> bool:
            nonlocal index
            val = parse_factor()
            while index < len(tokens) and tokens[index] == '^':
                index += 1
                next_val = parse_factor()
                val = val and next_val
            return val
            
        def parse_factor() -> bool:
            nonlocal index
            if index >= len(tokens):
                return False
            token = tokens[index]
            if token == '(':
                index += 1
                val = parse_expression()
                if index < len(tokens) and tokens[index] == ')':
                    index += 1
                return val
            else:
                index += 1
                canonical_token = self.find_canonical_name(token)
                if not canonical_token:
                    return False
                return self.is_satisfied(canonical_token, satisfied_skills)
                
        try:
            return parse_expression()
        except Exception as e:
            print(f"Error parsing rule '{rule}': {e}")
            return False

    def is_satisfied(self, skill_name: str, satisfied_terminals: Set[str]) -> bool:
        """
        Determines recursively whether a skill is satisfied given a set of completed terminal skills.
        - Terminal skills are satisfied if they are in the set and their prerequisites are satisfied.
        - Competency skills are satisfied if their production rules evaluate to True.
        """
        canonical = self.find_canonical_name(skill_name)
        if not canonical:
            # Fallback for dynamic skills outside DAG
            return skill_name.lower() in {s.lower() for s in satisfied_terminals}
            
        node = self.skills[canonical]
        if node["type"] == "terminal":
            is_self_present = canonical.lower() in {s.lower() for s in satisfied_terminals}
            if not is_self_present:
                return False
            # Check prerequisites
            for prereq in node.get("prerequisites", []):
                if not self.is_satisfied(prereq, satisfied_terminals):
                    return False
            return True
        else:
            rule = node.get("rule", "")
            # Competency requires the rule to evaluate to true based on satisfied sub-skills
            return self.evaluate_rule(rule, satisfied_terminals)

    def get_all_required_skills(self, target_skills: List[str]) -> List[str]:
        """
        Gathers all required skills (including prerequisites and sub-skills) 
        and returns them in a topologically sorted order.
        """
        required = set()
        
        # Phase 1: Recursively gather all required skills
        def visit(node: str):
            canonical = self.find_canonical_name(node)
            if not canonical:
                # If a skill isn't in DAG, keep it as is (terminal with no deps)
                required.add(node)
                return
            if canonical in required:
                return
            required.add(canonical)
            deps = self.get_direct_dependencies(canonical)
            for dep in deps:
                visit(dep)
                
        for skill in target_skills:
            visit(skill)
            
        # Phase 2: Perform topological sort on the gathered subset
        sorted_skills = []
        visited = set()
        temp_visited = set()
        
        def topo_visit(node: str):
            canonical = self.find_canonical_name(node) or node
            if canonical in temp_visited:
                # Cycle check fallback (should not occur since we check acyclic on load)
                return
            if canonical in visited:
                return
            temp_visited.add(canonical)
            deps = self.get_direct_dependencies(canonical)
            for dep in deps:
                dep_canonical = self.find_canonical_name(dep) or dep
                if dep_canonical in required:
                    topo_visit(dep_canonical)
            temp_visited.remove(canonical)
            visited.add(canonical)
            sorted_skills.append(canonical)
            
        for skill in required:
            topo_visit(skill)
            
        return sorted_skills


class ProbabilisticCluster:
    """
    Calculates conditional probabilities P(S_companion | S_demanded) to
    automatically suggest tools in the same market cluster.
    """
    def __init__(self, config_path: Optional[str] = None):
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "config", "market_probabilities.json"
            )
        self.config_path = config_path
        self.probabilities: Dict[str, Dict[str, float]] = {}
        self.load_probabilities()

    def load_probabilities(self):
        """Loads probability matrices from market_probabilities.json."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Probabilities config not found at: {self.config_path}")
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.probabilities = json.load(f)

    def get_companion_skills(self, demanded_skills: List[str], threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Given a list of demanded skills, returns companion skills that appear in the
        same market cluster above a threshold probability, sorted by probability descending.
        """
        companion_map = {}  # skill_name -> max_prob
        demanded_lower = {s.lower() for s in demanded_skills}
        
        for d_skill in demanded_skills:
            match_key = None
            d_skill_lower = d_skill.strip().lower()
            
            # Find in market_probabilities
            for key in self.probabilities:
                if key.lower() == d_skill_lower:
                    match_key = key
                    break
            if not match_key:
                for key in self.probabilities:
                    if key.lower() in d_skill_lower or d_skill_lower in key.lower():
                        match_key = key
                        break
                        
            if match_key:
                companions = self.probabilities[match_key]
                for companion, prob in companions.items():
                    if prob >= threshold:
                        # Only add if companion is not already in the demanded skills list
                        if companion.lower() not in demanded_lower:
                            companion_map[companion] = max(companion_map.get(companion, 0.0), prob)
                            
        sorted_companions = [{"skill": k, "probability": v} for k, v in companion_map.items()]
        sorted_companions.sort(key=lambda x: x["probability"], reverse=True)
        return sorted_companions
