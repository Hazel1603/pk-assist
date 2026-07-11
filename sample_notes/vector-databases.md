# Vector Databases

Vector databases store embeddings and make it possible to search by meaning
instead of exact keywords.

In a retrieval-augmented generation app, the basic flow is:

1. Split documents into chunks.
2. Turn each chunk into an embedding.
3. Store the embedding with its source text.
4. Search for chunks that are close to the question embedding.
5. Use the retrieved chunks as context for the answer.

I want to compare local options before choosing one for this project.
