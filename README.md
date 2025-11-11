# Pratica2_Grafos
Projeto 2 da disciplina de Teoria dos Grafos

É preciso instalar as bibliotecas em requirements.txt para rodar o algoritmo

Passos para rodar o projeto:
1. Baixe todos os arquivos e os salve na mesma pasta;
2. Abra a pasta no VScode e rode grafos.py;
3. Na pasta será gerado o grafo de visibilidade denominado grafo_visibilidade.png, grafo_visibilidade_e_mst.png, grafo_visibilidade_mst_e_proximo e grafo_visibilidade_caminho_bfs_e_mst;
   
Dessa forma, é possível verificar exatamente o retorno de cada função através da plotagem dos grafos sobre o mapa criado.

## Parte 1 & 2 do Projeto : Criação e Leitura de Mapa de Grafo de Visibilidade:

### Formatação de arquivo do mapa (.txt): 
```
35, -68
195, -180
4
6
84, -62
133, -12
155, -34
119, -69
140, -90
126, -105
5
174, -39
174, -29
255, -29
255, -39
215, -110
6
59, -164
140, -164
140, -234
124, -234
124, -185
59, -185
6

168, -166
197, -138
209, -150
183, -175
235, -227
232, -230
```
### Geração do Grafo de Visibilidade: 
<img width="592" height="593" alt="image" src="https://github.com/user-attachments/assets/aff72c62-abdb-4f15-946e-733af4eb5709" />


## Parte 3 a 6: 
### Grafo de Visibilidade com MST e Caminho BFS
 A visualização combina três camadas de informação sobre o mapa:
 
1. Obstáculos (Polígonos): As áreas sombreadas em cinza (lightgray) representam obstáculos que não podem ser atravessados.

2. Grafo de Visibilidade (Fundo): As linhas finas em vermelho claro mostram todas as conexões retas e visíveis (arestas) entre os vértices dos polígonos, o ponto de Início (verde) e o ponto de Fim (vermelho).

3. MST (Árvore Geradora Mínima): As arestas em roxo escuro representam a Árvore Geradora Mínima (MST) calculada a partir do grafo de visibilidade (provavelmente usando Prim, conforme o código implementado). A MST conecta todos os nós com o menor comprimento total possível.

4. Caminho BFS na MST (Laranja): A linha grossa em laranja representa o caminho encontrado usando a Busca em Largura (BFS), que conecta o ponto inicial ao ponto final usando somente as arestas da MST.

|`Tópico Solicitado` |`Demonstração na Imagem `|`Detalhes`|
|` Implementar Kruskal ou Prim no grafo de visibilidade |`Linhas Roxas (MST) |`O conjunto de arestas em roxo é o resultado da aplicação do Algoritmo de Prim ao Grafo de Visibilidade. Ele garante a menor distância total para conectar todos os nós do grafo`|
|`Implementação da função verticeMaisProximo `|`Estrela Amarela (Vértice Mais Próximo)`|` A estrela amarela mostra o nó da MST que foi identificado pela função verticeMaisProximo como sendo o mais próximo do ponto de teste ou da posição inicial.`|
|`Implementação de algoritmo de busca na árvore (BFS)`|`Linha Laranja (Caminho BFS) `|`A linha grossa em laranja é o resultado da Busca em Largura (BFS), um algoritmo de busca, executado somente sobre a MST (arestas roxas) para encontrar o caminho mais curto (em número de arestas) do início ao fim.`|
|`Plotar o caminho gerado no mapa (Extra) `|`Linha Laranja`|`O caminho final gerado pela BFS é plotado de forma clara e destacada (laranja) sobre o mapa, cumprindo o objetivo de visualização.`|
<img width="517" height="516" alt="image" src="https://github.com/user-attachments/assets/6877f52d-a8b1-4c5a-adcf-1b52d1e3cb0a" />


