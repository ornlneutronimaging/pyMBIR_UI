import time
import logging
from qtpy.QtGui import QGuiApplication
import numpy as np

from ngievaluation import evaluate_ngiexperiment
from dataio.experiment import NgiExperiment

from .utilities.thread import GenericThreadStartEnd
from .utilities.multicore_filtering import filter_image, filter_image_not_mulitprocessing
from .status_message_config import show_status_message, StatusMessageStatus
from .ngI_tool import ngItool as ngI
from .algorithms.epithermal_correction import epithermal_correction
from .utilities.get import Get


class Fitting:

    RUN_LABEL = "Run Fitting"
    CANCEL_LABEL = "Abort Fitting"

    step_index = 0
    number_of_steps = 11  # use to display progress bar

    sample = None
    ob = None
    dc = None
    stepping = None

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        if self.parent.ui.run_fitting_pushButton.text() == self.RUN_LABEL:
            show_status_message(parent=self.parent,
                                message="Running ngi calculation ...",
                                status=StatusMessageStatus.working)
            logging.info("Launching ngi calculation")
            self.parent.ui.run_fitting_pushButton.setText(self.CANCEL_LABEL)
            QGuiApplication.processEvents()
            time.sleep(1)  # trick needed to be able to update the button label
            self.parent.ui.top_tabWidget.setTabEnabled(0, False)
            self.parent.ui.top_tabWidget.setTabEnabled(1, False)
            self.parent.ui.top_tabWidget.setTabEnabled(2, False)
            # self.parent.ngi_thread = GenericThreadStartEnd(self.calculate_ngi())
            self.calculate_ngi()

        else:
            # if self.parent.ngi_thread.isRunning():
            #     self.parent.ngi_thread.terminate()
            show_status_message(parent=self.parent,
                                message="ngi calculation stopped by user!",
                                status=StatusMessageStatus.warning,
                                duration_s=5)
            logging.info("ngi calculation has been canceled by user")
            self.parent.ui.run_fitting_pushButton.setText(self.RUN_LABEL)
            QGuiApplication.processEvents()
            self.parent.ui.top_tabWidget.setTabEnabled(0, True)
            self.parent.ui.top_tabWidget.setTabEnabled(1, True)
            self.parent.ui.top_tabWidget.setTabEnabled(2, True)

    def calculate_ngi(self):

        QGuiApplication.processEvents()
        message = self.running_algorithms()

        # cleaning ui
        self.parent.ui.top_tabWidget.setTabEnabled(0, True)
        self.parent.ui.top_tabWidget.setTabEnabled(1, True)
        self.parent.ui.top_tabWidget.setTabEnabled(2, True)
        logging.info("ngi calculation done!")
        self.parent.ui.run_fitting_pushButton.setText(self.RUN_LABEL)
        if message:
            show_status_message(parent=self.parent,
                                message=message,
                                status=StatusMessageStatus.working,
                                duration_s=5)
        self.parent.eventProgress.setVisible(False)

    def running_algorithms(self):

        sample, ob, di = self._running_filters()  # 9 steps
        if self._user_stopped_running():
            return ""

        o_experiment = self.parent.o_experiment
        stepping_list = o_experiment.stepping
        sample, ob, stepping = self._combining(sample=sample,  # 1 step
                                               ob=ob,
                                               stepping=stepping_list)
        self.sample = stepping
        if self._user_stopped_running():
            return ""
        di = self._epithermal_filtering(di=di)  # 1 step

        if self._user_stopped_running():
            return ""
        self._running_fitting(sample=sample, ob=ob, di=di)

        return "ngi Calculation: Done!"

    def _running_fitting(self, sample, ob, di):

        o_get = Get(parent=self.parent)
        fitting_algorithm = o_get.algorithm_selected()

        is_full_period = self.parent.ui.full_period_true_radioButton.isChecked()
        number_of_scanned_periods = self.parent.ui.number_of_scanned_periods_spinBox.value()
        g0_rot = self.parent.ui.rotation_of_g0rz_doubleSpinBox.value()

        logging.info("Running fitting")
        logging.info(f"-> fitting algorithm: {fitting_algorithm}")
        logging.info(f"-> number of scanned periods: {number_of_scanned_periods}")
        logging.info(f"-> is full period: {is_full_period}")
        logging.info(f"-> g0_rot: {g0_rot}")
        logging.info(f"-> shape(sample): {np.shape(sample)}")
        logging.info(f"-> shape(ob): {np.shape(ob)}")
        logging.info(f"-> shape(di): {np.shape(di)}")

        ngiexperiment = NgiExperiment(name='sample',
                                      sample=sample,
                                      reference=ob,
                                      offset=di,
                                      facility=None)

        evaluate_ngiexperiment(ngiexperiment=ngiexperiment,
                               algorithm='dittmann1+marathe')

        logging.info(f"-> Result:")
        logging.info(f"--> sample oscilation data: {type(ngiexperiment.sample_oscillation_data)}")
        logging.info(f"--> shape(NgiOscillationData.offset): {np.shape(ngiexperiment.sample_oscillation_data.offset)}")
        logging.info(f"--> shape(NgiOscillationData.amplitude): "
                     f"{np.shape(ngiexperiment.sample_oscillation_data.amplitude)}")

        # # self.TI, self.DPC, self.DFI, \
        # self.a0_ob, self.a1_ob, self.phi_ob, \
        # self.a0_data, self.a1_data, self.phi_data = ngI.nGI(sample, ob, di,
        #                                                     fitting_algorithm,
        #                                                     is_full_period,
        #                                                     number_of_scanned_periods,
        #                                                     self.stepping,
        #                                                     self.stepping,
        #                                                     data_norm_list=None,
        #                                                     ob_norm_list=None,
        #                                                     G0_rot=g0_rot)

    def _epithermal_filtering(self, di=None):
        # worth 2 step
        if self.parent.ui.pre_processing_outlier_checkBox.isChecked():
            threshold = self.parent.ui.pre_processing_outlier_threshold_spinBox.value()

            show_status_message(parent=self.parent,
                                message=f"epithermal filtering using threshold of {threshold} ...",
                                status=StatusMessageStatus.working)

            logging.info(f"running outlier removal in epithermal dc using a threshold of {threshold}")
            di_corrected = [epithermal_correction(image=_image, threshold=threshold) for _image in di]
            self._progress_bar_next()

        else:
            logging.info("no outlier removal in epithermal dc")
            self._progress_bar_next(coefficient=2)
            di_corrected = di

        if len(di_corrected) == 1:
            logging.info("--> single DC image loaded. No further handling done")
            return di_corrected[0]
        elif len(di_corrected) == 2:
            _di_corrected = np.minimum(di_corrected[0], di_corrected[1])
            logging.info("--> 2 DC images loaded. Element-wise minimum of the images has been calculated")
            self._progress_bar_next()
            return _di_corrected
        else:
            _di_corrected = np.median(di_corrected, axis=0)
            logging.info("--> 3 or more DC images loaded. element-wise median of the images has been calculated")
            self._progress_bar_next()
            return _di_corrected

    def _combining(self, sample=None, ob=None, stepping=None):
        # worth 1 step

        nbr_images_per_step = self.parent.ui.images_per_step_spinBox.value()
        if nbr_images_per_step == 1:
            logging.info("no need to combine images")
            self._progress_bar_next(coefficient=1)
            return sample, ob, stepping

        show_status_message(parent=self.parent,
                            message=f"_combining data by {nbr_images_per_step} ...",
                            status=StatusMessageStatus.working)

        logging.info(f"combining images by {nbr_images_per_step}")
        sample_combined = []
        ob_combined = []
        stepping_combined = []
        for index in np.arange(0, len(sample), nbr_images_per_step):

            from_index = index
            to_index = index + nbr_images_per_step if index + nbr_images_per_step < len(sample) else len(sample)

            sample_combined.append(np.median(sample[from_index: to_index], axis=0))
            ob_combined.append(np.median(ob[from_index: to_index], axis=0))
            stepping_combined.append(np.median(stepping[from_index: to_index], axis=0))

        self._progress_bar_next(coefficient=1)
        return sample_combined, ob_combined, stepping_combined

    def _running_filters(self):
        # worth 9 steps total

        self.parent.eventProgress.setMaximum(self.number_of_steps)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        o_experiment = self.parent.o_experiment
        sample_img_dataimages = o_experiment.sample.dataimages
        ob_img_dataimages = o_experiment.reference.dataimages
        di_img_dataimages = o_experiment.offset.dataimages

        sample_img_list = [_img.data for _img in sample_img_dataimages]
        ob_img_list = [_img.data for _img in ob_img_dataimages]
        di_img_list = [_img.data for _img in di_img_dataimages]

        # cropping (worth 3 steps)
        sample, ob, di = self._crop(sample_list=sample_img_list,
                                    ob_list=ob_img_list,
                                    di_list=di_img_list)

        # gamma filter (worth 3 steps)
        sample, ob, di = self._gamma(sample_list=sample,
                                     ob_list=ob,
                                     di_list=di)

        # # binning (worth 3 steps)
        sample, ob, di = self._binning(sample_list=sample,
                                       ob_list=ob,
                                       di_list=di)

        return sample, ob, di

    def _binning(self, sample_list=None, ob_list=None, di_list=None):
        """ binning of all data """
        # this method is worth 3 steps

        if self.parent.ui.pre_processing_image_binning_checkBox.isChecked():

            # sample_list_working = copy.deepcopy(sample_list)
            # ob_list_working = copy.deepcopy(ob_list)
            # di_list_working = copy.deepcopy(di_list)

            bin_value = self.parent.ui.pre_processing_binned_pixels_spinBox.value()
            logging.info(f"-> binning of data (sample, ob and di): {bin_value}x{bin_value} pixels")

            show_status_message(parent=self.parent,
                                message="binning of sample data ...",
                                status=StatusMessageStatus.working)

            sample_list_rebinned = [ngI.rebin(_data, bin_value) for _data in sample_list]
            self._progress_bar_next()

            show_status_message(parent=self.parent,
                                message="binning of ob data ...",
                                status=StatusMessageStatus.working)

            ob_list_rebinned = [ngI.rebin(_data, bin_value) for _data in ob_list]
            self._progress_bar_next()

            show_status_message(parent=self.parent,
                                message="binning of di data ...",
                                status=StatusMessageStatus.working)

            di_list_rebinned = [ngI.rebin(_data, bin_value) for _data in di_list]
            self._progress_bar_next()

            logging.info(f"-> binning of data (sample, ob and di) ... Done!")
            return sample_list_rebinned, ob_list_rebinned, di_list_rebinned

        else:
            logging.info(f"-> no binning of data")
            self._progress_bar_next(coefficient=3)
            return sample_list, ob_list, di_list

    def _gamma(self, sample_list=None, ob_list=None, di_list=None):
        """ gamma filtering """
        # this method is worth 3 steps

        if self.parent.ui.pre_processing_sample_ob_checkBox.isChecked():
            logging.info("-> gamma filtering of sample and ob")

            show_status_message(parent=self.parent,
                                message="Gamma filtering of sample data ...",
                                status=StatusMessageStatus.working)

            threshold1 = self.parent.ui.sample_ob_threshold1_spinBox.value()
            threshold2 = self.parent.ui.sample_ob_threshold2_spinBox.value()
            threshold3 = self.parent.ui.sample_ob_threshold3_spinBox.value()
            sigma_for_log = self.parent.ui.sample_ob_sigma_for_log_spinBox.value()

            logging.info(f"--> threshold1 (3x3): {threshold1}")
            logging.info(f"--> threshold2 (5x5): {threshold2}")
            logging.info(f"--> threshold3 (7x7): {threshold3}")
            logging.info(f"--> sigma_for_log: {sigma_for_log}")

            gamma_params = [threshold1, threshold2, threshold3, sigma_for_log]
            #sample_list_gamma = filter_image(sample_list, gamma_params, self.parent.queue)
            sample_list_gamma = filter_image_not_mulitprocessing(sample_list, gamma_params)

            logging.info("-> gamma filtering of sample ... done")
            self._progress_bar_next()

            show_status_message(parent=self.parent,
                                message="Gamma filtering of ob data ...",
                                status=StatusMessageStatus.working)
            # ob_list_gamma = filter_image(ob_list, gamma_params, self.parent.queue)
            ob_list_gamma = filter_image_not_mulitprocessing(ob_list, gamma_params)

            logging.info("-> gamma filtering of ob ... done")
            self._progress_bar_next()

        else:
            sample_list_gamma = sample_list
            ob_list_gamma = ob_list
            logging.info("-> NO gamma filtering of sample and ob!")
            self._progress_bar_next(coefficient=2)

        if self.parent.ui.pre_processing_di_checkBox.isChecked():
            logging.info("-> gamma filtering of di")
            
            threshold1 = self.parent.ui.di_threshold1_spinBox.value()
            threshold2 = self.parent.ui.di_threshold2_spinBox.value()
            threshold3 = self.parent.ui.di_threshold3_spinBox.value()
            sigma_for_log = self.parent.ui.di_sigma_for_log_spinBox.value()

            logging.info(f"--> threshold1 (3x3): {threshold1}")
            logging.info(f"--> threshold2 (5x5): {threshold2}")
            logging.info(f"--> threshold3 (7x7): {threshold3}")
            logging.info(f"--> sigma_for_log: {sigma_for_log}")

            show_status_message(parent=self.parent,
                                message="Gamma filtering of id data",
                                status=StatusMessageStatus.working)

            gamma_params = [threshold1, threshold2, threshold3, sigma_for_log]
            # di_list_gamma = filter_image(di_list, gamma_params, None)
            di_list_gamma = filter_image_not_mulitprocessing(di_list, gamma_params)
            logging.info("-> gamma filtering of di ... done")
            self._progress_bar_next()

        else:
            di_list_gamma = di_list
            logging.info("-> NO gamma filtering of di")
            self._progress_bar_next()

        return sample_list_gamma, ob_list_gamma, di_list_gamma

    def _crop(self, sample_list=None, ob_list=None, di_list=None):
        """ cropping the data if any sample_roi_list"""
        # this method is worth 3 steps

        # sample_list = copy.deepcopy(sample_list)
        # ob_list = copy.deepcopy(ob_list)
        # di_list = copy.deepcopy(di_list)

        sample_roi_list = self.parent.sample_roi_list

        # step1 crop
        if sample_roi_list:

            show_status_message(parent=self.parent,
                                message="Cropping data (sample, ob and di) ...",
                                status=StatusMessageStatus.working)

            y0, y1, x0, x1 = sample_roi_list
            logging.info(f"-> cropping sample, ob and di using [y0, y1, x0, x1]: [{y0}, {y1}, {x0}, {x1}]")

            sample_img_list_crop = [_sample[y0: y1, x0: x1] for _sample in sample_list]
            self._progress_bar_next()

            ob_img_list_crop = [_ob[y0: y1, x0: x1] for _ob in ob_list]
            self._progress_bar_next()

            di_img_list_crop = [_di[y0: y1, x0: x1] for _di in di_list]
            self._progress_bar_next()

            return sample_img_list_crop, ob_img_list_crop, di_img_list_crop

        else:
            logging.info(f"-> no cropping ")
            self._progress_bar_next(coefficient=3)
            return sample_list, ob_list, di_list

    def _progress_bar_next(self, coefficient=1):
        """generalise the process of updating the progress bar"""
        self.parent.eventProgress.setValue(self.step_index + coefficient)
        self.step_index += coefficient
        QGuiApplication.processEvents()

    def _user_stopped_running(self):
        if self.parent.ui.run_fitting_pushButton.text() == "RUN_LABEL":
            show_status_message(parent=self.parent,
                                message="ngi calculation stopped by user!",
                                status=StatusMessageStatus.warning,
                                duration_s=5)
            logging.info("ngi calculation has been canceled by user")
            self.parent.ui.run_fitting_pushButton.setText(self.RUN_LABEL)
            self.parent.ui.top_tabWidget.setTabEnabled(0, True)
            self.parent.ui.top_tabWidget.setTabEnabled(1, True)
            self.parent.ui.top_tabWidget.setTabEnabled(2, True)
            return True
        return False
