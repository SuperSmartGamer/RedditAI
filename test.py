import pyautogui
import cv2
import numpy as np
import pyperclip
from PIL import Image
import webbrowser
from time import sleep

def find_and_click(window_title, target_image_path):
    # Take a screenshot of the specified window
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)  # Convert to NumPy array
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    
    # Load the target image
    target_image = cv2.imread(target_image_path, cv2.IMREAD_GRAYSCALE)
    if target_image is None:
        print("Error: Target image not found.")
        return
    
    # Match the target image in the screenshot
    result = cv2.matchTemplate(screenshot_gray, target_image, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    # Define a threshold for detection confidence
    threshold = 0.8
    if max_val >= threshold:
        # Calculate center of the matched region
        h, w = target_image.shape
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        
        # Click at the detected location
        pyautogui.click(center_x, center_y)
        print(f"Clicked at ({center_x}, {center_y}) with confidence {max_val}")
    else:
        print("Target not found in the screenshot.")

def set_clipboard(text):
    """
    Set text directly into the system clipboard.
    :param text: String to place into the clipboard.
    """
    pyperclip.copy(text)
    print(f"Text copied to clipboard: {text}")

def get_clipboard():
    """
    Retrieve text directly from the system clipboard.
    :return: Text currently in the clipboard.
    """
    text = pyperclip.paste()
    print(f"Text from clipboard: {text}")
    return text



import os



def get_file_paths_as_string(relative_path):
    """
    Get the absolute paths of all files in a directory (from a relative path)
    and return them as a single string with each path enclosed in double quotes 
    and separated by spaces.
    :param relative_path: Relative path to the directory.
    :return: A string of absolute file paths formatted as "path1" "path2" ...
    """
    # Convert relative path to absolute path
    directory = os.path.abspath(relative_path)
    
    if not os.path.isdir(directory):
        print(f"Error: {relative_path} is not a valid directory.")
        return ""

    # Collect file paths
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            absolute_path = os.path.abspath(os.path.join(root, file))
            file_paths.append(f'"{absolute_path}"')  # Add quotes around paths
    
    # Join paths into a single string
    result = " ".join(file_paths)
    print(f"Collected {len(file_paths)} files.")
    return result


"""
# Example usage
# 1. Click on the target
find_and_click("Window Title Here", "target_image.png")
"""
# 2. Set and retrieve clipboard contents
#set_clipboard(get_file_paths_as_string("reddit_videos/un-uploaded"))


#find_and_click("Window Title Here", "target_image.png")


def doStuff(path):
    webbrowser.open_new("https://studio.youtube.com/channel/UCA3UCKphsBkx2Ie0oHvnsaA/videos/upload?d=ud&filter=%5B%5D&sort=%7B%22columnType%22%3A%22date%22%2C%22sortOrder%22%3A%22DESCENDING%22%7D")
    sleep(10)
    find_and_click("Channel Content - Youtube Studio - Google Chrome", "img_resources/select_button.png")
    sleep(10)
    set_clipboard(path)
    sleep(10)
    pyautogui.hotkey('ctrl', 'v')
    sleep(10)
    pyautogui.hotkey('enter')
    sleep(10)
    find_and_click("Channel Content - Youtube Studio - Google Chrome", "img-resources/reuse.png")
    sleep(10)
    pyautogui.scroll(-100000)
    sleep(10)
    find_and_click("Channel Content - Youtube Studio - Google Chrome", "img-resources/daily_reddit_1.png")
    sleep(10)
    find_and_click("Channel Content - Youtube Studio - Google Chrome", "img-resources/reuse2.png")
    sleep(10)
    find_and_click("Channel Content - Youtube Studio - Google Chrome", "img-resources/reuse.png")
    sleep(10)
    pyautogui.scroll(-1000000)
    sleep(10)
    find_and_click("Channel Content - Youtube Studio - Google Chrome", "img-resources/notForKids.png")
    sleep(10)
    find_and_click("Channel Content - Youtube Studio - Google Chrome", "img-resources/visibility.png")
    sleep(10)
    find_and_click("Channel Content - Youtube Studio - Google Chrome", "img-resources/unlisted.png")
    #change
    sleep(10)
    find_and_click("Channel Content - Youtube Studio - Google Chrome", "img-resources/save.png")

doStuff(r"D:\reddit\reddit_videos\un-uploaded\12-08-2024 #1.mp4")