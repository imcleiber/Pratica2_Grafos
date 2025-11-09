import math
from typing import List, Tuple, Set
import matplotlib.pyplot as plt

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"({self.x}, {self.y})"
    
    def __eq__(self, other):
        return abs(self.x - other.x) < 1e-9 and abs(self.y - other.y) < 1e-9
    
    def __hash__(self):
        return hash((round(self.x, 6), round(self.y, 6)))

class Polygon:
    def __init__(self, vertices: List[Point]):
        self.vertices = vertices
    
    def edges(self):
        """Retorna lista de arestas (pares de pontos consecutivos)"""
        edges = []
        n = len(self.vertices)
        for i in range(n):
            edges.append((self.vertices[i], self.vertices[(i + 1) % n]))
        return edges

class VisibilityGraph:
    def __init__(self):
        self.nodes = set()
        self.edges = {}
    
    def add_node(self, point: Point):
        self.nodes.add(point)
        if point not in self.edges:
            self.edges[point] = set()
    
    def add_edge(self, p1: Point, p2: Point):
        self.add_node(p1)
        self.add_node(p2)
        self.edges[p1].add(p2)
        self.edges[p2].add(p1)
    
    def get_neighbors(self, point: Point):
        return self.edges.get(point, set())

def read_map(filename: str):
    """Lê o arquivo de mapa e retorna início, fim e lista de polígonos"""
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    idx = 0
    # Ponto de início
    start_coords = list(map(float, lines[idx].split(', ')))
    start = Point(start_coords[0], start_coords[1])
    idx += 1
    
    # Ponto de fim
    end_coords = list(map(float, lines[idx].split(', ')))
    end = Point(end_coords[0], end_coords[1])
    idx += 1
    
    # Polígonos
    polygons = []
    while idx < len(lines):
        n_vertices = int(lines[idx])
        idx += 1
        
        vertices = []
        for _ in range(n_vertices):
            coords = list(map(float, lines[idx].split(', ')))
            vertices.append(Point(coords[0], coords[1]))
            idx += 1
        
        polygons.append(Polygon(vertices))
    
    return start, end, polygons

def ccw(A: Point, B: Point, C: Point) -> float:
    """Teste de orientação: > 0 se anti-horário, < 0 se horário, 0 se colinear"""
    return (B.x - A.x) * (C.y - A.y) - (B.y - A.y) * (C.x - A.x)

def segments_intersect(p1: Point, p2: Point, p3: Point, p4: Point) -> bool:
    """Verifica se os segmentos p1-p2 e p3-p4 se intersectam"""
    d1 = ccw(p3, p4, p1)
    d2 = ccw(p3, p4, p2)
    d3 = ccw(p1, p2, p3)
    d4 = ccw(p1, p2, p4)
    
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    
    # Casos especiais de colinearidade
    if abs(d1) < 1e-9 and on_segment(p3, p1, p4):
        return True
    if abs(d2) < 1e-9 and on_segment(p3, p2, p4):
        return True
    if abs(d3) < 1e-9 and on_segment(p1, p3, p2):
        return True
    if abs(d4) < 1e-9 and on_segment(p1, p4, p2):
        return True
    
    return False

def on_segment(p: Point, q: Point, r: Point) -> bool:
    """Verifica se q está no segmento pr (assumindo colinearidade)"""
    return (min(p.x, r.x) <= q.x <= max(p.x, r.x) and
            min(p.y, r.y) <= q.y <= max(p.y, r.y))

def is_visible(p1: Point, p2: Point, polygons: List[Polygon]) -> bool:
    """Verifica se dois pontos são visíveis entre si (não cruzam obstáculos)"""
    if p1 == p2:
        return False
    
    for polygon in polygons:
        for edge_start, edge_end in polygon.edges():
            # Ignora se o segmento compartilha vértice com a aresta
            if p1 == edge_start or p1 == edge_end or p2 == edge_start or p2 == edge_end:
                continue
            
            if segments_intersect(p1, p2, edge_start, edge_end):
                return False
    
    return True

def build_visibility_graph(start: Point, end: Point, polygons: List[Polygon]) -> VisibilityGraph:
    """Constrói o grafo de visibilidade"""
    graph = VisibilityGraph()
    
    # Coleta todos os vértices
    all_vertices = [start, end]
    for polygon in polygons:
        all_vertices.extend(polygon.vertices)
    
    # Adiciona todos os vértices ao grafo
    for vertex in all_vertices:
        graph.add_node(vertex)
    
    # Testa visibilidade entre todos os pares de vértices
    n = len(all_vertices)
    for i in range(n):
        for j in range(i + 1, n):
            p1, p2 = all_vertices[i], all_vertices[j]
            if is_visible(p1, p2, polygons):
                graph.add_edge(p1, p2)
    
    return graph

def visualize_graph(start: Point, end: Point, polygons: List[Polygon], graph: VisibilityGraph):
    """Visualiza o grafo de visibilidade"""
    plt.figure(figsize=(12, 8))
    
    # Desenha polígonos
    for polygon in polygons:
        xs = [v.x for v in polygon.vertices] + [polygon.vertices[0].x]
        ys = [v.y for v in polygon.vertices] + [polygon.vertices[0].y]
        plt.fill(xs, ys, color='lightgray', edgecolor='black', linewidth=2)
    
    # Desenha arestas do grafo
    for node in graph.nodes:
        for neighbor in graph.get_neighbors(node):
            plt.plot([node.x, neighbor.x], [node.y, neighbor.y], 
                    'b-', alpha=0.3, linewidth=0.5)
    
    # Desenha vértices
    for polygon in polygons:
        xs = [v.x for v in polygon.vertices]
        ys = [v.y for v in polygon.vertices]
        plt.scatter(xs, ys, c='blue', s=50, zorder=5)
    
    # Destaca início e fim
    plt.scatter(start.x, start.y, c='green', s=200, marker='o', 
               label='Início', zorder=10, edgecolors='black', linewidths=2)
    plt.scatter(end.x, end.y, c='red', s=200, marker='s', 
               label='Fim', zorder=10, edgecolors='black', linewidths=2)
    
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Grafo de Visibilidade')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

# Exemplo de uso
if __name__ == "__main__":
    # Lê o mapa
    start, end, polygons = read_map('Pratica2_Grafos/mapa.txt')
    
    print(f"Início: {start}")
    print(f"Fim: {end}")
    print(f"Número de polígonos: {len(polygons)}")
    
    # Constrói o grafo de visibilidade
    graph = build_visibility_graph(start, end, polygons)
    
    print(f"\nNúmero de nós no grafo: {len(graph.nodes)}")
    total_edges = sum(len(neighbors) for neighbors in graph.edges.values()) // 2
    print(f"Número de arestas no grafo: {total_edges}")
    
    # Exibe algumas conexões
    print(f"\nConexões do ponto inicial {start}:")
    for neighbor in graph.get_neighbors(start):
        print(f"  -> {neighbor}")
    
    # Visualiza
    visualize_graph(start, end, polygons, graph)
