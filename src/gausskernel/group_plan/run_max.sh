#!/bin/bash

# 设置起始值、最大值和步长
start=100
end=33300
step=100

# 循环调用 get_makespan_no_group_just_max.py
# 这里只有一种算法 需要在 log_dir 手动修改输出地址
for ((i=$start; i<=$end; i+=$step)); do
  echo "运行 get_makespan_no_group_just_max.py 参数: $i"

  python3 get_makespan_no_group_just_max.py \
    --latency_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/1_latency/matrix_${i}.json \
    --bandwidth_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/bandwidth/bandwidth_${i}.json \
    --conflict_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/conflict_rate_0.3/conflict_${i}.json \
    --num_messages_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/num_message_200/num_message_${i}.json \
    --group_dir /Users/duling/Desktop/code/Geo_All2All/output/group_result/no_group_source \
    --log_dir /Users/duling/Desktop/code/Geo_All2All/output/total_result/conflict/0.3/no_group_conflict_200
done