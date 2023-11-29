import numpy as np
import torch
from src.utils.face_model import MobileFaceNet, l2_norm
from torchvision import transforms as trans

from pathlib import Path

def embeddings(model, img, tta=False, device=torch.device("cuda:0" if torch.cuda.is_available() else "cpu")):
    import cv2

    embs = []
    test_transform = trans.Compose([
        trans.ToTensor(),
        trans.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])])
    with torch.no_grad():
        if tta:
            mirror = cv2.flip(img, 1)
            emb = model(test_transform(img).to(device).unsqueeze(0))
            emb_mirror = model(test_transform(mirror).to(device).unsqueeze(0))
            embs.append(l2_norm(emb + emb_mirror))
        else:
            embs.append(model(test_transform(img).to(device).unsqueeze(0)))

    return embs


# so sanh 2 anh
def compare(embs, embs2):
    source_embs = torch.cat(embs)  # number of detected faces x 512
    source_embs2 = torch.cat(embs2)  # number of detected faces x 512
    diff = source_embs.unsqueeze(-1) - source_embs2.transpose(1, 0).unsqueeze(
        0)  # i.e. 3 x 512 x 1 - 1 x 512 x 2 = 3 x 512 x 2
    dist = torch.sum(torch.pow(diff, 2), dim=1)  # number of detected faces x numer of target faces
    minimum, min_idx = torch.min(dist, dim=1)  # min and idx for each row
    min_idx[minimum > ((60 - 156) / (-80))] = -1
    score = minimum
    results = min_idx
    score_100 = torch.clamp(score * -80 + 156, 0, 100)
    return score, results, score_100


def loadModel(path='Weights/MobileFace_Net'):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    detect_model = MobileFaceNet(512).to(device)  # embeding size is 512 (feature vector)
    detect_model.load_state_dict(torch.load(path, map_location=lambda storage, loc: storage))
    detect_model.eval()
    return detect_model
def load_facebank(path = 'facebank'):
    data_path = Path(path)
    embeddings = torch.load(data_path/'facebank.pth')
    names = np.load(data_path/'names.npy')
    return embeddings, names

# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# image = cv2.imread("data/linh.jpg")
# image2 = cv2.imread("data/linhk.jpg")
# detect_model = loadModel()
# startTime = time.time()
# embs = embeddings(detect_model, image, tta=True, device=device)
# embs2 = embeddings(detect_model, image2, tta=True, device=device)
# print(time.time() - startTime)
# score, results, score_100 = compare(embs, embs2)
# print(score)
