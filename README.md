# Multi-Programming Languages Code Question Generation System

This repository contains the implementation for a research project on template-based automatic question generation from code using static code analysis, supporting multiple programming languages and Bloom’s Taxonomy.

## Features
- **Multi-Programming Languages**: Supports Python, Java, C++, and C code.
- **Bloom’s Taxonomy**: Bloom's Taxonomy classifies educational learning objectives into levels of complexity and specificity. The six levels, from the simplest to the most complex, are Remembering, Understanding, Applying, Analyzing, Evaluating, and Creating.  
- **Template-based**: Uses customizable templates for question generation.
- **Static Code Analysis**: Extracts functions, loops, conditionals, variables, and algorithms from code.
- **Automated Evaluation**: Includes scripts for analyzing Bloom’s distribution and code quality.

## Research Background
This system implements the methodology from:
> *"Template-Based Question Generation from Code Using Static Code Analysis"*  
> by Jawad Alshboul and Erika Baksa-Varga

## Directory Structure
```
.
├── MultiProgrammingCodeQG.py         # Main question generator
├── regenerate_all_questions.py         # Script to regenerate all question files
├── bloom_distribution_analysis.py      # Bloom’s level analysis script
├── EvaluationCodeComplete.py           # Evaluation and plotting script
├── code_samples/                       # Example code and generated questions
├── evaluation_plots/                   # Output plots
├── template/                           # Question templates
├── Test Cases/                         # Test cases for evaluation
├── README.md                           # This file
├── LICENSE                             # License file
└── ...
```

## Setup
1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```
2. **Install dependencies:**
   - Python 3.8+
   - (Optional) Create a virtual environment:
     ```sh
     python -m venv venv
     venv\Scripts\activate  # On Windows
     source venv/bin/activate  # On Linux/Mac
     ```
   - Install required packages:
     ```sh
     pip install -r requirements.txt
     ```

## Usage
- **Generate Questions:**
  Run the main script to generate questions for a code sample:
  ```sh
  python MultiProgrammingCodeQG.py
  ```
- **Regenerate All Questions:**
  ```sh
  python regenerate_all_questions.py
  ```
- **Analyze Bloom’s Distribution:**
  ```sh
  python bloom_distribution_analysis.py
  ```
- **Evaluate and Plot Results:**
  ```sh
  python EvaluationCodeComplete.py
  ```

## Example
See the `code_samples/` directory for example code files and their generated question sets.

## Citing This Work
If you use this code for research, please cite our paper:
```
@article{alshboul2025template,
  title={Template-Based Automatic Question Generation from Program Codes using Static Code Analysis},
  author={Jawad Alshboul and Erika Baksa-Varga},
  journal={Pollack Periodica: An International Journal for Engineering and Information Sciences},
  year={2025}
}
```

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contact
For questions or contributions, please open an issue or contact the maintainer.
