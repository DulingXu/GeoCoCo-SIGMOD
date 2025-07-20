import json
import numpy as np
import itertools
import sys
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpBinary, LpContinuous, value, LpStatus

def load_and_parse_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    matrix = [[float(value) for value in row] for row in data]
    return np.array(matrix)

def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def optimize_grouping(delay_matrix, n_clusters):
    n = len(delay_matrix)
    nodes = range(n)
    groups = range(n_clusters)

    # 创建优化问题
    prob = LpProblem("NodeGroupingOptimization", LpMinimize)

    # 定义变量
    x = LpVariable.dicts("x", ((i, j) for i in nodes for j in groups), cat=LpBinary)  # 节点分配变量
    y = LpVariable.dicts("y", ((i, j) for i in nodes for j in groups), cat=LpBinary)  # 聚合节点选择变量
    l = LpVariable.dicts("l", (j for j in groups), lowBound=0, cat=LpContinuous)      # 组内最大延迟
    L = LpVariable("L", lowBound=0, cat=LpContinuous)                                  # 组间最大延迟
    T = LpVariable("T", lowBound=0, cat=LpContinuous)                                  # 总延迟

    # 添加约束：每个节点只能属于一个组
    for i in nodes:
        prob += lpSum(x[i, j] for j in groups) == 1, f"OneGroupPerNode_{i}"

    # 添加约束：每个组有且仅有一个聚合节点
    for j in groups:
        prob += lpSum(y[i, j] for i in nodes) == 1, f"OneAggregatorPerGroup_{j}"

    # 添加约束：只有属于组的节点才能成为该组的聚合节点
    for i in nodes:
        for j in groups:
            prob += y[i, j] <= x[i, j], f"AggregatorInGroup_{i}_{j}"

    # 引入辅助变量 z，用于线性化 x[i, j] * x[m, j]
    z = LpVariable.dicts("z", ((i, m, j) for i in nodes for m in nodes for j in groups), cat=LpBinary)

    # 添加线性化约束（对于组内节点对）
    for i in nodes:
        for m in nodes:
            for j in groups:
                prob += z[i, m, j] <= x[i, j], f"Linearize1_{i}_{m}_{j}"
                prob += z[i, m, j] <= x[m, j], f"Linearize2_{i}_{m}_{j}"
                prob += z[i, m, j] >= x[i, j] + x[m, j] - 1, f"Linearize3_{i}_{m}_{j}"

    # 引入辅助变量 w，用于线性化 y[i, j1] * y[m, j2]
    w = LpVariable.dicts("w", ((i, m, j1, j2) for i in nodes for m in nodes for j1 in groups for j2 in groups if j1 != j2), cat=LpBinary)

    # 添加线性化约束（对于组间聚合节点对）
    for i in nodes:
        for m in nodes:
            for j1 in groups:
                for j2 in groups:
                    if j1 != j2:
                        prob += w[i, m, j1, j2] <= y[i, j1], f"LinearizeY1_{i}_{m}_{j1}_{j2}"
                        prob += w[i, m, j1, j2] <= y[m, j2], f"LinearizeY2_{i}_{m}_{j1}_{j2}"
                        prob += w[i, m, j1, j2] >= y[i, j1] + y[m, j2] - 1, f"LinearizeY3_{i}_{m}_{j1}_{j2}"

    # 添加组内最大延迟约束
    for j in groups:
        for i in nodes:
            for m in nodes:
                if i != m:
                    prob += l[j] >= (delay_matrix[i][m] + delay_matrix[m][i]) * z[i, m, j], f"GroupLatency_{j}_{i}_{m}"

    # 添加组间最大延迟约束
    for j1, j2 in itertools.combinations(groups, 2):
        prob += L >= lpSum((delay_matrix[i][m] + delay_matrix[m][i]) * w[i, m, j1, j2] for i in nodes for m in nodes), f"InterGroupLatency_{j1}_{j2}"

    # 添加总延迟约束
    for j in groups:
        prob += T >= l[j], f"TotalLatencyGroup_{j}"
    prob += T >= L, "TotalLatencyInterGroup"

    # 目标函数：最小化总延迟
    prob += T, "TotalLatency"

    # 求解优化问题
    prob.solve()

    # 检查求解状态
    if LpStatus[prob.status] != 'Optimal':
        print("No optimal solution found.")
        return None

    # 获取分组结果和聚合节点
    group_plan = [[] for _ in groups]
    aggregators = {}
    for j in groups:
        for i in nodes:
            if value(y[i, j]) > 0.5:
                aggregators[j] = i
            if value(x[i, j]) > 0.5:
                group_plan[j].append(i)

    # 将聚合节点放在组的首位
    for j in groups:
        aggregate_node = aggregators[j]
        group = group_plan[j]
        group.remove(aggregate_node)
        group.insert(0, aggregate_node)
        group_plan[j] = group

    return group_plan

def main():
    if len(sys.argv) != 3:
        print("用法: python optimize_group.py <latency_matrix_file> <output_path>")
        sys.exit(1)

    # 从命令行参数中读取输入文件和输出文件
    latency_matrix_file = sys.argv[1]
    output_path = sys.argv[2]

    # 加载时延矩阵
    delay_matrix = load_and_parse_json(latency_matrix_file)

    # 设置组数为 3
    n_clusters = 3

    # 调用优化算法
    group_plan = optimize_grouping(delay_matrix, n_clusters)

    if group_plan:
        # 保存分组方案
        save_json(group_plan, output_path)
        print(f"分组结果已保存到: {output_path}")

if __name__ == "__main__":
    main()