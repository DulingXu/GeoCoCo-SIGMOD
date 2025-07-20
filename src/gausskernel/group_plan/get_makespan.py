import os
import json
import numpy as np
import subprocess
import argparse  # 用于解析命令行参数
import logging
import sys
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime


MESSAGE_SIZE_MB = 10  # 假设消息大小为10MB

# 路径统计文件保存路径
STAT_FILE_PATH = "/Users/duling/Desktop/code/Geo_All2All/src/path_usage_stats.json"
CALL_COUNT_FILE_PATH = "/Users/duling/Desktop/code/Geo_All2All/src/call_count.json"
HEATMAP_OUTPUT_DIR = "/Users/duling/Desktop/code/Geo_All2All/draw"

def setup_logger(log_file_path):
    """
    设置日志功能，记录所有终端输出到指定的日志文件。
    :param log_file_path: 日志文件路径
    """
    # 创建 logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 创建文件处理器
    file_handler = logging.FileHandler(log_file_path, mode='w')
    file_handler.setLevel(logging.INFO)

    # 创建终端处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 将处理器添加到 logger
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
    
# ---------------------------------------------------------------------------------------------------------

def load_data(file_path):
    """
    从指定的 JSON 文件路径加载数据（NxN 矩阵或 N 数组）。
    """
    if not os.path.exists(file_path):
        print(f"文件路径不存在: {file_path}")
        return None

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)  # 读取 JSON 数据
        array_data = np.array(data, dtype=float)
        return array_data
    
    except json.JSONDecodeError as e:
        print(f"解析 JSON 文件时出错: {e}")
        return None
    
    except Exception as e:
        print(f"加载数据时出错: {e}")
        return None

# ---------------------------------------------------------------------------------------------------------

def print_loaded_data(latency_matrix, bandwidth_array, conflict_matrix, num_messages_array, group_result):
    """
    打印所有加载的输入数据和分组情况，确保它们正确读取。
    """
    print("\n---- 加载的输入数据 ----")
    print("时延矩阵 (latency matrix):")
    print(latency_matrix)
    print("\n带宽数组 (bandwidth array):")
    print(bandwidth_array)
    print("\n冲突率矩阵 (conflict rate matrix):")
    print(conflict_matrix)
    print("\n每个节点的消息个数 (number of messages per node):")
    print(num_messages_array)
    print("\n分组情况 (group result):")
    print(group_result)
    print("--------------------------\n")

# ----------------------------------------------------------------------------------------------
def call_get_group(algorithm, latency_file, output_dir=None):
    """
    调用 get_group.py 并获取分组结果。
    :param algorithm: 分组算法的名称 (例如 "shortest")
    :param latency_file: 时延矩阵文件路径
    :param output_dir: 输出分组结果的目录路径，可选。如果不提供，将使用默认路径。
    :return: 分组结果列表
    """
    try:
        if output_dir is None:
            output_dir = "/Users/duling/Desktop/code/Geo_All2All/output/group_result/shortest"
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 调用 get_group.py
        result = subprocess.run(
            ["python3", "get_group.py", algorithm, latency_file, output_dir],
            capture_output=True, text=True, check=True
        )

        print(f"get_group.py 标准输出: {result.stdout}")
        print(f"get_group.py 标准错误: {result.stderr}")

        if result.returncode != 0:
            raise RuntimeError(f"get_group.py 执行失败，返回代码: {result.returncode}")

        # 读取保存的分组结果文件
        group_file = os.path.join(output_dir, f"{algorithm}_{os.path.splitext(os.path.basename(latency_file))[0]}_group.json")
        if not os.path.exists(group_file):
            raise FileNotFoundError(f"未找到分组结果文件: {group_file}")

        with open(group_file, 'r') as f:
            group_result = json.load(f)  # 读取 JSON 格式的分组结果

        print(f"读取的分组结果: {group_result}")  # 添加调试信息
        return group_result
    
    except subprocess.CalledProcessError as e:
        print(f"调用 get_group.py 时出错: {e}")
        return None
    except FileNotFoundError as e:
        print(f"文件未找到错误: {e}")
        return None
    except Exception as e:
        print(f"读取分组结果时出错: {e}")
        return None

