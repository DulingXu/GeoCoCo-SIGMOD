import numpy as np
import json
import sys

def floyd_warshall(matrix):
    N = len(matrix)
    dist = np.array(matrix)
    next_node = np.full((N, N), -1)

    # 初始化 next_node 矩阵
    for i in range(N):
        for j in range(N):
            if i != j and matrix[i][j] != np.inf:
                next_node[i][j] = j
    # 执行 Floyd-Warshall 算法
    for k in range(N):
        for i in range(N):
            for j in range(N):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_node[i][j] = next_node[i][k]

    return dist.tolist(), next_node.tolist()

def find_paths(dist, next_node):
    N = len(dist)
    paths = []

    # 查找每对节点之间的路径，包括一跳和多跳路径
    for i in range(N):
        for j in range(N):
            if i != j:
                path = [i]
                intermediate = i
                while intermediate != j:
                    intermediate = next_node[intermediate][j]
                    if intermediate == -1:  # 如果没有有效路径，退出
                        break
                    path.append(intermediate)
                    if len(path) > N:  # 防止死循环
                        break
                if intermediate != -1:  # 如果路径有效
                    total_latency = dist[i][j]
                    paths.append((i, j, path, total_latency))

    return paths

def group_nodes(paths, N):
    group_dict = {}
    node_group = {}

    # 处理依赖关系
    for path in paths:
        start, end, path_nodes, total_latency = path

        if len(path_nodes) > 1:  # 确保存在依赖关系
            intermediate = path_nodes[1]  # 中间节点是被依赖的节点

            # 如果 start 节点还没有分组，或依赖路径的时延更大
            if start not in node_group or total_latency > node_group[start]['latency']:
                node_group[start] = {'group': intermediate, 'latency': total_latency}

    # 分组生成
    for node, info in node_group.items():
        group_leader = info['group']
        if group_leader not in group_dict:
            group_dict[group_leader] = set()
        group_dict[group_leader].add(node)

    # 生成组列表
    groups = []
    for leader, members in group_dict.items():
        group = [leader] + list(members)
        groups.append(group)

    # 处理冲突，检查是否有节点已经分配组但发生冲突
    all_grouped_nodes = set()
    conflict_nodes = set()
    for group in groups:
        for node in group:
            if node in all_grouped_nodes:
                conflict_nodes.add(node)
            else:
                all_grouped_nodes.add(node)

    # 将冲突节点单独分组
    for node in conflict_nodes:
        groups.append([node])

    # 没有依赖关系的节点单独成组
    for node in range(N):
        if node not in all_grouped_nodes and node not in conflict_nodes:
            groups.append([node])  # 独立分组

    return groups

def save_group_result(groups, output_path):
    try:
        # 将分组结果保存为 JSON 文件
        with open(output_path, 'w') as f:
            json.dump(groups, f, indent=4)
        print(f"分组结果已保存到: {output_path}")
    except Exception as e:
        print(f"保存分组结果时出错: {e}")

def floyd_group(latency_matrix, output_path, num_groups=3):
    """
    使用 Floyd-Warshall 算法根据时延将节点进行分组
    :param latency_matrix: 时延矩阵
    :param output_path: 输出路径
    :param num_groups: 保留的参数，实际未使用
    """
    # 计算最短路径
    dist, next_node = floyd_warshall(latency_matrix)

    # 找到所有依赖关系路径
    paths = find_paths(dist, next_node)

    # 根据路径依赖关系进行分组
    groups = group_nodes(paths, len(latency_matrix))

    # 输出分组情况
    print(f"分组情况: {groups}")

    # 保存分组结果到文件
    save_group_result(groups, output_path)

def main():
    if len(sys.argv) < 3:
        print("用法: python floyd_group.py <latency_matrix_file> <output_path> [num_groups]")
        sys.exit(1)

    # 获取命令行参数
    latency_matrix_file = sys.argv[1]
    output_path = sys.argv[2]
    num_groups = int(sys.argv[3]) if len(sys.argv) > 3 else 3  # 可选参数，默认分3组（实际不使用）

    # 加载时延矩阵
    try:
        with open(latency_matrix_file, 'r') as f:
            latency_matrix = json.load(f)
    except Exception as e:
        print(f"加载时延矩阵时出错: {e}")
        sys.exit(1)

    # 调用 Floyd-Warshall 分组算法
    floyd_group(latency_matrix, output_path, num_groups)

if __name__ == "__main__":
    main()