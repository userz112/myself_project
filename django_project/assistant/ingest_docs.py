"""
文档向量化入库脚本
将 rag_docs/ 下的所有 .txt 文件切分、向量化、存入 ChromaDB

用法：
  python manage.py ingest_docs
  python manage.py ingest_docs --reset   # 清空旧库重建
"""
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader


RAG_DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "rag_docs"
CHROMA_PERSIST_DIR = Path(__file__).resolve().parent.parent / "chroma_db"

# 中文友好的切分器
TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=500,          # 每个 chunk 约 500 字符
    chunk_overlap=50,        # 重叠 50 字符，保证跨 chunk 连贯
    separators=[
        "\n## ",            # 二级标题优先断开
        "\n### ",
        "\n",                # 段落
        "。",                # 中文句号
        "；",
        "，",
        " ",                 # 最后才切空格
        "",
    ],
)

# 中文友好的 embedding 模型（本地运行，不调 API）
EMBEDDING_MODEL = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",   # 384 维，轻量，中文效果好
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)


class Command(BaseCommand):
    help = "将 rag_docs/ 下的知识文档向量化存入 ChromaDB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="清空现有向量库后重新入库",
        )

    def handle(self, *args, **options):
        if not RAG_DOCS_DIR.exists():
            self.stdout.write(
                self.style.ERROR(f"文档目录不存在: {RAG_DOCS_DIR}")
            )
            return

        # 收集所有 txt 文件
        txt_files = list(RAG_DOCS_DIR.rglob("*.txt"))
        if not txt_files:
            self.stdout.write(self.style.ERROR("未找到任何 .txt 知识文档"))
            return

        self.stdout.write(f"找到 {len(txt_files)} 篇文档，开始加载...")

        documents = []
        for filepath in txt_files:
            loader = TextLoader(str(filepath), encoding="utf-8")
            docs = loader.load()
            # 给每个文档打上来源标签
            category = filepath.parent.name       # policies / guides
            for doc in docs:
                doc.metadata["source"] = filepath.name
                doc.metadata["category"] = category
            documents.extend(docs)
            self.stdout.write(f"  已加载: {category}/{filepath.name}")

        # 切分
        chunks = TEXT_SPLITTER.split_documents(documents)
        self.stdout.write(f"切分完成，共 {len(chunks)} 个文本块")

        # 入库
        if options["reset"]:
            self.stdout.write("清空旧向量库...")
            # 删除旧库目录
            import shutil
            if CHROMA_PERSIST_DIR.exists():
                shutil.rmtree(CHROMA_PERSIST_DIR)

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=EMBEDDING_MODEL,
            persist_directory=str(CHROMA_PERSIST_DIR),
            collection_name="real_estate_kb",
        )
        vectorstore.persist()

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ 入库完成！{len(chunks)} 个文本块已存入 {CHROMA_PERSIST_DIR}"
            )
        )
