import numpy as np
import logging

from roiselector import RoiSelectorDialog

from tomoORNL_ui.status_message_config import show_status_message, StatusMessageStatus
from tomoORNL_ui.utilities.get import Get


class RoiHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def select_roi(self):
        o_get = Get(parent=self.parent)
        data = o_get.get_data_sample_selected()
        roi_dialog = RoiSelectorDialog(image=data,
                                       tags=['ROI', 'Norm ROI'],
                                       standalone=False)
        roi_dialog.show()
        if roi_dialog.exec_():
            o_roi = RoiHandler(parent=self.parent)
            o_roi.save_roi(o_roi=roi_dialog.get_roi())
        else:
            show_status_message(parent=self.parent,
                                message="No ROI has been set!",
                                status=StatusMessageStatus.warning,
                                duration_s=5)

    def save_roi(self, o_roi=None):
        sample_roi = o_roi.get_windows(tags='ROI')
        norm_roi = o_roi.get_windows(tags='Norm ROI')

        self._collect_sample_roi(roi=sample_roi)
        self._collect_norm_roi(roi=norm_roi)

        self.parent.use_normalization_roi_clicked(None)

    def _collect_sample_roi(self, roi=None):
        self.parent.sample_roi_list = self._get_roi(roi_type='sample ROI',
                                                    roi=roi)

    def _collect_norm_roi(self, roi):
        self.parent.norm_roi_list = self._get_roi(roi_type='norm ROI',
                                                  roi=roi)

    def _get_roi(self, roi_type="sample ROI", roi=None):
        roi_array = None
        if len(roi) == 0:
            pass
            # show_status_message(parent=self.parent,
            #                     message="No ROI window with the '{}' tag defined!".format(*roi_type),
            #                     status=StatusMessageStatus.error,
            #                     duration_s=10)
        elif len(roi) == 1:
            roi_bounds = roi[0].get_bounds()
            roi_array = [int(roi_bounds[2]),
                         int(roi_bounds[3]),
                         int(roi_bounds[0]),
                         int(roi_bounds[1])]
            show_status_message(parent=self.parent,
                                message="ROI has been set to: {}, {}, {}, {}".format(*roi_array),
                                status=StatusMessageStatus.ready,
                                duration_s=10)
        elif len(roi) > 1:
            # use the maximum bound of all regions
            roi_array = np.zeros((4))
            for _roi in roi:
                roi_bounds = _roi.get_bounds()
                roi_array[0] = int(min([roi_array[0], roi_bounds[2]]))
                roi_array[1] = int(min([roi_array[1], roi_bounds[3]]))
                roi_array[2] = int(min([roi_array[2], roi_bounds[0]]))
                roi_array[3] = int(min([roi_array[3], roi_bounds[1]]))
            show_status_message(parent=self.parent,
                                message="Multiple ROI windows selected, ROI has been set to: {}, {}, {}, {}".format(
                                        *roi_array),
                                status=StatusMessageStatus.ready,
                                duration_s=10)

        logging.info(f"{roi_type}: {roi_array}")

        return roi_array
