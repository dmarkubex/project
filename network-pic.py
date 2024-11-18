import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 设置中文字体
font = FontProperties(fname='/System/Library/Fonts/STHeiti Light.ttc')  # macOS 系统字体路径

# 创建一个有向图
G = nx.DiGraph()

# 添加节点
customers = ['客户A', '客户B', '客户C']
marketers = ['营销人员1', '营销人员2']
projects = ['项目X', '项目Y']

G.add_nodes_from(customers, type='customer')
G.add_nodes_from(marketers, type='marketer')
G.add_nodes_from(projects, type='project')

# 添加带权重的边
edges = [
    ('客户A', '营销人员1', 0.8),
    ('客户B', '营销人员1', 0.6),
    ('客户C', '营销人员2', 0.9),
    ('营销人员1', '项目X', 0.7),
    ('营销人员2', '项目Y', 0.5),
    ('客户A', '项目X', 0.4),
    ('客户B', '项目Y', 0.3),
]

for edge in edges:
    G.add_edge(edge[0], edge[1], weight=edge[2])

# 设置节点颜色和大小
node_colors = []
node_sizes = []
for node in G.nodes(data=True):
    if node[1]['type'] == 'customer':
        node_colors.append('blue')
        node_sizes.append(1000)  # 客户节点大小
    elif node[1]['type'] == 'marketer':
        node_colors.append('green')
        node_sizes.append(1500)  # 营销人员节点大小
    elif node[1]['type'] == 'project':
        node_colors.append('red')
        node_sizes.append(2000)  # 项目节点大小

# 绘制图形
pos = nx.spring_layout(G)  # 使用 spring 布局
plt.figure(figsize=(10, 8))

# 绘制节点
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)

# 绘制边
edges = nx.draw_networkx_edges(
    G, pos, arrowstyle='->', arrowsize=20, edge_color='gray', alpha=0.5,
    width=[G[u][v]['weight'] * 10 for u, v in G.edges()]  # 根据权重设置边的宽度
)

# 绘制节点标签
nx.draw_networkx_labels(G, pos, font_size=12, font_color='black', font_family=font.get_name())

# 绘制边标签（权重）
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, font_family=font.get_name())

# 显示图形
plt.title('客户、营销人员和项目的关系图', fontproperties=font)
plt.axis('off')
plt.show()