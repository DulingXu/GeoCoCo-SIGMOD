import numpy as np
import json
import sys

def floyd_warshall(matrix):
    """
    计算 Floyd-Warshall 最短路径并返回最短路径矩阵和 next_node 矩阵
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

    floyd_max = np.max(dist[np.isfinite(dist)])  # 获取所有点对最短路径中的最大值
    return dist, next_node, floyd_max

def prune_unused_edges(dist, next_node):
    """
    剪掉未使用的边，生成新的剪枝后的矩阵
    """
    N = len(dist)
    pruned_matrix = np.full((N, N), np.inf)

    for i in range(N):
        for j in range(N):
            if i != j and next_node[i][j] != -1:
                pruned_matrix[i][j] = dist[i][j]

    print("剪枝后的矩阵:")
    print(pruned_matrix)
    return pruned_matrix

def calculate_bridge_nodes(dist, next_node):
    """
    计算桥梁节点及其重要度，按照重要度排序返回
    """
    N = len(dist)
    bridge_nodes = {}
    
    for i in range(N):
        for j in range(N):
            if i != j and next_node[i][j] != j and next_node[i][j] != -1:
                intermediate = next_node[i][j]
                if intermediate not in bridge_nodes:
                    bridge_nodes[intermediate] = 0
                bridge_nodes[intermediate] += dist[i][j]

    # 按照重要度排序
    sorted_bridges = sorted(bridge_nodes.items(), key=lambda x: -x[1])
    print("桥梁节点及其重要度 (降序):")
    for node, importance in sorted_bridges:
        print(f"节点 {node} - 重要度: {importance}")
    
    return sorted_bridges

def assign_groups(bridge_nodes, floyd_max, dist, next_node):
    """
    分配组长和组员，返回分组结果
    """
    N = len(dist)
    groups = []  # 确保 groups 被初始化
    grouped = [False] * N

    if not bridge_nodes:  # 如果没有桥梁节点
        for i in range(N):
            groups.append([i])
        return groups  # 如果没有桥梁节点，每个节点单独分组

    for i in range(N):
        if grouped[i]:
            continue

        dependencies = []
        for j in range(N):
            if i != j and next_node[i][j] != -1 and next_node[i][j] != j:
                dependencies.append((next_node[i][j], dist[i][j]))

        if dependencies:
            # 按桥梁节点重要度排序，并按照距离
            dependencies.sort(key=lambda x: (-dict(bridge_nodes).get(x[0], 0), x[1]))
            aggregation_node = dependencies[0][0]

            if not grouped[aggregation_node]:
                groups.append([aggregation_node])
                grouped[aggregation_node] = True

            for group in groups:
                if group[0] == aggregation_node:
                    group.append(i)
                    grouped[i] = True
                    break
        else:
            groups.append([i])
            grouped[i] = True

    return groups

def get_shortest_groups(matrix, output_path):
    """
    根据 Floyd-Warshall 计算结果和桥梁节点分配分组，并保存结果
    """
    # 1. 计算最短路径矩阵
    dist, next_node, floyd_max = floyd_warshall(matrix)
    print("最短路径矩阵:")
    print(dist)
    
    # 2. 剪枝操作
    pruned_matrix = prune_unused_edges(dist, next_node)
    
    # 3. 计算桥梁节点并排序
    bridge_nodes = calculate_bridge_nodes(dist, next_node)
    
    # 4. 分配组长和组员
    groups = assign_groups(bridge_nodes, floyd_max, dist, next_node)
    
    if not groups:  # 如果分组为空，确保给予提示
        print("分组失败，groups为空")
        return
    
    print(f"分组结果: {groups}")

    # 保存分组结果到指定路径
    try:
        with open(output_path, 'w') as f:
            # 确保所有组内节点为 int
            groups = [[int(node) for node in group] for group in groups]
            json.dump(groups, f, indent=4)
        print(f"分组结果已保存到: {output_path}")
    except Exception as e:
        print(f"保存分组结果时出错: {e}")

def main():
    """
    主函数，处理命令行参数并调用分组算法
    """
    if len(sys.argv) < 3:
        print("用法: python shortest.py <latency_matrix_file> <output_path>")
        sys.exit(1)
    
    # 从命令行获取时延矩阵文件和输出路径
    latency_matrix_file = sys.argv[1]
    output_path = sys.argv[2]

    # 加载时延矩阵
    try:
        with open(latency_matrix_file, 'r') as f:
            latency_matrix = json.load(f)
            # 将字符串矩阵转换为浮点型
            latency_matrix = [[float(value) for value in row] for row in latency_matrix]
    except Exception as e:
        print(f"加载时延矩阵时出错: {e}")
        sys.exit(1)

    # 运行分组算法
    get_shortest_groups(latency_matrix, output_path)

if __name__ == "__main__":
    main()