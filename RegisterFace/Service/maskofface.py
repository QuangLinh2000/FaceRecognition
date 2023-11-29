import dlib
from mask.utils.aux_functions import *


def mask_faces(image, mask_type="all", pattern=None, pattern_weight=0.5, color="#0473e2", color_weight=0.5, code=None,
               verbose=False, write_original_image=False):
    # Set up dlib face detector and predictor
    detector = dlib.get_frontal_face_detector()
    # get real path
    path_to_dlib_model = os.getcwd() + "/mask/dlib_models/shape_predictor_68_face_landmarks.dat"

    predictor = dlib.shape_predictor(path_to_dlib_model)

    # Extract data from code
    mask_code = "".join(code.split('')).split(',') if code is not None else []
    code_count = np.zeros(len(mask_code))
    mask_dict_of_dict = {}

    for i, entry in enumerate(mask_code):
        mask_dict = {}
        mask_color = ""
        mask_texture = ""
        mask_type = entry.split("-")[0]
        if len(entry.split("-")) == 2:
            mask_variation = entry.split("-")[1]
            if "#" in mask_variation:
                mask_color = mask_variation
            else:
                mask_texture = mask_variation
        mask_dict["type"] = mask_type
        mask_dict["color"] = mask_color
        mask_dict["texture"] = mask_texture
        mask_dict_of_dict[i] = mask_dict

        # Proceed if file is image
    masked_image, mask, mask_binary_array, original_image = mask_image(
        image, mask_type, verbose, detector, predictor, pattern or "", color, code or "", mask_dict_of_dict,
        code_count, pattern_weight, color_weight)

    return masked_image

# Example of usage:
