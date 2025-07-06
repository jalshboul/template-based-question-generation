/**
 * Topological Sort implementation in C.
 *
 * Topological Sort is an algorithm for ordering the vertices of a directed acyclic graph (DAG)
 * such that for every directed edge (u, v), vertex u comes before vertex v in the ordering.
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

// Stack structure for topological sort
typedef struct {
    int items[MAX_VERTICES];
    int top;
} Stack;

// Create a new stack
Stack* createStack() {
    Stack* stack = (Stack*)malloc(sizeof(Stack));
    stack->top = -1;
    return stack;
}

// Check if the stack is empty
bool isStackEmpty(Stack* stack) {
    return stack->top == -1;
}

// Push element to stack
void push(Stack* stack, int value) {
    if (stack->top == MAX_VERTICES - 1)
        return; // Stack is full
    
    stack->items[++stack->top] = value;
}

// Pop element from stack
int pop(Stack* stack) {
    if (isStackEmpty(stack))
        return -1;
    
    return stack->items[stack->top--];
}

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

// Add directed edge between vertices
void addDirectedEdge(Graph* graph, int start, int end) {
    if (start >= 0 && start < graph->numVertices && 
        end >= 0 && end < graph->numVertices) {
        graph->adjacencyMatrix[start][end] = true;
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

// Recursive utility function for topological sort
void topologicalSortUtil(Graph* graph, int vertex, bool visited[], Stack* stack) {
    // Mark the current vertex as visited
    visited[vertex] = true;
    
    // Recur for all adjacent vertices
    for (int i = 0; i < graph->numVertices; i++) {
        if (graph->adjacencyMatrix[vertex][i] && !visited[i]) {
            topologicalSortUtil(graph, i, visited, stack);
        }
    }
    
    // After all adjacent vertices are processed, push the current vertex to stack
    push(stack, vertex);
}

// Perform topological sort on a directed acyclic graph
void topologicalSort(Graph* graph, int result[], int* resultSize) {
    // Mark all vertices as not visited
    bool visited[MAX_VERTICES] = {false};
    
    // Create a stack for topological sort
    Stack* stack = createStack();
    
    // Call the recursive helper function for all vertices
    for (int i = 0; i < graph->numVertices; i++) {
        if (!visited[i]) {
            topologicalSortUtil(graph, i, visited, stack);
        }
    }
    
    // Store the topological order
    int resultIndex = 0;
    while (!isStackEmpty(stack)) {
        result[resultIndex++] = pop(stack);
    }
    
    *resultSize = resultIndex;
    free(stack);
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
    addVertex(graph, 0, "5");
    addVertex(graph, 1, "4");
    addVertex(graph, 2, "2");
    addVertex(graph, 3, "3");
    addVertex(graph, 4, "1");
    addVertex(graph, 5, "0");
    
    // Add directed edges
    addDirectedEdge(graph, 0, 2); // 5 -> 2
    addDirectedEdge(graph, 0, 5); // 5 -> 0
    addDirectedEdge(graph, 1, 5); // 4 -> 0
    addDirectedEdge(graph, 1, 4); // 4 -> 1
    addDirectedEdge(graph, 2, 3); // 2 -> 3
    addDirectedEdge(graph, 3, 4); // 3 -> 1
    
    // Array to store result
    int result[MAX_VERTICES];
    int resultSize = 0;
    
    // Perform topological sort
    printf("Topological Sort order:\n");
    topologicalSort(graph, result, &resultSize);
    for (int i = 0; i < resultSize; i++) {
        printf("%s ", graph->vertices[result[i]]);
    }
    printf("\n");
    
    // Free memory
    freeGraph(graph);
    
    return 0;
}
