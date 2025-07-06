/**
 * Huffman Coding implementation in C.
 *
 * Huffman coding is a lossless data compression algorithm that assigns variable-length codes
 * to input characters based on their frequencies. The most frequent character gets the smallest code.
 *
 * Time Complexity: O(n log n) where n is the number of unique characters
 * Space Complexity: O(n)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

// Maximum number of characters (ASCII)
#define MAX_CHARS 256

// Node structure for Huffman Tree
typedef struct HuffmanNode {
    char character;
    int frequency;
    struct HuffmanNode* left;
    struct HuffmanNode* right;
} HuffmanNode;

// Min Heap structure for priority queue
typedef struct {
    int size;
    int capacity;
    HuffmanNode** array;
} MinHeap;

// Create a new Huffman node
HuffmanNode* createNode(char character, int frequency) {
    HuffmanNode* node = (HuffmanNode*)malloc(sizeof(HuffmanNode));
    node->character = character;
    node->frequency = frequency;
    node->left = NULL;
    node->right = NULL;
    return node;
}

// Create a min heap of given capacity
MinHeap* createMinHeap(int capacity) {
    MinHeap* minHeap = (MinHeap*)malloc(sizeof(MinHeap));
    minHeap->size = 0;
    minHeap->capacity = capacity;
    minHeap->array = (HuffmanNode**)malloc(capacity * sizeof(HuffmanNode*));
    return minHeap;
}

// Swap two nodes
void swapNodes(HuffmanNode** a, HuffmanNode** b) {
    HuffmanNode* temp = *a;
    *a = *b;
    *b = temp;
}

// Heapify function to maintain heap property
void minHeapify(MinHeap* minHeap, int idx) {
    int smallest = idx;
    int left = 2 * idx + 1;
    int right = 2 * idx + 2;
    
    if (left < minHeap->size && 
        minHeap->array[left]->frequency < minHeap->array[smallest]->frequency) {
        smallest = left;
    }
    
    if (right < minHeap->size && 
        minHeap->array[right]->frequency < minHeap->array[smallest]->frequency) {
        smallest = right;
    }
    
    if (smallest != idx) {
        swapNodes(&minHeap->array[smallest], &minHeap->array[idx]);
        minHeapify(minHeap, smallest);
    }
}

// Check if size of heap is 1
bool isSizeOne(MinHeap* minHeap) {
    return (minHeap->size == 1);
}

// Extract the minimum value node from heap
HuffmanNode* extractMin(MinHeap* minHeap) {
    HuffmanNode* temp = minHeap->array[0];
    minHeap->array[0] = minHeap->array[minHeap->size - 1];
    --minHeap->size;
    minHeapify(minHeap, 0);
    return temp;
}

// Insert a new node to Min Heap
void insertMinHeap(MinHeap* minHeap, HuffmanNode* node) {
    ++minHeap->size;
    int i = minHeap->size - 1;
    
    while (i && node->frequency < minHeap->array[(i - 1) / 2]->frequency) {
        minHeap->array[i] = minHeap->array[(i - 1) / 2];
        i = (i - 1) / 2;
    }
    
    minHeap->array[i] = node;
}

// Build min heap
void buildMinHeap(MinHeap* minHeap) {
    int n = minHeap->size - 1;
    for (int i = (n - 1) / 2; i >= 0; --i) {
        minHeapify(minHeap, i);
    }
}

// Check if this is a leaf node
bool isLeaf(HuffmanNode* root) {
    return !(root->left) && !(root->right);
}

// Create and build a min heap
MinHeap* createAndBuildMinHeap(char data[], int freq[], int size) {
    MinHeap* minHeap = createMinHeap(size);
    
    for (int i = 0; i < size; ++i) {
        minHeap->array[i] = createNode(data[i], freq[i]);
    }
    
    minHeap->size = size;
    buildMinHeap(minHeap);
    
    return minHeap;
}

// Build Huffman Tree
HuffmanNode* buildHuffmanTree(char data[], int freq[], int size) {
    HuffmanNode *left, *right, *top;
    
    // Create a min heap of capacity equal to size
    MinHeap* minHeap = createAndBuildMinHeap(data, freq, size);
    
    // Iterate while size of heap doesn't become 1
    while (!isSizeOne(minHeap)) {
        // Extract the two minimum frequency nodes
        left = extractMin(minHeap);
        right = extractMin(minHeap);
        
        // Create a new internal node with frequency equal to the
        // sum of the two nodes' frequencies. Make the two extracted
        // nodes as left and right children of this new node.
        top = createNode('$', left->frequency + right->frequency);
        top->left = left;
        top->right = right;
        
        insertMinHeap(minHeap, top);
    }
    
    // The remaining node is the root node and the tree is complete
    return extractMin(minHeap);
}

// Print codes from the root of Huffman Tree
void printCodes(HuffmanNode* root, int arr[], int top, char* characters, char* codes[]) {
    // Assign 0 to left edge and recur
    if (root->left) {
        arr[top] = 0;
        printCodes(root->left, arr, top + 1, characters, codes);
    }
    
    // Assign 1 to right edge and recur
    if (root->right) {
        arr[top] = 1;
        printCodes(root->right, arr, top + 1, characters, codes);
    }
    
    // If this is a leaf node, then it contains one of the input
    // characters, print the character and its code
    if (isLeaf(root)) {
        // Store character
        static int index = 0;
        characters[index] = root->character;
        
        // Store code
        char* code = (char*)malloc((top + 1) * sizeof(char));
        for (int i = 0; i < top; ++i) {
            code[i] = arr[i] + '0';
        }
        code[top] = '\0';
        codes[index] = code;
        
        printf("'%c': %s\n", root->character, code);
        index++;
    }
}

// Huffman coding function
void huffmanCodes(char data[], int freq[], int size) {
    // Construct Huffman Tree
    HuffmanNode* root = buildHuffmanTree(data, freq, size);
    
    // Print Huffman codes using the Huffman tree
    int arr[MAX_CHARS], top = 0;
    
    // Arrays to store characters and their codes
    char characters[size];
    char* codes[size];
    
    printf("Huffman Codes:\n");
    printCodes(root, arr, top, characters, codes);
    
    // Example of encoding a message
    char message[] = "this is an example for huffman encoding";
    printf("\nOriginal message: %s\n", message);
    
    // Encode the message
    char encodedMessage[1000] = "";
    for (int i = 0; message[i] != '\0'; i++) {
        for (int j = 0; j < size; j++) {
            if (characters[j] == message[i]) {
                strcat(encodedMessage, codes[j]);
                break;
            }
        }
    }
    
    printf("Encoded message: %s\n", encodedMessage);
    
    // Calculate compression ratio
    int originalSize = strlen(message) * 8;  // Assuming 8 bits per character
    int compressedSize = strlen(encodedMessage);
    double compressionRatio = (double)originalSize / compressedSize;
    
    printf("Original size: %d bits\n", originalSize);
    printf("Compressed size: %d bits\n", compressedSize);
    printf("Compression ratio: %.2fx\n", compressionRatio);
    
    // Free allocated memory for codes
    for (int i = 0; i < size; i++) {
        free(codes[i]);
    }
}

// Free the Huffman Tree
void freeHuffmanTree(HuffmanNode* node) {
    if (node) {
        freeHuffmanTree(node->left);
        freeHuffmanTree(node->right);
        free(node);
    }
}

// Example usage
int main() {
    // Sample text: "this is an example for huffman encoding"
    // Count frequency of each character
    char arr[] = {'t', 'h', 'i', 's', ' ', 'a', 'n', 'e', 'x', 'm', 'p', 'l', 'f', 'o', 'r', 'u', 'c', 'd', 'g'};
    int freq[] = {2, 2, 3, 3, 7, 2, 3, 3, 1, 2, 1, 1, 2, 2, 1, 1, 1, 1, 1};
    
    int size = sizeof(arr) / sizeof(arr[0]);
    
    huffmanCodes(arr, freq, size);
    
    return 0;
}