# --------------------------------------------------------------------------------------------------------------
# 用于统计路径使用频率

def load_statistics():
    """加载路径使用统计和调用次数"""
    try:
        # 初始化路径使用频率和调用计数
        if os.path.exists(STAT_FILE_PATH):
            with open(STAT_FILE_PATH, 'r') as f:
                path_usage_frequency = np.array(json.load(f))
            print(f"成功加载路径统计: {STAT_FILE_PATH}")
        else:
            path_usage_frequency = None

        if os.path.exists(CALL_COUNT_FILE_PATH):
            with open(CALL_COUNT_FILE_PATH, 'r') as f:
                call_count = json.load(f)
            print(f"成功加载调用计数: {CALL_COUNT_FILE_PATH}")
        else:
            call_count = 0

        return path_usage_frequency, call_count

    except Exception as e:
        print(f"加载统计数据时出错: {e}")
        return None, 0

def save_statistics(path_usage_frequency, call_count):
    """保存路径使用统计和调用次数"""
    try:
        # 确保路径存在
        if not os.path.exists(os.path.dirname(STAT_FILE_PATH)):
            os.makedirs(os.path.dirname(STAT_FILE_PATH))

        with open(STAT_FILE_PATH, 'w') as f:
            json.dump(path_usage_frequency.tolist(), f)

        with open(CALL_COUNT_FILE_PATH, 'w') as f:
            json.dump(call_count, f)
            
        print("成功保存统计数据")

    except Exception as e:
        print(f"保存统计数据时出错: {e}")

def use_delay(src, dst, latency_matrix, path_usage_frequency):
    """记录一次使用时延路径 src -> dst。"""
    # 使用时延矩阵中的值
    latency_value = latency_matrix[src][dst]

    # 记录路径使用次数
    path_usage_frequency[src, dst] += 1

    # 返回时延值
    return latency_value

def plot_path_usage_frequency(path_usage_frequency):
    """绘制路径使用频率的热力图，并保存为 PDF 文件"""
    try:
        os.makedirs(HEATMAP_OUTPUT_DIR, exist_ok=True)

        # 生成当前时间
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(HEATMAP_OUTPUT_DIR, f"heatmap_{current_time}.pdf")

        # 绘制热力图并保存
        plt.figure(figsize=(8, 6))
        sns.heatmap(path_usage_frequency, annot=True, cmap="Blues", linewidths=.5)
        plt.title("Path Usage Frequency")
        plt.xlabel("Destination Node (j)")
        plt.ylabel("Source Node (i)")

        # 保存为 PDF 文件
        plt.savefig(output_file)
        print(f"热力图已保存到: {output_file}")
        plt.close()

    except Exception as e:
        print(f"生成热力图时出错: {e}")

def update_path_usage(latency_matrix, N):
    """更新路径使用次数"""
    try:
        print("正在更新路径使用统计...")

        # 加载现有的统计数据
        path_usage_frequency, call_count = load_statistics()

        # 如果路径统计文件不存在，初始化路径统计矩阵
        if path_usage_frequency is None:
            print("初始化路径统计矩阵")
            path_usage_frequency = np.zeros((N, N))

        # 遍历时延矩阵，统计路径使用情况
        for i in range(N):
            for j in range(N):
                if i != j:
                    use_delay(i, j, latency_matrix, path_usage_frequency)

        # 更新调用计数
        call_count += 1
        print(f"当前调用次数: {call_count}")

        # 保存更新后的统计数据
        save_statistics(path_usage_frequency, call_count)

        # 当调用达到 100 次时，输出热力图并重置统计数据
        if call_count >= 100:
            print("达到100次调用，生成热力图...")
            plot_path_usage_frequency(path_usage_frequency)

            # 重置路径统计和调用计数
            path_usage_frequency = np.zeros((N, N))
            call_count = 0
            save_statistics(path_usage_frequency, call_count)

    except Exception as e:
        print(f"更新路径统计时出错: {e}")
