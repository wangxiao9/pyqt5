
import time

import serial
import struct
import binascii
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
from loguru import logger


class Pump:
    MODBUS_REG_LIST = [
        ('REG_COIL', 1, 'motor_run', 0x1001),
        ('REG_COIL', 1, 'motor_direction', 0x1002),
        ('REG_COIL', 1, 'flash_save', 0x1003),
        ('REG_COIL', 1, 'run_mode', 0x1004),
        ('REG_HOLDING', 2, 'motor_rpm', 0x3001),
        ('REG_HOLDING', 2, 'motor_rpm_max', 0x3003),
        ('REG_HOLDING', 2, 'run_time_or_volume', 0x3005),
        ('REG_HOLDING', 2, 'run_online_time_or_volume', 0x3007),
        ('REG_HOLDING', 2, 'run_total_time_or_volume', 0x3009),
        ('REG_HOLDING', 2, 'motor_calibrateLed_rpm', 0x300B),
    ]

    def __init__(self, port, slave_id=1, baud=115200, timeout=1, check=False, strip=True):
        self.master = modbus_rtu.RtuMaster(
            serial.Serial(port=port, baudrate=baud, bytesize=8, parity='N', stopbits=1, xonxoff=0))
        self.master.set_timeout(5.0)
        self.slave_id = slave_id
        logger.add("./logger/interface_log_{time}.log", rotation="500MB", encoding="utf-8", enqueue=True,
                   compression="zip",
                   retention="10 days")
        logger.info("pump instance created")

    def set_pump_rpm(self, rpm=30.0):
        try:
            res1 = self.master.execute(self.slave_id, cst.WRITE_MULTIPLE_REGISTERS, 0x3001, output_value=[rpm],
                                       data_format='>f')
            alarm = 'success'
            logger.info("pump rpm set success")
            return alarm
        except Exception as exc:
            logger.error("pump rpm set timeout")
            alarm = (str(exc))
        return alarm

    def get_pump_rmp(self):
        try:
            res1 = self.master.execute(self.slave_id, cst.READ_HOLDING_REGISTERS, 0x3001, 2, data_format='>f')
            alarm = 'success'
            logger.info("pump rpm get success ")
            return res1
        except Exception as exc:
            logger.error("pump rpm get timeout")
            alarm = (str(exc))
        return alarm

    def set_pump_time_volume(self, time_volume=0):
        try:
            # # # for volume only
            volume = 20.0
            volume = float(time_volume)
            if self.get_pump_mode()[0] == 1:
                res1 = self.master.execute(self.slave_id, cst.WRITE_MULTIPLE_REGISTERS, 0x3005, output_value=[volume],
                                           data_format='>f')
            else:
                if time_volume > 0xffff:
                    self.master.execute(self.slave_id, cst.WRITE_SINGLE_REGISTER, 0x3005,
                                        output_value=(time_volume >> 16))
                    self.master.execute(self.slave_id, cst.WRITE_SINGLE_REGISTER, 0x3006,
                                        output_value=(time_volume & 0xffff))
                else:
                    self.master.execute(self.slave_id, cst.WRITE_SINGLE_REGISTER, 0x3005, output_value=0)
                    self.master.execute(self.slave_id, cst.WRITE_SINGLE_REGISTER, 0x3006, output_value=time_volume)
            alarm = 'success'
            logger.info("pump time/volume set success")
            return alarm
        except Exception as exc:
            logger.error("pump time/volume set timeout")
            alarm = (str(exc))
        return alarm

    def get_pump_time_volume(self):
        try:
            if self.get_pump_mode()[0] == 1:
                res1 = self.master.execute(self.slave_id, cst.READ_HOLDING_REGISTERS, 0x3005, 2, data_format='>f')
            else:
                res1 = self.master.execute(self.slave_id, cst.READ_HOLDING_REGISTERS, 0x3005, 2)
            alarm = 'success'
            logger.info("pump time/volume get success ")
            return res1
        except Exception as exc:
            logger.error("pump time/volume get timeout")
            alarm = (str(exc))
        return alarm

    def get_pump_real_time_volume(self):
        try:
            res1 = self.master.execute(self.slave_id, cst.READ_HOLDING_REGISTERS, 0x3007, 2, data_format='>f')
            alarm = 'success'
            logger.info("pump real time/volume get success")
            return res1
        except Exception as exc:
            logger.error("pump real time/volume get timeout")
            alarm = (str(exc))
        return alarm

    def get_pump_total_time_volume(self):
        try:
            res1 = self.master.execute(self.slave_id, cst.READ_HOLDING_REGISTERS, 0x3009, 2, data_format='>f')
            alarm = 'success'
            logger.info("pump total time/volume get success")
            return res1
        except Exception as exc:
            logger.error("pump total time/volume get timeout")
            alarm = (str(exc))
        return alarm

    def set_pump_calibrated_factor(self, factor=0.0):
        try:
            res1 = self.master.execute(self.slave_id, cst.WRITE_MULTIPLE_REGISTERS, 0x300B, output_value=[factor],
                                       data_format='>f')
            alarm = 'success'
            logger.info("pump calibrated rpm set success")
            return alarm
        except Exception as exc:
            logger.error("pump calibrated rpm set timeout")
            alarm = (str(exc))
        return alarm

    def get_pump_calibrated_factor(self):
        try:
            res1 = self.master.execute(self.slave_id, cst.READ_HOLDING_REGISTERS, 0x300B, 2, data_format='>f')
            alarm = 'success'
            logger.info("pump calibrated rpm get success")
            return res1
        except Exception as exc:
            logger.error("pump calibrated rpm get timeout")
            alarm = (str(exc))
        return alarm

    def pump_run(self, state=0):
        try:
            res1 = self.master.execute(self.slave_id, cst.WRITE_SINGLE_COIL, 0x1001, output_value=state)
            alarm = 'success'
            logger.info("pump run success")
            return alarm
        except Exception as exc:
            logger.error("pump run timeout")
            alarm = (str(exc))
        return alarm

    def get_pump_state(self):
        try:
            res1 = self.master.execute(self.slave_id, cst.READ_COILS, 0x1001, 1, data_format='>b')
            alarm = 'success'
            logger.info("pump state get success ")
            return res1
        except Exception as exc:
            logger.error("pump state get timeout")
            alarm = (str(exc))
        return alarm

    def set_pump_direction(self, direction=0):
        try:
            res1 = self.master.execute(self.slave_id, cst.WRITE_SINGLE_COIL, 0x1002, output_value=direction)
            alarm = 'success'
            logger.info("pump direction set success")
            return alarm
        except Exception as exc:
            logger.error("pump direction set timeout")
            alarm = (str(exc))
        return alarm

    def set_pump_mode(self, mode=0):
        try:
            res1 = self.master.execute(self.slave_id, cst.WRITE_SINGLE_COIL, 0x1004, output_value=mode)
            alarm = 'success'
            logger.info("pump mode set success")
            return alarm
        except Exception as exc:
            logger.error("pump mode set timeout")
            alarm = (str(exc))
        return alarm

    def get_pump_mode(self):
        try:
            res1 = self.master.execute(self.slave_id, cst.READ_COILS, 0x1004, 1, data_format='>b')
            alarm = 'success'
            logger.info("pump mode get success ")
            return res1
        except Exception as exc:
            logger.error("pump mode get timeout")
            alarm = (str(exc))
        return alarm


if __name__ == '__main__':
    ins = Pump("/dev/ttyUSB1")
    ins.set_pump_rpm(60)
    ins.set_pump_mode(0)
    ins.set_pump_time_volume(0)

