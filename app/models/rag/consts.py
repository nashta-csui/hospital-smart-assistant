EMBEDDING_MODEL_NAME: str = "Qwen/Qwen3-Embedding-0.6B"
"""Nama model embedding yang digunakan untuk menghasilkan vektor embedding."""

# TODO: Finalisasi embedding dims untuk dev dan prod
EMBEDDING_DIMS: int = 1024
"""
Banyak dimensi vektor embedding yang dihasilkan model embedding

Untuk model Qwen3-Embedding-0.6B, embedding dimension berukuran 1024

Banyaknya dimensi vektor embedding memengaruhi tradeoff antara performa dan akurasi informasi.
"""
