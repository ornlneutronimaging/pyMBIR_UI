import multiprocessing

from ..utility_backend import multi_logger as ml
from ..utility_backend.gam_rem_adp_log.gam_rem_adp_log import gam_rem_adp_log as holy_grail


def _call_filterfunc(param_list):
    img = param_list[0]
    thr3 = param_list[1]
    thr5 = param_list[2]
    thr7 = param_list[3]
    sig_log = param_list[4]
    return holy_grail(img, thr3, thr5, thr7, sig_log)


def filter_image(img_list, filter_params, queue):
    """Takes a list of datasets and filters them using gam_rem_adp_log()"""
    filtered_images = []
    merged_data = [[img] + filter_params for img in img_list]

    pool = multiprocessing.Pool(initializer=ml.worker_configurer, initargs=(queue,))

    for filter_image, filter_para in pool.map(_call_filterfunc, merged_data):
        filtered_images.append(filter_image)
    pool.close()

    pool.join()
    return filtered_images


def filter_image_not_mulitprocessing(img_list, filter_params):
    filtered_images = [holy_grail(_img, *filter_params)[0] for _img in img_list]
    return filtered_images
