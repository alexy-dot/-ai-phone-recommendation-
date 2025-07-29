# 智能手机推荐系统 v2.0

一个智能化的、多维参数对比与对话推荐系统，集成LLM、可视化、数据库等先进功能。

## 🚀 新功能特性

### ✨ 核心增强
- **LLM集成**: 集成Gemini API，提供更自然的对话体验和智能需求理解
- **可视化对比**: 生成雷达图、柱状图等多种可视化图表
- **数据库存储**: SQLite数据库，支持数据持久化和历史记录
- **API服务**: FastAPI提供RESTful API接口
- **增强对话**: 解决澄清循环问题，提供更智能的对话管理

### 🎯 智能推荐
- **多维参数分析**: 性能、拍照、续航、便携、价格、外观等6个维度
- **个性化权重**: 根据用户偏好动态调整各维度权重
- **智能匹配**: 加权欧氏距离和余弦相似度算法
- **实时更新**: 支持动态数据更新和实时推荐

### 📊 可视化功能
- **雷达图对比**: 直观显示多款手机在各维度的表现
- **柱状图分析**: 价格、性能、拍照等关键指标对比
- **特性对比表**: 详细的参数对比表格
- **推荐总结图**: 匹配度和价格对比分析

## 📁 项目结构

```
神策/
├── api/                    # API接口层
│   └── endpoints.py       # FastAPI接口
├── core/                  # 核心业务逻辑
│   ├── data_processor.py  # 数据处理和归一化
│   ├── demand_analyzer.py # 需求分析和解析
│   ├── recommendation_engine.py # 推荐引擎
│   └── dialogue_controller.py   # 对话管理
├── database/              # 数据层
│   ├── database.py        # 数据库管理
│   └── sample_data.py     # 示例数据
├── services/              # 服务层
│   └── llm_provider.py    # LLM服务提供者
├── utils/                 # 工具层
│   └── visualization.py   # 可视化工具
├── scrapers/              # 数据采集（待实现）
├── main.py               # 原版主程序
├── main_enhanced.py      # 增强版主程序
├── requirements.txt      # 依赖包
└── README.md            # 项目文档
```

## 🛠️ 安装和运行

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd 神策

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置LLM（可选）
```bash
# 设置Gemini API密钥
export GEMINI_API_KEY="your_api_key_here"
```

### 3. 运行方式

#### 方式一：增强版交互模式
```bash
python main_enhanced.py
```

#### 方式二：演示模式
```bash
python main_enhanced.py demo
```

#### 方式三：API服务
```bash
python api/endpoints.py
# 访问 http://localhost:8000/docs 查看API文档
```

#### 方式四：原版系统
```bash
python main.py
```

## 🎮 使用示例

### 交互模式
```
欢迎使用增强版智能手机推荐系统！

系统状态:
- LLM服务: 可用
- 数据库: 已连接
- 可视化: 已就绪
- 手机数据: 12 款
- 平均价格: ¥3999
- 平均评分: 4.2/5.0

您可以描述您的需求，比如：
- 预算3000-4000，拍照优先
- 想要轻薄便携的手机
- 需要性能强劲的游戏手机
- 续航持久的商务手机

输入 'chart' 生成可视化图表
输入 'stats' 查看系统统计
```

### API调用示例

#### 获取推荐
```bash
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "budget_min": 3000,
    "budget_max": 4000,
    "preferences": ["拍照"],
    "camera_weight": 0.5
  }'
```

#### 对话交互
```bash
curl -X POST "http://localhost:8000/dialogue" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "预算3000-4000，拍照优先"
  }'
```

## 🔧 核心组件

### 1. 需求分析器 (DemandAnalyzer)
- 自然语言解析
- 预算提取（支持"XXXX以下"等表达）
- 偏好识别和权重计算
- LLM增强的意图理解

### 2. 推荐引擎 (RecommendationEngine)
- 多维向量相似度计算
- 预算过滤
- 排序因子应用（销量、评分）
- 匹配原因生成

### 3. 对话管理器 (DialogueController)
- 多轮对话状态管理
- 智能澄清问题生成
- 上下文记忆
- LLM驱动的自然回复

### 4. 可视化工具 (PhoneVisualizer)
- 雷达图生成
- 柱状图对比
- 特性对比表
- 推荐总结图

### 5. 数据库管理器 (DatabaseManager)
- SQLite数据存储
- 会话历史记录
- 统计信息查询
- 数据持久化

## 📈 系统架构

```
用户输入 → LLM意图理解 → 需求解析 → 推荐引擎 → 结果排序 → 可视化生成
    ↓
对话管理 ← 澄清问题 ← 上下文记忆 ← 历史记录 ← 数据库存储
```

## 🎯 解决的问题

### 1. 澄清循环问题
- **问题**: 系统重复询问相同问题
- **解决**: 引入澄清标记和上下文记忆机制

### 2. 预算理解问题
- **问题**: 无法正确解析"10000以下"等表达
- **解决**: 增强正则表达式和LLM辅助理解

### 3. 对话自然度问题
- **问题**: 回复机械，缺乏个性化
- **解决**: LLM集成，生成自然语言解释

### 4. 可视化缺失问题
- **问题**: 缺乏直观的参数对比
- **解决**: 多种图表类型，支持自定义对比

## 🔮 未来规划

### 短期目标
- [ ] 实现数据采集爬虫
- [ ] 添加更多LLM模型支持
- [ ] 优化推荐算法
- [ ] 增加Web界面

### 长期目标
- [ ] 扩展到电脑推荐
- [ ] 集成更多电商平台
- [ ] 实现个性化学习
- [ ] 移动端应用

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件
- 参与讨论

---

**版本**: v2.0.0  
**最后更新**: 2024年12月  
**状态**: 开发中 🚀