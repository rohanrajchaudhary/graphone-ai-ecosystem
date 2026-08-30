def chunk_text(text, max_chars=12000, overlap=500):
    """
    Split large text into overlapping chunks.

    This prevents LLM payloads from becoming too large.
    """

    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    chunks = []

    start = 0

    while start < len(text):

        end = start + max_chars

        chunk = text[start:end]

        chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


if __name__ == "__main__":

    sample = "A" * 30000

    chunks = chunk_text(sample)

    print("Original characters:", len(sample))
    print("Chunks:", len(chunks))

    for i, chunk in enumerate(chunks, 1):
        print(
            f"Chunk {i}: {len(chunk)} characters"
        )