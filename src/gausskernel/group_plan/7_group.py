import json
import sys
from sklearn.cluster import KMeans

def kmeans_group( latency_matrix, output_path, num_groups=7 ):
    """
    使用 KMeans 算法将节点分成 num_groups 组
    :param latency_matrix: 时延矩阵
    :param output_path: 输出路径
    :param num_groups: 需要划分的组数，默认是 7
    """
    num_nodes = len(latency_matrix)  # 节点数量

    # 使用 KMeans 进行聚类
    try:
        kmeans = KMeans(n_clusters=num_groups, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(latency_matrix)  # 聚类标签
        
        groups = [[] for _ in range(num_groups)]
        for i, label in enumerate(labels):
            groups[label].append(i)  # 根据标签将节点分到对应的组
        
        print(f"分组结果: {groups}")

        # 保存分组结果到指定路径
        with open(output_path, 'w') as f:
            json.dump(groups, f, indent=4)
        print(f"分组结果已保存到: {output_path}")
    except Exception as e:
        print(f"执行 KMeans 聚类时出错: {e}")

def main():
    if len(sys.argv) < 3:
        print("用法: python kmeans_group.py <latency_matrix_file> <output_path> [num_groups]")
        sys.exit(1)

    # 获取命令行参数
    latency_matrix_file = sys.argv[1]
    output_path = sys.argv[2]
    
    # 如果没有提供 num_groups 参数，默认设置为 7 组
    # 修改这里可以修改得到 k = x 参数
    num_groups = int(sys.argv[3]) if len(sys.argv) > 3 else 7

    # 加载时延矩阵
    try:
        with open(latency_matrix_file, 'r') as f:
            latency_matrix = json.load(f)
    except Exception as e:
        print(f"加载时延矩阵时出错: {e}")
        sys.exit(1)

    # 执行 KMeans 分组
    kmeans_group(latency_matrix, output_path, num_groups)

if __name__ == "__main__":
    main()