import math
import heapq
from typing import List, Tuple, Set, Dict, Optional
import matplotlib
matplotlib.use('Agg') # Backend não-interativo para salvar arquivos
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Point as ShapelyPoint, LineString, Polygon as ShapelyPolygon
from itertools import combinations
from collections import deque

# --- Definição de Grafo ---

class VisibilityGraph:
    """Grafo de visibilidade usando dicionários para armazenar nós e arestas"""
    def __init__(self):
        self.nodes: Set[Tuple[float, float]] = set()
        self.edges: Dict[Tuple[float, float], Set[Tuple[Tuple[float, float], float]]] = {}
    
    def add_node(self, point: Tuple[float, float]):
        """Adiciona um nó ao grafo"""
        self.nodes.add(point)
        if point not in self.edges:
            self.edges[point] = set()
    
    def add_edge(self, p1: Tuple[float, float], p2: Tuple[float, float], weight: float):
        """Adiciona uma aresta bidirecional entre dois pontos com peso"""
        self.add_node(p1)
        self.add_node(p2)
        
        p1_tuple = p1
        p2_tuple = p2
        
        self.edges[p1_tuple].add((p2_tuple, weight))
        self.edges[p2_tuple].add((p1_tuple, weight))
    
    def get_neighbors(self, point: Tuple[float, float]) -> Set[Tuple[float, float]]:
        """Retorna apenas as coordenadas dos vizinhos de um ponto"""
        return {neighbor[0] for neighbor in self.edges.get(point, set())}
    
    def get_edges_with_weights(self, point: Tuple[float, float]) -> Set[Tuple[Tuple[float, float], float]]:
        """Retorna os vizinhos e seus respectivos pesos"""
        return self.edges.get(point, set())

    def num_edges(self) -> int:
        """Retorna o número total de arestas (cada par contado uma vez)"""
        return sum(len(neighbors) for neighbors in self.edges.values()) // 2

# --- Funções Auxiliares ---

def parse_coords(line: str) -> Tuple[float, float]:
    """
    Parseia uma string 'x, y' ou 'x,y' para a tupla (x, y) de floats.
    
    Entrada: line (str)
    Retorno: Tuple[float, float]
    """
    line = line.replace('\xa0', ' ')
    parts = [p.strip() for p in line.split(',') if p.strip() != '']
    if len(parts) < 2:
        raise ValueError(f"Coordenadas malformadas: '{line}' (esperado 'x, y')")
    try:
        x = float(parts[0])
        y = float(parts[1])
    except ValueError:
        raise ValueError(f"Não foi possível converter para float: '{line}'")
    return (x, y)

def read_map(filename: str) -> Tuple[Tuple[float, float], Tuple[float, float], List[ShapelyPolygon]]:
    """
    Lê o arquivo de mapa.
    
    Entrada: filename (str)
    Retorno: (start, end, polygons)
    """
    with open(filename, 'r') as f:
        lines = [line.strip().replace('\xa0', ' ') for line in f if line.strip()] 
    
    idx = 0
    start = parse_coords(lines[idx])
    idx += 1
    end = parse_coords(lines[idx])
    idx += 1
    num_polygons = int(lines[idx])
    idx += 1
    
    polygons = []
    for _ in range(num_polygons):
        n_vertices = int(lines[idx])
        idx += 1
        vertices = []
        for _ in range(n_vertices):
            coords = parse_coords(lines[idx])
            vertices.append(coords)
            idx += 1
        polygons.append(ShapelyPolygon(vertices))
    
    return start, end, polygons

def is_visible(p1: Tuple[float, float], p2: Tuple[float, float], polygons: List[ShapelyPolygon]) -> bool:
    """
    Verifica se a linha entre p1 e p2 é visível (não cruza nem está dentro de nenhum polígono).
    
    Entrada: p1, p2 (Tuple[float, float]), polygons (List[ShapelyPolygon])
    Retorno: bool
    """
    if p1 == p2:
        return False
    
    line = LineString([p1, p2])
    
    for polygon in polygons:
        if line.crosses(polygon) or line.within(polygon):
            return False
    
    return True

