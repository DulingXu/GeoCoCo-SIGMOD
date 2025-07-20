import itertools
import json
import os

# 用于生成N个节点下全部的分组情形

def generate_partitions(nodes, k):
    """
    生成节点的所有可能的k个分组的组合，不考虑组员顺序。
    """
    def partitions(nodes, k):
        if k == 1:
            yield [nodes]
            return
        if len(nodes) == k:
            yield [[n] for n in nodes]
            return
        first = nodes[0]
        for smaller in partitions(nodes[1:], k-1):
            yield [[first]] + smaller
        for smaller in partitions(nodes[1:], k):
            for i, subset in enumerate(smaller):
                yield smaller[:i] + [[first] + subset] + smaller[i+1:]

    return list(partitions(nodes, k))

def generate_leader_variations(groups):
    """
    对于给定的组，产生所有组长不同的分组方案。
    组长为每个组第一个元素，生成每个组的组长顺序。
    """
    leader_variations = []
    for group in groups:
        perms = list(itertools.permutations(group))  # 组内所有排列
        leader_variations.append(perms)

    # 对于每个组的所有排列，选择一个
    all_variations = list(itertools.product(*leader_variations))
    return all_variations

def save_partition_to_file(partition_variation, x, y, output_dir):
    """
    将分组方案保存到文件。
    """
    filename = f"best_group_detection_{x}_{y}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w') as f:
        json.dump(partition_variation, f, indent=4)

def generate_groupings(n, output_dir):
    """
    生成n个节点的所有分组方案，并保存到文件。
    """
    nodes = list(range(n))  # 修改为从 0 到 n-1
    y = 1  # 每个x组的分组编号从1开始

    # 生成从2到n个组的所有分组方案
    for x in range(2, n + 1):
        partitions = generate_partitions(nodes, x)
        for partition in partitions:
            # 为每个分组方案生成所有可能的组长变体
            leader_variations = generate_leader_variations(partition)
            for variation in leader_variations:
                # 保存每个不同的分组方案
                save_partition_to_file(variation, x, y, output_dir)
                y += 1

def main():
    # 固定节点数和输出目录
    n = 7  # 节点数为7
    output_dir = "/Users/duling/Desktop/code/Geo_All2All/output/group_result/best_group_detection_source"  # 输出目录

    # 检查输出目录是否存在，不存在则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 生成分组方案并输出
    generate_groupings(n, output_dir)

if __name__ == "__main__":
    main()