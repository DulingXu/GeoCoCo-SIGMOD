import random
import json
import sys

def random_group(latency_matrix, output_path, num_groups=3):
    """
    随机将节点分成 num_groups 组
    :param latency_matrix: 时延矩阵
    :param output_path: 输出路径
    :param num_groups: 需要划分的组数，默认是 3
    """
    num_nodes = len(latency_matrix)  # 节点数量

    # 随机分配节点到不同的组
    nodes = list(range(num_nodes))
    random.shuffle(nodes)  # 打乱节点顺序
    groups = [[] for _ in range(num_groups)]

    for i, node in enumerate(nodes):
        groups[i % num_groups].append(node)  # 将节点均匀分配到各个组

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
        print("用法: python random_group.py <latency_matrix_file> <output_path> [num_groups]")
        sys.exit(1)

    # 获取命令行参数
    latency_matrix_file = sys.argv[1]
    output_path = sys.argv[2]
    num_groups = int(sys.argv[3]) if len(sys.argv) > 3 else 3  # 可选参数，默认分3组

    # 加载时延矩阵
    try:
        with open(latency_matrix_file, 'r') as f:
            latency_matrix = json.load(f)
    except Exception as e:
        print(f"加载时延矩阵时出错: {e}")
        sys.exit(1)

    # 执行随机分组
    random_group(latency_matrix, output_path, num_groups)

if __name__ == "__main__":
    main()
