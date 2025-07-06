import glob
import os
import importlib.util

# Path to your main generation script and class

GEN_SCRIPT = 'MultiProgrammingCodeQG.py'
CLASS_NAME = 'MultiLanguageQuestionGenerator'

# Dynamically import the main class
spec = importlib.util.spec_from_file_location(CLASS_NAME, GEN_SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
GenClass = getattr(mod, CLASS_NAME)
gen = GenClass()

# Find all code sample files (adjust pattern as needed)
code_files = glob.glob(os.path.join('code_samples', '**', '*.py'), recursive=True)

for code_file in code_files:
    with open(code_file, 'r', encoding='utf-8') as f:
        code = f.read()
    # Generate questions (6 per sample, one for each Bloom's level)
    questions = gen.generate_questions(code, num_questions=6)
    # Save to CSV
    import pandas as pd
    import os
    out_dir = os.path.dirname(code_file)
    out_csv = os.path.join(out_dir, os.path.splitext(os.path.basename(code_file))[0] + '_questions.csv')
    df = pd.DataFrame(questions)
    df.to_csv(out_csv, index=False)
    print(f'Generated: {out_csv}')
