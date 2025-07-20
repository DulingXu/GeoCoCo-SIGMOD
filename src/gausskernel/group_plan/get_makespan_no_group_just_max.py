import os
import json
import numpy as np
import argparse
import logging
import sys

MESSAGE_SIZE_MB = 10  # 假设消息大小为10MB

def setup_logger(log_file_path):
    """
    设置日志功能，记录所有终端输出到指定的日志文件。
    :param log_file_path: 日志文件路径
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 创建文件处理器和终端处理器
    file_handler = logging.FileHandler(log_file_path, mode='w')
    console_handler = logging.StreamHandler()
    file_handler.setLevel(logging.INFO)
    console_handler.setLevel(logging.INFO)

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 重定向print到log和控制台
    class PrintLogger:
        def __init__(self):
            self.terminal = sys.stdout

        def write(self, message):
            self.terminal.write(message)
            logging.info(message.strip())  # 记录到日志文件

        def flush(self):
            pass  # 需要为了兼容sys.stdout的功能

    sys.stdout = PrintLogger()

def load_data(file_path):
    if not os.path.exists(file_path):
        print(f"文件路径不存在: {file_path}")
        return None
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return np.array(data, dtype=float)
    except json.JSONDecodeError as e:
        print(f"解析 JSON 文件时出错: {e}")
        return None
    except Exception as e:
        print(f"加载数据时出错: {e}")
        return None

def calculate_single_path_time(src, dst, group_result, latency_matrix, num_messages_array, message_size, bandwidth_array):
    try:
        src_group, dst_group = None, None
        for group in group_result:
            if src in group:
                src_group = group
            if dst in group:
                dst_group = group

        if src_group is None or dst_group is None:
            raise ValueError(f"源节点或目标节点未找到分组: src={src}, dst={dst}")

        src_leader, dst_leader = src_group[0], dst_group[0]

        # 源节点 -> 源组组长时间
        src_to_leader_time = (num_messages_array[src] * message_size) / bandwidth_array[src] if src != src_leader else 0
        src_to_leader_latency = latency_matrix[src][src_leader] if src != src_leader else 0

        # 源组组长 -> 目标组组长时间
        leader_to_leader_latency = latency_matrix[src_leader][dst_leader]
        leader_send_time = (num_messages_array[src_leader] * message_size) / bandwidth_array[src_leader]

        # 目标组组长 -> 目标节点时间
        leader_to_dst_latency = latency_matrix[dst_leader][dst] if dst != dst_leader else 0
        dst_receive_time = (num_messages_array[dst] * message_size) / bandwidth_array[dst] if dst != dst_leader else 0

        total_time = max(src_to_leader_time + src_to_leader_latency, leader_to_leader_latency + leader_send_time) + leader_to_dst_latency + dst_receive_time

        return total_time
    except Exception as e:
        print(f"计算路径时间时出错: {e}")
        return float('inf')  # 返回无穷大以表示该路径计算失败

def calculate_makespan(latency_matrix, bandwidth_array, conflict_matrix, message_size, num_messages_array, group_result):
    N = len(latency_matrix)
    makespan_matrix = np.zeros((N, N))

    for i in range(N):
        for j in range(N):
            if i != j:
                makespan_matrix[i][j] = calculate_single_path_time(i, j, group_result, latency_matrix, num_messages_array, message_size, bandwidth_array)

    return np.max(makespan_matrix)

def process_single_group(latency_matrix, bandwidth_array, conflict_matrix, num_messages_array, group_file_path):
    """
    直接处理唯一的分组文件，计算 makespan 结果
    """
    try:
        with open(group_file_path, 'r') as f:
            group_result = json.load(f)

        # 调用 calculate_makespan，传递所有需要的参数
        makespan = calculate_makespan(latency_matrix, bandwidth_array, conflict_matrix, MESSAGE_SIZE_MB, num_messages_array, group_result)
        print(f"分组 {group_file_path}: makespan 的值: {makespan}")
        logging.info(f"分组 {group_file_path}: makespan 的值: {makespan}")
    except Exception as e:
        print(f"处理分组文件 {group_file_path} 时出错: {e}")

def main(latency_file, bandwidth_file, conflict_file, num_messages_file, group_dir, log_dir):
    try:
        # 提取时延矩阵的编号名称
        matrix_name = os.path.splitext(os.path.basename(latency_file))[0]

        # 创建日志文件路径
        log_file_path = os.path.join(log_dir, f'no_group_{matrix_name}.log')
        setup_logger(log_file_path)

        # 加载数据
        latency_matrix = load_data(latency_file)
        bandwidth_array = load_data(bandwidth_file)
        conflict_matrix = load_data(conflict_file)
        num_messages_array = load_data(num_messages_file)

        if latency_matrix is None or bandwidth_array is None or conflict_matrix is None or num_messages_array is None:
            print("加载数据失败，退出程序。")
            return

        # 直接处理单个分组文件
        group_file_path = os.path.join(group_dir, 'no_group.json')
        process_single_group(latency_matrix, bandwidth_array, conflict_matrix, num_messages_array, group_file_path)

    except Exception as e:
        print(f"程序执行过程中出错: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="处理没有分组的场景")
    parser.add_argument("--latency_file", required=True, help="时延矩阵文件路径")
    parser.add_argument("--bandwidth_file", required=True, help="带宽文件路径")
    parser.add_argument("--conflict_file", required=True, help="冲突率矩阵文件路径")
    parser.add_argument("--num_messages_file", required=True, help="每个节点的消息个数文件路径")
    parser.add_argument("--group_dir", required=True, help="分组方案文件夹路径")
    parser.add_argument("--log_dir", required=True, help="日志文件保存目录")

    args = parser.parse_args()

    main(
        args.latency_file,
        args.bandwidth_file,
        args.conflict_file,
        args.num_messages_file,
        args.group_dir,
        args.log_dir
    )