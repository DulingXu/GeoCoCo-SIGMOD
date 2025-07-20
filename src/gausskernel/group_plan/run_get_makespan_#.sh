#!/bin/bash

# 调用 get_makespan.py 并传递参数
python3 get_makespan.py \
  --algorithm random_group \
  --latency_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/latency/1/matrix_200.json \
  --bandwidth_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/bandwidth/bandwidth_200.json \
  --conflict_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/conflict_rate/conflict_200.json \
  --num_messages_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/num_message/num_message_200.json \
  --log_dir /Users/duling/Desktop/code/Geo_All2All/output/total_result/ \
  --output_dir  /Users/duling/Desktop/code/Geo_All2All/output/group_result/random_group


# 调用 get_makespan_best_group.py 并传递参数
python3 get_makespan_best_group.py \
  --latency_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/latency/1/matrix_0.json \
  --bandwidth_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/bandwidth/bandwidth_0.json \
  --conflict_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/conflict_rate/conflict_0.json \
  --num_messages_file /Users/duling/Desktop/code/Geo_All2All/dataset/reallset/num_message/num_message_0.json \
  --group_dir /Users/duling/Desktop/code/Geo_All2All/output/group_result/best_group_detection_source \
  --log_dir /Users/duling/Desktop/code/Geo_All2All/output/get_bset_group_logs