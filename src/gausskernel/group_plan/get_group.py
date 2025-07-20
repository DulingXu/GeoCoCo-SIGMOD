import sys
import os
import subprocess
import json

# 

def run_grouping_algorithm(algorithm, latency_matrix_file, output_path):
    """
    根据传入的算法名称，调用对应的分组算法文件，并传递时延矩阵文件路径和输出路径
    :param algorithm: 分组算法的名称 (例如 "shortest")
    :param latency_matrix_file: 时延矩阵文件路径
    :param output_path: 分组结果保存路径
    :return: 分组结果列表
    """
    try:
        if output_path is None:
            output_path = f"/Users/duling/Desktop/code/Geo_All2All/output/group_result/{algorithm_name}/{algorithm_name}_{matrix_name}_group.json"
        else:
        # 检查 output_path 是否是目录
            if os.path.isdir(output_path):
            # 如果是目录，自动在目录中创建文件
                matrix_name = os.path.splitext(os.path.basename(latency_matrix_file))[0]
                output_path = os.path.join(output_path, f"{algorithm}_{matrix_name}_group.json")
        # 调用分组算法并传递时延矩阵文件路径和输出路径
        result = subprocess.run(
            ["python3", f"{algorithm}.py", latency_matrix_file, output_path],
            capture_output=True, text=True, check=True
        )

        # 打印算法输出，供调试使用
        print(f"算法输出: {result.stdout}")

        # 从文件读取分组结果
        with open(output_path, 'r') as f:
            group_result = json.load(f)

        print(f"解析到的分组结果: {group_result}")  # 输出解析后的分组结果
        return group_result

    except subprocess.CalledProcessError as e:
        print(f"调用算法 {algorithm} 时出错: {e}")
        return None
    except Exception as e:
        print(f"读取分组结果时出错: {e}")
        return None

def save_group_result(group_result, algorithm_name, latency_matrix_file, output_path=None):
    """
    将分组结果保存到指定的路径，文件名格式为：algorithm_时延编号_group.json
    """
    # 提取时延矩阵文件编号
    matrix_name = os.path.splitext(os.path.basename(latency_matrix_file))[0]

    # 如果没有提供输出路径，使用默认路径
    if output_path is None:
        output_path = f"/Users/duling/Desktop/code/Geo_All2All/output/group_result/{algorithm_name}/{algorithm_name}_{matrix_name}_group.json"
    else:
        # 检查 output_path 是否是目录
        if os.path.isdir(output_path):
            # 如果是目录，自动在目录中创建文件
            output_path = os.path.join(output_path, f"{algorithm_name}_{matrix_name}_group.json")

    # 保存分组结果到文件
    try:
        with open(output_path, 'w') as f:
            json.dump(group_result, f, indent=4)
        print(f"分组结果已保存到: {output_path}")
    except Exception as e:
        print(f"保存分组结果时出错: {e}")

def main(algorithm_name, latency_matrix_file, output_path=None):
    # 如果没有提供输出路径，使用默认路径
    if output_path is None:
        matrix_name = os.path.splitext(os.path.basename(latency_matrix_file))[0]
        output_path = f"/Users/duling/Desktop/code/Geo_All2All/output/group_result/{algorithm_name}/{algorithm_name}_{matrix_name}_group.json"

    # 调用对应的分组算法并获取结果
    group_result = run_grouping_algorithm(algorithm_name, latency_matrix_file, output_path)
    if group_result is None:
        print("分组算法运行失败，退出程序。")
        return
    
# ------------------------------------------------------------------------------------------

def save_group_result(group_result, algorithm_name, latency_matrix_file, output_path=None):
    """
    将分组结果保存到指定的路径，文件名格式为：algorithm_时延编号_group.json
    :param group_result: 分组的结果，列表形式
    :param algorithm_name: 分组算法的名称
    :param latency_matrix_file: 时延矩阵文件路径，用于提取文件编号
    :param output_path: 输出目录，如果未提供则使用默认路径
    """
    # 提取时延矩阵文件编号
    matrix_name = os.path.splitext(os.path.basename(latency_matrix_file))[0]

    # 如果没有提供输出路径，使用默认路径
    if output_path is None:
        output_dir = "/Users/duling/Desktop/code/Geo_All2All/output/group_result/shortest/"
        os.makedirs(output_dir, exist_ok=True)  # 创建目录
        output_path = os.path.join(output_dir, f"{algorithm_name}_{matrix_name}_group.json")
    else:
        # 检查 output_path 是否是目录
        if os.path.isdir(output_path):
            # 如果是目录，自动在目录中创建文件
            output_path = os.path.join(output_path, f"{algorithm_name}_{matrix_name}_group.json")

    # 保存分组结果到文件
    try:
        with open(output_path, 'w') as f:
            json.dump(group_result, f, indent=4)
        print(f"分组结果已保存到: {output_path}")
    except Exception as e:
        print(f"保存分组结果时出错: {e}")


    # # 保存分组结果
    # save_group_result(group_result, algorithm_name, latency_matrix_file, output_path)

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        algorithm_name = sys.argv[1]  # 传递的算法名称
        latency_matrix_file = sys.argv[2]  # 传递的时延矩阵文件路径
        output_path = sys.argv[3] if len(sys.argv) > 3 else None  # 可选的输出路径
    else:
        print("用法: python get_group.py <algorithm_name> <latency_matrix_file> [output_path]")
        sys.exit(1)

    main(algorithm_name, latency_matrix_file, output_path)