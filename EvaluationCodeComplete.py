import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import spacy
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from scipy.stats import pearsonr
import textstat
import os

# Download required NLTK packages
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

class QuestionEvaluator:
    def __init__(self):
        self.languages = ['C', 'CPP', 'Java', 'Python']
        self.difficulty_levels = ['beginner', 'intermediate', 'advanced']
        self.dfs = {}
        
        # Define Bloom's taxonomy keywords for each level
        self.blooms_keywords = {
            'remember': ['define', 'describe', 'identify', 'list', 'name', 'recognize', 'what', 'when', 'where', 'who'],
            'understand': ['explain', 'interpret', 'summarize', 'classify', 'compare', 'discuss', 'restate', 'translate'],
            'apply': ['apply', 'demonstrate', 'implement', 'solve', 'use', 'calculate', 'execute', 'modify'],
            'analyze': ['analyze', 'break down', 'differentiate', 'examine', 'inspect', 'investigate', 'separate'],
            'evaluate': ['assess', 'critique', 'evaluate', 'judge', 'test', 'verify', 'argue', 'defend', 'support'],
            'create': ['create', 'design', 'develop', 'formulate', 'construct', 'invent', 'plan', 'produce']
        }
        
        # Weights for different metrics in the overall quality score
        self.metric_weights = {
            'linguistic_complexity': 0.15,
            'code_coverage': 0.20,
            'blooms_distribution': 0.15,
            'precision': 0.15,
            'recall': 0.10,
            'novelty': 0.10,
            'educational_alignment': 0.10,
            'cognitive_diversity': 0.05
        }
    
    def load_data(self, file_paths):
        """Load CSV data files for each programming language"""
        for lang, path in file_paths.items():
            try:
                self.dfs[lang] = pd.read_csv(path)
                print(f"Successfully loaded {lang} data with {len(self.dfs[lang])} entries")
            except Exception as e:
                print(f"Error loading {lang} data: {e}")
    
    def preprocess_data(self):
        """Preprocess the data and extract questions"""
        # Create a copy of the keys to iterate over
        language_keys = list(self.dfs.keys())
        
        for lang in language_keys:
            df = self.dfs[lang]
            # Extract questions as a list
            df['questions_list'] = df['GeneratedQuestions'].apply(
                lambda x: x.split("\n") if isinstance(x, str) else []
            )
            
            # Clean questions and extract features
            clean_questions = []
            for idx, row in df.iterrows():
                code = row['Code'] if isinstance(row['Code'], str) else ""
                complexity = row['complexity']
                
                # Extract code elements (variable names, function names)
                code_elements = self._extract_code_elements(code, lang)
                
                # Process each question
                for q in row['questions_list']:
                    # Extract difficulty level
                    level_match = re.search(r'\[(beginner|intermediate|advanced)\]', q.lower())
                    level = level_match.group(1) if level_match else "unknown"
                    
                    # Clean question text
                    clean_q = re.sub(r'\[(beginner|intermediate|advanced)\]', '', q).strip()
                    
                    if clean_q:  # Skip empty questions
                        clean_questions.append({
                            'algorithm': row['AlgorithmName'] if 'AlgorithmName' in row else f"Algorithm_{idx}",
                            'code': code,
                            'complexity': complexity,
                            'question': clean_q,
                            'level': level,
                            'code_elements': code_elements
                        })
            
            df_questions = pd.DataFrame(clean_questions)
            
            # Store the questions dataframe
            self.dfs[f"{lang}_questions"] = df_questions
            print(f"Processed {len(df_questions)} questions for {lang}")
    
    def _extract_code_elements(self, code, language):
        """Extract variable names, function names, etc. from code"""
        if not code:
            return {'variables': [], 'functions': [], 'classes': []}
        
        elements = {
            'variables': [],
            'functions': [],
            'classes': []
        }
        
        # Simple regex patterns for different languages
        # These are basic patterns and might need refinement for more accurate extraction
        if language == 'Python':
            # Variables (look for assignments)
            var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*='
            elements['variables'] = list(set(re.findall(var_pattern, code)))
            
            # Functions
            func_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
            elements['functions'] = list(set(re.findall(func_pattern, code)))
            
            # Classes
            class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            elements['classes'] = list(set(re.findall(class_pattern, code)))
            
        elif language in ['C', 'CPP', 'Java']:
            # Variables (match type declarations)
            var_pattern = r'\b(?:int|float|double|char|bool|boolean|String|long|short)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            elements['variables'] = list(set(re.findall(var_pattern, code)))
            
            # Functions (match return type + name + parameters)
            func_pattern = r'\b(?:void|int|float|double|char|bool|boolean|String|long|short)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
            elements['functions'] = list(set(re.findall(func_pattern, code)))
            
            # Classes (for C++ and Java)
            if language in ['CPP', 'Java']:
                class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)'
                elements['classes'] = list(set(re.findall(class_pattern, code)))
        
        return elements
    
    def evaluate_linguistic_complexity(self):
        """Analyze linguistic complexity of questions"""
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                
                # Calculate readability metrics
                df['flesch_reading_ease'] = df['question'].apply(lambda q: textstat.flesch_reading_ease(q))
                df['flesch_kincaid_grade'] = df['question'].apply(lambda q: textstat.flesch_kincaid_grade(q))
                df['sentence_count'] = df['question'].apply(lambda q: textstat.sentence_count(q))
                df['word_count'] = df['question'].apply(lambda q: len(q.split()))
                
                # Calculate average sentence length
                df['avg_sentence_length'] = df.apply(
                    lambda row: row['word_count'] / row['sentence_count'] if row['sentence_count'] > 0 else 0, 
                    axis=1
                )
                
                # Normalize metrics to 0-1 scale for the linguistic complexity score
                max_fk_grade = max(10, df['flesch_kincaid_grade'].max())  # Cap at 10 or the max
                df['normalized_fk_grade'] = df['flesch_kincaid_grade'].apply(lambda x: min(x / max_fk_grade, 1))
                
                max_sentence_length = 25  # Assuming 25 words is a complex sentence
                df['normalized_sentence_length'] = df['avg_sentence_length'].apply(
                    lambda x: min(x / max_sentence_length, 1)
                )
                
                # Calculate linguistic complexity score (higher = more complex)
                df['linguistic_complexity'] = 0.6 * df['normalized_fk_grade'] + 0.4 * df['normalized_sentence_length']
                
                # Update the dataframe
                self.dfs[lang] = df
                
                print(f"\n=== Linguistic Complexity Analysis for {lang_name} ===")
                print(f"Average Flesch Reading Ease: {df['flesch_reading_ease'].mean():.2f}")
                print(f"Average Flesch-Kincaid Grade: {df['flesch_kincaid_grade'].mean():.2f}")
                print(f"Average words per question: {df['word_count'].mean():.2f}")
                print(f"Average linguistic complexity score: {df['linguistic_complexity'].mean():.2f}")
                
                # Analyze by difficulty level
                for level in self.difficulty_levels:
                    level_df = df[df['level'] == level]
                    if not level_df.empty:
                        print(f"\n{level.capitalize()} questions:")
                        print(f"  Average Flesch-Kincaid Grade: {level_df['flesch_kincaid_grade'].mean():.2f}")
                        print(f"  Average linguistic complexity: {level_df['linguistic_complexity'].mean():.2f}")
    
    def evaluate_code_coverage(self):
        """Analyze how much of the code elements are covered by questions"""
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                
                # Create columns to track code element coverage
                df['variables_covered'] = df.apply(
                    lambda row: self._check_element_coverage(row['question'], row['code_elements']['variables']), 
                    axis=1
                )
                
                df['functions_covered'] = df.apply(
                    lambda row: self._check_element_coverage(row['question'], row['code_elements']['functions']), 
                    axis=1
                )
                
                # Calculate overall coverage percentage
                algorithms = df['algorithm'].unique()
                coverage_data = []
                
                for algo in algorithms:
                    algo_df = df[df['algorithm'] == algo]
                    
                    # Get all variables and functions for this algorithm
                    all_vars = set()
                    all_funcs = set()
                    
                    for _, row in algo_df.iterrows():
                        all_vars.update(row['code_elements']['variables'])
                        all_funcs.update(row['code_elements']['functions'])
                    
                    # Get all covered variables and functions
                    covered_vars = set()
                    covered_funcs = set()
                    
                    for _, row in algo_df.iterrows():
                        covered_vars.update(row['variables_covered'])
                        covered_funcs.update(row['functions_covered'])
                    
                    # Calculate coverage
                    var_coverage = len(covered_vars) / len(all_vars) if all_vars else 1.0
                    func_coverage = len(covered_funcs) / len(all_funcs) if all_funcs else 1.0
                    
                    # Weighted overall coverage (give functions more weight)
                    overall_coverage = (0.4 * var_coverage + 0.6 * func_coverage)
                    
                    coverage_data.append({
                        'algorithm': algo,
                        'var_coverage': var_coverage,
                        'func_coverage': func_coverage,
                        'overall_coverage': overall_coverage
                    })
                
                coverage_df = pd.DataFrame(coverage_data)
                self.dfs[f"{lang_name}_coverage"] = coverage_df
                
                # Add algorithm coverage to questions dataframe
                algo_coverage_map = {row['algorithm']: row['overall_coverage'] for _, row in coverage_df.iterrows()}
                df['code_coverage'] = df['algorithm'].map(algo_coverage_map)
                
                # Update the dataframe
                self.dfs[lang] = df
                
                print(f"\n=== Code Coverage Analysis for {lang_name} ===")
                print(f"Average variable coverage: {coverage_df['var_coverage'].mean():.2f}")
                print(f"Average function coverage: {coverage_df['func_coverage'].mean():.2f}")
                print(f"Average overall code coverage: {coverage_df['overall_coverage'].mean():.2f}")
    
    def _check_element_coverage(self, question, elements):
        """Check which code elements are mentioned in the question"""
        question_lower = question.lower()
        covered = []
        
        for element in elements:
            # Check if the element is mentioned in the question
            if element.lower() in question_lower:
                covered.append(element)
        
        return covered
    
    def analyze_blooms_taxonomy(self):
        """Analyze questions based on Bloom's taxonomy levels"""
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                
                # Detect Bloom's taxonomy level for each question
                blooms_levels = []
                for _, row in df.iterrows():
                    question = row['question'].lower()
                    levels_detected = {}
                    
                    for level, keywords in self.blooms_keywords.items():
                        matches = sum(1 for keyword in keywords if keyword in question)
                        levels_detected[level] = matches
                    
                    # Find the level with the most keywords (if tied, take the higher level)
                    max_matches = 0
                    primary_level = 'remember'  # Default
                    
                    # Order levels from lowest to highest
                    bloom_order = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']
                    
                    for level in bloom_order:
                        if levels_detected[level] >= max_matches:
                            max_matches = levels_detected[level]
                            primary_level = level
                    
                    blooms_levels.append(primary_level)
                
                df['blooms_level'] = blooms_levels
                
                # Map Bloom's levels to numeric values (higher = more advanced)
                bloom_values = {
                    'remember': 1,
                    'understand': 2,
                    'apply': 3,
                    'analyze': 4,
                    'evaluate': 5,
                    'create': 6
                }
                
                df['blooms_value'] = df['blooms_level'].map(bloom_values)
                
                # Normalize to 0-1 scale
                df['blooms_normalized'] = df['blooms_value'] / 6.0
                
                # Get distribution of Bloom's levels
                blooms_dist = df['blooms_level'].value_counts(normalize=True).to_dict()
                
                # Calculate Bloom's distribution evenness (higher value = more evenly distributed)
                # Using entropy for measuring distribution evenness
                if len(blooms_dist) > 1:
                    blooms_entropy = -sum(
                        p * np.log(p) if p > 0 else 0 
                        for p in blooms_dist.values()
                    ) / np.log(len(bloom_values))
                else:
                    blooms_entropy = 0
                
                # Assign blooms_distribution score to each question based on the algorithm's distribution
                algorithms = df['algorithm'].unique()
                algo_blooms_dist = {}
                
                for algo in algorithms:
                    algo_df = df[df['algorithm'] == algo]
                    algo_dist = algo_df['blooms_level'].value_counts(normalize=True).to_dict()
                    
                    if len(algo_dist) > 1:
                        dist_score = -sum(
                            p * np.log(p) if p > 0 else 0 
                            for p in algo_dist.values()
                        ) / np.log(len(bloom_values))
                    else:
                        dist_score = 0
                    
                    algo_blooms_dist[algo] = dist_score
                
                df['blooms_distribution'] = df['algorithm'].map(algo_blooms_dist)
                
                # Update the dataframe
                self.dfs[lang] = df
                
                print(f"\n=== Bloom's Taxonomy Analysis for {lang_name} ===")
                print("Bloom's Taxonomy Distribution:")
                for level, proportion in sorted(blooms_dist.items(), key=lambda x: bloom_values[x[0]]):
                    print(f"  {level.capitalize()}: {proportion:.2f}")
                
                print(f"Bloom's distribution evenness score: {blooms_entropy:.2f}")
                
                # Compare Bloom's levels across difficulty levels
                for level in self.difficulty_levels:
                    level_df = df[df['level'] == level]
                    if not level_df.empty:
                        avg_bloom = level_df['blooms_value'].mean()
                        print(f"{level.capitalize()} questions average Bloom's level: {avg_bloom:.2f}")
    
    def evaluate_precision_recall(self):
        """
        Evaluate precision and recall metrics for question generation
        
        Since we don't have ground truth for what constitutes a "good" question,
        we'll use heuristics to estimate precision and recall
        """
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                
                # Estimate precision: what proportion of questions are likely to be useful?
                # Heuristic: a question is "precise" if it mentions specific code elements 
                # or has good linguistic structure
                
                df['has_code_elements'] = df['variables_covered'].apply(len) + df['functions_covered'].apply(len) > 0
                df['good_structure'] = df['question'].apply(
                    lambda q: '?' in q and len(q.split()) >= 5  # Question has ? and at least 5 words
                )
                
                # Simple precision score (0-1)
                df['precision_score'] = (df['has_code_elements'].astype(int) * 0.6 + 
                                       df['good_structure'].astype(int) * 0.4)
                
                # Estimate recall: what proportion of important concepts are covered?
                # We'll use the algorithm-level code coverage as a proxy for recall
                df['recall_score'] = df['code_coverage']
                
                # Calculate aggregate metrics
                avg_precision = df['precision_score'].mean()
                avg_recall = df['recall_score'].mean()
                f1_score = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0
                
                print(f"\n=== Precision-Recall Analysis for {lang_name} ===")
                print(f"Average Precision: {avg_precision:.2f}")
                print(f"Average Recall: {avg_recall:.2f}")
                print(f"F1 Score: {f1_score:.2f}")
                
                # Update the dataframe
                self.dfs[lang] = df
    
    def evaluate_novelty(self):
        """
        Evaluate novelty of questions
        
        Novelty: Do questions go beyond trivial observations about the code?
        """
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                
                # Heuristics for novelty:
                # 1. Higher Bloom's taxonomy level (analysis, evaluation, creation > remembering)
                # 2. Questions that mention multiple code elements (indicating deeper understanding)
                # 3. Questions about specific aspects (complexity, optimization, edge cases)
                
                # Calculate novelty based on Bloom's level (higher levels = more novel)
                df['bloom_novelty'] = (df['blooms_value'] - 1) / 5.0  # Normalize to 0-1
                
                # Calculate novelty based on mentioned code elements
                df['element_count'] = df['variables_covered'].apply(len) + df['functions_covered'].apply(len)
                max_elements = max(df['element_count'].max(), 1)
                df['element_novelty'] = df['element_count'] / max_elements
                
                # Detect advanced question types
                advanced_keywords = ['complexity', 'optimize', 'efficient', 'edge case', 
                                    'corner case', 'improve', 'trade-off', 'alternative']
                df['advanced_question'] = df['question'].apply(
                    lambda q: any(kw in q.lower() for kw in advanced_keywords)
                )
                
                # Combine novelty factors
                df['novelty_score'] = (0.4 * df['bloom_novelty'] + 
                                      0.3 * df['element_novelty'] + 
                                      0.3 * df['advanced_question'].astype(int))
                
                avg_novelty = df['novelty_score'].mean()
                
                print(f"\n=== Novelty Analysis for {lang_name} ===")
                print(f"Average Novelty Score: {avg_novelty:.2f}")
                print(f"Proportion of Advanced Questions: {df['advanced_question'].mean():.2f}")
                
                # Update the dataframe
                self.dfs[lang] = df
    
    def evaluate_educational_alignment(self):
        """
        Evaluate whether difficulty labels match question complexity
        
        This checks whether beginner/intermediate/advanced labels accurately 
        reflect question difficulty
        """
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                
                # Expected Bloom's level for each difficulty
                expected_blooms = {
                    'beginner': [1, 2],  # Remember, Understand
                    'intermediate': [2, 3, 4],  # Understand, Apply, Analyze
                    'advanced': [4, 5, 6]  # Analyze, Evaluate, Create
                }
                
                # Check if Bloom's level matches the expected range for difficulty
                df['expected_bloom_match'] = df.apply(
                    lambda row: row['blooms_value'] in expected_blooms[row['level']], 
                    axis=1
                )
                
                # Check if linguistic complexity aligns with difficulty
                # Normalize linguistic complexity to 0-1 and compare with expected ranges
                expected_complexity = {
                    'beginner': (0, 0.4),
                    'intermediate': (0.3, 0.7),
                    'advanced': (0.6, 1.0)
                }
                
                df['expected_complexity_match'] = df.apply(
                    lambda row: (expected_complexity[row['level']][0] <= row['linguistic_complexity'] and
                               row['linguistic_complexity'] <= expected_complexity[row['level']][1]),
                    axis=1
                )
                
                # Combined educational alignment score
                df['educational_alignment'] = (0.7 * df['expected_bloom_match'].astype(int) + 
                                            0.3 * df['expected_complexity_match'].astype(int))
                
                alignment_by_level = {}
                for level in self.difficulty_levels:
                    level_df = df[df['level'] == level]
                    if not level_df.empty:
                        alignment_by_level[level] = level_df['educational_alignment'].mean()
                
                print(f"\n=== Educational Alignment Analysis for {lang_name} ===")
                print(f"Overall Educational Alignment: {df['educational_alignment'].mean():.2f}")
                for level, score in alignment_by_level.items():
                    print(f"{level.capitalize()} questions alignment: {score:.2f}")
                
                # Update the dataframe
                self.dfs[lang] = df
    
    def evaluate_cognitive_diversity(self):
        """
        Evaluate cognitive diversity of questions
        
        Do questions target different cognitive processes?
        """
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                
                # We'll measure cognitive diversity at the algorithm level
                # Count unique Bloom's levels and calculate diversity score
                
                algorithms = df['algorithm'].unique()
                algo_cognitive_div = {}
                
                for algo in algorithms:
                    algo_df = df[df['algorithm'] == algo]
                    
                    # Count unique Bloom's levels
                    unique_blooms = algo_df['blooms_level'].nunique()
                    
                    # Calculate distribution of Bloom's levels
                    blooms_dist = algo_df['blooms_level'].value_counts(normalize=True).to_dict()
                    
                    # Calculate entropy as a measure of diversity
                    if len(blooms_dist) > 1:
                        entropy = -sum(
                            p * np.log(p) if p > 0 else 0 
                            for p in blooms_dist.values()
                        ) / np.log(6)  # Normalize by log(# of categories)
                    else:
                        entropy = 0
                    
                    # Combine metrics (unique count and distribution entropy)
                    diversity_score = (0.4 * (unique_blooms / 6) + 0.6 * entropy)
                    
                    algo_cognitive_div[algo] = diversity_score
                
                # Assign cognitive diversity score to each question based on its algorithm
                df['cognitive_diversity'] = df['algorithm'].map(algo_cognitive_div)
                
                avg_diversity = df['cognitive_diversity'].mean()
                
                print(f"\n=== Cognitive Diversity Analysis for {lang_name} ===")
                print(f"Average Cognitive Diversity Score: {avg_diversity:.2f}")
                
                # Update the dataframe
                self.dfs[lang] = df
    
    def calculate_overall_quality_score(self):
        """Calculate weighted overall question quality score"""
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                
                # Calculate overall quality score using weights
                overall_score = (
                    self.metric_weights['linguistic_complexity'] * df['linguistic_complexity'] +
                    self.metric_weights['code_coverage'] * df['code_coverage'] +
                    self.metric_weights['blooms_distribution'] * df['blooms_distribution'] +
                    self.metric_weights['precision'] * df['precision_score'] +
                    self.metric_weights['recall'] * df['recall_score'] +
                    self.metric_weights['novelty'] * df['novelty_score'] +
                    self.metric_weights['educational_alignment'] * df['educational_alignment'] +
                    self.metric_weights['cognitive_diversity'] * df['cognitive_diversity']
                )
                
                df['quality_score'] = overall_score
                
                # Update the dataframe
                self.dfs[lang] = df
                
                print(f"\n=== Overall Quality Score for {lang_name} ===")
                print(f"Average Quality Score: {df['quality_score'].mean():.2f}")
                
                # Analyze by complexity level
                for complexity in ['Simple', 'Moderate', 'Complex']:
                    complexity_df = df[df['complexity'] == complexity]
                    if not complexity_df.empty:
                        print(f"{complexity} code questions average quality: {complexity_df['quality_score'].mean():.2f}")
                
                # Analyze by difficulty level
                for level in self.difficulty_levels:
                    level_df = df[df['level'] == level]
                    if not level_df.empty:
                        print(f"{level.capitalize()} questions average quality: {level_df['quality_score'].mean():.2f}")
    
    def generate_comparative_report(self):
        """Generate a comparative report across languages"""
        # Collect metrics across languages
        metrics_by_lang = {}
        
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                
                metrics_by_lang[lang_name] = {
                    'linguistic_complexity': df['linguistic_complexity'].mean(),
                    'code_coverage': df['code_coverage'].mean(),
                    'blooms_distribution': df['blooms_distribution'].mean(),
                    'precision_score': df['precision_score'].mean(),
                    'recall_score': df['recall_score'].mean(),
                    'novelty_score': df['novelty_score'].mean(),
                    'educational_alignment': df['educational_alignment'].mean(),
                    'cognitive_diversity': df['cognitive_diversity'].mean(),
                    'quality_score': df['quality_score'].mean()
                }
        
        if metrics_by_lang:
            print("\n=== Comparative Report Across Languages ===")
            
            # Create a dataframe for comparison
            metrics_df = pd.DataFrame(metrics_by_lang)
            
            # Print the comparison
            for metric in metrics_df.index:
                print(f"\n{metric.replace('_', ' ').title()}:")
                for lang in metrics_df.columns:
                    print(f"  {lang}: {metrics_df.loc[metric, lang]:.2f}")
            
            # Rank languages by overall quality score
            quality_ranks = {lang: metrics['quality_score'] 
                           for lang, metrics in metrics_by_lang.items()}
            
            print("\nLanguages Ranked by Overall Question Quality:")
            for rank, (lang, score) in enumerate(sorted(quality_ranks.items(), 
                                                   key=lambda x: x[1], reverse=True), 1):
                print(f"{rank}. {lang}: {score:.2f}")
            
            # Save metrics to CSV
            metrics_df.to_csv('language_comparison_metrics.csv')
            print("Saved metrics to language_comparison_metrics.csv")
            
            return metrics_df
    
    def visualize_results(self):
        """Create visualizations of evaluation results"""
        # Prepare directory for visualizations
        os.makedirs('evaluation_plots', exist_ok=True)
        
        # 1. Quality score by language and complexity
        quality_data = []
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                for complexity in df['complexity'].unique():
                    complexity_df = df[df['complexity'] == complexity]
                    quality_data.append({
                        'Language': lang_name,
                        'Complexity': complexity,
                        'Quality Score': complexity_df['quality_score'].mean()
                    })
        
        if quality_data:
            quality_df = pd.DataFrame(quality_data)
            plt.figure(figsize=(12, 8))
            sns.barplot(x='Language', y='Quality Score', hue='Complexity', data=quality_df)
            plt.title('Question Quality Score by Language and Code Complexity')
            plt.savefig('evaluation_plots/quality_by_language_complexity.png')
            plt.close()        
      
        # 2. Spider plots for evaluation metrics by language
        metrics = [
            'linguistic_complexity', 'code_coverage', 'blooms_distribution',
            'precision_score', 'recall_score', 'novelty_score', 
            'educational_alignment', 'cognitive_diversity'
        ]
        
        metric_names = [
            'Linguistic\nComplexity', 'Code\nCoverage', 'Bloom\'s\nDistribution',
            'Precision', 'Recall', 'Novelty', 
            'Educational\nAlignment', 'Cognitive\nDiversity'
        ]
        
        metrics_by_lang = {}
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                metrics_by_lang[lang_name] = [df[metric].mean() for metric in metrics]
        
        if metrics_by_lang:
            # Create radar plot
            plt.figure(figsize=(10, 10))
            ax = plt.subplot(111, polar=True)
            
            # Number of metrics
            num_metrics = len(metrics)
            
            # Compute angle for each metric
            angles = np.linspace(0, 2*np.pi, num_metrics, endpoint=False).tolist()
            angles += angles[:1]  # Close the polygon
            
            # Plot each language
            for lang_name, values in metrics_by_lang.items():
                values += values[:1]  # Close the polygon
                ax.plot(angles, values, linewidth=2, label=lang_name)
                ax.fill(angles, values, alpha=0.1)
            
            # Set labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metric_names)
            
            # Add legend
            plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
            plt.title('Evaluation Metrics by Programming Language', size=15)
            plt.savefig('evaluation_plots/metrics_radar_chart.png')
            plt.close()
        
        # 3. Quality score by difficulty level for each language
        level_data = []
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                for level in self.difficulty_levels:
                    level_df = df[df['level'] == level]
                    if not level_df.empty:
                        level_data.append({
                            'Language': lang_name,
                            'Difficulty': level.capitalize(),
                            'Quality Score': level_df['quality_score'].mean()
                        })
        
        if level_data:
            level_df = pd.DataFrame(level_data)
            plt.figure(figsize=(12, 8))
            sns.barplot(x='Language', y='Quality Score', hue='Difficulty', data=level_df)
            plt.title('Question Quality Score by Language and Difficulty Level')
            plt.savefig('evaluation_plots/quality_by_difficulty.png')
            plt.close()
        
        # 4. Heatmap of correlation between metrics
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                
                # Select metrics columns
                metrics_df = df[metrics + ['quality_score']]
                
                # Calculate correlation
                corr = metrics_df.corr()
                
                # Create heatmap
                plt.figure(figsize=(12, 10))
                mask = np.triu(np.ones_like(corr, dtype=bool))
                sns.heatmap(corr, mask=mask, cmap='coolwarm', annot=True, fmt=".2f", square=True)
                plt.title(f'Correlation Heatmap of Evaluation Metrics - {lang_name}')
                plt.tight_layout()
                plt.savefig(f'evaluation_plots/correlation_heatmap_{lang_name}.png')
                plt.close()
        
        # 5. Distribution of quality scores
        plt.figure(figsize=(14, 8))
        for i, (lang, lang_name) in enumerate(zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                                self.languages)):
            if lang in self.dfs:
                plt.subplot(2, 2, i+1)
                df = self.dfs[lang]
                sns.histplot(df['quality_score'], kde=True)
                plt.axvline(df['quality_score'].mean(), color='r', linestyle='--')
                plt.title(f'Quality Score Distribution - {lang_name}')
                plt.xlabel('Quality Score')
                plt.ylabel('Count')
        
        plt.tight_layout()
        plt.savefig('evaluation_plots/quality_distribution.png')
        plt.close()
        
        # 6. Boxplots of linguistic complexity by difficulty level
        plt.figure(figsize=(14, 8))
        ling_data = []
        
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                for _, row in df.iterrows():
                    ling_data.append({
                        'Language': lang_name,
                        'Difficulty': row['level'].capitalize(),
                        'Linguistic Complexity': row['linguistic_complexity']
                    })
        
        if ling_data:
            ling_df = pd.DataFrame(ling_data)
            sns.boxplot(x='Difficulty', y='Linguistic Complexity', hue='Language', data=ling_df)
            plt.title('Linguistic Complexity by Difficulty Level')
            plt.savefig('evaluation_plots/linguistic_complexity_boxplot.png')
            plt.close()
        
        # 7. Bar chart of top 10 algorithms by quality score
        algo_data = []
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                for algo in df['algorithm'].unique():
                    algo_df = df[df['algorithm'] == algo]
                    algo_data.append({
                        'Language': lang_name,
                        'Algorithm': algo,
                        'Quality Score': algo_df['quality_score'].mean()
                    })
        
        if algo_data:
            algo_df = pd.DataFrame(algo_data)
            top_algos = algo_df.nlargest(10, 'Quality Score')
            
            plt.figure(figsize=(14, 8))
            sns.barplot(x='Quality Score', y='Algorithm', hue='Language', data=top_algos)
            plt.title('Top 10 Algorithms by Question Quality Score')
            plt.savefig('evaluation_plots/top_algorithms.png')
            plt.close()
        
        print("\nVisualization complete. Plots saved to 'evaluation_plots' directory.")

    def analyze_blooms_by_code_complexity(self):
        """Analyze the relationship between code complexity and Bloom's taxonomy levels"""
        combined_data = []
        
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                
                # Group by complexity and calculate average Bloom's level
                for complexity in df['complexity'].unique():
                    complexity_df = df[df['complexity'] == complexity]
                    bloom_dist = complexity_df['blooms_level'].value_counts(normalize=True).to_dict()
                    
                    # Add to combined data
                    for bloom_level, proportion in bloom_dist.items():
                        combined_data.append({
                            'Language': lang_name,
                            'Code Complexity': complexity,
                            'Bloom\'s Level': bloom_level,
                            'Proportion': proportion
                        })
        
        if combined_data:
            blooms_df = pd.DataFrame(combined_data)
            
            plt.figure(figsize=(15, 10))
            g = sns.catplot(
                data=blooms_df, kind="bar",
                x="Code Complexity", y="Proportion", hue="Bloom\'s Level",
                col="Language", height=6, aspect=.7
            )
            
            g.set_axis_labels("Code Complexity", "Proportion of Questions")
            g.set_titles("{col_name}")
            plt.tight_layout()
            plt.savefig('evaluation_plots/blooms_by_complexity.png')
            plt.close()
            
            print("\nAnalysis of Bloom's levels by code complexity complete.")

    def generate_summary_statistics(self):
        """Generate summary statistics for all evaluation metrics"""
        summary_stats = {}
        
        for lang, lang_name in zip(['C_questions', 'CPP_questions', 'Java_questions', 'Python_questions'], 
                                  self.languages):
            if lang in self.dfs:
                df = self.dfs[lang]
                
                # Calculate summary statistics for each metric
                metrics = [
                    'linguistic_complexity', 'code_coverage', 'blooms_distribution',
                    'precision_score', 'recall_score', 'novelty_score', 
                    'educational_alignment', 'cognitive_diversity', 'quality_score'
                ]
                
                lang_stats = {}
                for metric in metrics:
                    lang_stats[metric] = {
                        'mean': df[metric].mean(),
                        'median': df[metric].median(),
                        'std': df[metric].std(),
                        'min': df[metric].min(),
                        'max': df[metric].max()
                    }
                
                summary_stats[lang_name] = lang_stats
        
        # Save summary statistics to CSV
        if summary_stats:
            # Flatten the nested dictionary for easier CSV export
            flat_stats = []
            for lang, metrics in summary_stats.items():
                for metric, stats in metrics.items():
                    row = {'Language': lang, 'Metric': metric}
                    row.update(stats)
                    flat_stats.append(row)
            
            stats_df = pd.DataFrame(flat_stats)
            stats_df.to_csv('evaluation_stats_summary.csv', index=False)
            print("\nSummary statistics saved to 'evaluation_stats_summary.csv'")
            
            # Print overall summary
            print("\n=== Summary Statistics ===")
            for lang, metrics in summary_stats.items():
                print(f"\n{lang} - Overall Quality Score:")
                print(f"  Mean: {metrics['quality_score']['mean']:.2f}")
                print(f"  Median: {metrics['quality_score']['median']:.2f}")
                print(f"  Std Dev: {metrics['quality_score']['std']:.2f}")
                print(f"  Range: {metrics['quality_score']['min']:.2f} to {metrics['quality_score']['max']:.2f}")
            
            return stats_df

    def evaluate_questions(self, file_paths):
        """Run the complete evaluation pipeline"""
        print("=== Starting Question Evaluation ===")
        
        # Step 1: Load data
        print("\nLoading data files...")
        self.load_data(file_paths)
        
        # Step 2: Preprocess data
        print("\nPreprocessing data...")
        self.preprocess_data()
        
        # Step 3: Evaluate linguistic complexity
        print("\nEvaluating linguistic complexity...")
        self.evaluate_linguistic_complexity()
        
        # Step 4: Evaluate code coverage
        print("\nEvaluating code coverage...")
        self.evaluate_code_coverage()
        
        # Step 5: Analyze Bloom's taxonomy
        print("\nAnalyzing Bloom's taxonomy...")
        self.analyze_blooms_taxonomy()
        
        # Step 6: Evaluate precision and recall
        print("\nEvaluating precision and recall...")
        self.evaluate_precision_recall()
        
        # Step 7: Evaluate novelty
        print("\nEvaluating novelty...")
        self.evaluate_novelty()
        
        # Step 8: Evaluate educational alignment
        print("\nEvaluating educational alignment...")
        self.evaluate_educational_alignment()
        
        # Step 9: Evaluate cognitive diversity
        print("\nEvaluating cognitive diversity...")
        self.evaluate_cognitive_diversity()
        
        # Step 10: Calculate overall quality score
        print("\nCalculating overall quality score...")
        self.calculate_overall_quality_score()
        
        # Step 11: Generate comparative report
        print("\nGenerating comparative report...")
        self.generate_comparative_report()
        
        # Step 12: Analyze Bloom's levels by code complexity
        print("\nAnalyzing Bloom's levels by code complexity...")
        self.analyze_blooms_by_code_complexity()
        
        # Step 13: Generate summary statistics
        print("\nGenerating summary statistics...")
        self.generate_summary_statistics()
        
        # Step 14: Create visualizations
        print("\nCreating visualizations...")
        self.visualize_results()
        
        print("\n=== Question Evaluation Complete ===")

# Example usage
if __name__ == "__main__":
    # Create evaluator
    evaluator = QuestionEvaluator()
    
    # Redirect output to a file
    import sys
    with open('analysis_results.txt', 'w') as f:
        original_stdout = sys.stdout
        sys.stdout = f
        
        # Define file paths
        file_paths = {
            'C': 'CodeQualityMetricsFinal-C.csv',
            'CPP': 'CodeQualityMetricsFinal-CPP.csv',
            'Java': 'CodeQualityMetricsFinal-Java.csv',
            'Python': 'CodeQualityMetricsFinal-Python.csv'
        }
        
        # Run evaluation
        evaluator.evaluate_questions(file_paths)
        
        # Restore stdout
        sys.stdout = original_stdout
    
    print("Analysis complete! Results saved to analysis_results.txt")