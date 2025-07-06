import glob
import pandas as pd
import matplotlib.pyplot as plt
import os

# Find all question CSVs recursively in code_samples
files = glob.glob(os.path.join('code_samples', '**', '*_questions.csv'), recursive=True)

# Aggregate Bloom's levels

# Only count real, actually generated questions for each Bloom's level
bloom_levels = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']
bloom_counts = {level: 0 for level in bloom_levels}
for file in files:
    df = pd.read_csv(file)
    for level in df['bloom']:
        if level in bloom_counts:
            bloom_counts[level] += 1
        else:
            bloom_counts[level] = 1  # In case of unexpected label

# Convert to DataFrame for table/plot
bloom_df = pd.DataFrame(list(bloom_counts.items()), columns=['Bloom_Level', 'Count'])
bloom_df['Percent'] = 100 * bloom_df['Count'] / bloom_df['Count'].sum()

# Print the table
print('Bloom\'s Level Distribution Table:')
print(bloom_df)

# Plot
plt.figure(figsize=(8,5))
plt.bar(bloom_df['Bloom_Level'], bloom_df['Percent'], color='skyblue')
plt.ylabel('Percent of Questions')
plt.xlabel('Bloom\'s Level')
plt.title("Bloom's Taxonomy Distribution of Generated Questions")
plt.tight_layout()
plt.savefig('blooms_distribution_plot.png')
plt.show()
