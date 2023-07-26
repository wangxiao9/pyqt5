import signal
import time
# from Pump import *
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication
from mettler_toledo_device import MettlerToledoDevice
from enum import Enum
from openpyxl import Workbook

from base.MainWindow import NMainWindow
from dispense.Pump import Pump



def set_timeout(num):
    def wrap(func):
        def handle(signum, frame):
            raise RuntimeError

        def to_do(*args):
            try:
                signal.signal(signal.SIGALRM, handle)
                signal.alarm(num)
                print("Start alarm signal.")
                result = func(*args)
                print("Close alarm signal.")
                signal.alarm(0)
                return result
            except RuntimeError as e:
                return "Timeout!!!"

        return to_do

    return wrap


class PumpType(Enum):
    separate_run = 1
    dispensing_run = 2


class PumpItem(Enum):
    pump_balance = 1
    pump_volume = 2
    pump_time = 3
    p_pump_balance = 4
    p_pump_volume = 5
    p_pump_time = 6


class PumpRPMConfigure(Enum):
    p3700 = 600.0
    p3700_cal = 40.0
    pp3700 = 100.0
    pp3700_cal = 10.0
    p225 = 80.0
    p225_cal = 30.0
    pp225 = 10.0
    pp225_cal = 10.0


class DispensePump(Pump):
    # by default, clockwise, time mode


    def __init__(self, port, rpm, rpm_cal, direction, mode=0):
        # balance
        super().__init__(port)
        # pump
        # self.run_rpm = rpm
        # self.run_rpm_cal = rpm_cal
        # self.run_direction = direction
        # self.run_mode = mode  # pump -> volume or time




def dispense_save_export(data_list=[]):
    workbook = Workbook()
    sheet = workbook.active
    for row in data_list:
        assert isinstance(sheet, object)
        sheet.append(row)
    time_stamp = time.gmtime()
    workbook.save('Dispensing_' + time.strftime("%Y%m%d%H%M%S", time_stamp) + '.xlsx')





