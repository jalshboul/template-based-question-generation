/**
 * Bubble Sort implementation in C.
 *
 * Bubble Sort is a simple sorting algorithm that repeatedly steps through the list,
 * compares adjacent elements and swaps them if they are in the wrong order.
 * The pass through the list is repeated until the list is sorted.
 *
 * Time Complexity: O(n^2)
 * Space Complexity: O(1)
 */
#include <stdio.h>

/**
 * Sort an array using bubble sort algorithm.
 *
 * @param arr Array of comparable elements
 * @param n Size of the array
 */
void bubbleSort(int arr[], int n) {
    // Traverse through all array elements
    for (int i = 0; i < n; i++) {
        // Flag to optimize if no swapping occurs
        int swapped = 0;
        
        // Last i elements are already in place
        for (int j = 0; j < n - i - 1; j++) {
            // Traverse the array from 0 to n-i-1
            // Swap if the element found is greater than the next element
            if (arr[j] > arr[j + 1]) {
                // Swap arr[j] and arr[j+1]
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
                swapped = 1;
            }
        }
        
        // If no swapping occurred in this pass, array is sorted
        if (swapped == 0) {
            break;
        }
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
    int testArray[] = {64, 34, 25, 12, 22, 11, 90};
    int n = sizeof(testArray) / sizeof(testArray[0]);
    
    printf("Original array: ");
    printArray(testArray, n);
    
    bubbleSort(testArray, n);
    printf("Sorted array: ");
    printArray(testArray, n);
    
    return 0;
}
