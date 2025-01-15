# 从当前包的 Mango_random_nodes 模块导入节点相关的映射字典
from .Mango_random_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
import random

# 定义一个包含有趣的技术相关随机提示语的列表
tech_rambling = [
    "Zap zap zoom!", "Sproing-a-ling!", "Flux capacitor charged!", "Circuit party started!",
    "Electrons dancing!", "Voltage va-va-voom!", "Capacitor doing the cha-cha!", "Resistor raving!"
]

# 打印带颜色的欢迎信息，使用随机的技术提示语
print(f"\033[1;34m[Mango Suite]: 🥭🥭🥭 \033[96m\033[3m{random.choice(tech_rambling)}\033[0m 🥭🥭🥭")
# 打印已激活的节点数量信息
print(f"\033[1;34m[Mango Suite]:\033[0m Activated \033[96m{len(NODE_CLASS_MAPPINGS)}\033[0m file nodes.")

# 定义此包可以导出的名称列表
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# 定义web目录的路径常量
WEB_DIRECTORY = "./web"