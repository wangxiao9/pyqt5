import time

from base.MainWindow import NMainWindow, ConsolePanelHandler
# from base.action import Action
from dispense.DispensePump import DispensingRun


class NautilusUI(NMainWindow):

    def __init__(self):
        super().__init__()
        # self.action = Action()
        self.layout_dispensing_device()
        self.layout_dispensing_default_status()
        # self.dispense_default_style()
        # # self.layout_logs()
        # handler = ConsolePanelHandler(self)
        # self.logger.addHandler(handler)
        # for i in range(100):
        #     self.logger.error("测试错误")
        #     self.logger.warning("警告")
        #     self.logger.info("正常")

    """
     ----------------------------------------------------
    |  1. init layout dispense module        控件信号-槽的设置  |
     -----------------------------------------------------
    """

    def layout_dispensing_device(self):
        # self.ui.combox.addItems(com_ports)
        self.ui.RunTYPE.addItems(self.config.get('dispense', 'RunType'))
        self.ui.SeparateMode.addItems(self.config.get('dispense', 'SeparateType'))
        self.ui.WaterSlugeMode.addItems(self.config.get('dispense', 'WaterSludgeType'))

    def layout_dispensing_default_status(self):
        self.ui.WaterSluge.setEnabled(False)
        """
         -------------------------------------------
        |  event    binging                         |
         -------------------------------------------
        """
        self.ui.RunTYPE.currentIndexChanged.connect(lambda: self.dispense_default_style(self.ui.RunTYPE.currentIndex()))
        self.ui.SeparateMode.currentIndexChanged.connect(lambda : self.dispense_separate_change(self.ui.SeparateMode.currentIndex()))
        self.ui.dispense_start.clicked.connect(lambda: self.dispense_separate_run(self.ui.RunTYPE.currentIndex()))
        self.ui.StopPump.clicked.connect(self.dispense_pump_stop)
        self.ui.clear_logs.clicked.connect(self.clean_logs)



    """
     -------------------------------------------
    |  init reference default layout Style      |
      ------------------------------------------
    """

    def dispense_default_style(self, type):
        if type == 0:
            self.ui.WaterSluge.setEnabled(False)
            self.ui.Separate.setEnabled(True)
            self.ui.Weight.setValue(10.0)

        else:
            self.ui.Separate.setEnabled(False)
            self.ui.WaterSluge.setEnabled(True)
            self.ui.Weight.setValue(148.0)

    def dispense_separate_change(self, type):
        if type in (3, 4, 5):
            self.ui.Separate_RPM.setValue(100.0)
            self.ui.Separate_RPMCal.setValue(10.0)
        else:
            self.ui.Separate_RPM.setValue(600.0)
            self.ui.Separate_RPMCal.setValue(40.0)


    """
     -------------------------------------------
    | Function                                  |
      ------------------------------------------
    """
    def clean_logs(self):
        self.ui.logs_text.clear()


    def dispense_pump_stop(self):
        parameter = self.dispense_base_data()
        print(parameter)
        try:
            DispensingRun(**parameter).stop_pumps()

        except Exception as e:
            self.logger.error(f"{e}")

    def dispense_base_data(self):
        balance_port = self.ui.BalancePorts.currentText()
        pump_port = self.ui.PumpPort.currentText()
        p_pump_port = self.ui.PPumpPort.currentText()
        save_record = self.ui.saveRecord.isChecked()
        parameter = {"balance_port": balance_port, "pump_port": pump_port, "p_pump_port": p_pump_port, "save_record": save_record}
        return parameter

    def dispense_separate_run(self, type):
        # balance_port = self.ui.BalancePorts.currentText()
        # pump_port = self.ui.PumpPort.currentText()
        # p_pump_port = self.ui.PPumpPort.currentText()
        # save_record = self.ui.saveRecord.isChecked()

        parameter = self.dispense_base_data()
        weight = self.ui.Weight.value()
        if type == 0:
            separate_mode = self.ui.SeparateMode.currentIndex()
            rpm = self.ui.Separate_RPM.value()
            rpm_cal = self.ui.Separate_RPMCal.value()
            direction = self.ui.Separate_Direction.value()
            cycles = self.ui.Separate_Cycles.value()

            parameter["dispense_type"] = type
            parameter["separate_mode"] = separate_mode
            parameter["rpm"] = rpm
            parameter["rpm_cal"] = rpm_cal
            parameter["direction"] = direction
            parameter["cycles"] = cycles
            #
            # separate_paramters = {"dispense_type": type, "balance_port": balance_port, "pump_port": pump_port, "p_pump_port": p_pump_port, "separate_mode": separate_mode, "rpm": rpm ,
            #                       "rpm_cal": rpm_cal, "direction": direction, "cycles": cycles, "save_record": save_record}

            self.logger.info(f"mode: {self.ui.SeparateMode.currentText()}")

            if separate_mode in (0, 3):
                try:
                    DispensingRun(**parameter).separate_pump_balance(weight)
                except Exception as e:
                    self.logger.error(f"{e}")
            else:
                if separate_mode in (2, 5): # -> time mode = 0
                    parameter["run_mode"] = 0
                else:
                    parameter["run_mode"] = 1
                try:
                    DispensingRun(**parameter).separate_pump_volume(weight)
                except Exception as e:
                    self.logger.error(f"{e}")


        else:
            watersludge_mode = self.ui.WaterSlugeMode.currentIndex()
            rpm = self.ui.WaterSluge_RPM.value(),
            rpm_cal = self.ui.WaterSluge_RPMCal.value()
            p_rpm = self.ui.WaterSluge_PRPM.value(),
            p_rpm_cal = self.ui.WaterSluge_PRPMCal.value()
            parameter["watersludge_mode"] = watersludge_mode
            parameter["rpm"] = rpm
            parameter["rpm_cal"] = rpm_cal
            parameter["p_rpm"] = p_rpm
            parameter["p_rpm_cal"] = p_rpm_cal

            self.logger.info(f"mode:  {self.ui.WaterSlugeMode.currentText()}")

            try:
                DispensingRun(**parameter).dispense_2pumps_balance(weight)
            except Exception as e:
                self.logger.error(f"{e}")



    # def logs(self, action=None, level = "INFO", logs=None):
    #     if action == 'clear':
    #         self.ui.logs_text.clear()
    #     else:
    #         logger_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    #         current_logs = self.ui.logs_text.toPlainText()
    #         new_logs = f"{current_logs}{logger_time}   -  |     {level}     |  -   {str(logs)}"
    #         self.ui.logs_text.setPlainText(new_logs + '\n')


