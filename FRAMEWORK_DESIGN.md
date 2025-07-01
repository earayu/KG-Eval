## **KG-Eval: A Framework for Evaluating Large Language Models' Knowledge Graph Construction Capabilities**

> 🌍 **中文文档**: [FRAMEWORK_DESIGN-zh.md](FRAMEWORK_DESIGN-zh.md) | [README-zh.md](README-zh.md)

### **1. Introduction**

**KG-Eval** (Knowledge Graph Evaluation) is a comprehensive framework designed to thoroughly assess the ability of Large Language Models (LLMs) to construct knowledge graphs (KGs) from unstructured text. Traditional evaluation methods, such as merely counting nodes and edges, are far from sufficient to measure the quality, accuracy, and structural integrity of generated knowledge graphs. KG-Eval proposes a multi-dimensional, hierarchical evaluation system to provide a holistic and in-depth assessment solution.

This framework's design is independent of underlying databases or specific implementation technologies. It operates on a set of abstract data objects defined by their core properties, including: **`Entities`**, **`Relationships`**, and **`Source Texts`**.

---
### **2. Core Data Objects**

KG-Eval's evaluation process requires the following conceptual data objects as input.

* **Entity Object**: Represents a node in the knowledge graph.
    * `entity_name` (string, required): The **unique, canonical, human-readable name** of the entity (e.g., "Cao Cao"). This name serves as the primary key and unique identifier for the entity within the knowledge graph.
    * `entity_type` (string, optional): The category of the entity (e.g., "Person", "Location").
    * `description` (string, optional): A text description of the entity.

* **Relationship Object**: Represents a directed edge between two entities.
    * `source_entity_name` (string, required): The `entity_name` of the source entity.
    * `target_entity_name` (string, required): The `entity_name` of the target entity.
    * `description` (string, required): A text description of the relationship (e.g., "defeated in the Battle of Red Cliffs").
    * `keywords` (list of strings, optional): A list of keywords or tags summarizing the type of relationship.
    * `weight` (float, optional): A numerical value representing the confidence or importance of the relationship.

* **Source Text Object**: Represents the original text snippet from which knowledge is extracted.
    * `content` (string, required): The raw content of the text block.
    * `linked_entity_names` (list of strings, required): A list of `entity_name`s extracted from this text block.
    * `linked_edges` (list of tuples, required): A list of relationships extracted from this text block, where each relationship is represented by a tuple of `(source_entity_name, target_entity_name)`, used to establish the connection between the text and the graph structure.

---
### **3. Evaluation Dimensions and Metrics**

KG-Eval assesses model performance across four fundamental dimensions.

#### **Dimension One: Generative Scale & Richness**

* **Objective**: Measure the breadth and depth of information extracted by the model.
* **Metrics**:
    1.  **Entity/Relationship Count**: The overall size of the knowledge graph.
    2.  **Property Fill Rate**: The proportion of optional attributes (e.g., `entity_type`, `description`, `keywords`) in `Entity` and `Relationship` objects that are successfully populated. **A higher fill rate indicates richer metadata in the graph.**
    3.  **Relational Diversity**: The total number of distinct relationship types extracted. This is approximated by clustering or taking unique values from the `Relationship.keywords` field. **More diversity indicates a stronger ability of the model to identify complex relationships.**

#### **Dimension Two: Structural & Topological Integrity**

* **Objective**: Analyze the health, connectivity, and structural characteristics of the graph using graph theory principles.
* **Metrics**:
    1.  **Graph Density**: Defined as `Total Relationships / Total Entities`, measuring the overall interconnectedness of the graph.
    2.  **Connectedness Analysis**:
        * **Largest Connected Component (LCC) Ratio**: The proportion of entities belonging to the Largest Connected Component relative to the total number of entities. The ideal value should be close to 1.0, representing a single, cohesive knowledge network.
        * **Singleton Ratio**: The proportion of entities without any connections relative to the total number of entities. **A lower value is better.**
    3.  **Centrality Distribution**:
        * **Algorithm**: PageRank or Degree Centrality.
        * **Assessment**: Examine whether the distribution of entity importance (centrality scores) aligns with domain common sense. For specific topics (e.g., *Romance of the Three Kingdoms*), core characters (e.g., "Cao Cao", "Liu Bei") should have the highest centrality scores. **This metric validates whether the graph structure accurately reflects the hierarchy of knowledge importance.**

