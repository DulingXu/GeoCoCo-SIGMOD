import numpy as np
import json
import sys

def floyd_warshall(matrix):
    N = len(matrix)
    dist = np.array(matrix)
    next_node = np.full((N, N), -1)

    # 初始化 next_node
    for i in range(N):
        for j in range(N):
            if i != j and matrix[i][j] != np.inf:
                next_node[i][j] = j

    # Floyd-Warshall 算法
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

    print("开始查找路径...")  # 调试输出
    # 查找所有有效路径，包括一跳路径和多跳路径
    for i in range(N):
        for j in range(N):
            if i != j:
                path = [i]
                intermediate = i
                while intermediate != j:
                    intermediate = next_node[intermediate][j]
                    if intermediate == -1:  # 检查是否有无效路径
                        break
                    path.append(intermediate)
                    if len(path) > N:  # 防止死循环
                        break
                if intermediate != -1:  # 包括一跳路径
                    paths.append((i, j, path))
                    print(f"路径: {i} --> {' --> '.join(map(str, path[1:]))} --> {j}")  # 输出路径

    if not paths:
        print("未找到任何超过一跳的路径！")
    else:
        print(f"找到的路径: {paths}")

    return paths

def group_nodes(paths, N):
    group_dict = {}

    # 按照路径分组，将依赖的节点分到被依赖的节点的组
    for path in paths:
        start, end, path_nodes = path
        if len(path_nodes) > 1:  # 确保存在依赖关系
            intermediate = path_nodes[1]  # 中间节点被认为是被依赖的节点
            if intermediate not in group_dict:
                group_dict[intermediate] = set()
            group_dict[intermediate].add(start)  # 把依赖的节点分给中间节点组

    # 生成组列表
    groups = []
    for leader, members in group_dict.items():
        group = [leader] + list(members)
        groups.append(group)

    # 确保没有依赖关系的节点单独成组
    all_grouped_nodes = set()
    for group in groups:
        all_grouped_nodes.update(group)

    for node in range(N):
        if node not in all_grouped_nodes:
            groups.append([node])  # 独立分组

    return groups

def save_group_result(groups, output_path):
    try:
        # 将所有组数据转换为标准 Python 类型以便 JSON 序列化
        groups = [[int(node) for node in group] for group in groups]

        # 保存分组结果
        with open(output_path, 'w') as f:
            json.dump(groups, f, indent=4)
        print(f"分组结果已保存到: {output_path}")
    except Exception as e:
        print(f"保存分组结果时出错: {e}")

def floyd_group(latency_matrix, output_path, num_groups=3):
    """
    使用 Floyd-Warshall 算法将节点分成组
    :param latency_matrix: 时延矩阵
    :param output_path: 输出路径
    :param num_groups: 需要划分的组数，默认为 3（保留该参数，但不用于算法）
    """
    # 计算最短路径
    dist, next_node = floyd_warshall(latency_matrix)

    # 找到所有路径
    paths = find_paths(dist, next_node)

    # 分组
    groups = group_nodes(paths, len(latency_matrix))

    if not groups:
        print("未找到合适的分组，可能所有节点之间没有多跳路径。")
    else:
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