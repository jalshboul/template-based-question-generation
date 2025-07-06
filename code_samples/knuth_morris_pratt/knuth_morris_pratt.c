/**
 * Knuth-Morris-Pratt (KMP) algorithm implementation in C.
 *
 * KMP is a string searching algorithm that uses information about the pattern
 * to minimize comparisons by avoiding re-examination of previously matched characters.
 *
 * Time Complexity: O(n + m) where n is the length of the text and m is the length of the pattern
 * Space Complexity: O(m) for the LPS array
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * Compute the Longest Prefix Suffix (LPS) array for the pattern.
 *
 * @param pattern String pattern to search for
 * @param m Length of the pattern
 * @param lps Array to store the LPS values
 */
void computeLPSArray(const char* pattern, int m, int* lps) {
    // Length of the previous longest prefix suffix
    int length = 0;
    
    lps[0] = 0; // First element is always 0
    
    // Loop to fill LPS array
    int i = 1;
    while (i < m) {
        if (pattern[i] == pattern[length]) {
            length++;
            lps[i] = length;
            i++;
        } else {
            if (length != 0) {
                // This is tricky. Consider the example AAACAAAA and i = 7
                length = lps[length - 1];
            } else {
                lps[i] = 0;
                i++;
            }
        }
    }
}

/**
 * Search for pattern in text using KMP algorithm.
 *
 * @param text String to search in
 * @param pattern String pattern to search for
 * @param results Array to store the indices where pattern is found
 * @param max_results Maximum number of results to store
 * @return Number of occurrences found
 */
int kmpSearch(const char* text, const char* pattern, int* results, int max_results) {
    int n = strlen(text);
    int m = strlen(pattern);
    
    if (m == 0) {
        return 0; // Empty pattern matches nothing
    }
    
    // Create LPS array to hold the longest prefix suffix values for pattern
    int* lps = (int*)malloc(m * sizeof(int));
    computeLPSArray(pattern, m, lps);
    
    int count = 0; // Count of matches
    
    // Index for text
    int i = 0;
    // Index for pattern
    int j = 0;
    
    while (i < n) {
        // Current characters match, move both pointers
        if (pattern[j] == text[i]) {
            i++;
            j++;
        }
        
        // Pattern completely found
        if (j == m) {
            if (count < max_results) {
                results[count] = i - j;
            }
            count++;
            // Look for the next match, start from lps[j-1]
            j = lps[j - 1];
        }
        // Mismatch after j matches
        else if (i < n && pattern[j] != text[i]) {
            if (j != 0) {
                j = lps[j - 1];
            } else {
                i++;
            }
        }
    }
    
    free(lps);
    return count;
}

// Example usage
int main() {
    const char* text = "ABABDABACDABABCABAB";
    const char* pattern = "ABABCABAB";
    
    // Allocate space for results (assume maximum 10 matches)
    int max_results = 10;
    int* results = (int*)malloc(max_results * sizeof(int));
    
    int count = kmpSearch(text, pattern, results, max_results);
    
    if (count > 0) {
        printf("Pattern found at indices: ");
        for (int i = 0; i < (count < max_results ? count : max_results); i++) {
            printf("%d ", results[i]);
        }
        printf("\n");
        
        if (count > max_results) {
            printf("(and %d more occurrences)\n", count - max_results);
        }
    } else {
        printf("Pattern not found in text\n");
    }
    
    free(results);
    return 0;
}
