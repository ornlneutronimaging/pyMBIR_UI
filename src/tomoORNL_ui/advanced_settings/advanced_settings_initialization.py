import numpy as np

from tomoORNL_ui.utilities.get import Get


class AdvancedSettingsInitialization:

    def __init__(self, parent=None):
        self.parent = parent

    def from_config_to_session_dict(self):
        config = self.parent.config['default widgets values']
        wavelet_level = config['wavelet level']
        max_number_of_iterations = config['max number of iterations']
        stop_threshold = config['stop threshold']

        o_get = Get(parent=self.parent)
        number_of_cores = o_get.get_number_of_cpu()
        number_of_gpus = o_get.get_number_of_gpu()

        median_filter_size = config['median filter size']

        exporting_file_frequency = config['exporting file frequency']

        det_x_y_linked = config['det_x, det_y']['linked']
        det_x_y_value = config['det_x, det_y']['value']
        det_x = config['det_x, det_y']['det_x']
        det_y = config['det_x, det_y']['det_y']

        if det_x_y_linked:
            det_x_to_use = det_x_y_value
            det_y_to_use = det_x_y_value
        else:
            det_x_to_use = det_x
            det_y_to_use = det_y

        vox_xy_z_linked = config['vox_xy, vox_z']['linked']
        vox_xy_z_value = config['vox_xy, vox_z']['value']
        vox_xy = config['vox_xy, vox_z']['vox_xy']
        vox_z = config['vox_xy, vox_z']['vox_z']

        if vox_xy_z_linked:
            vox_xy_to_use = vox_xy_z_value
            vox_z_to_use = vox_xy_z_value
        else:
            vox_xy_to_use = vox_xy
            vox_z_to_use = vox_z

        n_vox_x_y_mode = config['n_vox_x, n_vox_y']['mode']
        if n_vox_x_y_mode == "user_linked":
            n_vox_x = config['n_vox_x, n_vox_y']['n_vox_x_y_value']
            n_vox_y = n_vox_x
        elif n_vox_x_y_mode == "user_not_linked":
            n_vox_x = config['n_vox_x, n_vox_y']['n_vox_x']
            n_vox_y = config['n_vox_x, n_vox_y']['n_vox_y']
        else:
            session_dict = self.parent.session_dict
            if session_dict.get('crop', None) is None:
                image_width = self.parent.image_size['width']
                n_vox_x = int(int(image_width / vox_xy_to_use) * det_x_to_use)
                n_vox_y = int(int(image_width / vox_xy_to_use) * det_x_to_use)
                n_vox_x_y_value = n_vox_x
            else:
                crop_width = session_dict['crop']['width']
                n_vox_x_y_value = int(int(crop_width / vox_xy_to_use) * det_x_to_use)
                n_vox_x = n_vox_x_y_value
                n_vox_y = n_vox_x_y_value
        n_vox_x_to_use = n_vox_x
        n_vox_y_to_use = n_vox_y

        n_vox_z_mode = config['n_vox_z']["mode"]
        if n_vox_z_mode == "user":
            n_vox_z = int(config['n_vox_z']['user_value'])
        else:
            if session_dict.get('crop', None) is None:
                image_height = self.parent.image_size['height']
                n_vox_z = int(int(image_height / vox_z_to_use) * det_y_to_use)
            else:
                crop_height = session_dict['crop']['to slice - from slice']
                n_vox_z = int(int(crop_height / vox_z_to_use) * det_y_to_use)
        n_vox_z_to_use = n_vox_z

        write_output_flag = config['write output']

        self.parent.session_dict["advanced settings"] = {"wavelet level": wavelet_level,
                                                         "max number of iterations": max_number_of_iterations,
                                                         "stop threshold": stop_threshold,
                                                         "number of cores": number_of_cores,
                                                         "number of gpus": number_of_gpus,
                                                         "median filter size": median_filter_size,
                                                         "exporting file frequency": exporting_file_frequency,
                                                         "det_x, det_y": {"linked": det_x_y_linked,
                                                                          "det_x_y": det_x_y_value,
                                                                          "det_x": det_x,
                                                                          "det_y": det_y,
                                                                          "det_x_to_use": det_x_to_use,
                                                                          "det_y_to_use": det_y_to_use,
                                                                          },
                                                         "vox_xy, vox_z": {"linked": vox_xy_z_linked,
                                                                           "vox_xy_z": vox_xy_z_value,
                                                                           "vox_xy": vox_xy,
                                                                           "vox_z": vox_z,
                                                                           "vox_xy_to_use": vox_xy_to_use,
                                                                           "vox_z_to_use": vox_z_to_use,
                                                                           },
                                                         "n_vox_x, n_vox_y": {"mode": n_vox_x_y_mode,
                                                                              "n_vox_x_y": n_vox_x_y_value,
                                                                              "n_vox_x": n_vox_x,
                                                                              "n_vox_y": n_vox_y,
                                                                              "n_vox_x_to_use": n_vox_x_to_use,
                                                                              "n_vox_y_to_use": n_vox_y_to_use,
                                                                              },
                                                         "n_vox_z": {"mode": n_vox_z_mode,
                                                                     "n_vox_z": n_vox_z,
                                                                     "n_vox_z_to_use": n_vox_z_to_use,
                                                                     },
                                                         "write output": write_output_flag,
                                                         }
