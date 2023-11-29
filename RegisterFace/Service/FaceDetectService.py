import time

import cv2
import numpy as np
import torch
from Service.face_model import MobileFaceNet, l2_norm
from torchvision import transforms as trans

from pathlib import Path


class FaceDetectService():
    __instance = None

    def __init__(self):
        super().__init__()
        if FaceDetectService.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.model = self.loadModel()
            self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
            FaceDetectService.__instance = self

    @staticmethod
    def getInstance():
        if FaceDetectService.__instance == None:
            FaceDetectService()
        return FaceDetectService.__instance

    def embeddings(self, img, tta=False):
        embs = []
        test_transform = trans.Compose([
            trans.ToTensor(),
            trans.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])])
        with torch.no_grad():
            if tta:
                mirror = cv2.flip(img, 1)
                emb = self.model(test_transform(img).to(self.device).unsqueeze(0))
                emb_mirror = self.model(test_transform(mirror).to(self.device).unsqueeze(0))
                embs.append(l2_norm(emb + emb_mirror))
            else:
                embs.append(self.model(test_transform(img).to(self.device).unsqueeze(0)))

        return embs

    def convertToNumpy(self, img, tta=False):
        ems = self.embeddings(img, tta)
        ems = ems[0].cpu().numpy()
        return ems



    # so sanh 2 anh
    def compare(self, embs, embs2):
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

    def loadModel(self, path='weights/MobileFace_Net'):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        detect_model = MobileFaceNet(512).to(device)  # embeding size is 512 (feature vector)
        detect_model.load_state_dict(torch.load(path, map_location=lambda storage, loc: storage))
        detect_model.eval()
        return detect_model

    def load_facebank(self, path='facebank'):
        data_path = Path(path)
        embeddings = torch.load(data_path / 'facebank.pth')
        names = np.load(data_path / 'names.npy')
        return embeddings, names
