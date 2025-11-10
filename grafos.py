import math
from typing import List, Tuple, Set, Dict
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo (salva arquivos sem abrir janelas)
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Point as ShapelyPoint, LineString, Polygon as ShapelyPolygon
from itertools import combinations

class VisibilityGraph:
    """Grafo de visibilidade usando dicionários para armazenar nós e arestas"""
    def __init__(self):
        self.nodes: Set[Tuple[float, float]] = set()
        self.edges: Dict[Tuple[float, float], Set[Tuple[float, float]]] = {}
    
    def add_node(self, point: Tuple[float, float]):
        """Adiciona um nó ao grafo"""
        self.nodes.add(point)
        if point not in self.edges:
            self.edges[point] = set()
    
    def add_edge(self, p1: Tuple[float, float], p2: Tuple[float, float], weight: float = None):
        """Adiciona uma aresta entre dois pontos"""
        self.add_node(p1)
        self.add_node(p2)
        self.edges[p1].add(p2)
        self.edges[p2].add(p1)
    
    def get_neighbors(self, point: Tuple[float, float]) -> Set[Tuple[float, float]]:
        """Retorna os vizinhos de um ponto"""
        return self.edges.get(point, set())
    
    def num_edges(self) -> int:
        """Retorna o número total de arestas"""
        return sum(len(neighbors) for neighbors in self.edges.values()) // 2

def parse_coords(line: str) -> Tuple[float, float]:
    """Parseia uma linha com coordenadas no formato 'x, y' ou 'x,y' e retorna (x, y) como floats.
    
    Args:
        line: String com coordenadas no formato 'x, y' ou 'x,y'
        
    Returns:
        Tupla (x, y) com as coordenadas
        
    Raises:
        ValueError: Se a linha estiver malformada ou não puder ser convertida
    """
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
    """Lê o arquivo de mapa e retorna início, fim e lista de polígonos Shapely
    
    Formato do arquivo:
    - Linha 1: coordenadas do ponto de início (x, y)
    - Linha 2: coordenadas do ponto de fim (x, y)
    - Linha 3: quantidade total de polígonos
    - Para cada polígono:
        - Uma linha com o número de vértices
        - N linhas com as coordenadas (x, y) de cada vértice
    
    Args:
        filename: Caminho para o arquivo de mapa
        
    Returns:
        Tupla com (start, end, polygons) onde:
        - start: coordenadas (x, y) do ponto inicial
        - end: coordenadas (x, y) do ponto final
        - polygons: lista de objetos Polygon do Shapely
    """
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    idx = 0
    # Ponto de início
    start = parse_coords(lines[idx])
    idx += 1
    
    # Ponto de fim
    end = parse_coords(lines[idx])
    idx += 1
    
    # Quantidade de polígonos
    num_polygons = int(lines[idx])
    idx += 1
    
    # Polígonos
    polygons = []
    for _ in range(num_polygons):
        n_vertices = int(lines[idx])
        idx += 1
        
        vertices = []
        for _ in range(n_vertices):
            coords = parse_coords(lines[idx])
            vertices.append(coords)
            idx += 1
        
        # Cria polígono Shapely
        polygons.append(ShapelyPolygon(vertices))
    
    return start, end, polygons

def is_visible(p1: Tuple[float, float], p2: Tuple[float, float], polygons: List[ShapelyPolygon]) -> bool:
    """Verifica se dois pontos são visíveis entre si usando Shapely
    
    Dois pontos são visíveis se a linha entre eles não cruza ou está dentro de nenhum polígono.
    
    Args:
        p1: Coordenadas (x, y) do primeiro ponto
        p2: Coordenadas (x, y) do segundo ponto
        polygons: Lista de polígonos Shapely que são obstáculos
        
    Returns:
        True se os pontos são visíveis, False caso contrário
    """
    if p1 == p2:
        return False
    
    # Cria uma linha entre os dois pontos
    line = LineString([p1, p2])
    
    # Verifica se a linha cruza ou está dentro de algum polígono
    for polygon in polygons:
        # Se a linha cruza ou está dentro do polígono, não é visível
        if line.crosses(polygon) or line.within(polygon):
            return False
    
    return True