def build_visibility_graph(start: Tuple[float, float], 
                             end: Tuple[float, float], 
                             polygons: List[ShapelyPolygon]) -> VisibilityGraph:
    """
    Constrói o grafo de visibilidade com base em start, end e vértices dos polígonos.
    
    Entrada: start, end (Tuple[float, float]), polygons (List[ShapelyPolygon])
    Retorno: VisibilityGraph
    """
    graph = VisibilityGraph()
    vertices = [start, end]
    for polygon in polygons:
        vertices.extend(list(polygon.exterior.coords)[:-1])
    
    for vertex in vertices:
        graph.add_node(vertex)
    
    for v1, v2 in combinations(vertices, 2):
        if is_visible(v1, v2, polygons):
            dist = math.hypot(v2[0] - v1[0], v2[1] - v1[1])
            graph.add_edge(v1, v2, weight=dist)
    
    return graph

def find_mst_prim(graph: VisibilityGraph) -> Tuple[List[Tuple[Tuple[float, float], Tuple[float, float]]], float]:
    """
    Encontra a Árvore Geradora Mínima (MST/AGM) no grafo usando o Algoritmo de Prim.
    
    Entrada: graph (VisibilityGraph)
    Retorno: (mst_edges, total_weight)
    """
    if not graph.nodes:
        return [], 0.0

    start_node = next(iter(graph.nodes))
    mst_edges: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []
    visited: Set[Tuple[float, float]] = {start_node}
    total_weight = 0.0
    min_heap = []
    
    for neighbor, weight in graph.get_edges_with_weights(start_node):
        heapq.heappush(min_heap, (weight, neighbor, start_node))
        
    while min_heap and len(visited) < len(graph.nodes):
        weight, target_node, source_node = heapq.heappop(min_heap)
        
        if target_node in visited:
            continue
            
        visited.add(target_node)
        mst_edges.append((source_node, target_node))
        total_weight += weight
        
        for neighbor, new_weight in graph.get_edges_with_weights(target_node):
            if neighbor not in visited:
                heapq.heappush(min_heap, (new_weight, neighbor, target_node))
                
    if len(visited) != len(graph.nodes):
        print("\nAviso: O grafo de visibilidade não é conexo. A MST foi calculada apenas para o componente do nó inicial.")

    return mst_edges, total_weight

def verticeMaisProximo(
    posicao: Tuple[float, float], 
    mst_edges: List[Tuple[Tuple[float, float], Tuple[float, float]]]
) -> Optional[Tuple[float, float]]:
    """
    Encontra o vértice mais próximo da posição fornecida dentro da Árvore Geradora Mínima.
    
    Entrada: posicao (Tuple[float, float]), mst_edges (List[Tuple[...]])
    Retorno: Optional[Tuple[float, float]]
    """
    if not mst_edges:
        return None

    vertices_mst: Set[Tuple[float, float]] = set()
    for p1, p2 in mst_edges:
        vertices_mst.add(p1)
        vertices_mst.add(p2)

    min_dist_sq = float('inf') 
    nearest_vertex: Optional[Tuple[float, float]] = None
    
    px, py = posicao

    for vx, vy in vertices_mst:
        dist_sq = (vx - px)**2 + (vy - py)**2
        
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            nearest_vertex = (vx, vy)
            
    return nearest_vertex

def build_mst_graph(mst_edges: List[Tuple[Tuple[float, float], Tuple[float, float]]]) -> VisibilityGraph:
    """
    Constrói um objeto VisibilityGraph contendo apenas os nós e arestas da MST.
    
    Entrada: mst_edges (List[Tuple[...]])
    Retorno: VisibilityGraph
    """
    mst_graph = VisibilityGraph()
    for p1, p2 in mst_edges:
        dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        mst_graph.add_edge(p1, p2, weight=dist)
    return mst_graph

# -----------------------------------------------------------------
# Algoritmo de Busca
# -----------------------------------------------------------------