# --------------------------------------------------------------------------------------------------------------
# 瓜分带宽的计算版本

def calculate_makespan(latency_matrix, bandwidth_array, conflict_matrix, message_size, num_messages_array, group_result):
    """
    计算 makespan 的逻辑。
    :param latency_matrix: 时延矩阵 (NxN)
    :param bandwidth_array: 带宽数组 (N)
    :param conflict_matrix: 冲突率矩阵 (NxN)
    :param message_size: 消息大小（ MB ）
    :param num_messages_array: 每个节点发送的消息个数 (N)
    :param group_result: 分组情况
    :return: 最终完成时间 (makespan)
    """
    N = len(latency_matrix)  # 节点数量
    makespan_matrix = np.zeros((N, N))  # 初始化完成时间矩阵

    # # 更新路径使用频率
    # update_path_usage(latency_matrix, N)
    
    # 计算 单条路径 makespan
    
    def calculate_single_path_time(src, dst, group_result):
        """
        计算单条路径的完成时间。
        :param src: 源节点
        :param dst: 目标节点
        :param group_result: 分组结果
        :return: 该路径的完成时间
        """
        src_group = None
        dst_group = None
        for group in group_result:
            if src in group:
                src_group = group
            if dst in group:
                dst_group = group
        
        if src_group is None or dst_group is None:
            raise ValueError(f"源节点或目标节点未找到分组: src={src}, dst={dst}")
        
        src_leader = src_group[0]  # 源节点的组长
        dst_leader = dst_group[0]  # 目标节点的组长
        N = len(group_result)  # 总的节点数量

        # 1. 计算源节点 -> 源组组长的时间，并考虑组内带宽分配
        if src != src_leader:
            group_size = len(src_group)
            # 组员向组长发送，带宽除以组内其他节点数量
            src_bandwidth = bandwidth_array[src] / (group_size - 1) if group_size > 1 else bandwidth_array[src]
            src_to_leader_time = (num_messages_array[src] * message_size) / src_bandwidth  # 组员到组长的发送时间
            src_to_leader_latency = latency_matrix[src][src_leader]  # 组员到组长的时延
        else:
            src_to_leader_time = 0  # 组长自身不需要发送到自己
            src_to_leader_latency = 0

        # 2. 计算源组组长 -> 目标组组长的时间，并考虑组间带宽分配
        leader_to_leader_latency = latency_matrix[src_leader][dst_leader]  # 组长到目标组组长的时延

        # 组间带宽：如果有多个组同时发送，带宽需均分
        num_groups = len(group_result)  # 组的数量
        leader_bandwidth = bandwidth_array[src_leader] / (num_groups - 1) if num_groups > 1 else bandwidth_array[src_leader]

        # 检查组长的组是否有其他组员，只有存在组员时才使用冲突率过滤
        if len(src_group) > 1 or len(dst_group) > 1:
        # 冲突率过滤：减少组长之间的消息量
            filtered_data_leader_to_leader = (num_messages_array[src_leader]) * (1 - conflict_matrix[src_leader][dst_leader])
        else:
            # 没有组员时，发送所有数据
            filtered_data_leader_to_leader = num_messages_array[src_leader]
        # 组长之间的发送时间，基于过滤后的数据量和均分后的带宽
        
        leader_send_time = filtered_data_leader_to_leader * message_size / leader_bandwidth

        # 3. 计算目标组组长 -> 目标节点的时间，并考虑组内带宽分配
        if dst != dst_leader:
            group_size_dst = len(dst_group)
            # 组员向组长发送，带宽除以组内其他节点数量
            dst_bandwidth = bandwidth_array[dst] / (group_size_dst - 1) if group_size_dst > 1 else bandwidth_array[dst]
            leader_to_dst_latency = latency_matrix[dst_leader][dst]  # 组长到目标组员的时延
            dst_receive_time = (num_messages_array[dst] * message_size) / dst_bandwidth  # 组员接收时间
        else:
            leader_to_dst_latency = 0
            dst_receive_time = 0

        # 取消聚合时间，设置为 0
        aggregation_time = 0

        # 最终路径完成时间 = 组内发送时间 + 组间发送时间 + 目标组的转发时间
        localmakespan = max(src_to_leader_time + src_to_leader_latency, leader_to_leader_latency + leader_send_time) + \
                        leader_to_dst_latency + dst_receive_time
        print(f"makespan [{src}][{dst}] 结果: {localmakespan}")
        return localmakespan
        
    # 遍历所有路径，计算每条路径的完成时间
    for i in range(N):
        for j in range(N):
            if i != j:
                makespan_matrix[i][j] = calculate_single_path_time(i, j, group_result)
    
    # 最终完成时间取所有路径中的最大值
    final_makespan = np.max(makespan_matrix)
    return final_makespan