class DispensingRun(NMainWindow):

    def __init__(self, **kwargs):
        super(DispensingRun, self).__init__()
        self.kwargs = kwargs
        self.balance = MettlerToledoDevice(port=self.kwargs["balance_port"])
        self.pump = DispensePump(port = self.kwargs["pump_port"], rpm=self.kwargs["rpm"],
                                     rpm_cal=self.kwargs["rpm_cal"])
        self.p_pump = DispensePump(port = self.kwargs["p_pump_port"], rpm= self.kwargs["p_rpm"],
                                     rpm_cal= self.kwargs["p_rpm_cal"])

        ##################################################
        #   修改2：
        #      1. configure value -> get value from GUI
        #      2. througth gui value , system automatically determine the object of the pump
        ##################################################
        if self.kwargs["dispense_type"] == 0:

            if self["separate_mode"] in (0, 3):
                self.data_list = [["Water real weight", "Fly time(s)", "Accuracy", "RPM", "RPM-CAL"]]
            else:
                self.data_list = [["Water real weight", "Fly time(s)", "Accuracy", "RPM"]]

        else:
            self.data_list = [["Sludge real weight", "Water real weight", "Fly time(s)", "Accuracy", "RPM", "RPM-CAL",
                      "P-RPM", "P-RPM-CAL"]]

        self.run_volume = 10.0
        self.type = self.kwargs["dispense_type"]

    # @set_timeout(300)
    def separate_pump_balance(self, weight, try_times = 0):
        try:
            while try_times < self.kwargs["cycles"]:
                multi_rpms = True
                rpm_switch_span = 20.0
                ##################################################
                #   修改3：
                #      1. configure value -> get value from GUI
                #
                ##################################################
                if self.kwargs["separate_mode"] in (0,1,2):
                    run_pump = self.pump
                    delta_volume = 2.0  # may have better algorithm later
                else:
                    run_pump = self.p_pump
                    delta_volume = 0.20  # may have better algorithm later

                if self.kwargs["rpm_cal"] < 5 :
                    multi_rpms = False
                else:
                    rpm_switch_span = self.kwargs["rpm_cal"] / 15.0
                rpm_change_flag = False
                water_weight = weight
                balance_s = self.balance.get_weight()[0]

                self.logger.info(f"Pump water weight: {water_weight}")
                self.logger.info(f"Water start balance: {balance_s}")

                run_pump.set_pump_rpm(self.kwargs["rpm"])
                run_pump.set_pump_mode(self.kwargs["rpm_cal"])
                run_pump.set_pump_direction(self.kwargs["direction"])
                run_pump.set_pump_time_volume(0)  # long run for time mode
                run_pump.pump_run(1)
                time_ini = time.time()
                while True:
                    data = self.balance.get_weight()[0]
                    if ((data - balance_s + delta_volume) > (water_weight - rpm_switch_span)) and (
                            not rpm_change_flag) and multi_rpms:
                        run_pump.pump_run(0)
                        run_pump.set_pump_rpm(self.kwargs["rpm_cal"])
                        rpm_change_flag = True
                        time.sleep(0.002)
                        run_pump.pump_run(1)
                    elif (data - balance_s + delta_volume) < water_weight:
                        time.sleep(0.002)
                    else:
                        # Stop pump
                        run_pump.pump_run(0)
                        break
                time_end = time.time()
                run_pump.pump_run(0)
                time.sleep(1)
                balance_e_s = self.balance.get_weight_stable()[0]
                water_weight_final = balance_e_s - balance_s
                QApplication.processEvents()

                self.logger.info(f"Real weight: {water_weight_final}")
                self.logger.info(f"Time fly: { time_end - time_ini} s")
                self.logger.info(f"Accuracy:  {water_weight_final / water_weight * 100} %")



                self.data_list.append([water_weight_final, time_end - time_ini,
                                  water_weight_final / water_weight, self.kwargs["rpm"], self.kwargs["rpm_cal"]])
                time.sleep(3)
                try_times +=1
        except Exception as e:
            self.logger.error(f"Separate Run Exception: {e}")
        finally:
            self.logger.info("Separate Pump Run Completed!")
            self.pump.pump_run(0)
            self.p_pump.pump_run(0)
            if self.kwargs["save_record"]:
                dispense_save_export(self.data_list)

    # @set_timeout(300)
    def separate_pump_volume(self, weight, try_times = 0):
        try:
            while try_times < self.kwargs["cycles"]:
                if self.kwargs["separate_mode"] in (0,1,2):
                    run_pump = self.pump
                else:
                    run_pump = self.p_pump
                water_weight = weight
                balance_s = self.balance.get_weight()[0]
                self.logger.info(f"Pump water weight: {water_weight}")
                self.logger.info(f"Water start balance: {balance_s}")


                run_pump.set_pump_rpm(self.kwargs["rpm"])
                run_pump.set_pump_mode(self.kwargs["run_mode"])
                run_pump.set_pump_direction(self.kwargs["direction"])
                run_pump.set_pump_time_volume(water_weight)  # long run for time mode
                run_pump.pump_run(1)
                time_ini = time.time()
                while True:
                    if run_pump.get_pump_state()[0] == 0:
                        break
                    time.sleep(0.002)
                time_end = time.time()
                time.sleep(1)
                balance_e_s = self.balance.get_weight_stable()[0]
                water_weight_final = balance_e_s - balance_s

                QApplication.processEvents()

                self.logger.info(f"Real weight: {water_weight_final}")
                self.logger.info(f"Time fly: { time_end - time_ini} s")
                self.logger.info(f"Accuracy:  {water_weight_final / water_weight * 100} %")

                self.data_list.append([water_weight_final, time_end - time_ini,
                                  water_weight_final / water_weight, self.kwargs["rpm"]])
        except Exception as e:
            self.logger.error(f'Volume Run Exception:  {e}')
        finally:
            self.logger.info("Volume run completed!")
            self.pump.pump_run(0)
            self.p_pump.pump_run(0)
            # self.p_pump.pump_run(0)
            if self.kwargs["save_record"]:
                dispense_save_export(self.data_list)

    # @set_timeout(3000)
    # save_record=False -> 界面选择
    def dispense_2pumps_balance(self, weight=148.0):
        try:
            while True:
                # Pump sludge
                multi_rpms_p = True
                sludge_weight = weight
                delta_p = 0.20
                rpm_switch_span_p = 10
                self.logger.info(f"Pump sluge weight:  {sludge_weight}")

                balance_s = self.balance.get_weight()[0]

                self.logger.info(f"Sludge start balance:   {balance_s}")

                rpm_change_flag = False



                if self.kwargs["p_rpm_cal"] < 5.0:
                    multi_rpms_p = False
                # start pump
                self.p_pump.set_pump_rpm(self.kwargs["p_rpm"])
                self.p_pump.set_pump_time_volume(0)
                self.p_pump.set_pump_direction(1)
                self.p_pump.pump_run(1)
                time_ini_s = time.time()
                time_ini = time_ini_s
                while True:
                    data = self.balance.get_weight()[0]
                    if ((data - balance_s + delta_p) > (sludge_weight - rpm_switch_span_p)) and (
                            not rpm_change_flag) and multi_rpms_p:
                        self.p_pump.pump_run(0)
                        self.p_pump.set_pump_rpm(self.kwargs["p_rpm_cal"])
                        rpm_change_flag = True
                        time.sleep(0.002)
                        self.p_pump.pump_run(1)
                    elif (data - balance_s + delta_p) < sludge_weight:
                        time.sleep(0.002)
                    else:
                        # Stop pump
                        self.p_pump.pump_run(0)
                        break
                time_end = time.time()
                self.p_pump.pump_run(0)
                time.sleep(1)
                balance_e_s = self.balance.get_weight_stable()[0]
                sludge_weight_final = balance_e_s - balance_s

                QApplication.processEvents()

                self.logger.info("Sludge:-----------------------------")
                self.logger.info(f"Real sludge weight:  { sludge_weight_final} ")
                self.logger.info(f"Time fly:  { time_end - time_ini} s")
                self.logger.info(f"Sludge accuracy {sludge_weight_final / sludge_weight * 100} % ")


                # Pump back to avoid block
                self.p_pump.set_pump_direction(0)
                self.p_pump.set_pump_rpm(10.0)
                self.p_pump.set_pump_time_volume(5000)
                self.p_pump.pump_run(1)

                # Pump water
                multi_rpms = True
                water_weight = sludge_weight_final * 25.0 - sludge_weight_final / 2.0

                self.logger.info(f"Pump water weight:   { water_weight} ")

                balance_s = self.balance.get_weight()[0]

                self.logger.info(f"Water start balance:  { balance_s} ")


                delta = 2.0
                rpm_switch_span = 40
                rpm_change_flag = False
                if self.kwargs["p_rpm_cal"] < 10.0:
                    multi_rpms = False
                self.pump.set_pump_rpm(self.kwargs["rpm"])
                self.pump.pump_run(1)
                time_ini = time.time()
                while True:
                    data = self.balance.get_weight()[0]
                    if ((data - balance_s + delta) > (water_weight - rpm_switch_span)) and (
                            not rpm_change_flag) and multi_rpms:
                        self.pump.pump_run(0)
                        self.pump.set_pump_rpm(self.kwargs["rpm_cal"])
                        rpm_change_flag = True
                        time.sleep(0.002)
                        self.pump.pump_run(1)
                    elif (data - balance_s + delta_p) < water_weight:
                        time.sleep(0.002)
                    else:
                        # Stop pump
                        self.pump.pump_run(0)
                        break
                time_end = time.time()
                self.pump.pump_run(0)
                time.sleep(1)
                balance_e_s = self.balance.get_weight_stable()[0]
                water_weight_final = balance_e_s - balance_s

                self.logger.info("Water:-----------------------")
                self.logger.info(f"Real water weight:  {water_weight_final}")
                self.logger.info(f"Time fly :  {time_end - time_ini} s")
                self.logger.info(f"Water accuracy { water_weight_final / water_weight * 100} %")


                self.data_list.append([sludge_weight_final, water_weight_final, time_end - time_ini_s,
                                  (sludge_weight_final + water_weight_final) / (sludge_weight + water_weight),
                                  self.kwargs["rpm"], self.kwargs["rpm_cal"], self.kwargs["p_rpm"],
                                  self.kwargs["p_rpm_cal"]])

                text = input("Do you want to do another try? Press Y/N.")
                if text == 'Y' or text == 'y':
                    continue
                else:
                    break
        except Exception as e:
            self.logger.error(f"Dispensing error:  {e}")
        finally:
            self.logger.info("Dispensing 2 pumps completed!")
            print("Dispensing 2 pumps completed!")
            self.pump.pump_run(0)
            self.p_pump.pump_run(0)
            if self.kwargs["save_record"]:
                dispense_save_export(self.data_list)

    # @set_timeout(300)
    def stop_pumps(self):
        try:
            self.pump.pump_run(0)
            self.p_pump.pump_run(0)
        except Exception as e:
            self.logger.error(f"Stop Pump Exception:  {e}")
        finally:
            self.logger.info(f"Stop Pump Completed!")

            self.pump.pump_run(0)
            self.p_pump.pump_run(0)


if __name__ == '__main__':
    run_ins = DispensingRun()
    run_ins.dispense_2pumps_balance(148.0)
    run_ins.stop_pumps()
