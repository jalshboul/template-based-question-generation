/**
 * Breadth-First Search (BFS) implementation in C.
 *
 * BFS is a graph traversal algorithm that explores all vertices at the present depth
 * before moving on to vertices at the next depth level. It uses a queue data structure.
 *
 * Time Complexity: O(V + E) where V is the number of vertices and E is the number of edges
 * Space Complexity: O(V) for the visited set and queue
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

// Maximum number of vertices
#define MAX_VERTICES 100

// Queue structure for BFS
typedef struct {
    int items[MAX_VERTICES];
    int front;
    int rear;
} Queue;

// Graph structure using adjacency list
typedef struct {
    int numVertices;
    char* vertices[MAX_VERTICES];
    bool adjacencyMatrix[MAX_VERTICES][MAX_VERTICES];
} Graph;

// Create a new queue
Queue* createQueue() {
    Queue* queue = (Queue*)malloc(sizeof(Queue));
    queue->front = -1;
    queue->rear = -1;
    return queue;
}

// Check if the queue is empty
bool isEmpty(Queue* queue) {
    return queue->rear == -1;
}

// Add element to queue
void enqueue(Queue* queue, int value) {
    if (queue->rear == MAX_VERTICES - 1)
        return; // Queue is full
    
    if (queue->front == -1)
        queue->front = 0;
    
    queue->rear++;
    queue->items[queue->rear] = value;
}

// Remove element from queue
int dequeue(Queue* queue) {
    if (isEmpty(queue))
        return -1;
    
    int item = queue->items[queue->front];
    
    if (queue->front == queue->rear) {
        // Queue has only one element, reset it
        queue->front = -1;
        queue->rear = -1;
    } else {
        queue->front++;
    }
    
    return item;
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

// BFS traversal starting from a given vertex
void bfs(Graph* graph, int start, int result[], int* resultSize) {
    // Mark all vertices as not visited
    bool visited[MAX_VERTICES] = {false};
    
    // Create a queue for BFS
    Queue* queue = createQueue();
    
    // Mark the current vertex as visited and enqueue it
    visited[start] = true;
    enqueue(queue, start);
    
    int resultIndex = 0;
    
    while (!isEmpty(queue)) {
        // Dequeue a vertex from queue and add to result
        int vertex = dequeue(queue);
        result[resultIndex++] = vertex;
        
        // Get all adjacent vertices of the dequeued vertex
        // If an adjacent vertex has not been visited, mark it
        // visited and enqueue it
        for (int i = 0; i < graph->numVertices; i++) {
            if (graph->adjacencyMatrix[vertex][i] && !visited[i]) {
                visited[i] = true;
                enqueue(queue, i);
            }
        }
    }
    
    *resultSize = resultIndex;
    free(queue);
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
    
    // Array to store result
    int result[MAX_VERTICES];
    int resultSize = 0;
    
    // Perform BFS traversal starting from vertex A (index 0)
    printf("BFS starting from vertex 'A':\n");
    bfs(graph, 0, result, &resultSize);
    for (int i = 0; i < resultSize; i++) {
        printf("%s ", graph->vertices[result[i]]);
    }
    printf("\n");
    
    // Free memory
    freeGraph(graph);
    
    return 0;
}