def build_visibility_graph(start: Tuple[float, float], 
                          end: Tuple[float, float], 
                          polygons: List[ShapelyPolygon]) -> VisibilityGraph:
    """Constrói o grafo de visibilidade usando Shapely
    
    Args:
        start: Coordenadas (x, y) do ponto inicial
        end: Coordenadas (x, y) do ponto final
        polygons: Lista de polígonos Shapely que são obstáculos
        
    Returns:
        VisibilityGraph com todos os nós e arestas de visibilidade
    """
    graph = VisibilityGraph()
    
    # Coleta todos os vértices (start, end + vértices dos polígonos)
    vertices = [start, end]
    for polygon in polygons:
        # Extrai coordenadas dos vértices do polígono (exterior)
        vertices.extend(list(polygon.exterior.coords)[:-1])  # Remove duplicata do último ponto
    
    # Adiciona todos os vértices ao grafo
    for vertex in vertices:
        graph.add_node(vertex)
    
    # Testa visibilidade entre todos os pares de vértices
    for v1, v2 in combinations(vertices, 2):
        if is_visible(v1, v2, polygons):
            # Calcula distância euclidiana
            dist = math.hypot(v2[0] - v1[0], v2[1] - v1[1])
            graph.add_edge(v1, v2, weight=dist)
    
    return graph

def visualize_graph(start: Tuple[float, float], 
                   end: Tuple[float, float], 
                   polygons: List[ShapelyPolygon], 
                   graph: VisibilityGraph, 
                   save_file: str = None):
    """Visualiza o grafo de visibilidade
    
    Args:
        start: Coordenadas (x, y) do ponto inicial
        end: Coordenadas (x, y) do ponto final
        polygons: Lista de polígonos Shapely
        graph: Grafo de visibilidade
        save_file: Caminho para salvar a imagem (None para 'grafo_visibilidade.png')
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Desenha polígonos
    for polygon in polygons:
        # Extrai coordenadas do polígono
        coords = list(polygon.exterior.coords)
        
        # Adiciona patch do polígono preenchido
        poly_patch = MplPolygon(coords, closed=True, facecolor='lightgray', 
                                edgecolor='black', alpha=0.7, linewidth=2)
        ax.add_patch(poly_patch)
        
        # Desenha as bordas explicitamente
        xs, ys = zip(*coords)
        ax.plot(xs, ys, color='black', linewidth=2)
    
    # Desenha arestas do grafo de visibilidade
    drawn_edges = set()
    for node in graph.nodes:
        for neighbor in graph.get_neighbors(node):
            # Para evitar desenhar a mesma aresta duas vezes
            edge = tuple(sorted([node, neighbor]))
            if edge not in drawn_edges:
                ax.plot([node[0], neighbor[0]], [node[1], neighbor[1]], 
                       color='#FF0000', linewidth=0.5, alpha=0.3)
                drawn_edges.add(edge)
    
    # Desenha vértices dos polígonos
    for polygon in polygons:
        coords = list(polygon.exterior.coords)[:-1]  # Remove duplicata
        if coords:
            xs, ys = zip(*coords)
            ax.scatter(xs, ys, c='blue', s=30, zorder=5)
    
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
    ax.set_title('Grafo de Visibilidade (Shapely)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Salva o gráfico
    output_file = save_file if save_file else 'grafo_visibilidade.png'
    fig.savefig(output_file, dpi=250, bbox_inches='tight')
    print(f"\n✓ Gráfico salvo em: {output_file}")
    plt.close()

def main():
    """Função principal"""
    try:
        # Lê o mapa
        start, end, polygons = read_map('mapa.txt')
        
        print(f"Início: {start}")
        print(f"Fim: {end}")
        print(f"Número de polígonos: {len(polygons)}")
        
        # Constrói o grafo de visibilidade
        print("\nConstruindo grafo de visibilidade...")
        graph = build_visibility_graph(start, end, polygons)
        
        print(f"\nNúmero de nós no grafo: {len(graph.nodes)}")
        print(f"Número de arestas no grafo: {graph.num_edges()}")
        
        # Exibe algumas conexões
        print(f"\nConexões do ponto inicial {start}:")
        for neighbor in sorted(graph.get_neighbors(start)):
            dist = math.hypot(neighbor[0] - start[0], neighbor[1] - start[1])
            print(f"  -> {neighbor} (distância: {dist:.2f})")
        
        # Visualiza e salva
        print("\nGerando visualização...")
        visualize_graph(start, end, polygons, graph, save_file='grafo_visibilidade.png')
        
        print("\n✓ Processamento concluído com sucesso!")
        
    except Exception as e:
        print(f"✗ Erro: {e}")
        raise

# Exemplo de uso
if __name__ == "__main__":
    main()