#--------------------------------------------------------------------------------------------------------、

# def calculate_makespan(latency_matrix, bandwidth_array, conflict_matrix, message_size, num_messages_array, group_result):
#     """
#     计算 makespan 的逻辑。
#     :param latency_matrix: 时延矩阵 (NxN)
#     :param bandwidth_array: 带宽数组 (N)
#     :param conflict_matrix: 冲突率矩阵 (NxN)
#     :param message_size: 消息大小（ MB ）
#     :param num_messages_array: 每个节点发送的消息个数 (N)
#     :param group_result: 分组情况
#     :return: 最终完成时间 (makespan)
#     """
#     N = len(latency_matrix)  # 节点数量
#     makespan_matrix = np.zeros((N, N))  # 初始化完成时间矩阵

#     # 计算 单条路径 makespan
    
#     def calculate_single_path_time(src, dst, group_result):
#         """
#         计算单条路径的完成时间。
#         :param src: 源节点
#         :param dst: 目标节点
#         :param group_result: 分组结果
#         :return: 该路径的完成时间
#         """
#         src_group = None
#         dst_group = None
#         for group in group_result:
#             if src in group:
#                 src_group = group
#             if dst in group:
#                 dst_group = group
        
#         if src_group is None or dst_group is None:
#             raise ValueError(f"源节点或目标节点未找到分组: src={src}, dst={dst}")
        
#         src_leader = src_group[0]  # 源节点的组长
#         dst_leader = dst_group[0]  # 目标节点的组长

#         # 1. 计算源节点 -> 源组组长的时间
#         if src != src_leader:
#             src_to_leader_time = (num_messages_array[src] * message_size) / bandwidth_array[src]  # 组员到组长的发送时间
#             src_to_leader_latency = latency_matrix[src][src_leader]  # 组员到组长的时延
#         else:
#             src_to_leader_time = 0  # 组长自身不需要发送到自己
#             src_to_leader_latency = 0

#         # 2. 计算源组组长 -> 目标组组长的时间
#         leader_to_leader_latency = latency_matrix[src_leader][dst_leader]  # 组长到目标组组长的时延
#         leader_send_time = (num_messages_array[src_leader] * message_size) / bandwidth_array[src_leader]  # 组长发送时间

#         # 3. 计算目标组组长 -> 目标节点的时间
#         if dst != dst_leader:
#             leader_to_dst_latency = latency_matrix[dst_leader][dst]  # 组长到目标组员的时延
#             dst_receive_time = (num_messages_array[dst] * message_size) / bandwidth_array[dst]  # 组员接收时间
#         else:
#             leader_to_dst_latency = 0
#             dst_receive_time = 0

#         # 4. 计算聚合时间：在源组组长上聚合消息
#         # 消息量可能因为冲突率减少
#         total_aggregated_data = (num_messages_array[src] + num_messages_array[src_leader]) * (1 - conflict_matrix[src][src_leader])
        
