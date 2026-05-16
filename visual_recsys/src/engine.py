import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import requests
import io
import json
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics.pairwise import cosine_similarity

class FeatureExtractionEngine:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT).to(self.device)
        self.model.eval()
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def extract_vector(self, image_source):
        try:
            if image_source.startswith('http://') or image_source.startswith('https://'):
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(image_source, headers=headers, timeout=5)
                img = Image.open(io.BytesIO(response.content)).convert('RGB')
            else:
                img = Image.open(image_source).convert('RGB')
                
            tensor = self.transform(img).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                # Extract features from the pooled layer preceding the final classification head
                features = self.model.avgpool(self.model.layer4(self.model.layer3(self.model.layer2(self.model.layer1(self.model.conv1(tensor))))))
                vector = torch.flatten(features, 1).cpu().numpy()[0]
                
            return vector / np.linalg.norm(vector)
        except Exception:
            return np.zeros(2048)

def cluster_vectors(vectors, n_clusters=10):
    matrix = np.array(vectors)
    kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, batch_size=100)
    clusters = kmeans.fit_predict(matrix)
    return [int(c) for c in clusters]

def get_top_k_recommendations(target_vector, pool_vectors, pool_indices, k=3):
    if len(pool_vectors) == 0:
        return []
    target = np.array(target_vector).reshape(1, -1)
    pool = np.array(pool_vectors)
    
    similarities = cosine_similarity(target, pool)[0]
    top_indices = np.argsort(similarities)[::-1][:k]
    
    return [(pool_indices[i], float(similarities[i])) for i in top_indices]