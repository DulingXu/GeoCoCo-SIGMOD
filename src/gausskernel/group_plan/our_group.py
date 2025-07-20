import numpy as np
import json
import sys

def floyd_warshall(matrix):
    """
    使用 Floyd-Warshall 算法计算最短路径
    :param matrix: 时延矩阵
    :return: dist 矩阵 (最短路径距离), next_node 矩阵 (最短路径中继节点)
    """
    N = len(matrix)
    dist = np.array(matrix)
    next_node = np.full((N, N), -1)

    for i in range(N):
        for j in range(N):
            if i != j and matrix[i][j] != np.inf:
                next_node[i][j] = j

    for k in range(N):
        for i in range(N):
            for j in range(N):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_node[i][j] = next_node[i][k]

    return dist, next_node

def remove_non_shortest_paths(matrix, dist, next_node):
    """
    移除不在最短路径中的边
    :param matrix: 时延矩阵
    :param dist: Floyd-Warshall 算法得到的最短路径矩阵
    :param next_node: Floyd-Warshall 算法得到的中继节点矩阵
    """
    N = len(matrix)
    for i in range(N):
        for j in range(N):
            if i != j and next_node[i][j] == -1:
                matrix[i][j] = np.inf  # 不在最短路径中的边设为无穷大
    return matrix

def group_nodes(matrix, dist, next_node):
    """
    通过分析最短路径进行分组
    :param matrix: 时延矩阵
    :param dist: 最短路径矩阵
    :param next_node: 中继节点矩阵
    :return: 节点分组
    """
    N = len(matrix)
    groups = {}
    
    for i in range(N):
        for j in range(N):
            if i != j and next_node[i][j] != j:
                intermediate = next_node[i][j]
                if intermediate != -1:
                    if intermediate not in groups:
                        groups[intermediate] = set()
                    groups[intermediate].add(i)

    # 按最长路径决定依赖关系的分组
    final_groups = {}
    for i in range(N):
        longest_path = -1
        chosen_group = None
        for j in range(N):
            if i != j and next_node[i][j] != j:
                intermediate = next_node[i][j]
                if dist[i][j] > longest_path:
                    longest_path = dist[i][j]
                    chosen_group = intermediate

        if chosen_group is not None:
            if chosen_group not in final_groups:
                final_groups[chosen_group] = set()
            final_groups[chosen_group].add(i)
        else:
            final_groups[i] = {i}

    return final_groups

def save_group_result(groups, output_path, matrix):
    """
    保存分组结果，并将未分组的节点单独成组
    :param groups: 分组结果
    :param output_path: 输出路径
    :param matrix: 输入的时延矩阵，用于确定所有节点
    """
    # 获取所有节点的编号
    all_nodes = set(range(len(matrix)))
    grouped_nodes = set(node for group in groups.values() for node in group)
    ungrouped_nodes = all_nodes - grouped_nodes

    # 将未分组的节点单独分为一组
    for node in ungrouped_nodes:
        groups[node] = {node}

    # 保存分组结果
    with open(output_path, 'w') as f:
        json.dump([list(group) for group in groups.values()], f, indent=4)
    print(f"分组结果已保存到: {output_path}")

def main():
    if len(sys.argv) < 3:
        print("用法: python group_algorithm.py <latency_matrix_file> <output_path>")
        sys.exit(1)

    # 获取命令行参数
    latency_matrix_file = sys.argv[1]
    output_path = sys.argv[2]

    # 加载时延矩阵并将其转换为float类型
    with open(latency_matrix_file, 'r') as f:
        matrix = np.array(json.load(f), dtype=float)

    # 使用 Floyd-Warshall 算法计算最短路径
    dist, next_node = floyd_warshall(matrix)

    # 移除不在最短路径中的边
    matrix = remove_non_shortest_paths(matrix, dist, next_node)

    # 通过最短路径分析进行分组
    groups = group_nodes(matrix, dist, next_node)

    # 保存分组结果，并将未分组的节点单独成组
    save_group_result(groups, output_path, matrix)

if __name__ == "__main__":
    # 
    main()