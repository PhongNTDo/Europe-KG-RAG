import os
import numpy as np
import google.generativeai as genai

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])


# The model name for embeddings is different from generative models.
# Use 'models/embedding-001' or 'models/text-embedding-004'.
embedding_model_name = 'models/embedding-001'
query_text = "This is the text I want to embed."

# Call the top-level function
result = genai.embed_content(
    model=embedding_model_name,
    content=query_text,
    task_type="RETRIEVAL_QUERY" # Important for getting the best embeddings
)

# The embedding is directly in the result dictionary
query_embedding = result['embedding']

# Convert to a NumPy array if needed (the result is a simple list)
query_embedding = np.array(query_embedding)

print(query_embedding)
print(f"Shape: {query_embedding.shape}")