import os
import glob
from typing import List, Dict, Any


class KnowledgeBase:
    """知识库管理器 - 使用延迟加载避免启动时的依赖问题"""

    # 中文嵌入模型 - 专为中文语义优化
    DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"

    def __init__(self, embedding_model: str = None):
        """
        初始化知识库

        Args:
            embedding_model: 嵌入模型名称，默认使用中文模型 BAAI/bge-small-zh-v1.5
        """
        self.documents: List[Dict[str, Any]] = []
        self.embeddings = None
        self.model = None
        self._model_name = embedding_model or self.DEFAULT_EMBEDDING_MODEL
        self._model_loaded = False

        # 设置默认知识库路径
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.knowledge_dir = os.path.join(self.base_path, "data", "knowledge")

        # 确保目录存在
        os.makedirs(self.knowledge_dir, exist_ok=True)

        # 初始化时自动加载知识文件（但不加载模型）
        self.auto_load_knowledge()

    def _load_model(self):
        """延迟加载嵌入模型"""
        if self._model_loaded:
            return True

        try:
            print(f"正在加载嵌入模型: {self._model_name}")
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self._model_name)
            print(f"嵌入模型加载成功: {self._model_name}")
            self._model_loaded = True
            return True
        except Exception as e:
            print(f"加载模型 {self._model_name} 失败: {e}")
            print("尝试使用备用模型...")
            try:
                from sentence_transformers import SentenceTransformer
                fallback_model = "paraphrase-multilingual-MiniLM-L12-v2"
                self.model = SentenceTransformer(fallback_model)
                print(f"已加载备用模型: {fallback_model}")
                self._model_loaded = True
                return True
            except Exception as e2:
                print(f"备用模型加载也失败: {e2}")
                print("知识库将使用基础关键词匹配模式")
                return False

    def auto_load_knowledge(self):
        """自动加载知识文件"""
        # 支持 .md 和 .txt 文件
        file_patterns = ["*.md", "*.txt"]

        files_found = False
        for pattern in file_patterns:
            file_paths = glob.glob(os.path.join(self.knowledge_dir, pattern))
            for file_path in file_paths:
                self._load_file(file_path)
                files_found = True

        if not files_found:
            # 如果目录为空，创建一些基础知识文件
            self._create_default_knowledge()

    def _load_file(self, file_path: str):
        """加载单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 按章节分割（以##或更大的标题为分割点）
            sections = self._split_into_sections(content)

            for i, section in enumerate(sections):
                if len(section.strip()) > 50:  # 只保留有意义的文本块
                    self.documents.append({
                        "id": f"{os.path.basename(file_path)}-{i}",
                        "content": section.strip(),
                        "source": file_path,
                        "category": self._get_category_from_filename(file_path)
                    })
        except Exception as e:
            print(f"加载文件失败 {file_path}: {e}")

    def _create_default_knowledge(self):
        """创建默认知识文件"""
        default_files = {
            "procurement_guide.md": """# 采购流程指南

## 需求确认
采购前需要明确：
- 用途和应用场景
- 功能边界和功能模块
- 关键性能指标（KPI）
- 预算范围
- 交付时间要求

## 供应商选择
选择供应商时应考虑：
- 供应商资质和信誉
- 产品或服务的技术参数
- 历史业绩和客户评价
- 售后服务能力
- 价格合理性""",

            "faq.md": """# 采购常见问题

### Q: 采购需求文档应包含哪些内容？
A: 应包含用途说明、功能边界、关键性能指标、技术要求、预算范围、交付期限等六大要素。

### Q: 如何判断价格是否合理？
A: 可查询历史价格数据、对比同类产品价格、分析配置差异，建议使用系统价格参考功能。

### Q: 合同中需要特别注意哪些条款？
A: 需要特别注意免责条款、无限期条款、单方面变更条款、模糊表述等风险条款。""",

            "server_guide.md": """# 服务器选型指南

## 机架式 vs 塔式
- **机架式**：适合机房，密度高，易管理
- **塔式**：适合办公室，噪音低，扩展好

## 关键配置
- CPU：Intel Xeon Silver/Gold/Platinum
- 内存：64GB-512GB根据需求
- 存储：SSD系统盘，HDD数据盘，NVMe高速存储

