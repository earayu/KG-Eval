 # KG-Eval 🧠✨

> 评估大语言模型知识图谱构建能力的综合框架

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![uv](https://img.shields.io/badge/packaged%20with-uv-blueviolet)](https://github.com/astral-sh/uv)

## 🎯 什么是 KG-Eval？

KG-Eval 是一个专门用于评估 **大语言模型构建知识图谱能力** 的多维度评估框架。

**传统评估方法的问题**：仅看节点/边的数量，忽略质量和结构
**KG-Eval 的解决方案**：四个维度全面评估，类似 RAGAs 但专注于知识图谱

> 📖 **详细技术设计和方法论**，请参考 [框架设计文档](FRAMEWORK_DESIGN-zh.md)  
> 🌍 **English Documentation**: [README.md](README.md)

### 四大评估维度

| 维度 | 评估内容 | 核心指标 |
|------|----------|----------|
| 🔢 **规模丰富度** | 信息提取的广度和深度 | 实体数量、关系多样性、属性完整度 |
| 🕸️ **结构完整性** | 图的连通性和拓扑健康度 | 图密度、连通性、中心性分布 |
| ✅ **语义质量** | 准确性、一致性和相关性 | 实体规范化、事实精确度、上下文相关性 |
| ⚡ **转换效率** | 文本到知识的转换效率 | 知识密度、源文本覆盖率 |

---

## 🚀 5分钟快速体验

### 1. 安装

```bash
# 推荐使用 uv
uv add kg-eval

# 或使用 pip
pip install kg-eval
```

### 2. 配置环境（可选）

```bash
# 复制环境配置模板
cp env.template .env

# 编辑 .env 文件，填入你的 API Key（如需高级语义评估）
# 没有 API Key 也可以使用基础评估功能
```

### 3. 运行 Demo

```bash
# 运行示例脚本
python examples/sample_usage.py

# 查看生成的报告
open examples/sample_report.html
```

**Demo 生成的文件**：
- `sample_kg.json` - 示例知识图谱
- `sample_report.html` - 可视化报告  
- `sample_report.json` - 详细评估数据

### 4. 命令行快速评估

```bash
# 评估你的知识图谱
kg-eval evaluate your_kg.json --output report.html

# 生成雷达图可视化
kg-eval radar your_kg.json --output chart.html

# 比较多个知识图谱
kg-eval compare kg1.json kg2.json --output comparison.html
```

---

## 💡 进阶使用

### 知识图谱数据格式

KG-Eval 使用标准 JSON 格式：

```json
{
  "entities": [
    {
      "entity_name": "爱因斯坦",
      "entity_type": "人物",
      "description": "著名物理学家"
    }
  ],
  "relationships": [
    {
      "source_entity_name": "爱因斯坦",
      "target_entity_name": "相对论",
      "description": "提出了",
      "keywords": ["科学", "物理"],
      "weight": 0.9
    }
  ],
  "source_texts": [
    {
      "content": "爱因斯坦提出了相对论。",
      "linked_entity_names": ["爱因斯坦", "相对论"],
      "linked_edges": [["爱因斯坦", "相对论"]]
    }
  ]
}
```

### Python API 使用

```python
from kg_eval import Entity, Relationship, SourceText, KnowledgeGraph, KGEvaluator

# 创建知识图谱
kg = KnowledgeGraph(entities=entities, relationships=relationships, source_texts=source_texts)

# 评估知识图谱
evaluator = KGEvaluator()
results = evaluator.evaluate(kg)

# 获取评估摘要
summary = evaluator.get_evaluation_summary(results)
print(summary["recommendations"])
```

### 配置 LLM 评估器（高级语义评估）

```python
from kg_eval import OpenAIReferee, AnthropicReferee

# OpenAI 配置
referee = OpenAIReferee(
    api_key="your-key",
    model="gpt-4o-mini",
    base_url="https://api.openai.com/v1"  # 可选：自定义 API 地址
)

# Anthropic 配置
referee = AnthropicReferee(
    api_key="your-key", 
    model="claude-3-sonnet-20240229"
)

# 使用 LLM 评估器
evaluator = KGEvaluator(llm_referee=referee)
```

### 环境变量配置

编辑 `.env` 文件：

```bash
# OpenAI 配置（二选一）
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选
OPENAI_MODEL=gpt-4o-mini

# Anthropic 配置（二选一）
ANTHROPIC_API_KEY=your_anthropic_key
ANTHROPIC_BASE_URL=https://api.anthropic.com  # 可选
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### 高级 CLI 选项

```bash
# 使用自定义 OpenAI 配置
kg-eval evaluate my_kg.json \
  --openai-model gpt-3.5-turbo \
  --openai-base-url https://your-proxy.com/v1 \
  --output report.json

# 使用 Anthropic
kg-eval evaluate my_kg.json \
  --anthropic-key "your-key" \
  --anthropic-model claude-3-sonnet-20240229 \
  --output report.json

# 仅评估特定维度
kg-eval evaluate my_kg.json \
  --dimensions scale_richness structural_integrity \
  --output basic_report.json
```

---

## 📊 评估结果可视化

### 生成的报告类型

- **HTML 报告**：交互式详细分析
- **JSON 报告**：结构化数据，便于进一步分析
- **雷达图**：多维度性能概览
- **比较表**：多个知识图谱并排比较

### 评估指标详解

**规模丰富度**：
- 实体数量、关系数量
- 属性填充率
- 关系类型多样性

**结构完整性**：
- 图密度 (使用 NetworkX 分析)
- 连通分量分析
- 中心性分布

**语义质量** (需要 LLM)：
- 实体规范化得分
- 事实精确度
- 上下文相关性

**转换效率**：
- 每个文本块的知识密度
- 源文本覆盖率

---

## 📚 深度文档

### 完整技术文档

- **[框架设计文档](FRAMEWORK_DESIGN-zh.md)** - 详细的技术规范和设计思路
- **[示例教程](examples/README.md)** - 完整的使用示例和教程
- **[API 参考](docs/api.md)** - 完整的 API 文档

### 实际应用场景

- **LLM 知识提取评估**：评估不同 LLM 的知识图谱构建能力
- **提示工程优化**：通过多维度评估优化知识提取提示
- **知识图谱质量监控**：在生产环境中监控知识图谱质量
- **学术研究**：为知识图谱构建研究提供标准化评估工具

### 支持的自定义配置

- **API 代理**：支持通过代理访问 OpenAI/Anthropic
- **Azure OpenAI**：支持 Azure OpenAI 部署
- **自托管模型**：支持 LocalAI、Ollama 等本地部署
- **企业 API 网关**：支持企业级 API 管理

---

## 🛠️ 开发者指南

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/earayu/KG-Eval.git
cd KG-Eval

# 安装开发依赖
uv sync --dev

# 运行测试
pytest

# 代码格式化
black src/
isort src/
```

### 贡献指南

我们欢迎贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详情。

---

## 🤝 社区与支持

- **GitHub Issues**: [问题反馈](https://github.com/earayu/KG-Eval/issues)
- **GitHub Discussions**: [讨论区](https://github.com/earayu/KG-Eval/discussions)
- **邮件联系**: earayu@163.com

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

- 灵感来源于 RAGAs 等评估框架
- 使用现代 Python 工具构建 (uv, pydantic, networkx, plotly)
- 为 LLM 驱动的知识提取领域而设计

---

*KG-Eval: 让知识图谱评估像知识本身一样严谨。* 🧠✨