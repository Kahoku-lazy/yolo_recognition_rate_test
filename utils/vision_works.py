"""
问题:
1. MAC系统 全屏显示图片； 副屏全屏显示图片。 方法 open_image_screen  open_image
"""
import cv2
import os
from mss import mss, tools
import pyautogui
from PIL import Image
from screeninfo import get_monitors

def calculate_timestamp(frame_number, fps):
    """
    计算帧的时间戳

    参数:
    frame_number (int): 帧序号，从 0 开始
    fps (float): 视频的帧率 (Frames Per Second)

    返回:
    float: 该帧对应的时间戳（秒）
    """
    return frame_number / fps

def is_single_letter(s):
    """ 判断是否为单个字符串 """
    return len(s) == 1 and s.isalpha()

def open_video(video_path):
    """ 打开视频    
    参数：
        video_path: 视频路径
    """
    # video_path = '/Users/kahokuliu/Movies/0630/0630.mp4'  # 替换为你的视频路径
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        exit()

    # 全屏模式
    # cv2.namedWindow('Video Frame', cv2.WND_PROP_FULLSCREEN)
    # cv2.setWindowProperty('Video Frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("视频播放结束")
            break
        cv2.imshow('Video Frame', frame)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def open_image(image_path, delay_time=1000, keyword=None):
    """ 打开图片
    参数:
        image_path: 图片路径
        delay_time: 图片窗口持续时间
        keyword: 单个英文字符串, 强制关闭图片窗口按键
    """
    # 读取图片
    # image_path = '/Users/kahokuliu/Pictures/Kahoku/电脑壁纸图片/C8A3EB12-69ED-4DBE-B47C-4EE8829F3C9E_1_105_c.jpeg'  # 替换为你的图片路径
    image = cv2.imread(image_path)

    # 检查是否成功读取图片
    if image is None:
        exit()

    # 创建一个窗口并设置为全屏模式
    # cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    # cv2.setWindowProperty('Image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    cv2.imshow('Image', image)
    
    if keyword and is_single_letter(keyword):
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    else:
        cv2.waitKey(delay_time)  

    # 关闭窗口
    cv2.destroyAllWindows()

def open_image_screen(image_path, delay_time=1000):
    """ 副屏中显示图片
    参数:
        image_path: 图片路径
        delay_time: 图片窗口持续时间
    """
    image = cv2.imread(image_path)
    # 获取图片的长和宽
    height, width, channels = image.shape
    if image is None:
        exit()

    # 获取主屏幕的分辨率
    screen_width, screen_height = pyautogui.size()
    secondary_screen_x = screen_width
    secondary_screen_y = 0

    # # 创建窗口
    cv2.namedWindow('screen_windows', cv2.WINDOW_NORMAL)
    cv2.moveWindow('screen_windows', secondary_screen_x, secondary_screen_y)
    cv2.resizeWindow('screen_windows', width=width, height=height)
    cv2.setWindowProperty('screen_windows', cv2.WND_PROP_FULLSCREEN ,cv2.WINDOW_FULLSCREEN)

    # 显示图片
    cv2.imshow('screen_windows', image)

    cv2.waitKey(delay_time)
    cv2.destroyAllWindows()

def split_video_to_frames(video_path, output_dir):
    """ 视频分帧为图片
    参数:
    video_path (str): 视频文件的路径
    output_dir (str): 输出图片的文件夹路径
    """
    cap = cv2.VideoCapture(video_path)

    # 检查视频是否成功打开
    if not cap.isOpened():
        print("无法打开视频文件")
        return

    # 获取视频的帧率（FPS）和总帧数
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 确保输出文件夹存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 逐帧读取视频
    frame_index = 0
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        timestamp = calculate_timestamp(frame_index, fps)

        frame_filename = os.path.join(output_dir, f"frame_{fps}_{frame_index:04d}.jpg")
        cv2.imwrite(frame_filename, frame)

        print(f"保存帧 {frame_index}，时间戳: {timestamp:.2f} 秒")

        frame_index += 1

    cap.release()
    print(f"视频处理完成，总帧数: {total_frames}")


def screenshot_images(save_image):

    monitors = get_monitors()

    if len(monitors) > 1:
        second_monitor = monitors[1]

        monitor = {'top': 0, 'left': 1920, 'width': 1920, 'height': 1080}

        with mss() as sct:
            screenshot = sct.grab(monitor)
        tools.to_png(screenshot.rgb, screenshot.size, output=save_image)


def screennshot_windows(outpyt_dir, flag=False):
    """ 截屏
    参数:
        flag: 是否为副屏截图; False: 主屏截图， True: 副屏截图
    
    """
    # 获取屏幕大小信息（通常是主屏的分辨率）
    screen_width, screen_height = pyautogui.size()
    secondary_screen_region = (0, 0, screen_width, screen_height)
    if flag:
        secondary_screen_region = (screen_width, 0, 1920, 1080)

    # 截取副屏区域
    screenshot = pyautogui.screenshot(region=secondary_screen_region)

    # 保存截图
    
    screenshot.save(outpyt_dir)