## 推荐品牌
Dell PowerEdge、HP ProLiant、联想 ThinkSystem、华为 FusionServer"""
        }

        for filename, content in default_files.items():
            file_path = os.path.join(self.knowledge_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self._load_file(file_path)
            print(f"创建默认知识文件: {filename}")

    def _get_category_from_filename(self, filename: str) -> str:
        """从文件名获取分类"""
        if 'guide' in filename:
            return '指南'
        elif 'faq' in filename:
            return 'FAQ'
        elif 'server' in filename or 'it' in filename:
            return 'IT设备'
        else:
            return '其他'

    def _generate_embeddings(self):
        """为所有文档生成嵌入向量"""
        if not self.documents:
            return

        if not self._load_model():
            return

        try:
            texts = [doc["content"] for doc in self.documents]
            self.embeddings = self.model.encode(texts, show_progress_bar=False)
        except Exception as e:
            print(f"生成嵌入向量失败: {e}")

    def _split_into_sections(self, content: str) -> List[str]:
        """将内容分割成多个部分"""
        import re

        # 匹配 Markdown 标题
        sections = re.split(r'\n(?=##+\s)', content)

        if len(sections) <= 1:
            # 如果没有标题，按段落分割
            paragraphs = content.split('\n\n')
            # 合并小段
            result = []
            current_chunk = ""
            for para in paragraphs:
                if len(current_chunk) + len(para) < 1000:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        result.append(current_chunk)
                    current_chunk = para + "\n\n"
            if current_chunk:
                result.append(current_chunk)
            return result

        return sections

    def query(self, query_text: str, top_k: int = 3) -> str:
        """
        查询知识库

        Args:
            query_text: 查询文本
            top_k: 返回最相关的k个文档

        Returns:
            拼接后的相关文本
        """
        if not self.documents:
            return "当前知识库为空，正在初始化中..."

        # 尝试使用语义搜索
        if self._load_model():
            return self._semantic_search(query_text, top_k)
        else:
            # 降级到关键词匹配
            return self._keyword_search(query_text, top_k)

    def _semantic_search(self, query_text: str, top_k: int) -> str:
        """语义搜索"""
        try:
            import numpy as np

            # 生成查询的嵌入向量
            query_embedding = self.model.encode([query_text])[0]

            # 确保已有嵌入向量
            if self.embeddings is None:
                self._generate_embeddings()

            if self.embeddings is None:
                return self._keyword_search(query_text, top_k)

            # 计算相似度
            similarities = np.dot(self.embeddings, query_embedding) / (
                np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
            )

            # 获取最相关的文档索引
            top_indices = np.argsort(similarities)[-top_k:][::-1]

            # 拼接相关文档
            relevant_docs = []
            for idx in top_indices:
                if similarities[idx] > 0.3:  # 相似度阈值
                    relevant_docs.append(self.documents[idx]["content"])

            if not relevant_docs:
                return "未找到相关知识，建议尝试其他查询方式。"

            return "\n\n---\n\n".join(relevant_docs)
        except Exception as e:
            print(f"语义搜索失败: {e}")
            return self._keyword_search(query_text, top_k)

    def _keyword_search(self, query_text: str, top_k: int) -> str:
        """关键词搜索（降级方案）"""
        # 简单的关键词匹配
        query_keywords = set(query_text.lower())
        scored_docs = []

        for doc in self.documents:
            content_lower = doc["content"].lower()
            score = sum(1 for kw in query_keywords if kw in content_lower)
            scored_docs.append((score, doc["content"]))

        # 按分数排序
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # 返回前top_k个结果
        results = [doc for score, doc in scored_docs[:top_k] if score > 0]

        if not results:
            return "未找到相关知识，建议尝试其他查询方式。"

        return "\n\n---\n\n".join(results)

    def add_document(self, content: str, source: str, category: str = "用户添加"):
        """
        添加单个文档

        Args:
            content: 文档内容
            source: 文档来源
            category: 分类
        """
        doc_id = f"{source}-{len(self.documents)}"
        self.documents.append({
            "id": doc_id,
            "content": content,
            "source": source,
            "category": category
        })
        # 重新生成嵌入
        self.embeddings = None  # 重置，下次查询时重新生成
