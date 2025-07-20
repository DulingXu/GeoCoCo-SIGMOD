#!/bin/bash

# 设置起始值、最大值和步长
start=100
end=33300
step=100

# 循环调用 get_makespan_best_group.py
for ((i=$start; i<=$end; i+=$step)); do
  echo "运行 get_makespan_best_group.py 参数: $i"

  # 动态创建 log_dir 子目录
  # 存放单次调用 get_makespan_best_group.py 的日志文件
  log_dir="/Users/duling/Desktop/code/Geo_All2All/output/total_result/best_group_detection"

  # 确保日志目录存在
  mkdir -p $log_dir

  # 分组方案的目录
  # 分组方案的目录下应为直接的目录分组 .json 文件。在这里是需要遍历的所有的分组情况
  group_dir="/Users/duling/Desktop/code/Geo_All2All/output/group_result/best_group_detection_source"

  # 调用 get_makespan_best_group.py 脚本
  # fanal_group_selection_output_dir  存遍历之后最终被选择的时延矩阵的路径
  # log_dir 输出日志文件

  python3 get_makespan_best_group.py \
    --latency_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/latency/1/matrix_${i}.json \
    --bandwidth_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/bandwidth/bandwidth_${i}.json \
    --conflict_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/conflict_rate/conflict_${i}.json \
    --num_messages_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/num_message/num_message_${i}.json \
    --group_dir $group_dir \
    --log_dir $log_dir \
    --final_group_selection_output_dir  /Users/duling/Desktop/code/Geo_All2All/output/group_result/best_group_detection
    
done