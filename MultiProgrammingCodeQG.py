import ast
import re
import random
import subprocess
import tempfile
import os
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple, Set

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Language(Enum):
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    C = "c"

class CodeParser:
    """Base class for language-specific parsers"""
    
    def parse(self, code: str) -> Any:
        """Parse code into an internal representation"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_functions(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract function information from parsed code"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_loops(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract loop information from parsed code"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_conditionals(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract conditional statement information from parsed code"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_variables(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract variable information from parsed code"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def identify_algorithm(self, code: str) -> Optional[str]:
        """Identify algorithm in the code"""
        raise NotImplementedError("Subclasses must implement this method")

class PythonParser(CodeParser):
    """Parser for Python code"""
    
    def __init__(self):
        self.algorithm_patterns = {
            'binary_search': r'(mid|middle).*(low|left|start).*(high|right|end)|(low|left|start).*(high|right|end).*(mid|middle)',
            'linear_search': r'for\s+\w+\s+in\s+\w+\s*:.*(==|is)\s+\w+',
            'bubble_sort': r'for.*for.*if.*\[.*\].*\[.*\+.*\].*swap',
            'insertion_sort': r'for.*while.*>.*\[.*\].*\[.*\-.*\]',
            'selection_sort': r'for.*for.*min.*if.*<',
            'merge_sort': r'merge.*split|split.*merge|divide.*conquer',
            'quick_sort': r'partition.*pivot',
            'dfs': r'(stack|depth).*append.*pop',
            'bfs': r'(queue|breadth).*append.*pop',
            'dijkstra': r'priority.*queue.*distance',
            'dynamic_programming': r'memo.*\[.*\].*\[.*\]|dp.*\[.*\].*\[.*\]',
            'greedy_algorithm': r'greedy|optimal.*local',
            'kmp_algorithm': r'pattern.*matching.*prefix',
            'kruskal_algorithm': r'minimum.*spanning.*tree.*sort.*edge',
            'prim_algorithm': r'minimum.*spanning.*tree.*priority.*queue',
            'floyd_warshall': r'all.*pairs.*shortest.*path',
            'topological_sort': r'directed.*acyclic.*graph.*order',
            'a_star_search': r'heuristic.*open.*closed.*priority',
            'huffman_coding': r'frequency.*prefix.*compression'
        }
    
    def parse(self, code: str) -> Any:
        """Parse Python code into an AST"""
        try:
            return ast.parse(code)
        except SyntaxError as e:
            print(f"Syntax error in the provided Python code: {e}")
            return None
    
    def get_functions(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract function information from Python AST"""
        functions = []
        for node in ast.walk(parsed_code):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'params': [arg.arg for arg in node.args.args],
                    'has_return': any(isinstance(n, ast.Return) for n in ast.walk(node)),
                    'line_num': node.lineno,
                    'is_recursive': False,
                    'docstring': ast.get_docstring(node) or "",
                    'complexity': self._estimate_complexity(node)
                }
                
                # Check for recursion
                for inner_node in ast.walk(node):
                    if isinstance(inner_node, ast.Call) and getattr(inner_node.func, 'id', '') == node.name:
                        func_info['is_recursive'] = True
                        break
                
                functions.append(func_info)
        return functions
    
    def _estimate_complexity(self, node: ast.AST) -> str:
        """Estimate time complexity of a function based on loop nesting"""
        max_loop_depth = 0
        current_depth = 0
        
        def traverse(node):
            nonlocal max_loop_depth, current_depth
            
            if isinstance(node, (ast.For, ast.While)):
                current_depth += 1
                max_loop_depth = max(max_loop_depth, current_depth)
                for child in ast.iter_child_nodes(node):
                    traverse(child)
                current_depth -= 1
            else:
                for child in ast.iter_child_nodes(node):
                    traverse(child)
        
        traverse(node)
        
        if max_loop_depth == 0:
            return "O(1)"
        elif max_loop_depth == 1:
            return "O(n)"
        elif max_loop_depth == 2:
            return "O(n²)"
        elif max_loop_depth == 3:
            return "O(n³)"
        else:
            return f"O(n^{max_loop_depth})"
    
    def get_loops(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract loop information from Python AST"""
        loops = []
        for node in ast.walk(parsed_code):
            if isinstance(node, ast.For):
                loop_info = {
                    'type': 'for',
                    'line_num': node.lineno,
                    'target': getattr(node.target, 'id', str(node.target)) if isinstance(node.target, ast.Name) else str(node.target),
                    'iter_type': type(node.iter).__name__,
                }
                loops.append(loop_info)
            elif isinstance(node, ast.While):
                loop_info = {
                    'type': 'while',
                    'line_num': node.lineno,
                    'condition': self._get_condition_str(node.test),
                }
                loops.append(loop_info)
        return loops
    
    def _get_condition_str(self, node: ast.AST) -> str:
        """Convert condition AST node to string representation"""
        if isinstance(node, ast.Compare):
            left = self._get_condition_str(node.left)
            ops = []
            for i, op in enumerate(node.ops):
                op_str = {
                    ast.Eq: '==',
                    ast.NotEq: '!=',
                    ast.Lt: '<',
                    ast.LtE: '<=',
                    ast.Gt: '>',
                    ast.GtE: '>=',
                    ast.Is: 'is',
                    ast.IsNot: 'is not',
                    ast.In: 'in',
                    ast.NotIn: 'not in'
                }.get(type(op), type(op).__name__)
                right = self._get_condition_str(node.comparators[i])
                ops.append(f"{left} {op_str} {right}")
            return ' and '.join(ops)
        elif isinstance(node, ast.BoolOp):
            op_str = 'and' if isinstance(node.op, ast.And) else 'or'
            values = [self._get_condition_str(value) for value in node.values]
            return f" {op_str} ".join(values)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        else:
            return type(node).__name__
    
    def get_conditionals(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract conditional statement information from Python AST"""
        conditionals = []
        for node in ast.walk(parsed_code):
            if isinstance(node, ast.If):
                cond_info = {
                    'line_num': node.lineno,
                    'condition': self._get_condition_str(node.test),
                    'has_else': bool(node.orelse),
                    'nested_level': self._get_nested_level(node),
                }
                conditionals.append(cond_info)
        return conditionals
    
    def _get_nested_level(self, node: ast.AST, level: int = 0) -> int:
        """Calculate how deeply nested a node is in the AST"""
        if not hasattr(node, 'parent'):
            # Annotate AST with parent pointers
            for parent in ast.walk(ast.parse('') if not hasattr(node, 'root') else node.root):
                for child in ast.iter_child_nodes(parent):
                    child.parent = parent
        
        current = node
        while hasattr(current, 'parent'):
            if isinstance(current.parent, ast.If) and current in current.parent.body:
                level += 1
            current = current.parent
        
        return level
    
    def get_variables(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract variable information from Python AST"""
        variables = {}
        for node in ast.walk(parsed_code):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        if var_name not in variables:
                            variables[var_name] = {
                                'name': var_name,
                                'line_num': node.lineno,
                                'modifications': [node.lineno],
                                'data_type': self._infer_type(node.value),
                            }
                        else:
                            variables[var_name]['modifications'].append(node.lineno)
        
        return list(variables.values())
    
    def _infer_type(self, node: ast.AST) -> str:
        """Infer the data type of a value"""
        if isinstance(node, ast.List):
            return "list"
        elif isinstance(node, ast.Dict):
            return "dict"
        elif isinstance(node, ast.Set):
            return "set"
        elif isinstance(node, ast.Tuple):
            return "tuple"
        elif isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.Call):
            func_name = getattr(node.func, 'id', '') if hasattr(node.func, 'id') else str(node.func)
            if func_name in ('int', 'float', 'str', 'list', 'dict', 'set', 'tuple'):
                return func_name
            return "object"
        else:
            return "unknown"
    
    def identify_algorithm(self, code: str) -> Optional[str]:
        """Identify algorithm in Python code based on patterns"""
        for algo, pattern in self.algorithm_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                return algo
        return None

class JavaParser(CodeParser):
    """Parser for Java code"""
    
    def __init__(self):
        self.algorithm_patterns = {
            'binary_search': r'(mid|middle).*(low|left|start).*(high|right|end)|(low|left|start).*(high|right|end).*(mid|middle)',
            'linear_search': r'for\s*\(.+\).*(==|equals).+return',
            'bubble_sort': r'for\s*\(.+\).+for\s*\(.+\).+if\s*\(.+>\s*.+\)',
            'insertion_sort': r'for\s*\(.+\).+while\s*\(.+>\s*.+\)',
            'selection_sort': r'for\s*\(.+\).+min.*for\s*\(.+\)',
            'merge_sort': r'merge.+sort|sort.+merge|divide.+conquer',
            'quick_sort': r'partition.+pivot',
            'dfs': r'(stack|depth).*(push|add).*pop',
            'bfs': r'(queue|breadth).*(push|add|offer).*poll',
            'dijkstra': r'priority.*queue.*distance',
            'dynamic_programming': r'dp\[.+\]\[.+\]',
            'greedy_algorithm': r'greedy|optimal.*local',
            'kmp_algorithm': r'pattern.*matching.*prefix',
            'kruskal_algorithm': r'minimum.*spanning.*tree.*sort.*edge',
            'prim_algorithm': r'minimum.*spanning.*tree.*priority.*queue',
            'floyd_warshall': r'all.*pairs.*shortest.*path',
            'topological_sort': r'directed.*acyclic.*graph.*order',
            'a_star_search': r'heuristic.*open.*closed.*priority',
            'huffman_coding': r'frequency.*prefix.*compression'
        }
    
    def parse(self, code: str) -> Any:
        """Parse Java code using regex-based analysis (simplified)"""
        # Note: A robust implementation would use a proper Java parser like javalang
        # For this example, we'll use a simplified regex-based approach
        try:
            return {
                'code': code,
                'lines': code.split('\n')
            }
        except Exception as e:
            print(f"Error parsing Java code: {e}")
            return None
    
    def get_functions(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract method information from Java code using regex"""
        functions = []
        # Match method declarations
        method_pattern = r'(?:public|private|protected)?\s+(?:static\s+)?(?:\w+(?:<.+>)?)\s+(\w+)\s*\((.*?)\)'
        
        for i, line in enumerate(parsed_code['lines']):
            match = re.search(method_pattern, line)
            if match:
                method_name = match.group(1)
                params_str = match.group(2);
                
                # Extract parameters
                params = []
                if params_str.strip():
                    for param in params_str.split(','):
                        param_parts = param.strip().split()
                        if len(param_parts) >= 2:
                            param_type = param_parts[0]
                            param_name = param_parts[1]
                            params.append({'name': param_name, 'type': param_type})
                
                # Check for recursion (simplified)
                is_recursive = method_name in parsed_code['code'][match.end():]
                
                functions.append({
                    'name': method_name,
                    'params': [p['name'] for p in params],
                    'param_types': [p['type'] for p in params],
                    'line_num': i + 1,
                    'is_recursive': is_recursive,
                    'complexity': self._estimate_complexity(parsed_code['code'])
                })
        
        return functions
    
    def _estimate_complexity(self, code: str) -> str:
        """Estimate time complexity based on loop nesting (simplified)"""
        # Count nested loops
        lines = code.split('\n')
        max_depth = 0
        current_depth = 0
        
        for line in lines:
            if re.search(r'\bfor\s*\(', line) or re.search(r'\bwhile\s*\(', line):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif '}' in line and current_depth > 0:
                current_depth -= 1
        
        if max_depth == 0:
            return "O(1)"
        elif max_depth == 1:
            return "O(n)"
        elif max_depth == 2:
            return "O(n²)"
        else:
            return f"O(n^{max_depth})"
    
    def get_loops(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract loop information from Java code using regex"""
        loops = []
        for_pattern = r'\bfor\s*\(\s*(?:\w+\s+)?(\w+)\s*=\s*(\w+|[0-9]+)\s*;\s*\1\s*(?:<|<=|>|>=|!=)\s*(\w+|[0-9]+)\s*;'
        while_pattern = r'\bwhile\s*\(\s*(.+?)\s*\)'
        
        for i, line in enumerate(parsed_code['lines']):
            for_match = re.search(for_pattern, line)
            if for_match:
                loops.append({
                    'type': 'for',
                    'line_num': i + 1,
                    'variable': for_match.group(1),
                    'start_value': for_match.group(2),
                    'end_condition': for_match.group(3)
                })
                continue
            
            while_match = re.search(while_pattern, line)
            if while_match:
                loops.append({
                    'type': 'while',
                    'line_num': i + 1,
                    'condition': while_match.group(1)
                })
        
        return loops
    
    def get_conditionals(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract conditional statement information from Java code using regex"""
        conditionals = []
        if_pattern = r'\bif\s*\(\s*(.+?)\s*\)'
        
        for i, line in enumerate(parsed_code['lines']):
            if_match = re.search(if_pattern, line)
            if if_match:
                # Check if there's an else statement
                has_else = False
                if i + 1 < len(parsed_code['lines']):
                    for j in range(i + 1, min(i + 10, len(parsed_code['lines']))):
                        if 'else' in parsed_code['lines'][j]:
                            has_else = True
                            break
                
                conditionals.append({
                    'line_num': i + 1,
                    'condition': if_match.group(1),
                    'has_else': has_else
                })
        
        return conditionals
    
    def get_variables(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract variable information from Java code using regex"""
        variables = {}
        var_pattern = r'\b(?:int|float|double|long|String|boolean|char|byte|short)\s+(\w+)\s*=\s*(.+?);'
        var_pattern_no_init = r'\b(?:int|float|double|long|String|boolean|char|byte|short)\s+(\w+)\s*;'
        
        for i, line in enumerate(parsed_code['lines']):
            var_match = re.search(var_pattern, line)
            if var_match:
                var_name = var_match.group(1)
                var_value = var_match.group(2)
                var_type = line.split()[0]
                
                if var_name not in variables:
                    variables[var_name] = {
                        'name': var_name,
                        'line_num': i + 1,
                        'data_type': var_type,
                        'modifications': [i + 1]
                    }
                else:
                    variables[var_name]['modifications'].append(i + 1)
                continue
            
            var_match_no_init = re.search(var_pattern_no_init, line)
            if var_match_no_init:
                var_name = var_match_no_init.group(1)
                var_type = line.split()[0]
                
                if var_name not in variables:
                    variables[var_name] = {
                        'name': var_name,
                        'line_num': i + 1,
                        'data_type': var_type,
                        'modifications': [i + 1]
                    }
                else:
                    variables[var_name]['modifications'].append(i + 1)
        
        return list(variables.values())
    
    def identify_algorithm(self, code: str) -> Optional[str]:
        """Identify algorithm in Java code based on patterns"""
        for algo, pattern in self.algorithm_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                return algo
        return None

class CppParser(CodeParser):
    """Parser for C++ code"""
    
    def __init__(self):
        self.algorithm_patterns = {
            'binary_search': r'(mid|middle).*(low|left|start).*(high|right|end)|(low|left|start).*(high|right|end).*(mid|middle)',
            'linear_search': r'for\s*\(.+\).*(==).+return',
            'bubble_sort': r'for\s*\(.+\).+for\s*\(.+\).+if\s*\(.+>\s*.+\)',
            'insertion_sort': r'for\s*\(.+\).+while\s*\(.+>\s*.+\)',
            'selection_sort': r'for\s*\(.+\).+min.*for\s*\(.+\)',
            'merge_sort': r'merge.+sort|sort.+merge|divide.+conquer',
            'quick_sort': r'partition.+pivot',
            'dfs': r'(stack|depth).*(push).*pop',
            'bfs': r'(queue|breadth).*(push).*pop',
            'dijkstra': r'priority.*queue.*distance',
            'dynamic_programming': r'dp\[.+\]\[.+\]',
            'greedy_algorithm': r'greedy|optimal.*local',
            'kmp_algorithm': r'pattern.*matching.*prefix',
            'kruskal_algorithm': r'minimum.*spanning.*tree.*sort.*edge',
            'prim_algorithm': r'minimum.*spanning.*tree.*priority.*queue',
            'floyd_warshall': r'all.*pairs.*shortest.*path',
            'topological_sort': r'directed.*acyclic.*graph.*order',
            'a_star_search': r'heuristic.*open.*closed.*priority',
            'huffman_coding': r'frequency.*prefix.*compression'
        }
    
    def parse(self, code: str) -> Any:
        """Parse C++ code using regex-based analysis (simplified)"""
        try:
            return {
                'code': code,
                'lines': code.split('\n')
            }
        except Exception as e:
            print(f"Error parsing C++ code: {e}")
            return None
    
    def get_functions(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract function information from C++ code using regex"""
        functions = []
        # Match function declarations
        func_pattern = r'(?:(?:inline|static|constexpr|virtual)\s+)?(?:\w+\s+)?(\w+)\s*\((.*?)\)\s*(?:const)?\s*{'
        
        for i, line in enumerate(parsed_code['lines']):
            match = re.search(func_pattern, line)
            if match:
                func_name = match.group(1)
                params_str = match.group(2)
                
                # Extract parameters
                params = []
                if params_str.strip() and params_str != "void":
                    for param in params_str.split(','):
                        param = param.strip()
                        # Handle complex C++ parameter declarations
                        param_parts = param.split()
                        if len(param_parts) >= 2:
                            param_name = param_parts[-1].replace('*', '').replace('&', '')
                            params.append(param_name)
                
                # Check for recursion (simplified)
                is_recursive = func_name in parsed_code['code'][match.end():]
                
                functions.append({
                    'name': func_name,
                    'params': params,
                    'line_num': i + 1,
                    'is_recursive': is_recursive,
                    'complexity': self._estimate_complexity(parsed_code['code'])
                })
        
        return functions
    
    def _estimate_complexity(self, code: str) -> str:
        """Estimate time complexity based on loop nesting (simplified)"""
        lines = code.split('\n')
        max_depth = 0
        current_depth = 0
        
        for line in lines:
            if re.search(r'\bfor\s*\(', line) or re.search(r'\bwhile\s*\(', line):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif '}' in line and current_depth > 0:
                current_depth -= 1
        
        if max_depth == 0:
            return "O(1)"
        elif max_depth == 1:
            return "O(n)"
        elif max_depth == 2:
            return "O(n²)"
        else:
            return f"O(n^{max_depth})"
    
    def get_loops(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract loop information from C++ code using regex"""
        loops = []
        for_pattern = r'\bfor\s*\(\s*(?:\w+\s+)?(\w+)\s*=\s*(\w+|[0-9]+)\s*;\s*\1\s*(?:<|<=|>|>=|!=)\s*(\w+|[0-9]+)\s*;'
        while_pattern = r'\bwhile\s*\(\s*(.+?)\s*\)'
        
        for i, line in enumerate(parsed_code['lines']):
            for_match = re.search(for_pattern, line)
            if for_match:
                loops.append({
                    'type': 'for',
                    'line_num': i + 1,
                    'variable': for_match.group(1),
                    'start_value': for_match.group(2),
                    'end_condition': for_match.group(3)
                })
                continue
            
            while_match = re.search(while_pattern, line)
            if while_match:
                loops.append({
                    'type': 'while',
                    'line_num': i + 1,
                    'condition': while_match.group(1)
                })
        
        return loops
    
    def get_conditionals(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract conditional statement information from C++ code using regex"""
        conditionals = []
        if_pattern = r'\bif\s*\(\s*(.+?)\s*\)'
        
        for i, line in enumerate(parsed_code['lines']):
            if_match = re.search(if_pattern, line)
            if if_match:
                has_else = False
                if i + 1 < len(parsed_code['lines']):
                    for j in range(i + 1, min(i + 10, len(parsed_code['lines']))):
                        if 'else' in parsed_code['lines'][j]:
                            has_else = True
                            break
                
                conditionals.append({
                    'line_num': i + 1,
                    'condition': if_match.group(1),
                    'has_else': has_else
                })
        
        return conditionals
    
    def get_variables(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract variable information from C++ code using regex"""
        variables = {}
        var_pattern = r'\b(?:int|float|double|long|string|bool|char|auto|size_t|unsigned|short)\s+(\w+)\s*(?:\[\s*\d+\s*\])?\s*=\s*(.+?);'
        var_pattern_no_init = r'\b(?:int|float|double|long|string|bool|char|auto|size_t|unsigned|short)\s+(\w+)\s*(?:\[\s*\d+\s*\])?\s*;'
        
        for i, line in enumerate(parsed_code['lines']):
            var_match = re.search(var_pattern, line)
            if var_match:
                var_name = var_match.group(1)
                var_value = var_match.group(2)
                var_type = line.split()[0]
                
                if var_name not in variables:
                    variables[var_name] = {
                        'name': var_name,
                        'line_num': i + 1,
                        'data_type': var_type,
                        'modifications': [i + 1]
                    }
                else:
                    variables[var_name]['modifications'].append(i + 1)
                continue
            
            var_match_no_init = re.search(var_pattern_no_init, line)
            if var_match_no_init:
                var_name = var_match_no_init.group(1)
                var_type = line.split()[0]
                
                if var_name not in variables:
                    variables[var_name] = {
                        'name': var_name,
                        'line_num': i + 1,
                        'data_type': var_type,
                        'modifications': [i + 1]
                    }
                else:
                    variables[var_name]['modifications'].append(i + 1)
        
        return list(variables.values())
    
    def identify_algorithm(self, code: str) -> Optional[str]:
        """Identify algorithm in C++ code based on patterns"""
        for algo, pattern in self.algorithm_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                return algo
        return None

class CParser(CodeParser):
    """Parser for C code"""
    
    def __init__(self):
        self.algorithm_patterns = {
            'binary_search': r'(mid|middle).*(low|left|start).*(high|right|end)|(low|left|start).*(high|right|end).*(mid|middle)',
            'linear_search': r'for\s*\(.+\).*(==).+return',
            'bubble_sort': r'for\s*\(.+\).+for\s*\(.+\).+if\s*\(.+>\s*.+\)',
            'insertion_sort': r'for\s*\(.+\).+while\s*\(.+>\s*.+\)',
            'selection_sort': r'for\s*\(.+\).+min.*for\s*\(.+\)',
            'merge_sort': r'merge.+sort|sort.+merge|divide.+conquer',
            'quick_sort': r'partition.+pivot',
            'dfs': r'(stack|depth).*(push).*pop',
            'bfs': r'(queue|breadth).*(push).*pop',
            'dijkstra': r'priority.*queue.*distance',
            'dynamic_programming': r'dp\[.+\]\[.+\]',
            'greedy_algorithm': r'greedy|optimal.*local',
            'kmp_algorithm': r'pattern.*matching.*prefix',
            'kruskal_algorithm': r'minimum.*spanning.*tree.*sort.*edge',
            'prim_algorithm': r'minimum.*spanning.*tree.*priority.*queue',
            'floyd_warshall': r'all.*pairs.*shortest.*path',
            'topological_sort': r'directed.*acyclic.*graph.*order',
            'a_star_search': r'heuristic.*open.*closed.*priority',
            'huffman_coding': r'frequency.*prefix.*compression'
        }
    
    def parse(self, code: str) -> Any:
        """Parse C code using regex-based analysis"""
        try:
            return {
                'code': code,
                'lines': code.split('\n')
            }
        except Exception as e:
            print(f"Error parsing C code: {e}")
            return None
    
    def get_functions(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract function information from C code using regex"""
        functions = []
        # Match function declarations (simplified for C)
        func_pattern = r'(?:static\s+)?(?:\w+\s+)?(\w+)\s*\((.*?)\)\s*{'
        
        for i, line in enumerate(parsed_code['lines']):
            match = re.search(func_pattern, line)
            if match:
                func_name = match.group(1)
                params_str = match.group(2)
                
                # Extract parameters
                params = []
                if params_str.strip() and params_str != "void":
                    for param in params_str.split(','):
                        param = param.strip()
                        # Handle C parameter declarations
                        param_parts = param.split()
                        if len(param_parts) >= 2:
                            param_name = param_parts[-1].replace('*', '')
                            params.append(param_name)
                
                # Check for recursion (simplified)
                is_recursive = func_name in parsed_code['code'][match.end():]
                
                functions.append({
                    'name': func_name,
                    'params': params,
                    'line_num': i + 1,
                    'is_recursive': is_recursive,
                    'complexity': self._estimate_complexity(parsed_code['code'])
                })
        
        return functions
    
    def _estimate_complexity(self, code: str) -> str:
        """Estimate time complexity based on loop nesting"""
        lines = code.split('\n')
        max_depth = 0
        current_depth = 0
        
        for line in lines:
            if re.search(r'\bfor\s*\(', line) or re.search(r'\bwhile\s*\(', line):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif '}' in line and current_depth > 0:
                current_depth -= 1
        
        if max_depth == 0:
            return "O(1)"
        elif max_depth == 1:
            return "O(n)"
        elif max_depth == 2:
            return "O(n²)"
        else:
            return f"O(n^{max_depth})"
    
    def get_loops(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract loop information from C code using regex"""
        loops = []
        for_pattern = r'\bfor\s*\(\s*(?:\w+\s+)?(\w+)\s*=\s*(\w+|[0-9]+)\s*;\s*\1\s*(?:<|<=|>|>=|!=)\s*(\w+|[0-9]+)\s*;'
        while_pattern = r'\bwhile\s*\(\s*(.+?)\s*\)'
        
        for i, line in enumerate(parsed_code['lines']):
            for_match = re.search(for_pattern, line)
            if for_match:
                loops.append({
                    'type': 'for',
                    'line_num': i + 1,
                    'variable': for_match.group(1),
                    'start_value': for_match.group(2),
                    'end_condition': for_match.group(3)
                })
                continue
            
            while_match = re.search(while_pattern, line)
            if while_match:
                loops.append({
                    'type': 'while',
                    'line_num': i + 1,
                    'condition': while_match.group(1)
                })
        
        return loops
    
    def get_conditionals(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract conditional statement information from C code using regex"""
        conditionals = []
        if_pattern = r'\bif\s*\(\s*(.+?)\s*\)'
        
        for i, line in enumerate(parsed_code['lines']):
            if_match = re.search(if_pattern, line)
            if if_match:
                has_else = False
                if i + 1 < len(parsed_code['lines']):
                    for j in range(i + 1, min(i + 10, len(parsed_code['lines']))):
                        if 'else' in parsed_code['lines'][j]:
                            has_else = True
                            break
                
                conditionals.append({
                    'line_num': i + 1,
                    'condition': if_match.group(1),
                    'has_else': has_else
                })
        
        return conditionals
    
    def get_variables(self, parsed_code: Any) -> List[Dict[str, Any]]:
        """Extract variable information from C code using regex"""
        variables = {}
        var_pattern = r'\b(?:int|float|double|long|char|unsigned|short|size_t)\s+(\w+)\s*(?:\[\s*\d+\s*\])?\s*=\s*(.+?);'
        var_pattern_no_init = r'\b(?:int|float|double|long|char|unsigned|short|size_t)\s+(\w+)\s*(?:\[\s*\d+\s*\])?\s*;'
        
        for i, line in enumerate(parsed_code['lines']):
            var_match = re.search(var_pattern, line)
            if var_match:
                var_name = var_match.group(1)
                var_value = var_match.group(2)
                var_type = line.split()[0]
                
                if var_name not in variables:
                    variables[var_name] = {
                        'name': var_name,
                        'line_num': i + 1,
                        'data_type': var_type,
                        'modifications': [i + 1]
                    }
                else:
                    variables[var_name]['modifications'].append(i + 1)
                continue
            
            var_match_no_init = re.search(var_pattern_no_init, line)
            if var_match_no_init:
                var_name = var_match_no_init.group(1)
                var_type = line.split()[0]
                
                if var_name not in variables:
                    variables[var_name] = {
                        'name': var_name,
                        'line_num': i + 1,
                        'data_type': var_type,
                        'modifications': [i + 1]
                    }
                else:
                    variables[var_name]['modifications'].append(i + 1)
        
        return list(variables.values())
    
    def identify_algorithm(self, code: str) -> Optional[str]:
        """Identify algorithm in C code based on patterns"""
        for algo, pattern in self.algorithm_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                return algo
        return None


class MultiLanguageQuestionGenerator:
    def print_bloom_template_distribution(self):
        """Print the number of templates per Bloom level for each category and difficulty."""
        from collections import Counter, defaultdict
        print("\nBloom's Template Distribution by Category and Difficulty:")
        summary = defaultdict(lambda: Counter())
        for category, diff_dict in self.question_templates.items():
            for difficulty, templates in diff_dict.items():
                blooms = [t['bloom'] for t in templates]
                bloom_counts = Counter(blooms)
                summary[category, difficulty] = bloom_counts
        # Print nicely
        for (category, difficulty), bloom_counts in summary.items():
            print(f"  {category} [{difficulty.name}]:")
            for bloom, count in sorted(bloom_counts.items()):
                print(f"    {bloom:10}: {count}")
        # Also print total per Bloom level
        total = Counter()
        for bloom_counts in summary.values():
            total.update(bloom_counts)
        print("\nTotal templates per Bloom level:")
        for bloom, count in sorted(total.items()):
            print(f"  {bloom:10}: {count}")

    """
    Enhanced question generator for multiple programming languages
    with difficulty levels and more sophisticated templates
    """
    
    def __init__(self):
        self.parsers = {
            Language.PYTHON: PythonParser(),
            Language.JAVA: JavaParser(),
            Language.CPP: CppParser(),
            Language.C: CParser()
        }
        
        self.question_templates = self._initialize_question_templates()
    
    def _initialize_question_templates(self) -> Dict[str, Dict[DifficultyLevel, List[Dict[str, str]]]]:
        """Initialize question templates for different code elements and difficulty levels, with Bloom's taxonomy annotation"""
        # Each template is a dict with 'template' and 'bloom' keys
        # --- BEGIN PATCH: Add more templates for underrepresented Bloom levels ---
        return {
            'function': {
                DifficultyLevel.BEGINNER: [
                    {"template": "Analyze the consequences of removing function '{name}' from the code.", "bloom": "analyze"},
                    {"template": "Evaluate the impact of function '{name}' on code maintainability.", "bloom": "evaluate"},
                    {"template": "Apply the function '{name}' to a new set of inputs and predict the output.", "bloom": "apply"},
                    {"template": "Demonstrate how to use function '{name}' in a real-world scenario.", "bloom": "apply"},
                    {"template": "Analyze the effect of changing a parameter in function '{name}'.", "bloom": "analyze"},
                    {"template": "Evaluate the readability of function '{name}' and suggest improvements.", "bloom": "evaluate"},
                    # ...existing code...
                ],
                DifficultyLevel.INTERMEDIATE: [
                    {"template": "Analyze the dependencies between function '{name}' and other functions.", "bloom": "analyze"},
                    {"template": "Evaluate the testability of function '{name}'.", "bloom": "evaluate"},
                    {"template": "Apply function '{name}' to a boundary case and explain the result.", "bloom": "apply"},
                    {"template": "Demonstrate the use of function '{name}' in a different context.", "bloom": "apply"},
                    {"template": "Analyze the impact of removing a parameter from function '{name}'.", "bloom": "analyze"},
                    {"template": "Evaluate the efficiency of function '{name}' for large datasets.", "bloom": "evaluate"},
                    {"template": "Recall a scenario where function '{name}' would be most useful.", "bloom": "remember"},
                    {"template": "List the possible outputs of function '{name}' given different inputs.", "bloom": "remember"},
                    {"template": "Explain in detail how function '{name}' transforms its inputs to outputs.", "bloom": "understand"},
                    {"template": "Summarize the changes you would make to function '{name}' to adapt it for a new requirement.", "bloom": "create"},
                    {"template": "Devise a new use case for function '{name}' in a different context.", "bloom": "create"},
                    # ...existing code...
                    {"template": "Recall the return type of function '{name}'.", "bloom": "remember"},
                    {"template": "List all parameters and their types for function '{name}'.", "bloom": "remember"},
                    {"template": "Describe a scenario where function '{name}' would be useful.", "bloom": "understand"},
                    {"template": "Summarize the changes you would make to function '{name}' to add a new feature.", "bloom": "create"},
                    {"template": "Propose a modification to function '{name}' to improve its efficiency.", "bloom": "create"},
                ],
                DifficultyLevel.ADVANCED: [
                    {"template": "Analyze the security implications of function '{name}'.", "bloom": "analyze"},
                    {"template": "Evaluate the scalability of function '{name}' in distributed systems.", "bloom": "evaluate"},
                    {"template": "Apply function '{name}' in a multi-threaded environment and discuss the outcome.", "bloom": "apply"},
                    {"template": "Demonstrate how to refactor function '{name}' for better modularity.", "bloom": "apply"},
                    {"template": "Analyze the trade-offs between time and space complexity in function '{name}'.", "bloom": "analyze"},
                    {"template": "Evaluate the robustness of function '{name}' under invalid input.", "bloom": "evaluate"},
                    {"template": "Recall a time when a similar function to '{name}' caused a bug. How would you prevent it here?", "bloom": "remember"},
                    {"template": "Explain the rationale behind the design of function '{name}'.", "bloom": "understand"},
                    {"template": "Summarize the improvements you would make to function '{name}' for scalability.", "bloom": "understand"},
                    {"template": "Invent a new function that extends the capabilities of '{name}'.", "bloom": "create"},
                    {"template": "Design a test suite to validate all edge cases for function '{name}'.", "bloom": "create"},
                    # ...existing code...
                    {"template": "Recall the signature and return type of function '{name}'.", "bloom": "remember"},
                    {"template": "Describe the most complex part of function '{name}'.", "bloom": "understand"},
                    {"template": "Summarize the improvements you would make to function '{name}' for scalability.", "bloom": "create"},
                    {"template": "Invent a new function inspired by '{name}' that solves a related problem.", "bloom": "create"},
                ]
            },
            'loop': {
                DifficultyLevel.BEGINNER: [
                    {"template": "Analyze the effect of removing the {type} loop on program output.", "bloom": "analyze"},
                    {"template": "Evaluate the necessity of the {type} loop on line {line_num} for program correctness.", "bloom": "evaluate"},
                    {"template": "Apply the {type} loop on line {line_num} to a new input and describe the result.", "bloom": "apply"},
                    {"template": "Demonstrate the use of a different loop type for the same logic.", "bloom": "apply"},
                    {"template": "Analyze the effect of changing the loop's start value.", "bloom": "analyze"},
                    {"template": "Evaluate the maintainability of the {type} loop on line {line_num}.", "bloom": "evaluate"},
                    # ...existing code...
                ],
                DifficultyLevel.INTERMEDIATE: [
                    {"template": "Analyze the interaction between nested loops in the code.", "bloom": "analyze"},
                    {"template": "Evaluate the impact of the {type} loop on memory usage.", "bloom": "evaluate"},
                    {"template": "Apply the {type} loop to process a reversed list and explain the output.", "bloom": "apply"},
                    {"template": "Demonstrate how to break out of the {type} loop early.", "bloom": "apply"},
                    {"template": "Analyze the impact of nested loops on performance.", "bloom": "analyze"},
                    {"template": "Evaluate the scalability of the {type} loop for large data sets.", "bloom": "evaluate"},
                    {"template": "Recall a common mistake when writing {type} loops and how to avoid it.", "bloom": "remember"},
                    {"template": "List all {type} loops in the code and their purposes.", "bloom": "remember"},
                    {"template": "Explain why a {type} loop was chosen over other loop types on line {line_num}.", "bloom": "understand"},
                    {"template": "Summarize the effect of changing the loop variable's increment in the {type} loop.", "bloom": "understand"},
                    {"template": "Create a new {type} loop that achieves the same result with fewer lines of code.", "bloom": "create"},
                    # ...existing code...
                    {"template": "Recall the type of loop used on line {line_num}.", "bloom": "remember"},
                    {"template": "List all variables modified inside the {type} loop on line {line_num}.", "bloom": "remember"},
                    {"template": "Describe a real-world scenario where a {type} loop is appropriate.", "bloom": "understand"},
                    {"template": "Summarize the changes you would make to the {type} loop to handle a new requirement.", "bloom": "create"},
                ],
                DifficultyLevel.ADVANCED: [
                    {"template": "Analyze the concurrency issues that may arise in the {type} loop.", "bloom": "analyze"},
                    {"template": "Evaluate the trade-offs of using the {type} loop versus recursion.", "bloom": "evaluate"},
                    {"template": "Apply the {type} loop in a parallel processing context.", "bloom": "apply"},
                    {"template": "Demonstrate loop fusion to optimize performance.", "bloom": "apply"},
                    {"template": "Analyze the bottlenecks caused by the {type} loop.", "bloom": "analyze"},
                    {"template": "Evaluate the effect of loop invariants on correctness.", "bloom": "evaluate"},
                    {"template": "Recall a scenario where a poorly designed loop caused performance issues. How would you address it here?", "bloom": "remember"},
                    {"template": "Explain the impact of loop unrolling on the {type} loop on line {line_num}.", "bloom": "understand"},
                    {"template": "Summarize the trade-offs between different loop structures for this problem.", "bloom": "understand"},
                    {"template": "Invent a new loop structure to optimize the code's performance.", "bloom": "create"},
                    {"template": "Design a parallel version of the {type} loop for distributed systems.", "bloom": "create"},
                    # ...existing code...
                    {"template": "Recall the main variable controlling the {type} loop on line {line_num}.", "bloom": "remember"},
                    {"template": "Describe the most complex aspect of the {type} loop on line {line_num}.", "bloom": "understand"},
                    {"template": "Invent a new loop structure to optimize the code on line {line_num}.", "bloom": "create"},
                ]
            },
            'condition': {
                DifficultyLevel.BEGINNER: [
                    {"template": "Analyze the effect of removing the condition on line {line_num}.", "bloom": "analyze"},
                    {"template": "Evaluate the importance of the condition on line {line_num} for program safety.", "bloom": "evaluate"},
                    {"template": "Apply the condition on line {line_num} to a new scenario.", "bloom": "apply"},
                    {"template": "Demonstrate the use of a compound condition.", "bloom": "apply"},
                    {"template": "Analyze the effect of changing the condition's logic.", "bloom": "analyze"},
                    {"template": "Evaluate the clarity of the conditional statement on line {line_num}.", "bloom": "evaluate"},
                    # ...existing code...
                ],
                DifficultyLevel.INTERMEDIATE: [
                    {"template": "Analyze the logical flow created by the condition on line {line_num}.", "bloom": "analyze"},
                    {"template": "Evaluate the effectiveness of the condition for preventing errors.", "bloom": "evaluate"},
                    {"template": "Apply the condition on line {line_num} to a boundary case.", "bloom": "apply"},
                    {"template": "Demonstrate the use of short-circuit logic in a new condition.", "bloom": "apply"},
                    {"template": "Analyze the impact of nested conditionals.", "bloom": "analyze"},
                    {"template": "Evaluate the effectiveness of the condition for error handling.", "bloom": "evaluate"},
                    {"template": "Recall a situation where a conditional statement led to a bug. How could it be prevented?", "bloom": "remember"},
                    {"template": "List all unique conditions checked in the code.", "bloom": "remember"},
                    {"template": "Explain the difference between the condition on line {line_num} and similar conditions elsewhere.", "bloom": "understand"},
                    {"template": "Summarize the logic behind combining multiple conditions on line {line_num}.", "bloom": "understand"},
                    {"template": "Create a new condition to handle an additional edge case.", "bloom": "create"},
                    # ...existing code...
                    {"template": "Recall the condition being checked on line {line_num}.", "bloom": "remember"},
                    {"template": "List all variables involved in the condition on line {line_num}.", "bloom": "remember"},
                    {"template": "Describe a real-world analogy for the condition on line {line_num}.", "bloom": "understand"},
                    {"template": "Invent a new condition to check for an additional case on line {line_num}.", "bloom": "create"},
                ],
                DifficultyLevel.ADVANCED: [
                    {"template": "Analyze the maintainability of complex conditionals in the code.", "bloom": "analyze"},
                    {"template": "Evaluate the impact of conditionals on code performance.", "bloom": "evaluate"},
                    {"template": "Apply the condition on line {line_num} in a multi-branch scenario.", "bloom": "apply"},
                    {"template": "Demonstrate how to refactor complex conditionals for readability.", "bloom": "apply"},
                    {"template": "Analyze the risks of deeply nested conditionals.", "bloom": "analyze"},
                    {"template": "Evaluate the impact of conditionals on program correctness.", "bloom": "evaluate"},
                    {"template": "Recall a time when a missing condition caused a failure. How would you fix it here?", "bloom": "remember"},
                    {"template": "Explain the consequences of incorrect condition ordering on line {line_num}.", "bloom": "understand"},
                    {"template": "Summarize the impact of nested conditionals on code maintainability.", "bloom": "understand"},
                    {"template": "Invent a new conditional structure to improve code safety.", "bloom": "create"},
                    {"template": "Design a set of conditions to validate all possible input scenarios.", "bloom": "create"},
                    # ...existing code...
                    {"template": "Recall the main variable in the condition on line {line_num}.", "bloom": "remember"},
                    {"template": "Describe the most complex aspect of the condition on line {line_num}.", "bloom": "understand"},
                    {"template": "Invent a new conditional structure to improve reliability on line {line_num}.", "bloom": "create"},
                ]
            },
            'variable': {
                DifficultyLevel.BEGINNER: [
                    {"template": "Analyze the consequences of changing the type of variable '{name}'.", "bloom": "analyze"},
                    {"template": "Evaluate the impact of variable '{name}' on program output.", "bloom": "evaluate"},
                    {"template": "Apply variable '{name}' in a new assignment and predict the result.", "bloom": "apply"},
                    {"template": "Demonstrate the use of variable '{name}' in a different function.", "bloom": "apply"},
                    {"template": "Analyze the effect of changing the type of variable '{name}'.", "bloom": "analyze"},
                    {"template": "Evaluate the naming convention of variable '{name}'.", "bloom": "evaluate"},
                    # ...existing code...
                ],
                DifficultyLevel.INTERMEDIATE: [
                    {"template": "Analyze the risks of using variable '{name}' in multiple functions.", "bloom": "analyze"},
                    {"template": "Evaluate the appropriateness of variable '{name}' for its purpose.", "bloom": "evaluate"},
                    {"template": "Apply variable '{name}' in a new context and explain the outcome.", "bloom": "apply"},
                    {"template": "Demonstrate variable shadowing with '{name}'.", "bloom": "apply"},
                    {"template": "Analyze the dependencies of variable '{name}' in the code.", "bloom": "analyze"},
                    {"template": "Evaluate the impact of variable '{name}' on code readability.", "bloom": "evaluate"},
                    {"template": "Recall the last value assigned to variable '{name}' in the code.", "bloom": "remember"},
                    {"template": "List all variables that interact with '{name}'.", "bloom": "remember"},
                    {"template": "Explain how variable '{name}' changes throughout the program.", "bloom": "understand"},
                    {"template": "Summarize the dependencies of variable '{name}'.", "bloom": "understand"},
                    {"template": "Create a new variable to optimize memory usage in the code.", "bloom": "create"},
                    # ...existing code...
                    {"template": "Recall the data type of variable '{name}'.", "bloom": "remember"},
                    {"template": "List all lines where variable '{name}' is used.", "bloom": "remember"},
                    {"template": "Describe a scenario where variable '{name}' is essential.", "bloom": "understand"},
                    {"template": "Invent a new variable to store additional information in the code.", "bloom": "create"},
                ],
                DifficultyLevel.ADVANCED: [
                    {"template": "Analyze the effect of variable '{name}' on concurrency.", "bloom": "analyze"},
                    {"template": "Evaluate the trade-offs of using global versus local variables.", "bloom": "evaluate"},
                    {"template": "Apply variable '{name}' in a concurrent context and discuss the result.", "bloom": "apply"},
                    {"template": "Demonstrate the use of immutable variables for safety.", "bloom": "apply"},
                    {"template": "Analyze the risks of variable aliasing in the code.", "bloom": "analyze"},
                    {"template": "Evaluate the effect of variable scope on program behavior.", "bloom": "evaluate"},
                    {"template": "Recall a scenario where improper variable usage led to a bug. How would you prevent it here?", "bloom": "remember"},
                    {"template": "Explain the impact of variable '{name}' on the program's performance.", "bloom": "understand"},
                    {"template": "Summarize the risks of using global variables in this code.", "bloom": "understand"},
                    {"template": "Invent a new variable naming convention to improve code clarity.", "bloom": "create"},
                    {"template": "Design a refactoring plan to minimize variable scope in the code.", "bloom": "create"},
                    # ...existing code...
                    {"template": "Recall the initial value and type of variable '{name}'.", "bloom": "remember"},
                    {"template": "Describe the most complex use of variable '{name}' in the code.", "bloom": "understand"},
                    {"template": "Invent a new variable and explain how it would improve the code.", "bloom": "create"},
                ]
            },
            'algorithm': {
                DifficultyLevel.BEGINNER: [
                    {"template": "Analyze the effect of changing the input type for this algorithm.", "bloom": "analyze"},
                    {"template": "Evaluate the effectiveness of this algorithm for different problem sizes.", "bloom": "evaluate"},
                    {"template": "Apply this algorithm to a new input and describe the result.", "bloom": "apply"},
                    {"template": "Demonstrate the use of this algorithm in a real-world problem.", "bloom": "apply"},
                    {"template": "Analyze the effect of changing the input size on this algorithm.", "bloom": "analyze"},
                    {"template": "Evaluate the suitability of this algorithm for different data types.", "bloom": "evaluate"},
                    # ...existing code...
                ],
                DifficultyLevel.INTERMEDIATE: [
                    {"template": "Analyze the impact of algorithmic complexity on resource usage.", "bloom": "analyze"},
                    {"template": "Evaluate the reliability of this algorithm in edge cases.", "bloom": "evaluate"},
                    {"template": "Apply this algorithm to a sorted input and explain the result.", "bloom": "apply"},
                    {"template": "Demonstrate the algorithm's use in a different domain.", "bloom": "apply"},
                    {"template": "Analyze the impact of algorithmic choices on performance.", "bloom": "analyze"},
                    {"template": "Evaluate the trade-offs between this algorithm and another.", "bloom": "evaluate"},
                    {"template": "Recall the input and output types for this algorithm.", "bloom": "remember"},
                    {"template": "List the steps required to implement this algorithm from scratch.", "bloom": "remember"},
                    {"template": "Explain the difference between this algorithm and a similar one.", "bloom": "understand"},
                    {"template": "Summarize the main challenges in implementing this algorithm.", "bloom": "understand"},
                    {"template": "Create a new variant of this algorithm for a related problem.", "bloom": "create"},
                    # ...existing code...
                    {"template": "Recall the name of the algorithm implemented.", "bloom": "remember"},
                    {"template": "List all steps required to implement this algorithm.", "bloom": "remember"},
                    {"template": "Describe a real-world analogy for this algorithm.", "bloom": "understand"},
                    {"template": "Invent a new step to improve the algorithm's performance.", "bloom": "create"},
                ],
                DifficultyLevel.ADVANCED: [
                    {"template": "Analyze the scalability limitations of this algorithm.", "bloom": "analyze"},
                    {"template": "Evaluate the algorithm's suitability for real-time systems.", "bloom": "evaluate"},
                    {"template": "Apply this algorithm in a distributed system and discuss the challenges.", "bloom": "apply"},
                    {"template": "Demonstrate how to optimize this algorithm for parallel execution.", "bloom": "apply"},
                    {"template": "Analyze the limitations of this algorithm in edge cases.", "bloom": "analyze"},
                    {"template": "Evaluate the algorithm's performance on large-scale data.", "bloom": "evaluate"},
                    {"template": "Recall a real-world application of this algorithm.", "bloom": "remember"},
                    {"template": "Explain the historical context or origin of this algorithm.", "bloom": "understand"},
                    {"template": "Summarize the trade-offs between this algorithm and alternatives.", "bloom": "understand"},
                    {"template": "Invent a new algorithm inspired by the one in the code.", "bloom": "create"},
                    {"template": "Design an experiment to compare this algorithm's performance with others.", "bloom": "create"},
                    # ...existing code...
                    {"template": "Recall the main problem solved by this algorithm.", "bloom": "remember"},
                    {"template": "Describe the most complex part of this algorithm.", "bloom": "understand"},
                    {"template": "Invent a new algorithm inspired by this one to solve a related problem.", "bloom": "create"},
                ]
            }
        }
        # --- END PATCH ---
    

    def detect_language(self, code: str) -> Language:
        """Detect the programming language of the provided code"""

        # C++ Detection
        if '#include' in code and (
            'std::' in code or 'namespace' in code or 'class ' in code or 'cout' in code or 'cin' in code or 'vector<' in code or 
            'template <' in code or '<iostream>' in code
        ):
            return Language.CPP

        # C Detection
        if '#include' in code and (
            '<stdio.h>' in code or '<stdlib.h>' in code or '<string.h>' in code or 'typedef struct' in code or 'printf' in code or 
            'scanf' in code or '#define' in code
        ):
            if not (
                'std::' in code or 'namespace' in code or 'class ' in code or 'cout' in code or 'cin' in code or '<iostream>' in code
            ):
                return Language.C

        # Java Detection
        if 'public class' in code or 'public static void main' in code or 'extends' in code or 'implements' in code:
            return Language.JAVA

        # Python Detection
        if 'def ' in code and ':' in code or 'import ' in code or ('class ' in code and ':' in code):
            return Language.PYTHON

        # Return UNKNOWN if the language can't be determined
        return Language.UNKNOWN
      
    def generate_params_example(self, params: List[str]) -> str:
        """Generate example parameter values for function calls"""
        if not params:
            return "()"
            
        examples = []
        for param in params:
            param = param.lower()
            if 'index' in param or 'idx' in param or 'position' in param:
                examples.append("0")
            elif 'list' in param or 'array' in param or '[]' in param:
                examples.append("[1, 2, 3]")
            elif 'str' in param or 'name' in param or 'text' in param:
                examples.append("'example'")
            elif 'num' in param or 'count' in param or 'size' in param:
                examples.append("5")
            elif 'bool' in param or 'flag' in param:
                examples.append("True")
            elif 'map' in param or 'dict' in param:
                examples.append("{key: value}")
            else:
                examples.append("x")
        
        return ", ".join(examples)
    
    def generate_function_questions(self, functions: List[Dict[str, Any]], difficulty: DifficultyLevel) -> List[Dict[str, Any]]:
        """Generate all possible questions about functions at the specified difficulty level (no Bloom enforcement here)"""
        all_questions = []
        for func in functions:
            templates = self.question_templates['function'][difficulty]
            for template_info in templates:
                template = template_info["template"]
                bloom = template_info["bloom"]
                if '{params_example}' in template and 'params' in func:
                    params_example = self.generate_params_example(func['params'])
                    question = template.format(name=func['name'], params_example=params_example)
                else:
                    question = template.format(name=func['name'])
                all_questions.append({
                    'question': question,
                    'difficulty': difficulty.value,
                    'category': 'function',
                    'function_name': func['name'],
                    'bloom': bloom,
                })
        return all_questions
    
    def generate_loop_questions(self, loops: List[Dict[str, Any]], difficulty: DifficultyLevel) -> List[Dict[str, Any]]:
        """Generate all possible questions about loops at the specified difficulty level (no Bloom enforcement here)"""
        all_questions = []
        for loop in loops:
            templates = self.question_templates['loop'][difficulty]
            for template_info in templates:
                template = template_info["template"]
                bloom = template_info["bloom"]
                try:
                    question = template.format(**loop)
                except Exception:
                    continue
                all_questions.append({
                    'question': question,
                    'difficulty': difficulty.value,
                    'category': 'loop',
                    'loop_type': loop.get('type', 'loop'),
                    'line_num': loop.get('line_num', 'unknown'),
                    'bloom': bloom,
                })
        return all_questions
    
    def generate_conditional_questions(self, conditionals: List[Dict[str, Any]], difficulty: DifficultyLevel) -> List[Dict[str, Any]]:
        """Generate all possible questions about conditionals at the specified difficulty level (no Bloom enforcement here)"""
        all_questions = []
        for cond in conditionals:
            templates = self.question_templates['condition'][difficulty]
            for template_info in templates:
                template = template_info["template"]
                bloom = template_info["bloom"]
                try:
                    question = template.format(**cond)
                except Exception:
                    continue
                all_questions.append({
                    'question': question,
                    'difficulty': difficulty.value,
                    'category': 'condition',
                    'line_num': cond.get('line_num', 'unknown'),
                    'bloom': bloom,
                })
        return all_questions
    
    def generate_variable_questions(self, variables: List[Dict[str, Any]], difficulty: DifficultyLevel) -> List[Dict[str, Any]]:
        """Generate all possible questions about variables at the specified difficulty level (no Bloom enforcement here)"""
        all_questions = []
        for var in variables:
            templates = self.question_templates['variable'][difficulty]
            for template_info in templates:
                template = template_info["template"]
                bloom = template_info["bloom"]
                try:
                    question = template.format(**var)
                except Exception:
                    continue
                all_questions.append({
                    'question': question,
                    'difficulty': difficulty.value,
                    'category': 'variable',
                    'variable_name': var.get('name', 'unknown'),
                    'bloom': bloom,
                })
        return all_questions
    
    def generate_algorithm_questions(self, algorithm: str, code: str, difficulty: DifficultyLevel) -> List[Dict[str, Any]]:
        """Generate all possible questions about the algorithm at the specified difficulty level (no Bloom enforcement here)"""
        all_questions = []
        if algorithm:
            templates = self.question_templates['algorithm'][difficulty]
            for template_info in templates:
                template = template_info["template"]
                bloom = template_info["bloom"]
                # Generate example input based on algorithm type
                example_input = "[1, 3, 5, 7, 9]"  # Default
                if 'sort' in algorithm:
                    example_input = "[5, 2, 9, 1, 7]"
                elif 'search' in algorithm:
                    example_input = "[1, 2, 3, 4, 5], target=3"
                elif 'path' in algorithm:
                    example_input = "graph={'A': ['B', 'C'], 'B': ['D'], 'C': ['D']}, start='A', end='D'"
                try:
                    question = template.format(algorithm=algorithm, example_input=example_input)
                except Exception:
                    continue
                all_questions.append({
                    'question': question,
                    'difficulty': difficulty.value,
                    'category': 'algorithm',
                    'algorithm_name': algorithm,
                    'bloom': bloom,
                })
        return all_questions
    def _enforce_bloom_distribution(self, questions: List[Dict[str, Any]], num_questions: int = 6) -> List[Dict[str, Any]]:
        """Randomly sample questions, but limit the max per Bloom level to avoid domination. Distribution is random but not strictly even, allowing some levels to be more frequent."""
        import collections, math, random
        if not questions:
            return []

        # Group questions by Bloom level
        bloom_groups = collections.defaultdict(list)
        for q in questions:
            bloom = q.get('bloom', 'other')
            bloom_groups[bloom].append(q)

        bloom_levels = list(bloom_groups.keys())
        n_levels = len(bloom_levels)
        if n_levels == 0:
            return random.sample(questions, min(num_questions, len(questions)))

        # Set a soft cap for each Bloom level (allowing some levels to be more frequent, e.g., up to 40% for any one level)
        min_cap = max(1, num_questions // n_levels)
        max_cap = max(min_cap + 1, int(num_questions * 0.4))  # No more than 40% from any one level
        # Shuffle all questions for randomness
        all_qs = questions[:]
        random.shuffle(all_qs)

        # Track how many picked per Bloom level
        picked_per_bloom = collections.defaultdict(int)
        result = []
        for q in all_qs:
            bloom = q.get('bloom', 'other')
            if picked_per_bloom[bloom] < max_cap:
                result.append(q)
                picked_per_bloom[bloom] += 1
            if len(result) >= num_questions:
                break

        # If not enough, fill with any remaining
        if len(result) < num_questions:
            leftovers = [q for q in all_qs if q not in result]
            random.shuffle(leftovers)
            result.extend(leftovers[:num_questions - len(result)])

        return result[:num_questions]
    def generate_questions(self, code: str, num_questions: int = 6, difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE, min_remember: int = 1, min_evaluate: int = 1) -> List[Dict[str, Any]]:
        """Generate questions for the given code with the specified difficulty level, enforcing Bloom's rule only at the end."""
        language = self.detect_language(code)
        parser = self.parsers[language]

        parsed_code = parser.parse(code)
        if not parsed_code:
            return [{'question': f"There seems to be a syntax error in the {language.value} code. Can you fix it?", 'difficulty': difficulty.value, 'category': 'general'}]

        functions = parser.get_functions(parsed_code)
        loops = parser.get_loops(parsed_code)
        conditionals = parser.get_conditionals(parsed_code)
        variables = parser.get_variables(parsed_code)
        algorithm = parser.identify_algorithm(code)

        all_questions = []

        if functions:
            all_questions.extend(self.generate_function_questions(functions, difficulty))

        if loops:
            all_questions.extend(self.generate_loop_questions(loops, difficulty))

        if conditionals:
            all_questions.extend(self.generate_conditional_questions(conditionals, difficulty))

        if variables:
            all_questions.extend(self.generate_variable_questions(variables, difficulty))

        if algorithm:
            all_questions.extend(self.generate_algorithm_questions(algorithm, code, difficulty))

        return self._enforce_bloom_distribution(all_questions, num_questions)

        return final_questions
    
    def generate_mixed_difficulty_questions(self, code: str, num_beginner: int = 2, num_intermediate: int = 2, num_advanced: int = 1) -> List[Dict[str, Any]]:
        """Generate questions with mixed difficulty levels, always 1 remember and rest evaluate, no duplicates, correct difficulty fields."""
        slot_difficulties = (
            [DifficultyLevel.BEGINNER] * num_beginner +
            [DifficultyLevel.INTERMEDIATE] * num_intermediate +
            [DifficultyLevel.ADVANCED] * num_advanced
        )
        num_questions = len(slot_difficulties)
        all_questions = (
            self.generate_questions(code, num_beginner, DifficultyLevel.BEGINNER)
            + self.generate_questions(code, num_intermediate, DifficultyLevel.INTERMEDIATE)
            + self.generate_questions(code, num_advanced, DifficultyLevel.ADVANCED)
        )
        return self._enforce_bloom_distribution(all_questions, num_questions)
    
    def generate_quiz(self, code: str, num_questions: int = 5, mixed_difficulty: bool = True) -> Dict[str, Any]:
        """Generate a complete quiz for the given code, always 1 remember and rest evaluate, correct difficulty fields."""
        language = self.detect_language(code)
        # Determine slot difficulties
        if mixed_difficulty:
            num_beginner = max(1, num_questions // 2)
            num_advanced = max(1, num_questions // 5)
            num_intermediate = num_questions - num_beginner - num_advanced
            slot_difficulties = (
                [DifficultyLevel.BEGINNER] * num_beginner +
                [DifficultyLevel.INTERMEDIATE] * num_intermediate +
                [DifficultyLevel.ADVANCED] * num_advanced
            )
            all_questions = (
                self.generate_questions(code, num_beginner, DifficultyLevel.BEGINNER)
                + self.generate_questions(code, num_intermediate, DifficultyLevel.INTERMEDIATE)
                + self.generate_questions(code, num_advanced, DifficultyLevel.ADVANCED)
            )
        else:
            slot_difficulties = [DifficultyLevel.INTERMEDIATE] * num_questions
            all_questions = self.generate_questions(code, num_questions, DifficultyLevel.INTERMEDIATE)
        final_questions = self._enforce_bloom_distribution(all_questions, slot_difficulties)
        algorithm = self.parsers[language].identify_algorithm(code)
        algorithm_name = algorithm if algorithm else "Unknown"
        return {
            'language': language.value,
            'algorithm': algorithm_name,
            'num_questions': len(final_questions),
            'questions': final_questions
        }
    
    def evaluate_code_quality(self, code: str) -> Dict[str, Any]:
        """Evaluate code quality based on various metrics"""
        language = self.detect_language(code)
        parser = self.parsers[language]
        
        parsed_code = parser.parse(code)
        if not parsed_code:
            return {'error': f"Could not parse {language.value} code due to syntax errors"}
        
        functions = parser.get_functions(parsed_code)
        loops = parser.get_loops(parsed_code)
        conditionals = parser.get_conditionals(parsed_code)
        variables = parser.get_variables(parsed_code)
        
        # Calculate metrics
        metrics = {
            'language': language.value,
            'num_functions': len(functions),
            'num_loops': len(loops),
            'num_conditionals': len(conditionals),
            'num_variables': len(variables),
            'line_count': len(code.split('\n')),
            'complexity': self._calculate_complexity(functions, loops, conditionals)
        }
        
        return metrics
    
    def _calculate_complexity(self, functions: List[Dict[str, Any]], loops: List[Dict[str, Any]], conditionals: List[Dict[str, Any]]) -> str:
        """Calculate overall code complexity"""
        # Simple heuristic for overall complexity
        if not functions and not loops and not conditionals:
            return "Simple"
        
        recursive_functions = sum(1 for f in functions if f.get('is_recursive', False))
        nested_loops = sum(1 for l in loops if l.get('nested_level', 0) > 0)
        nested_conditionals = sum(1 for c in conditionals if c.get('nested_level', 0) > 0)
        
        complexity_score = len(functions) + len(loops) * 2 + len(conditionals) + recursive_functions * 3 + nested_loops * 2 + nested_conditionals
        
        if complexity_score < 5:
            return "Simple"
        elif complexity_score < 15:
            return "Moderate"
        elif complexity_score < 30:
            return "Complex"
        else:
            return "Very Complex"
    
    def generate_code_explanation(self, code: str) -> str:
        """Generate a detailed explanation of the code"""
        language = self.detect_language(code)
        parser = self.parsers[language]
        
        parsed_code = parser.parse(code)
        if not parsed_code:
            return f"The provided {language.value} code has syntax errors and could not be explained."
        
        functions = parser.get_functions(parsed_code)
        algorithm = parser.identify_algorithm(code)
        
        explanation = f"This is {language.value} code"
        
        if algorithm:
            explanation += f" implementing a {algorithm} algorithm"
        
        explanation += ".\n\n"
        
        if functions:
            explanation += "Functions in this code:\n"
            for func in functions:
                explanation += f"- {func['name']}({', '.join(func.get('params', []))}): "
                if func.get('docstring'):
                    explanation += f"{func['docstring']}\n"
                else:
                    explanation += "No documentation available.\n"
                
                if func.get('is_recursive', False):
                    explanation += "  This function is recursive.\n"
                
                explanation += f"  Estimated time complexity: {func.get('complexity', 'Unknown')}\n"
        
        return explanation
    
    def run_unit_tests(self, code: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run unit tests on the provided code"""
        language = self.detect_language(code)
        
        results = {
            'language': language.value,
            'total_tests': len(test_cases),
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'test_results': []
        }
        
        if language == Language.PYTHON:
            for i, test in enumerate(test_cases):
                test_result = self._run_python_test(code, test)
                results['test_results'].append(test_result)
                
                if test_result['status'] == 'passed':
                    results['passed'] += 1
                elif test_result['status'] == 'failed':
                    results['failed'] += 1
                else:
                    results['errors'] += 1
        else:
            # For other languages, we'd implement language-specific testing logic
            results['error'] = f"Automated testing for {language.value} is not implemented yet."
        
        return results
    
    def _run_python_test(self, code: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single Python test case"""
        function_name = test_case.get('function_name')
        inputs = test_case.get('inputs', [])
        expected_output = test_case.get('expected_output')
        
        if not function_name or expected_output is None:
            return {
                'test_id': test_case.get('id', 'unknown'),
                'status': 'error',
                'message': 'Invalid test case: missing function name or expected output'
            }
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            test_code = code + '\n\n'
            
            # Add the test case
            params = ', '.join(repr(inp) for inp in inputs)
            test_code += f"""
import sys
try:
    result = {function_name}({params})
    print(repr(result))
except Exception as e:
    print(f"ERROR: {{type(e).__name__}}: {{e}}")
    sys.exit(1)
"""
            temp_file.write(test_code.encode('utf-8'))
            temp_file_path = temp_file.name
        
        try:
            # Run the test
            process = subprocess.run(
                ['python', temp_file_path], 
                capture_output=True, 
                text=True,
                timeout=5  # 5 seconds timeout
            )
            
            os.unlink(temp_file_path)  # Clean up
            
            if process.returncode != 0:
                return {
                    'test_id': test_case.get('id', 'unknown'),
                    'status': 'error',
                    'message': process.stderr.strip() or process.stdout.strip()
                }
            
            # Parse the output
            actual_output = process.stdout.strip()
            
            # Evaluate using safe eval
            try:
                actual_value = eval(actual_output)
                
                if actual_value == expected_output:
                    return {
                        'test_id': test_case.get('id', 'unknown'),
                        'status': 'passed',
                        'message': 'Test passed successfully'
                    }
                else:
                    return {
                        'test_id': test_case.get('id', 'unknown'),
                        'status': 'failed',
                        'message': f'Expected {expected_output}, but got {actual_value}'
                    }
            except Exception as e:
                return {
                    'test_id': test_case.get('id', 'unknown'),
                    'status': 'error',
                    'message': f'Error evaluating output: {str(e)}'
                }
                
        except subprocess.TimeoutExpired:
            os.unlink(temp_file_path)  # Clean up
            return {
                'test_id': test_case.get('id', 'unknown'),
                'status': 'error',
                'message': 'Test timed out (possibly infinite loop)'
            }
        except Exception as e:
            try:
                os.unlink(temp_file_path)  # Clean up
            except:
                pass
            return {
                'test_id': test_case.get('id', 'unknown'),
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }

# Add a main function to demonstrate usage
def main():
    """Demonstrate the Enhanced Multilingual Code Question Generator"""
       
    import os
    generator = MultiLanguageQuestionGenerator()

    # Prompt user for an algorithm, then a language implementation
    code_samples_dir = os.path.join(os.path.dirname(__file__), "code_samples")
    print("\nAvailable algorithms in 'code_samples':")
    if not os.path.exists(code_samples_dir):
        print("No 'code_samples' directory found. Please create it and add code files.")
        return
    algo_folders = [f for f in os.listdir(code_samples_dir) if os.path.isdir(os.path.join(code_samples_dir, f))]
    if not algo_folders:
        print("No algorithm folders found in 'code_samples'. Please add at least one algorithm folder with code files.")
        return
    for idx, folder in enumerate(algo_folders, 1):
        print(f"  {idx}. {folder}")
    try:
        algo_choice = int(input(f"\nEnter the number of the algorithm to analyze (1-{len(algo_folders)}): "))
        if not (1 <= algo_choice <= len(algo_folders)):
            print("Invalid selection.")
            return
    except Exception:
        print("Invalid input.")
        return
    selected_algo = algo_folders[algo_choice - 1]
    algo_path = os.path.join(code_samples_dir, selected_algo)
    # List code files in the selected algorithm folder
    code_files = [f for f in os.listdir(algo_path) if os.path.isfile(os.path.join(algo_path, f)) and f.lower().endswith((".py", ".java", ".cpp", ".c"))]
    if not code_files:
        print(f"No code files found in '{selected_algo}'.")
        return
    print(f"\nAvailable implementations for '{selected_algo}':")
    for idx, fname in enumerate(code_files, 1):
        print(f"  {idx}. {fname}")
    try:
        file_choice = int(input(f"\nEnter the number of the code file to analyze (1-{len(code_files)}): "))
        if not (1 <= file_choice <= len(code_files)):
            print("Invalid selection.")
            return
    except Exception:
        print("Invalid input.")
        return
    selected_file = code_files[file_choice - 1]
    file_path = os.path.join(algo_path, selected_file)
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    print(f"\nAnalyzing file: {selected_algo}/{selected_file}\n")


    print("====== Generated Questions (Mixed Difficulty) ======")
    questions = generator.generate_mixed_difficulty_questions(code, 2, 2, 2)
    for i, q in enumerate(questions, 1):
        print(f"{i}. [{q['difficulty']}] {q['question']}")

    # Save generated questions to a file (CSV and JSON)
    import csv, json
    base_name = f"{selected_algo}_{os.path.splitext(selected_file)[0]}_questions"
    csv_path = os.path.join(algo_path, base_name + ".csv")
    json_path = os.path.join(algo_path, base_name + ".json")
    # Compute all fieldnames across all questions for CSV
    all_fieldnames = set()
    for q in questions:
        all_fieldnames.update(q.keys())
    fieldnames = sorted(all_fieldnames)
    # Save as CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for q in questions:
            # Fill missing fields with empty string
            row = {k: q.get(k, "") for k in fieldnames}
            writer.writerow(row)
    # Save as JSON
    with open(json_path, "w", encoding="utf-8") as jsonfile:
        json.dump(questions, jsonfile, indent=2, ensure_ascii=False)
    print(f"\nQuestions saved to: {csv_path} and {json_path}")

    print("\n====== Code Explanation ======")
    explanation = generator.generate_code_explanation(code)
    print(explanation)

    print("\n====== Code Quality Metrics ======")
    metrics = generator.evaluate_code_quality(code)
    for key, value in metrics.items():
        print(f"{key}: {value}")

    # === Automatic Evaluation ===
    # If EvaluationCodeComplete.py exists, use it to evaluate the generated questions
    eval_script = os.path.join(os.path.dirname(__file__), "EvaluationCodeComplete.py")
    if os.path.exists(eval_script):
        print("\n====== Automatic Evaluation of Generated Questions ======")
        import subprocess
        try:
            # Run the evaluation script with the generated questions file as argument (JSON preferred)
            result = subprocess.run([
                "python", eval_script, json_path
            ], capture_output=True, text=True, timeout=60)
            print(result.stdout)
            if result.stderr:
                print("[Evaluation script stderr]", result.stderr)
        except Exception as e:
            print(f"[Error running evaluation script]: {e}")
    else:
        print("\n[Info] Evaluation script 'EvaluationCodeComplete.py' not found. Skipping automatic evaluation.")


if __name__ == "__main__":
    main()