#### **Dimension Three: Semantic Quality & Faithfulness**

* **Objective**: Evaluate the "value" of the knowledge, focusing on its accuracy, consistency, and relevance.
* **Metrics**:
    1.  **Entity Normalization Score**:
        * **Principle**: Since `entity_name` is a unique identifier, the model's ability to correctly **normalize** different textual mentions (e.g., "Zhuge Liang", "Kongming", "Sleeping Dragon") to a single, canonical `entity_name` ("Zhuge Liang") is crucial for measuring its intelligence. This metric aims to quantify the degree of "entity fragmentation."
        * **Algorithm**:
            1.  Identify pairs of entities with different names that might refer to the same real-world object within the dataset, using string similarity algorithms (e.g., Levenshtein distance) or a predefined alias dictionary. These are called "alias pairs."
            2.  The score is inversely proportional to the number of identified alias pairs: `Score = 1 - (Number of Identified Alias Pairs / Total Entities)`.
        * **Interpretation**: **A higher score indicates stronger entity normalization capabilities by the model, resulting in a "cleaner," higher-quality graph.**
    2.  **Factual Precision (Faithfulness)**:
        * **Algorithm**: This metric requires an external "referee" LLM.
            1.  Randomly sample N `Relationship` objects.
            2.  For each `relationship`, trace back to its corresponding `source_text.content`.
            3.  Present both the `source text content` and the semantic triplet of the `relationship` (`source_entity_name`, `relationship_description`, `target_entity_name`) to the "referee" LLM.
            4.  The "referee" determines if the relationship is "correct," "partially correct," or "incorrect/hallucination."
        * **Interpretation**: Measures the graph's fidelity to the original text and its resistance to hallucination. `Precision = (Number of Correct + 0.5 * Number of Partially Correct) / N`.
    3.  **Contextual Relevance**:
        * **Algorithm**: This metric also requires a "referee" LLM.
            1.  Randomly sample N `Entity` or `Relationship` objects and trace back to their `source_text.content`.
            2.  Ask the "referee" LLM: "Is the sampled knowledge point a core fact from the source text, or a marginal, trivial piece of information?"
        * **Interpretation**: This metric goes beyond simple correctness to assess whether the model can identify and prioritize important information, preventing the graph from being diluted by excessive insignificant details.

#### **Dimension Four: End-to-End Efficiency**

* **Objective**: Measure the model's efficiency in transforming unstructured text into structured knowledge.
* **Metric**:
    1.  **Knowledge Density per Chunk**:
        * **Calculation**: `(Total Entities + Total Relationships) / Total Source Texts`.
        * **Interpretation**: How much structured knowledge can be produced from each unit of source text, on average.

---
### **4. Final Evaluation and Report**

The final evaluation report will synthesize metrics from all four dimensions to form a comprehensive analysis.

* **Scoring**: Normalize the raw values of each metric to a uniform scale (e.g., 0 to 10 points).
* **Visualization**: **Radar charts** are highly recommended for visually comparing the performance of different LLMs across all key dimensions. The axes of the radar chart can be set as: **Scalability, Richness, Connectivity, Faithfulness, Normalization Capability, Relevance**.
* **Overall Score**: By calculating a weighted average of the metrics from each dimension, a total **KG-Eval Score** can be derived for quantitative ranking of models. Weights can be adjusted based on the specific application scenario of the knowledge graph (e.g., for high-risk medical knowledge graphs, "Factual Precision" and "Entity Normalization Score" should be given the highest weights).

The **KG-Eval** framework provides a structured, multi-dimensional, and extensible methodology for conducting deep and meaningful evaluations of any LLM's capabilities in knowledge graph construction tasks.