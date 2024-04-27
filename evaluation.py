from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, jaccard_score

# Human classified categories

human_categories = ['PremierLeague', 'Everton', 'Brentford', 'Last Fixture']


# LLM classified categories

llm_categories = ['PremierLeague', 'Brentford', 'Everton', 'Liverpool', 'Manchester City', 'Nottingham Forest', 'Chelsea', 'Manchester United', 'Transfer News', 'Team Statistics']


# Union of categories
all_categories = list(set(human_categories) | set(llm_categories))

# Create binary arrays indicating presence of categories
human_binary = [1 if cat in human_categories else 0 for cat in all_categories]
llm_binary = [1 if cat in llm_categories else 0 for cat in all_categories]

# Calculate Jaccard similarity
jaccard_similarity = jaccard_score(human_binary, llm_binary)

# Calculate accuracy
accuracy = accuracy_score(human_binary, llm_binary)

# Calculate precision, recall, and F1-score
precision = precision_score(human_binary, llm_binary)
recall = recall_score(human_binary, llm_binary)
f1 = f1_score(human_binary, llm_binary)

print("Jaccard Similarity:", jaccard_similarity)
print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1-score:", f1)

# CODE FOR COSINE SIMILARITY

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Create vectors representing the categories
unique_categories = list(set(human_categories + llm_categories))
human_vector = [1 if category in human_categories else 0 for category in unique_categories]
llm_vector = [1 if category in llm_categories else 0 for category in unique_categories]

# Reshape vectors into numpy arrays
human_vector = np.array(human_vector).reshape(1, -1)
llm_vector = np.array(llm_vector).reshape(1, -1)

# Compute cosine similarity
cosine_sim = cosine_similarity(human_vector, llm_vector)

print("Cosine Similarity between Human and LLM classified categories:", cosine_sim[0][0])

# CODE FOR HAMMING LOSS

# Total number of categories
total_categories = len(set(human_categories + llm_categories))

# Find the number of incorrectly predicted labels
incorrect_labels = sum(human_category not in llm_categories for human_category in human_categories) + sum(llm_category not in human_categories for llm_category in llm_categories)

# Calculate Hamming loss
hamming_loss = incorrect_labels / total_categories

print("Hamming Loss:", hamming_loss)
