from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO

def thumbnail_gen(subreddit_text, textbox_text, username, output_filepath, html_file_path):
    # Set up WebDriver (use Chrome or Firefox)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run browser in headless mode (no GUI)
    driver = webdriver.Chrome(options=options)

    # Open the HTML file
    driver.get(html_file_path)

    # Wait for the elements to be present
    wait = WebDriverWait(driver, 20)

    try:
        # Modify the subreddit text
        subreddit_element = wait.until(EC.presence_of_element_located((By.ID, 'subreddit')))
        driver.execute_script("arguments[0].innerText = arguments[1]", subreddit_element, subreddit_text)
        
        # Modify the textbox content
        textbox_element = wait.until(EC.presence_of_element_located((By.ID, 'textbox')))
        driver.execute_script("arguments[0].innerText = arguments[1]", textbox_element, textbox_text)
        
        username_element = wait.until(EC.presence_of_element_located((By.ID, 'username')))
        driver.execute_script("arguments[0].innerText = arguments[1]", username_element, username)
        

        # Optionally, modify other elements (for example, change text, background color, etc.)
        # Example: Change background color of #back element
        

        # Take a screenshot of the entire page
        screenshot = driver.get_screenshot_as_png()

        # Open the screenshot using PIL
        screenshot_image = Image.open(BytesIO(screenshot))

        # Function to filter out all green pixels and convert to RGBA
        def filter_all_green(image):
            # Ensure the image is in RGBA mode
            image = image.convert("RGBA")
            width, height = image.size
            data = image.getdata()
            new_data = []

            # Loop through each pixel and check for green hues
            for item in data:
                r, g, b, a = item

                # If the green channel is significantly stronger than red or blue, make it transparent
                if g > max(r, b):
                    new_data.append((255, 255, 255, 0))  # Transparent
                else:
                    new_data.append(item)

            # Update the image with the new filtered data
            image.putdata(new_data)
            return image

        # Apply filtering to remove all green shades
        screenshot_image = filter_all_green(screenshot_image)

        # Save the screenshot after filtering to the provided filepath
        screenshot_image.save(output_filepath)

        # Optionally, display the screenshot
        #screenshot_image.show()

    finally:
        # Close the driver after operations
        driver.quit()
    return output_filepath
# Example usage:
"""
thumbnail_gen(
    subreddit_text="r/python",
    username="u/StillPillWill",
    textbox_text="How do you manage your time effectively?",
    output_filepath="D:/reddit/modified_page_filtered.png",
    html_file_path="file:///D:/reddit/index.html"
)
"""