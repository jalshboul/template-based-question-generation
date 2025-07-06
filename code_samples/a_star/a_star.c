/**
 * A* Search Algorithm implementation in C.
 *
 * A* is a best-first search algorithm that finds the least-cost path from a given initial node
 * to a goal node. It uses a heuristic function to estimate the cost from the current node to the goal,
 * which guides the search towards the goal more efficiently than algorithms like Dijkstra's.
 *
 * Time Complexity: O(b^d) where b is the branching factor and d is the depth of the goal
 * Space Complexity: O(b^d) to store all generated nodes
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <limits.h>
#include <math.h>

// Maximum grid size for the example
#define MAX_GRID_SIZE 100

// Position structure for grid-based pathfinding
typedef struct {
    int x;
    int y;
} Position;

// Node structure for A* algorithm
typedef struct Node {
    Position pos;
    double gScore;
    double fScore;
    struct Node* parent;
} Node;

// Priority queue structure
typedef struct {
    Node** nodes;
    int capacity;
    int size;
} PriorityQueue;

// Create a new node
Node* createNode(Position pos, double gScore, double fScore, Node* parent) {
    Node* node = (Node*)malloc(sizeof(Node));
    node->pos = pos;
    node->gScore = gScore;
    node->fScore = fScore;
    node->parent = parent;
    return node;
}

// Create a priority queue
PriorityQueue* createPriorityQueue(int capacity) {
    PriorityQueue* pq = (PriorityQueue*)malloc(sizeof(PriorityQueue));
    pq->nodes = (Node**)malloc(capacity * sizeof(Node*));
    pq->capacity = capacity;
    pq->size = 0;
    return pq;
}

// Free memory used by priority queue
void freePriorityQueue(PriorityQueue* pq) {
    // Note: This doesn't free the nodes themselves
    free(pq->nodes);
    free(pq);
}

// Check if priority queue is empty
bool isPQEmpty(PriorityQueue* pq) {
    return pq->size == 0;
}

// Swap two nodes in the priority queue
void swapNodes(Node** a, Node** b) {
    Node* temp = *a;
    *a = *b;
    *b = temp;
}

// Heapify function to maintain heap property
void heapify(PriorityQueue* pq, int idx) {
    int smallest = idx;
    int left = 2 * idx + 1;
    int right = 2 * idx + 2;
    
    if (left < pq->size && pq->nodes[left]->fScore < pq->nodes[smallest]->fScore) {
        smallest = left;
    }
    
    if (right < pq->size && pq->nodes[right]->fScore < pq->nodes[smallest]->fScore) {
        smallest = right;
    }
    
    if (smallest != idx) {
        swapNodes(&pq->nodes[idx], &pq->nodes[smallest]);
        heapify(pq, smallest);
    }
}

// Insert a node into the priority queue
void insertPQ(PriorityQueue* pq, Node* node) {
    if (pq->size == pq->capacity) {
        // Resize if needed
        pq->capacity *= 2;
        pq->nodes = (Node**)realloc(pq->nodes, pq->capacity * sizeof(Node*));
    }
    
    // Insert at the end
    int i = pq->size;
    pq->nodes[i] = node;
    pq->size++;
    
    // Fix the min heap property
    while (i > 0 && pq->nodes[(i - 1) / 2]->fScore > pq->nodes[i]->fScore) {
        swapNodes(&pq->nodes[i], &pq->nodes[(i - 1) / 2]);
        i = (i - 1) / 2;
    }
}

// Extract the minimum node from the priority queue
Node* extractMinPQ(PriorityQueue* pq) {
    if (isPQEmpty(pq)) {
        return NULL;
    }
    
    // Store the root
    Node* root = pq->nodes[0];
    
    // Replace root with last element
    pq->nodes[0] = pq->nodes[pq->size - 1];
    pq->size--;
    
    // Heapify the root
    heapify(pq, 0);
    
    return root;
}

// Check if a position is in the priority queue
bool isInPQ(PriorityQueue* pq, Position pos) {
    for (int i = 0; i < pq->size; i++) {
        if (pq->nodes[i]->pos.x == pos.x && pq->nodes[i]->pos.y == pos.y) {
            return true;
        }
    }
    return false;
}

// Check if two positions are equal
bool posEqual(Position a, Position b) {
    return a.x == b.x && a.y == b.y;
}

// Calculate Manhattan distance heuristic
double manhattanDistance(Position a, Position b) {
    return abs(a.x - b.x) + abs(a.y - b.y);
}

// A* search algorithm
Node* aStarSearch(int grid[MAX_GRID_SIZE][MAX_GRID_SIZE], int rows, int cols, 
                 Position start, Position goal) {
    // Create open and closed sets
    PriorityQueue* openSet = createPriorityQueue(rows * cols);
    bool closedSet[MAX_GRID_SIZE][MAX_GRID_SIZE];
    memset(closedSet, false, sizeof(closedSet));
    
    // Initialize start node
    double hScore = manhattanDistance(start, goal);
    Node* startNode = createNode(start, 0.0, hScore, NULL);
    insertPQ(openSet, startNode);
    
    // Define possible moves (up, right, down, left)
    int dx[] = {0, 1, 0, -1};
    int dy[] = {-1, 0, 1, 0};
    
    while (!isPQEmpty(openSet)) {
        // Get node with lowest f_score
        Node* current = extractMinPQ(openSet);
        
        // Check if goal is reached
        if (posEqual(current->pos, goal)) {
            freePriorityQueue(openSet);
            return current;
        }
        
        // Add current node to closed set
        closedSet[current->pos.x][current->pos.y] = true;
        
        // Explore neighbors
        for (int i = 0; i < 4; i++) {
            int nx = current->pos.x + dx[i];
            int ny = current->pos.y + dy[i];
            Position neighborPos = {nx, ny};
            
            // Check if position is valid
            if (nx >= 0 && nx < rows && ny >= 0 && ny < cols && grid[nx][ny] == 0 && !closedSet[nx][ny]) {
                double tentativeGScore = current->gScore + 1.0;
                
                // Create neighbor node
                double hScore = manhattanDistance(neighborPos, goal);
                Node* neighbor = createNode(neighborPos, tentativeGScore, tentativeGScore + hScore, current);
                
                // Check if neighbor is in open set
                bool inOpenSet = isInPQ(openSet, neighborPos);
                
                if (!inOpenSet) {
                    insertPQ(openSet, neighbor);
                } else {
                    // This is a simplification - in a full implementation, we would
                    // update the existing node in the open set if this path is better
                    free(neighbor);
                }
            }
        }
    }
    
    // No path found
    freePriorityQueue(openSet);
    return NULL;
}

// Reconstruct path from goal node to start
void reconstructPath(Node* goalNode, Position path[], int* pathLength) {
    Node* current = goalNode;
    int length = 0;
    
    // Count path length
    while (current != NULL) {
        length++;
        current = current->parent;
    }
    
    // Allocate path array
    *pathLength = length;
    
    // Fill path array in reverse order
    current = goalNode;
    for (int i = length - 1; i >= 0; i--) {
        path[i] = current->pos;
        current = current->parent;
    }
}

// Free memory used by nodes in the path
void freePath(Node* goalNode) {
    Node* current = goalNode;
    while (current != NULL) {
        Node* parent = current->parent;
        free(current);
        current = parent;
    }
}

// Example usage: Grid-based pathfinding
int main() {
    // Define a simple grid (0 = empty, 1 = obstacle)
    int grid[MAX_GRID_SIZE][MAX_GRID_SIZE] = {
        {0, 0, 0, 0, 0},
        {0, 1, 1, 0, 0},
        {0, 0, 0, 1, 0},
        {0, 1, 0, 0, 0},
        {0, 0, 0, 0, 0}
    };
    int rows = 5;
    int cols = 5;
    
    // Define start and goal positions
    Position start = {0, 0};
    Position goal = {4, 4};
    
    // Run A* search
    Node* goalNode = aStarSearch(grid, rows, cols, start, goal);
    
    if (goalNode != NULL) {
        // Reconstruct path
        Position path[MAX_GRID_SIZE * MAX_GRID_SIZE];
        int pathLength;
        reconstructPath(goalNode, path, &pathLength);
        
        printf("Path found with length %d:\n", pathLength);
        for (int i = 0; i < pathLength; i++) {
            printf("  (%d, %d)\n", path[i].x, path[i].y);
        }
        
        // Visualize the path
        int pathGrid[MAX_GRID_SIZE][MAX_GRID_SIZE];
        memcpy(pathGrid, grid, sizeof(grid));
        
        for (int i = 0; i < pathLength; i++) {
            pathGrid[path[i].x][path[i].y] = 2;
        }
        
        // Print the grid
        printf("\nGrid visualization:\n");
        for (int i = 0; i < rows; i++) {
            printf("  ");
            for (int j = 0; j < cols; j++) {
                printf("%c ", pathGrid[i][j] == 0 ? '.' : pathGrid[i][j] == 1 ? '#' : 'o');
            }
            printf("\n");
        }
        
        // Free memory
        freePath(goalNode);
    } else {
        printf("No path found\n");
    }
    
    return 0;
}
