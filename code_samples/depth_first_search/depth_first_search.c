/**
 * Depth-First Search (DFS) implementation in C.
 *
 * DFS is a graph traversal algorithm that explores as far as possible along each branch
 * before backtracking. It uses a stack data structure (or recursion) to keep track of vertices.
 *
 * Time Complexity: O(V + E) where V is the number of vertices and E is the number of edges
 * Space Complexity: O(V) for the visited set and recursion stack
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

// Maximum number of vertices
#define MAX_VERTICES 100

// Graph structure using adjacency list
typedef struct {
    int numVertices;
    char* vertices[MAX_VERTICES];
    bool adjacencyMatrix[MAX_VERTICES][MAX_VERTICES];
} Graph;

// Create a new graph
Graph* createGraph(int numVertices) {
    Graph* graph = (Graph*)malloc(sizeof(Graph));
    graph->numVertices = numVertices;
    
    // Initialize adjacency matrix to false
    for (int i = 0; i < MAX_VERTICES; i++) {
        for (int j = 0; j < MAX_VERTICES; j++) {
            graph->adjacencyMatrix[i][j] = false;
        }
    }
    
    return graph;
}

// Add vertex to the graph
void addVertex(Graph* graph, int index, const char* name) {
    if (index >= 0 && index < graph->numVertices) {
        graph->vertices[index] = strdup(name);
    }
}

// Add edge between vertices
void addEdge(Graph* graph, int start, int end) {
    if (start >= 0 && start < graph->numVertices && 
        end >= 0 && end < graph->numVertices) {
        graph->adjacencyMatrix[start][end] = true;
        graph->adjacencyMatrix[end][start] = true; // For undirected graph
    }
}

// Find vertex index by name
int findVertexIndex(Graph* graph, const char* name) {
    for (int i = 0; i < graph->numVertices; i++) {
        if (strcmp(graph->vertices[i], name) == 0) {
            return i;
        }
    }
    return -1;
}

// Recursive DFS utility function
void dfsUtil(Graph* graph, int vertex, bool visited[], int result[], int* resultIndex) {
    // Mark the current vertex as visited and add to result
    visited[vertex] = true;
    result[(*resultIndex)++] = vertex;
    
    // Recur for all adjacent vertices
    for (int i = 0; i < graph->numVertices; i++) {
        if (graph->adjacencyMatrix[vertex][i] && !visited[i]) {
            dfsUtil(graph, i, visited, result, resultIndex);
        }
    }
}

// DFS traversal starting from a given vertex
void dfs(Graph* graph, int start, int result[], int* resultSize) {
    // Mark all vertices as not visited
    bool visited[MAX_VERTICES] = {false};
    
    // Call the recursive helper function
    int resultIndex = 0;
    dfsUtil(graph, start, visited, result, &resultIndex);
    
    *resultSize = resultIndex;
}

// Iterative DFS traversal
void dfsIterative(Graph* graph, int start, int result[], int* resultSize) {
    // Mark all vertices as not visited
    bool visited[MAX_VERTICES] = {false};
    
    // Create a stack for DFS
    int stack[MAX_VERTICES];
    int top = -1;
    
    // Push the starting vertex
    stack[++top] = start;
    
    int resultIndex = 0;
    
    while (top >= 0) {
        // Pop a vertex from stack
        int vertex = stack[top--];
        
        // If not visited, mark it as visited and add to result
        if (!visited[vertex]) {
            visited[vertex] = true;
            result[resultIndex++] = vertex;
            
            // Push all adjacent vertices to stack (in reverse order to match recursive DFS)
            for (int i = graph->numVertices - 1; i >= 0; i--) {
                if (graph->adjacencyMatrix[vertex][i] && !visited[i]) {
                    stack[++top] = i;
                }
            }
        }
    }
    
    *resultSize = resultIndex;
}

// Free graph memory
void freeGraph(Graph* graph) {
    for (int i = 0; i < graph->numVertices; i++) {
        free(graph->vertices[i]);
    }
    free(graph);
}

// Example usage
int main() {
    // Create a graph with 6 vertices
    Graph* graph = createGraph(6);
    
    // Add vertices
    addVertex(graph, 0, "A");
    addVertex(graph, 1, "B");
    addVertex(graph, 2, "C");
    addVertex(graph, 3, "D");
    addVertex(graph, 4, "E");
    addVertex(graph, 5, "F");
    
    // Add edges
    addEdge(graph, 0, 1); // A - B
    addEdge(graph, 0, 2); // A - C
    addEdge(graph, 1, 3); // B - D
    addEdge(graph, 1, 4); // B - E
    addEdge(graph, 2, 5); // C - F
    addEdge(graph, 4, 5); // E - F
    
    // Arrays to store results
    int recursiveResult[MAX_VERTICES];
    int recursiveResultSize = 0;
    
    int iterativeResult[MAX_VERTICES];
    int iterativeResultSize = 0;
    
    // Perform DFS traversal starting from vertex A (index 0)
    printf("Recursive DFS starting from vertex 'A':\n");
    dfs(graph, 0, recursiveResult, &recursiveResultSize);
    for (int i = 0; i < recursiveResultSize; i++) {
        printf("%s ", graph->vertices[recursiveResult[i]]);
    }
    printf("\n");
    
    printf("\nIterative DFS starting from vertex 'A':\n");
    dfsIterative(graph, 0, iterativeResult, &iterativeResultSize);
    for (int i = 0; i < iterativeResultSize; i++) {
        printf("%s ", graph->vertices[iterativeResult[i]]);
    }
    printf("\n");
    
    // Free memory
    freeGraph(graph);
    
    return 0;
}
