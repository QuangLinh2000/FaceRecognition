import os
from flask import Flask, request, jsonify
from Service.FaceIdAuthService import FaceIdAuthService
from Service.MainService import createFace, checkFace

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/register', methods=['POST'])
def upload_file():
    data = checkFace(request)
    if type(data) == tuple:
        cardNumber, img, bounding_boxes, faces = data
        return jsonify({'status': createFace(cardNumber, img, bounding_boxes, faces)}), 200
    else:
        return jsonify({'status': False, 'error': data}), 400


@app.route('/edit', methods=['PUT'])
def editFace():
    cardNumber = request.form.get('CardNumber')
    if cardNumber is None:
        return jsonify({'status': False, 'error': 'no card number'}), 400
    faceIdAuthService = FaceIdAuthService.getInstance()
    data = faceIdAuthService.getByCardNumber(cardNumber)
    if len(data) == 0:
        return jsonify({'status': False, 'error': 'no card number'}), 400
    data = checkFace(request)
    if type(data) == tuple:
        cardNumber, img, bounding_boxes, faces = data
        faceIdAuthService.deleteByCardNumber(cardNumber)
        return jsonify({'status': createFace(cardNumber, img, bounding_boxes, faces)}), 200
    else:
        return jsonify({'status': False, 'error': data}), 400


@app.route('/delete', methods=['DELETE'])
def deleteFace():
    cardNumber = request.form.get('CardNumber')
    if cardNumber is None:
        return jsonify({'status': False, 'error': 'no card number'}), 400
    urlImage = "data/" + cardNumber + ".jpg"
    if os.path.exists(urlImage):
        os.remove(urlImage)
    faceIdAuthService = FaceIdAuthService.getInstance()
    faceIdAuthService.deleteByCardNumber(cardNumber)
    return jsonify({'status': True}), 200


if __name__ == '__main__':
    app.run("0.0.0.0", port=3300)
