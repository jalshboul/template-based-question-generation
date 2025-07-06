/**
 * Insertion Sort implementation in C.
 *
 * Insertion Sort is a simple sorting algorithm that builds the final sorted array one item at a time.
 * It is much less efficient on large lists than more advanced algorithms such as quicksort, heapsort, or merge sort.
 * However, it performs well for small data sets or nearly sorted data.
 *
 * Time Complexity: O(n^2)
 * Space Complexity: O(1)
 */
#include <stdio.h>

/**
 * Sort an array using insertion sort algorithm.
 *
 * @param arr Array of comparable elements
 * @param n Size of the array
 */
void insertionSort(int arr[], int n) {
    // Traverse through 1 to n
    for (int i = 1; i < n; i++) {
        int key = arr[i];
        
        // Move elements of arr[0..i-1], that are greater than key,
        // to one position ahead of their current position
        int j = i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j = j - 1;
        }
        arr[j + 1] = key;
    }
}

// Utility function to print an array
void printArray(int arr[], int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

// Example usage
int main() {
    // Test with a sample array
    int testArray[] = {12, 11, 13, 5, 6};
    int n = sizeof(testArray) / sizeof(testArray[0]);
    
    printf("Original array: ");
    printArray(testArray, n);
    
    insertionSort(testArray, n);
    printf("Sorted array: ");
    printArray(testArray, n);
    
    return 0;
}
