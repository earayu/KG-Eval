### **KG-Eval：大语言模型知识图谱构建能力评估框架**

> 🌍 **English Documentation**: [FRAMEWORK_DESIGN.md](FRAMEWORK_DESIGN.md) | [README.md](README.md)

#### **1. 引言**

**KG-Eval** (Knowledge Graph Evaluation) 是一个旨在全面评估大语言模型（LLM）从非结构化文本中构建知识图谱（KG）能力的综合性框架。传统的评估方法，如仅统计节点和边的数量，远不足以衡量所生成知识图谱的质量、准确性及结构完整性。KG-Eval 提出一个多维度、分层次的评估体系，以提供一个整体性、深度的测评方案。

本框架的设计独立于底层的数据库或具体实现技术。它操作于一组抽象的数据对象之上，这些对象由其核心属性定义，包括：`实体`、`关系`和`源文本`。

#### **2. 核心数据对象**

KG-Eval 的评估流程需要以下概念性的数据对象作为输入。

*   **实体 (Entity) 对象**：代表知识图谱中的一个节点。
    *   `entity_name` (字符串, 必需): 实体的**唯一、规范化、人类可读的名称**（例如：“曹操”）。此名称在知识图谱中作为实体的主键和唯一标识符。
    *   `entity_type` (字符串, 可选): 实体的类别（例如：“人物”, “地点”）。
    *   `description` (字符串, 可选): 对该实体的文本描述。

*   **关系 (Relationship) 对象**：代表两个实体之间的一种有向边。
    *   `source_entity_name` (字符串, 必需): 源实体的 `entity_name`。
    *   `target_entity_name` (字符串, 必需): 目标实体的 `entity_name`。
    *   `description` (字符串, 必需): 对该关系的文本描述（例如：“在赤壁之战中击败”）。
    *   `keywords` (字符串列表, 可选): 概括关系类型的关键词或标签列表。
    *   `weight` (浮点数, 可选): 代表关系置信度或重要性的数值。

*   **源文本 (Source Text) 对象**：代表从中提取知识的原始文本片段。
    *   `content` (字符串, 必需): 文本块的原始内容。
    *   `linked_entity_names` (字符串列表, 必需): 从此文本块中提取出的 `entity_name` 列表。
    *   `linked_edges` (元组列表, 必需): 从此文本块中提取出的关系的列表，每条关系由 `(源实体名称, 目标实体名称)` 的元组（Tuple）表示，用于建立文本与图谱结构间的关联。

#### **3. 评估维度与指标**

KG-Eval 通过四个基本维度对模型性能进行评估。

##### **维度一：生成规模与丰富度 (Generative Scale & Richness)**

*   **目标**: 衡量模型所抽取信息的广度与深度。
*   **指标**:
    1.  **实体/关系总数 (Entity/Relationship Count)**: 知识图谱的整体规模。
    2.  **属性填充率 (Property Fill Rate)**: `实体`和`关系`对象中可选属性（如`entity_type`, `description`, `keywords`）被成功填充的比例。**填充率越高，图谱的元数据越丰富。**
    3.  **关系多样性 (Relational Diversity)**: 提取出的关系类型的总数。此项通过对 `Relationship.keywords` 字段进行聚类或取唯一值来近似计算。**种类越多，表明模型对复杂关系的辨识能力越强。**

##### **维度二：结构与拓扑完整性 (Structural & Topological Integrity)**

*   **目标**: 运用图论原理，分析图谱的健康度、连通性与结构特性。
*   **指标**:
    1.  **图密度 (Graph Density)**: 定义为 `关系总数 / 实体总数`，衡量图谱的整体连接紧密程度。
    2.  **连通性分析 (Connectedness)**:
        *   **最大连通分量占比 (LCC Ratio)**: 属于最大连通分量（Largest Connected Component）的实体占总实体数的比例。理想值应接近1.0，代表一个单一、内聚的知识网络。
        *   **孤立实体占比 (Singleton Ratio)**: 没有任何连接关系的实体占总实体数的比例。**此值越低越好。**
    3.  **中心性分布 (Centrality Distribution)**:
        *   **算法**: PageRank 或度中心性（Degree Centrality）。
        *   **评估**: 考察实体重要性（中心性得分）的分布是否符合领域常识。针对特定主题（如《三国演义》），其核心角色（如“曹操”、“刘备”）应具有最高的中心性得分。**此项用于验证图谱结构是否准确反映了知识的重要性层次。**