#         # 计算聚合后的消息发送时间
#         aggregation_time = total_aggregated_data / bandwidth_array[src_leader]

#         # 最终路径完成时间 = 组内发送时间 + 聚合时间 + 组间发送时间 + 目标组的转发时间
#         localmakespan = max(src_to_leader_time + src_to_leader_latency, aggregation_time + \
#                    leader_to_leader_latency + leader_send_time) + leader_to_dst_latency + dst_receive_time
#         print(f"makespan [{src}][{dst}] 结果: {localmakespan}")
#         return localmakespan
        
#     # 遍历所有路径，计算每条路径的完成时间
#     for i in range(N):
#         for j in range(N):
#             if i != j:
#                 makespan_matrix[i][j] = calculate_single_path_time(i, j, group_result)
    
#     # 最终完成时间取所有路径中的最大值
#     final_makespan = np.max(makespan_matrix)
#     return final_makespan

# -------------------------------------------------------------------------------------------

def create_log_file(log_dir, algorithm, latency_file):
    """
    动态生成日志文件名，并返回日志文件的完整路径
    :param log_dir: 日志目录
    :param algorithm: 分组算法名称
    :param latency_file: 时延矩阵文件路径，用于提取文件名称
    :return: 日志文件路径
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)  # 如果日志目录不存在则创建

    # 提取时延矩阵文件名（例如 matrix_100）
    matrix_name = os.path.splitext(os.path.basename(latency_file))[0]

    # 生成文件名，例如：random_group_matrix_100_result.log
    log_filename = f"{algorithm}_{matrix_name}_result.log"

    # 返回完整的日志文件路径
    return os.path.join(log_dir, log_filename)

# -------------------------------------------------------------------------------------------

def main(latency_file, bandwidth_file, conflict_file, num_messages_file, algorithm, log_dir, output_dir):
    try:
        # 创建日志文件
        log_file_path = create_log_file(log_dir, algorithm, latency_file)

        # 设置日志系统
        setup_logger(log_file_path)

        # 加载数据
        latency_matrix = load_data(latency_file)
        bandwidth_array = load_data(bandwidth_file)
        conflict_matrix = load_data(conflict_file)
        num_messages_array = load_data(num_messages_file)

        # 检查是否所有数据都已加载
        if latency_matrix is None or bandwidth_array is None or conflict_matrix is None or num_messages_array is None:
            print("加载数据失败，退出程序。")
            return

        # 调用 get_group.py 获取分组情况
        group_result = call_get_group(latency_file=latency_file, algorithm=algorithm, output_dir=output_dir)
        if group_result is None:
            print("获取分组结果失败，退出程序。")
            return

        # 打印所有加载的输入数据和分组情况
        print_loaded_data(latency_matrix, bandwidth_array, conflict_matrix, num_messages_array, group_result)

        # 计算 makespan
        makespan = calculate_makespan(latency_matrix, bandwidth_array, conflict_matrix, MESSAGE_SIZE_MB, num_messages_array, group_result)
        print(f"Makespan 结果: {makespan}")

    except Exception as e:
        print(f"程序执行过程中出错: {e}")
        return
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="计算 makespan 并生成日志")
    parser.add_argument("--algorithm", required=True, help="分组算法名称")
    parser.add_argument("--latency_file", required=True, help="时延矩阵文件路径")
    parser.add_argument("--bandwidth_file", required=True, help="带宽文件路径")
    parser.add_argument("--conflict_file", required=True, help="冲突率矩阵文件路径")
    parser.add_argument("--num_messages_file", required=True, help="每个节点的消息个数文件路径")
    parser.add_argument("--log_dir", required=True, help="日志文件保存目录")
    parser.add_argument("--output_dir", required=True, help="分组结果保存目录")

    args = parser.parse_args()

    # 调用 main 函数
    main(
        args.latency_file,
        args.bandwidth_file,
        args.conflict_file,
        args.num_messages_file,
        args.algorithm,
        args.log_dir,
        args.output_dir
    )