def bfs_path_in_mst(
    mst_graph: 'VisibilityGraph', 
    start: Tuple[float, float], 
    end: Tuple[float, float]
) -> Optional[List[Tuple[float, float]]]:
    """
    Realiza a Busca em Largura (BFS) na MST para encontrar um caminho do início ao fim.
    
    Entrada: mst_graph (VisibilityGraph), start, end (Tuple[float, float])
    Retorno: Optional[List[Tuple[float, float]]] (O caminho encontrado ou None)
    """
    if start not in mst_graph.nodes or end not in mst_graph.nodes:
        return None

    queue = deque([start])
    previous_nodes = {node: None for node in mst_graph.nodes}
    visited = {start}
    
    path_found = False
    
    while queue:
        current_node = queue.popleft()
        
        if current_node == end:
            path_found = True
            break
            
        for neighbor, _ in mst_graph.get_edges_with_weights(current_node):
            if neighbor not in visited:
                visited.add(neighbor)
                previous_nodes[neighbor] = current_node
                queue.append(neighbor)

    if not path_found:
        return None
        
    path = []
    current_node = end
    
    while current_node is not None:
        path.append(current_node)
        current_node = previous_nodes[current_node]
    
    return path[::-1] 


# --- Visualização e Main ---

def visualize_graph(start: Tuple[float, float], 
                    end: Tuple[float, float], 
                    polygons: List[ShapelyPolygon], 
                    graph: VisibilityGraph, 
                    mst_edges: Optional[List[Tuple[Tuple[float, float], Tuple[float, float]]]] = None,
                    path_in_mst: Optional[List[Tuple[float, float]]] = None,
                    nearest_pt: Optional[Tuple[float, float]] = None,
                    save_file: str = None):
    """
    Gera e salva a visualização do mapa, obstáculos, grafo de visibilidade, MST e caminho BFS.
    
    Entrada: start, end, polygons, graph, mst_edges (Optional), path_in_mst (Optional), nearest_pt (Optional), save_file (Optional)
    Retorno: None (Salva o arquivo de imagem)
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Desenha polígonos
    for polygon in polygons:
        coords = list(polygon.exterior.coords)
        poly_patch = MplPolygon(coords, closed=True, facecolor='lightgray', 
                                edgecolor='black', alpha=0.7, linewidth=2)
        ax.add_patch(poly_patch)
        xs, ys = zip(*coords)
        ax.plot(xs, ys, color='black', linewidth=2)
    
    # Desenha arestas do grafo de visibilidade (fundo)
    drawn_edges = set()
    for node, neighbors_with_weights in graph.edges.items():
        for neighbor, _ in neighbors_with_weights:
            edge = tuple(sorted([node, neighbor]))
            if edge not in drawn_edges:
                ax.plot([node[0], neighbor[0]], [node[1], neighbor[1]], 
                         color='#FF0000', linewidth=0.5, alpha=0.3, zorder=2)
                drawn_edges.add(edge)
    
    # Desenha as arestas da MST em destaque
    if mst_edges:
        for p1, p2 in mst_edges:
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 
                     color='purple', linewidth=2.5, alpha=1.0, zorder=4)
                     
    # Desenha o Caminho encontrado na MST (BFS)
    if path_in_mst and len(path_in_mst) > 1:
        path_xs = [p[0] for p in path_in_mst]
        path_ys = [p[1] for p in path_in_mst]
        
        ax.plot(path_xs, path_ys, 
                 color='orange', linewidth=4.0, 
                 marker='o', markersize=5, 
                 label='Caminho BFS na MST', zorder=12) 

    # Desenha vértices dos polígonos
    for polygon in polygons:
        coords = list(polygon.exterior.coords)[:-1]
        if coords:
            xs, ys = zip(*coords)
            ax.scatter(xs, ys, c='blue', s=30, zorder=5)
    
    # Destaca o vértice mais próximo (se fornecido)
    if nearest_pt:
        ax.plot(nearest_pt[0], nearest_pt[1], marker='*', color='gold', markersize=20, 
                 label='Vértice Mais Próximo', markeredgecolor='black', markeredgewidth=1.5, zorder=15)
    
    # Destaca início e fim
    ax.plot(start[0], start[1], marker='o', color='green', markersize=10, 
             label='Início', markeredgecolor='black', markeredgewidth=1.5, zorder=10)
    ax.plot(end[0], end[1], marker='x', color='red', markersize=12, 
             label='Fim', markeredgewidth=2.5, zorder=10)
    
    # Configurações de limites e aspecto
    all_xs = [start[0], end[0]]
    all_ys = [start[1], end[1]]
    for polygon in polygons:
        coords = list(polygon.exterior.coords)
        xs, ys = zip(*coords)
        all_xs.extend(xs)
        all_ys.extend(ys)
    
    padding = 20.0
    ax.set_xlim(min(all_xs) - padding, max(all_xs) + padding)
    ax.set_ylim(min(all_ys) - padding, max(all_ys) + padding)
    ax.set_aspect('equal', 'box')
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    title = 'Grafo de Visibilidade com MST e Caminho BFS'
    ax.set_title(title)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    output_file = save_file if save_file else 'grafo_visibilidade_caminho_e_mst.png'
    fig.savefig(output_file, dpi=250, bbox_inches='tight')
    print(f"\n✓ Gráfico salvo em: {output_file}")
    plt.close()

def main():
    """Função principal: lê o mapa, constrói o grafo de visibilidade, encontra a MST e o caminho BFS na MST."""
    try:
        start, end, polygons = read_map('mapa.txt')
        
        print(f"Início: {start}")
        print(f"Fim: {end}")
        print(f"Número de polígonos: {len(polygons)}")
        
        print("\nConstruindo grafo de visibilidade...")
        graph = build_visibility_graph(start, end, polygons)
        
        print(f"\nNúmero de nós no grafo: {len(graph.nodes)}")
        print(f"Número de arestas no grafo: {graph.num_edges()}")
        
        print("\nEncontrando a Árvore Geradora Mínima (MST) com Prim...")
        mst_edges, mst_weight = find_mst_prim(graph)
        
        print(f"✓ MST encontrada. Peso total: {mst_weight:.2f}")
        print(f"Número de arestas na MST: {len(mst_edges)}")
        
        mst_graph = build_mst_graph(mst_edges)

        print("\nRealizando Busca em Largura (BFS) na **MST** entre Início e Fim...")
        
        path_in_mst = bfs_path_in_mst(mst_graph, start, end)
        
        path_length = 0.0
        if path_in_mst:
            for i in range(len(path_in_mst) - 1):
                p1 = path_in_mst[i]
                p2 = path_in_mst[i+1]
                path_length += math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            
            print(f"✓ Caminho BFS na MST encontrado com {len(path_in_mst)} nós.")
            print(f"  Comprimento total do caminho: {path_length:.2f}")
        else:
            print("✗ Não foi encontrado um caminho entre Início e Fim na MST. (Os vértices não estão conectados na árvore).")
        
        if polygons:
            test_point_coords = list(polygons[0].centroid.coords)[0]
        else:
            test_point_coords = (100.0, 100.0) 
            
        test_point = test_point_coords
        
        print(f"\nTestando 'verticeMaisProximo' para a posição: {test_point}")
        nearest_vertex = verticeMaisProximo(test_point, mst_edges)
        
        if nearest_vertex:
            dist = math.hypot(nearest_vertex[0] - test_point[0], nearest_vertex[1] - test_point[1])
            print(f"✓ Vértice mais próximo encontrado: {nearest_vertex}")
            print(f"  Distância até o ponto de teste: {dist:.2f}")
            
            graph.add_node(test_point)
            
            if nearest_vertex and is_visible(test_point, nearest_vertex, polygons):
                 graph.add_edge(test_point, nearest_vertex, weight=dist) 
        
        print("\nGerando visualização (Grafo, MST, Caminho BFS e Ponto Mais Próximo)...")
        visualize_graph(start, end, polygons, graph, 
                        mst_edges=mst_edges, 
                        path_in_mst=path_in_mst,
                        nearest_pt=nearest_vertex, 
                        save_file='grafo_visibilidade_caminho_bfs_e_mst.png')
        
        print("\n✓ Processamento concluído com sucesso!")
        
    except Exception as e:
        print(f"✗ Erro: {e}")
        if "[Errno 2] No such file or directory" in str(e):
             print("\n🚨 Dica: O arquivo 'mapa.txt' deve estar no mesmo diretório que o script.")
        raise

if __name__ == "__main__":
    main()
