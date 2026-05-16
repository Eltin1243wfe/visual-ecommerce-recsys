import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

class FeatureExtractionEngine:
    def __init__(self):
        weights = models.ResNet50_Weights.DEFAULT
        self.model = models.resnet50(weights=weights)
        self.model.eval()
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406], 
                std=[0.229, 0.224, 0.225]
            )
        ])

    def extract_vector(self, image_path):
        img = Image.open(image_path).convert('RGB')
        tensor = self.transform(img).unsqueeze(0)
        
        with torch.no_grad():
            features = self.model(tensor)
            
        return features.squeeze().numpy()

def calculate_similarity_matrix(vectors):
    matrix = np.array(vectors)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    normalized_matrix = matrix / norms
    similarity = np.dot(normalized_matrix, normalized_matrix.T)
    return similarity

def get_top_k_recommendations(similarity_matrix, target_index, k=3):
    scores = similarity_matrix[target_index]
    sorted_indices = np.argsort(scores)[::-1]
    
    recommendations = []
    for idx in sorted_indices:
        if idx != target_index:
            recommendations.append((idx, float(scores[idx])))
        if len(recommendations) == k:
            break
            
    return recommendations