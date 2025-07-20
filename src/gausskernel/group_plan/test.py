import subprocess

def run_makespan():
    # 指定 get_makespan.py 的绝对路径
    get_makespan_script = "/Users/duling/Desktop/code/Geo_All2All/src/get_makespan.py"

    # 定义参数
    algorithm = "shortest"  # 你可以根据需要调整分组算法名称
    latency_file = "/Users/duling/Desktop/code/Geo_All2All/dataset/reallset/latency/1/matrix_0.json"
    bandwidth_file = "/Users/duling/Desktop/code/Geo_All2All/dataset/reallset/bandwidth/bandwidth_0.json"
    conflict_file = "/Users/duling/Desktop/code/Geo_All2All/dataset/reallset/conflict_rate/conflict_0.json"
    num_messages_file = "/Users/duling/Desktop/code/Geo_All2All/dataset/reallset/num_message/num_message_0.json"
    output_dir = "/Users/duling/Desktop/code/Geo_All2All/output/makespan_result"

    # 使用 subprocess 调用 get_makespan.py 并传递参数
    try:
        result = subprocess.run(
            [
                "python3", get_makespan_script, 
                "--algorithm", algorithm, 
                "--latency_file", latency_file,
                "--bandwidth_file", bandwidth_file,
                "--conflict_file", conflict_file,
                "--num_messages_file", num_messages_file,
                "--output_dir", output_dir
            ],
            capture_output=True, text=True
        )

        # 打印输出，用于调试
        print(f"get_makespan.py 标准输出: {result.stdout}")
        print(f"get_makespan.py 标准错误: {result.stderr}")

        if result.returncode != 0:
            raise RuntimeError(f"get_makespan.py 执行失败，返回代码: {result.returncode}")

    except subprocess.CalledProcessError as e:
        print(f"调用 get_makespan.py 时出错: {e}")
        return None

if __name__ == "__main__":
    run_makespan()