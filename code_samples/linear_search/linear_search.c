/**
 * Linear Search implementation in C.
 *
 * Linear Search is a simple search algorithm that checks each element in the list
 * sequentially until it finds the target value or reaches the end of the list.
 *
 * Time Complexity: O(n)
 * Space Complexity: O(1)
 */
#include <stdio.h>

/**
 * Search for a target value in an array using linear search algorithm.
 *
 * @param arr Array of elements
 * @param n Size of the array
 * @param target Value to search for
 * @return Index of the target if found, -1 otherwise
 */
int linearSearch(int arr[], int n, int target) {
    // Traverse the array sequentially
    for (int i = 0; i < n; i++) {
        if (arr[i] == target) {
            return i;
        }
    }
    
    // Target is not present in the array
    return -1;
}

// Example usage
int main() {
    // Test with an array
    int testArray[] = {64, 34, 25, 12, 22, 11, 90};
    int n = sizeof(testArray) / sizeof(testArray[0]);
    int target = 22;
    
    int result = linearSearch(testArray, n, target);
    if (result != -1) {
        printf("Element %d is present at index %d\n", target, result);
    } else {
        printf("Element %d is not present in array\n", target);
    }
    
    return 0;
}
