import json
import sys

def edge_node_grouping(latency_matrix, output_path):
    """
    根据边缘节点和帮助节点进行分组
    :param latency_matrix: 时延矩阵
    :param output_path: 输出路径
    """
    num_nodes = len(latency_matrix)  # 节点数量

    # 将时延矩阵中的字符串转换为浮点数，并将无法转换的值设为无穷大
    for i in range(num_nodes):
        for j in range(num_nodes):
            try:
                latency_matrix[i][j] = float(latency_matrix[i][j])
            except (ValueError, TypeError):
                latency_matrix[i][j] = float('inf')  # 无法转换的值视为无穷大

    max_latency = max([max(row) for row in latency_matrix])  # 集群的最长时延

    groups = []
    ungrouped_nodes = set(range(num_nodes))  # 还没有分组的节点

    # 遍历所有节点，寻找边缘节点和帮助节点
    for node in range(num_nodes):
        if node not in ungrouped_nodes:
            continue  # 已经分组的节点跳过

        # 寻找帮助节点
        best_helper = None
        best_reduced_latency = float('inf')

        for potential_helper in range(num_nodes):
            if node == potential_helper:
                continue

            # 计算转发后的最长时延
            max_original_latency = max(latency_matrix[node])
            max_forward_latency = max(
                latency_matrix[node][potential_helper] + latency_matrix[potential_helper][i] for i in range(num_nodes)
            )

            # 判断是否满足条件
            if max_forward_latency < max_original_latency and max_forward_latency <= max_latency:
                if max_forward_latency < best_reduced_latency:
                    best_helper = potential_helper
                    best_reduced_latency = max_forward_latency

        if best_helper is not None:
            # 如果找到了帮助节点，则组成一个组
            group = [node, best_helper]
            groups.append(group)
            ungrouped_nodes.discard(node)
            ungrouped_nodes.discard(best_helper)
        else:
            # 如果没有找到帮助节点，单独成组
            groups.append([node])
            ungrouped_nodes.discard(node)

    # 将剩下的未分组的节点单独成组
    for node in ungrouped_nodes:
        groups.append([node])

    print(f"分组结果: {groups}")

    # 保存分组结果到指定路径
    try:
        with open(output_path, 'w') as f:
            json.dump(groups, f, indent=4)
        print(f"分组结果已保存到: {output_path}")
    except Exception as e:
        print(f"保存分组结果时出错: {e}")

def main():
    if len(sys.argv) < 3:
        print("用法: python rule_group.py <latency_matrix_file> <output_path>")
        sys.exit(1)

    # 获取命令行参数
    latency_matrix_file = sys.argv[1]
    output_path = sys.argv[2]

    # 加载时延矩阵
    try:
        with open(latency_matrix_file, 'r') as f:
            latency_matrix = json.load(f)
    except Exception as e:
        print(f"加载时延矩阵时出错: {e}")
        sys.exit(1)

    # 执行分组算法
    edge_node_grouping(latency_matrix, output_path)

if __name__ == "__main__":
    main()