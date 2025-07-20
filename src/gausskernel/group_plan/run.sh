#!/bin/bash

# use to run the get_makespan.py  
# 设置起始值和最大值
start=100
end=200
step=100

# 定义分组算法变量
algorithm="random_group"

# 循环调用 get_makespan.py
for ((i=$start; i<=$end; i+=$step)); do
  echo "运行 get_makespan.py 参数: $i"
  
  # 动态创建 log_dir 子目录，基于分组算法名称 用于存放输出
  # log_dir="/Users/duling/Desktop/code/Geo_All2All/output/total_result/conflict/0.5/${algorithm}_conflict_0.5_60"
  # log_dir="/Users/duling/Desktop/code/Geo_All2All/output-1/total_result/conflict-0.5/band-50/${algorithm}/"

  log_dir="/Users/duling/Desktop/code/Geo_All2All/output-1/draft/group/${algorithm}/"
  # 确保目录存在
  mkdir -p $log_dir

  # 调用 get_makespan.py 脚本
  # output_dir 用于存放算出的分组矩阵，供参考
  python3 get_makespan.py \
    --algorithm $algorithm \
    --latency_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/1_latency/matrix_${i}.json \
    --bandwidth_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/bandwidth/bandwidth_${i}.json \
    --conflict_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/conflict_rate/conflict_${i}.json \
    --num_messages_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/num_message/num_message_${i}.json \
    --log_dir $log_dir \
    --output_dir /Users/duling/Desktop/code/Geo_All2All/output-1/draft/total/${algorithm}/
    # --output_dir /Users/duling/Desktop/code/Geo_All2All/output-1/group_result/conflict-0.5/band-50/${algorithm}/
done