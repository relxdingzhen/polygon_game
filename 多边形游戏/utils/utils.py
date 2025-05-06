# 示例：格式化历史记录
def format_step(step, step_num):
    content = f"步骤 {step_num}:\n"
    content += f"顶点数: {len(step['vertices'])}\n"
    if 'merge_info' in step and step['merge_info']:
        info = step['merge_info']
        content += "┌───────── 合并详情 ────────┐\n"
        content += f"│ 合并顶点: {info['indices'][0]+1}号({info['values'][0]}) 和 {info['indices'][1]+1}号({info['values'][1]})\n"
        content += f"│ 运算符: {info['operator']}\n"
        content += f"│ 结果值: {info['result']}\n"
        content += "└──────────────────────┘\n"
    else:
        content += "状态类型: 初始配置\n"
    content += f"当前顶点: {', '.join(map(str, step['vertices']))}\n"
    if len(step['operators']) > 0:
        content += f"剩余运算符: {' → '.join(step['operators'])}\n"
    content += "━" * 40 + "\n"
    return content
