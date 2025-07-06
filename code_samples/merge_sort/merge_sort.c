/**
 * Merge Sort implementation in C.
 *
 * Merge Sort is a divide and conquer algorithm that divides the input array into two halves,
 * recursively sorts them, and then merges the sorted halves.
 *
 * Time Complexity: O(n log n)
 * Space Complexity: O(n)
 */
#include <stdio.h>
#include <stdlib.h>

/**
 * Merge two sorted arrays into a single sorted array.
 *
 * @param arr Original array
 * @param left First index
 * @param mid Middle index
 * @param right Last index
 */
void merge(int arr[], int left, int mid, int right) {
    int i, j, k;
    int n1 = mid - left + 1;
    int n2 = right - mid;
    
    // Create temporary arrays
    int* L = (int*)malloc(n1 * sizeof(int));
    int* R = (int*)malloc(n2 * sizeof(int));
    
    // Copy data to temporary arrays L[] and R[]
    for (i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (j = 0; j < n2; j++)
        R[j] = arr[mid + 1 + j];
    
    // Merge the temporary arrays back into arr[left..right]
    i = 0; // Initial index of first subarray
    j = 0; // Initial index of second subarray
    k = left; // Initial index of merged subarray
    
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        } else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }
    
    // Copy the remaining elements of L[], if there are any
    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }
    
    // Copy the remaining elements of R[], if there are any
    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }
    
    // Free allocated memory
    free(L);
    free(R);
}

/**
 * Sort an array using merge sort algorithm.
 *
 * @param arr Array to be sorted
 * @param left Starting index
 * @param right Ending index
 */
void mergeSort(int arr[], int left, int right) {
    if (left < right) {
        // Same as (left+right)/2, but avoids overflow for large left and right
        int mid = left + (right - left) / 2;
        
        // Sort first and second halves
        mergeSort(arr, left, mid);
        mergeSort(arr, mid + 1, right);
        
        // Merge the sorted halves
        merge(arr, left, mid, right);
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
    int testArray[] = {38, 27, 43, 3, 9, 82, 10};
    int n = sizeof(testArray) / sizeof(testArray[0]);
    
    printf("Original array: ");
    printArray(testArray, n);
    
    mergeSort(testArray, 0, n - 1);
    printf("Sorted array: ");
    printArray(testArray, n);
    
    return 0;
}
