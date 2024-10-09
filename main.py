''' @author: Kahoku 
    @date: 2024/10/07
'''
from pathlib import Path
import time
import csv

from utils.utils import *
from utils.vision_works import *

class AutoTest:
    
    def __init__(self):

        self._u2 = U2Tools()
        self.config = read_config(os.path.join(os.getcwd(), "config.ini"))

        self._log_init()
        self._serila_init()
        self._save_csv()
        
    def _log_init(self):

        path = os.path.join(os.getcwd(), "logs")
        if not Path(path).exists():
            Path(path).mkdir(parents=True, exist_ok=True)
        self.log = GetLog(log_path=os.path.join(os.getcwd(), "logs", "run_log.log"))

    def _serila_init(self):

        self._serial = SerialWindows(port=self.config.get("Serial", "port"), 
                                        baudrate=self.config.get("Serial", "baudrate"))
        self._serial.open_serial()
        self._serial.set_buffer_size()

    def _save_csv(self):
        
        self._save_csv = os.path.join(os.getcwd(), "result", "test_result.csv")
        if not Path(self._save_csv).parent.exists():
            Path(self._save_csv).parent.mkdir(parents=True, exist_ok=True)


    def write_csv_values(self, file_path, values):

        with open(file_path, mode='a+', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(values)

    def main(self):
        
        self.log.info("start test")
        image_path = self.config.get("Image", "path")
        
        for folder in os.listdir(image_path):

            self.log.info(f"image folder {folder}")

            self.log.info(f"clean serial buffer data")
            self._serial.reset_buffer()
            time.sleep(0.5)

            self.log.info(f"app switch {folder} model")
            self._u2.switch_game_model(folder)
            time.sleep(5)

            serila_log = self._serial.get_buffer_data()
            results = find_all_values(serila_log, pattern=r"Model change to (\d+)")
            self.log.info(f"device model id: {results}")
            images = get_images_from_directory(os.path.join(image_path, folder))
            for i, im in enumerate(images):

                values = [folder, im, None, None, None]

                self.log.info(f"clean serial buffer data")
                self._serial.reset_buffer()
                time.sleep(0.5)

                # show image 
                self.log.info(f"[{i}/{len(images)}]  show image: {im}")
                open_image_screen(im)
                
                # get serial data
                serila_log = self._serial.get_buffer_data()
                results = find_all_values(serila_log)

                # devices IOU test
                change_class = find_all_values(serila_log, pattern=r'Class change to:\s*(\d+),.*')
                self.log.info(f"Class change to:: {change_class}")

                light_effect = find_all_values(serila_log, pattern=r'>> send >>\s*(.*)\r\r')
                
                print(f">>>>[info:] detect result: {folder}, {im}, {change_class}, {results}, {light_effect}")

                # model detect 
                if results and len(results) == 1 and len(light_effect) == 1:
                    self.log.info(f"model Detect class: {results}")
                    l = light_effect[-1].split(" ")[:2][::-1]
                    light_effect_id = int("".join(l), 16)
                    self.log.info(f"light effect id: {light_effect_id}")
                    self.log.info(f"light effect result: {light_effect}")
                    values = [folder, im, results[-1], light_effect_id, light_effect[-1].rstrip()]

                elif len(results) > 1 or len(light_effect) > 1:
                    self.log.error(f"model reuslt error")
                    self.log.error(f"model result: {results}")
                    self.log.error(f"light effect result: {light_effect}")

                else:
                    self.log.error(f"model not found")

                self.write_csv_values(self._save_csv, values)   
            self.log.info("\n")
            

if __name__ == "__main__":
    AutoTest().main()