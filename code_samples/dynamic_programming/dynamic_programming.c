/**
 * Dynamic Programming implementation in C - Knapsack Problem.
 *
 * The 0/1 Knapsack problem is a classic optimization problem where we need to select items
 * to maximize value while keeping the total weight under a given limit. Each item can be
 * selected only once (0/1 property).
 *
 * Time Complexity: O(n*W) where n is the number of items and W is the capacity
 * Space Complexity: O(n*W)
 */
#include <stdio.h>
#include <stdlib.h>

/**
 * Solve the 0/1 Knapsack problem using dynamic programming.
 *
 * @param weights Array of weights of the items
 * @param values Array of values of the items
 * @param n Number of items
 * @param capacity Maximum weight capacity of the knapsack
 * @param selectedItems Output array to store selected items (1 if selected, 0 otherwise)
 * @return Maximum value that can be obtained
 */
int knapsack01(int weights[], int values[], int n, int capacity, int selectedItems[]) {
    // Create a 2D DP table
    // dp[i][w] represents the maximum value that can be obtained
    // using first i items and with weight limit w
    int** dp = (int**)malloc((n + 1) * sizeof(int*));
    for (int i = 0; i <= n; i++) {
        dp[i] = (int*)malloc((capacity + 1) * sizeof(int));
    }
    
    // Initialize the dp table
    for (int i = 0; i <= n; i++) {
        for (int w = 0; w <= capacity; w++) {
            dp[i][w] = 0;
        }
    }
    
    // Fill the dp table in bottom-up manner
    for (int i = 1; i <= n; i++) {
        for (int w = 0; w <= capacity; w++) {
            // If current item weight is less than or equal to capacity w
            // We have two choices: include the item or exclude it
            if (weights[i-1] <= w) {
                // Maximum of including the current item or excluding it
                dp[i][w] = (values[i-1] + dp[i-1][w-weights[i-1]] > dp[i-1][w]) ? 
                           values[i-1] + dp[i-1][w-weights[i-1]] : dp[i-1][w];
            } else {
                // If current item weight is more than capacity w, we can't include it
                dp[i][w] = dp[i-1][w];
            }
        }
    }
    
    // Find the selected items
    int w = capacity;
    for (int i = 0; i < n; i++) {
        selectedItems[i] = 0;  // Initialize all to not selected
    }
    
    for (int i = n; i > 0; i--) {
        // If the value comes from including this item
        if (dp[i][w] != dp[i-1][w]) {
            selectedItems[i-1] = 1;  // Mark as selected
            w -= weights[i-1];
        }
    }
    
    // Store the maximum value
    int maxValue = dp[n][capacity];
    
    // Free the dp table
    for (int i = 0; i <= n; i++) {
        free(dp[i]);
    }
    free(dp);
    
    return maxValue;
}

// Example usage
int main() {
    // Example problem
    int weights[] = {2, 3, 4, 5};
    int values[] = {3, 4, 5, 6};
    int n = 4;
    int capacity = 8;
    
    // Array to store which items are selected
    int* selectedItems = (int*)malloc(n * sizeof(int));
    
    int maxValue = knapsack01(weights, values, n, capacity, selectedItems);
    
    printf("Maximum value: %d\n", maxValue);
    printf("Selected items (0-indexed): ");
    int first = 1;
    for (int i = 0; i < n; i++) {
        if (selectedItems[i]) {
            if (!first) {
                printf(", ");
            }
            printf("%d", i);
            first = 0;
        }
    }
    printf("\n");
    
    printf("Selected items details:\n");
    for (int i = 0; i < n; i++) {
        if (selectedItems[i]) {
            printf("Item %d: Weight = %d, Value = %d\n", i, weights[i], values[i]);
        }
    }
    
    free(selectedItems);
    
    return 0;
}