##### **维度三：语义质量与忠实度 (Semantic Quality & Faithfulness)**

*   **目标**: 评估知识的“含金量”，聚焦于其准确性、一致性与相关性。
*   **指标**:
    1.  **实体规范化得分 (Entity Normalization Score)**:
        *   **原理**: 由于 `entity_name` 是唯一标识符，模型能否将不同文本称谓（如“诸葛亮”、“孔明”、“卧龙先生”）正确地**归一化**到单一的、规范的 `entity_name`（“诸葛亮”）是衡量其智能水平的关键。该指标旨在量化这种“实体碎片化”的程度。
        *   **算法**:
            1.  通过字符串相似度算法（如 Levenshtein 距离）或预定义的别名词典，找出数据集中可能指向同一现实世界对象的、名称不同的实体对，称之为“别名对”。
            2.  得分与别名对的数量成反比：`得分 = 1 - (识别出的别名对数量 / 实体总数)`。
        *   **解读**: **得分越高，代表模型实体规范化的能力越强，图谱越“干净”、质量越高。**
    2.  **事实精确率（忠实度）(Factual Precision)**:
        *   **算法**: 此指标需引入外部的“裁判”LLM。
            1.  随机抽取 N 个 `关系` 对象。
            2.  对每个`关系`，追溯其对应的`源文本.content`。
            3.  将`源文本内容`与该`关系`的语义三元组（`源实体名称`, `关系描述`, `目标实体名称`）同时呈现给“裁判”LLM。
            4.  由“裁判”将关系判定为“正确”、“部分正确”或“错误/幻觉”。
        *   **解读**: 衡量图谱对原文的忠实程度及抗幻觉能力。`精确率 = (正确数 + 0.5 * 部分正确数) / N`。
    3.  **上下文相关性 (Contextual Relevance)**:
        *   **算法**: 此指标同样需要“裁判”LLM。
            1.  随机抽取 N 个`实体`或`关系`，并追溯其`源文本.content`。
            2.  向“裁判”LLM提问：“被抽取的知识点是源文本的核心事实，还是一个边缘、琐碎的信息？”
        *   **解读**: 此指标超越了简单的正确性判断，旨在评估模型是否能识别并优先提取重要信息，避免图谱被大量无关紧要的细节所稀释。

##### **维度四：端到端转化效率 (End-to-End Efficiency)**

*   **目标**: 衡量模型将非结构化文本转化为结构化知识的效率。
*   **指标**:
    1.  **单位文本知识密度 (Knowledge Density per Chunk)**:
        *   **计算**: `(实体总数 + 关系总数) / 源文本总数`。
        *   **解读**: 平均每个单位的源文本能产出多少结构化的知识。

#### **4. 最终评估与报告**

最终评估报告将综合所有四个维度的指标，形成一份全面的分析。

*   **评分**: 将每个指标的原始值归一化到统一的尺度（例如0到10分）。
*   **可视化**: 强烈推荐使用**雷达图**，以直观地比较不同LLM在所有关键维度上的表现。雷达图的轴可设置为：**规模性、丰富度、连通性、忠实度、规范化能力、相关性**。
*   **综合得分**: 通过对各维度指标进行加权平均，可以得出一个总体的 **KG-Eval 分数**，用于模型的量化排名。权重可根据知识图谱的具体应用场景进行调整（例如，对于高风险的医疗知识图谱，“事实精确率”和“实体规范化得分”的权重应设为最高）。

**KG-Eval** 框架提供了一套结构化、多维度、可扩展的方法论，能够对任何LLM在知识图谱构建任务上的能力进行深入且有意义的评估。