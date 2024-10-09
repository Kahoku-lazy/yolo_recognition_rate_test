from pathlib import Path

from utils.utils import *
from utils.vision_works import *

import configparser
import time
import shutil
import csv

def read_config(file_path):
    # 创建 ConfigParser 对象
    config = configparser.ConfigParser()

    # 读取配置文件
    config.read(file_path)

    return config

class AutoTest:
    
    def __init__(self):
        self.log = GetLog(log_path=os.path.join(os.getcwd(), "run_log.log"))
        self._serial_log = GetLog(log_path=os.path.join(os.getcwd(), "serial_log.log"))

        self._u2 = U2Tools()

        self.config = read_config(os.path.join(os.getcwd(), "config.ini"))

        # serial 
        self._serial = SerialWindows(port=self.config.get("Serial", "port"), 
                                        baudrate=self.config.get("Serial", "baudrate"))
        self._serial.open_serial()
        self._serial.set_buffer_size()
        
        # self._im = os.path.join(os.getcwd(), "screen_images", "screen.png")
        # if not Path(self._im).parent.exists():
        #     Path(self._im).parent.mkdir(parents=True, exist_ok=True)
        
    def main(self):
        
        self.log.info("start")
        image_path = self.config.get("Image", "path")
        
        # debug code 
        for dir in os.listdir(image_path):
            if dir not in ["Helldivers2"]:
                continue
            self.log.info(f"image dir: {dir}")
            # APP switch models
            # self._serial.reset_buffer()
            time.sleep(0.5)
            self._u2.switch_game_model(dir)
            time.sleep(5)
            serila_log = self._serial.get_buffer_data()
            results = find_all_values(serila_log, pattern=r"Model change to (\d+)")
            self.log.info(f"device model id: {results}")
            
            images = get_images_from_directory(os.path.join(image_path,dir))
            for i, im in enumerate(images):
                
                # show image 
                self.log.info(f"clean buffer data")
                self._serial.reset_buffer()
                time.sleep(0.5)
                self.log.info(f"[{i}/{len(images)}] image: {im}")
                open_image_screen(im)
                
                # model result 
                serila_log = self._serial.get_buffer_data()
                self._serial_log.info(serila_log)
                results = find_all_values(serila_log)
                light_effect = find_all_values(serila_log, pattern=r'>> send >>\s*(.*)')
   
                # model detect error
                if len(results) > 1 or len(light_effect) > 1:
                    self.log.error(f"model  reuslt error")
                    self.log.error(f"model result: {results}")
                    self.log.error(f"light effect result: {light_effect}")
                    continue
                
                # model detect result
                print([dir, im, results, light_effect])
                if results:
                    self.log.info(f"model result: {results}")
                    self.log.info(f"light effect result: {light_effect}")
                    with open(f'results/{dir}.csv', mode='a+', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([dir, im, results[-1], light_effect[-1].strip()])
                else:
                    self.log.error(f"model not found")
                    with open(f'results/{dir}.csv', mode='a+', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([dir, im, None, None])
                    
            self.log.info("\n")
            

if __name__ == "__main__":
    AutoTest().main()