import math
from typing import List, Tuple, Set
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString, Polygon as ShapelyPolygon

class VisibilityGraph:
    def __init__(self):
        self.nodes = set()
        self.edges = {}
    
    def add_node(self, point):
        self.nodes.add(point)
        if point not in self.edges:
            self.edges[point] = set()
    
    def add_edge(self, p1, p2):
        self.add_node(p1)
        self.add_node(p2)
        self.edges[p1].add(p2)
        self.edges[p2].add(p1)
    
    def get_neighbors(self, point):
        return self.edges.get(point, set())

def read_map(filename):
    """Lê o arquivo de mapa e retorna início, fim e lista de polígonos"""
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    idx = 0
    
    # Ponto de início
    coords = list(map(float, lines[idx].split(', ')))
    start = Point(coords[0], coords[1])
    idx += 1
    
    # Ponto de fim
    coords = list(map(float, lines[idx].split(', ')))
    end = Point(coords[0], coords[1])
    idx += 1
    
    # Polígonos
    polygons = []
    while idx < len(lines):
        n_vertices = int(lines[idx])
        idx += 1
        
        vertices = []
        for _ in range(n_vertices):
            n_coords = int(lines[idx])
            idx += 1
            for _ in range(n_coords):
                coords = list(map(float, lines[idx].split(', ')))
                vertices.append((coords[0], coords[1]))
                idx += 1
        
        # Cria polígono do Shapely
        polygons.append(ShapelyPolygon(vertices))
    
    return start, end, polygons

def is_visible(p1, p2, polygons):
    """Verifica se dois pontos são visíveis (usando Shapely) - CORRIGIDO"""
    if p1.equals(p2):
        return False
    
    # Cria linha entre os dois pontos
    line = LineString([p1, p2])
    
    # Verifica cada polígono
    for polygon in polygons:
        # Verifica se ambos os pontos estão no boundary do polígono
        p1_on_boundary = p1.distance(polygon.boundary) < 1e-9
        p2_on_boundary = p2.distance(polygon.boundary) < 1e-9
        
        # Se ambos estão no mesmo polígono, verifica se a linha fica fora
        if p1_on_boundary and p2_on_boundary:
            # Cria um ponto no meio da linha
            mid_point = line.interpolate(0.5, normalized=True)
            # Se o ponto do meio está dentro do polígono, não é visível
            if polygon.contains(mid_point):
                return False
            # Se cruza a borda (não apenas toca), não é visível
            if line.crosses(polygon.boundary):
                return False
        else:
            # Caso geral: verifica se a linha cruza ou está dentro do polígono
            # Exclui apenas os casos onde apenas toca a borda
            intersection = line.intersection(polygon)
            
            # Se não há interseção, ok
            if intersection.is_empty:
                continue
            
            # Se a interseção é apenas um ponto ou pontos (toca vértices), ok
            if intersection.geom_type in ['Point', 'MultiPoint']:
                continue
            
            # Se há interseção de linha (cruza ou está dentro), não é visível
            if intersection.geom_type in ['LineString', 'MultiLineString', 'GeometryCollection']:
                return False
            
            # Se a linha está completamente dentro do polígono
            if polygon.contains(line):
                return False
    
    return True

def build_visibility_graph(start, end, polygons):
    """Constrói o grafo de visibilidade"""
    graph = VisibilityGraph()
    
    # Coleta todos os vértices
    all_vertices = [start, end]
    for polygon in polygons:
        # Extrai coordenadas do exterior do polígono
        coords = list(polygon.exterior.coords[:-1])  # Remove último (duplicado)
        all_vertices.extend([Point(x, y) for x, y in coords])
    
    # Adiciona todos os vértices
    for vertex in all_vertices:
        graph.add_node(vertex)
    
    # Testa visibilidade entre todos os pares
    n = len(all_vertices)
    for i in range(n):
        for j in range(i + 1, n):
            if is_visible(all_vertices[i], all_vertices[j], polygons):
                graph.add_edge(all_vertices[i], all_vertices[j])
    
    return graph

def visualize_graph(start, end, polygons, graph):
    """Visualiza o grafo de visibilidade"""
    plt.figure(figsize=(12, 8))
    
    # Desenha polígonos usando Shapely
    for polygon in polygons:
        xs, ys = polygon.exterior.xy
        plt.fill(xs, ys, color='lightgray', edgecolor='black', linewidth=2)
    
    # Desenha arestas do grafo
    for node in graph.nodes:
        for neighbor in graph.get_neighbors(node):
            plt.plot([node.x, neighbor.x], [node.y, neighbor.y], 
                    'b-', alpha=0.3, linewidth=0.5)
    
    # Desenha vértices dos polígonos
    for polygon in polygons:
        xs, ys = polygon.exterior.xy
        plt.scatter(xs[:-1], ys[:-1], c='blue', s=50, zorder=5)
    
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
    
    # Salva ao invés de mostrar
    plt.savefig('grafo_visibilidade.png', dpi=300, bbox_inches='tight')
    print("Grafo salvo em: grafo_visibilidade.png")

# Execução
if __name__ == "__main__":
    start, end, polygons = read_map('mapa.txt')
    
    print(f"Início: ({start.x}, {start.y})")
    print(f"Fim: ({end.x}, {end.y})")
    print(f"Número de polígonos: {len(polygons)}")
    
    graph = build_visibility_graph(start, end, polygons)
    
    print(f"\nNúmero de nós: {len(graph.nodes)}")
    print(f"Número de arestas: {sum(len(n) for n in graph.edges.values()) // 2}")
    
    visualize_graph(start, end, polygons, graph)
