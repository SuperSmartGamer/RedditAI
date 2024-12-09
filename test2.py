from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO

# Path to your HTML file
html_file_path = "file:///D:/reddit/index.html"

# Set up WebDriver (use Chrome or Firefox)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run browser in headless mode (no GUI)
driver = webdriver.Chrome(options=options)

# Open the HTML file
driver.get(html_file_path)

# Set the window size to 8K (7680x4320)
driver.set_window_size(7680, 4320)

# Find the element to screenshot
element = driver.find_element(By.ID, 'back')

# Get the location and size of the element (including children)
location = element.location
size = element.size

# Take a screenshot of the entire page
screenshot = driver.get_screenshot_as_png()

# Open the screenshot using PIL
screenshot_image = Image.open(BytesIO(screenshot))

# Define the cropping box for the element and its children
left = location['x']
top = location['y']
right = left + size['width']
bottom = top + size['height']

# Crop the image to the specific element
element_image = screenshot_image.crop((left, top, right, bottom))

# Convert to RGBA (if not already in that format)
element_image = element_image.convert("RGBA")

# Function to filter out all green pixels
def filter_all_green(image):
    width, height = image.size
    data = image.getdata()
    new_data = []
    
    # Loop through each pixel and check for green hues
    for item in data:
        r, g, b, a = item
        
        # If the green channel is significantly stronger than red or blue, mark as transparent
        if g > max(r, b):
            new_data.append((255, 255, 255, 0))  # Transparent
        else:
            new_data.append(item)
    
    # Update the image with the new filtered data
    image.putdata(new_data)
    return image

# Apply filtering to remove all green shades
element_image = filter_all_green(element_image)

# Function to remove green border by reverse filtering (optional)
def reverse_filter_green(image):
    width, height = image.size
    data = image.getdata()
    new_data = list(data)
    
    # Reverse filter from the edges inwards
    for y in range(height):
        for x in range(width):
            # Top border
            if new_data[y * width + x][1] > max(new_data[y * width + x][0], new_data[y * width + x][2]):
                new_data[y * width + x] = (255, 255, 255, 0)  # Transparent
            # Bottom border
            if new_data[(height - y - 1) * width + x][1] > max(new_data[(height - y - 1) * width + x][0], new_data[(height - y - 1) * width + x][2]):
                new_data[(height - y - 1) * width + x] = (255, 255, 255, 0)  # Transparent

    for x in range(width):
        for y in range(height):
            # Left border
            if new_data[y * width + x][1] > max(new_data[y * width + x][0], new_data[y * width + x][2]):
                new_data[y * width + x] = (255, 255, 255, 0)  # Transparent
            # Right border
            if new_data[y * width + (width - x - 1)][1] > max(new_data[y * width + (width - x - 1)][0], new_data[y * width + (width - x - 1)][2]):
                new_data[y * width + (width - x - 1)] = (255, 255, 255, 0)  # Transparent

    # Update the image with the new filtered data
    image.putdata(new_data)
    return image

# Apply reverse filtering (optional, based on your needs)
element_image = reverse_filter_green(element_image)

# Save the image as a PNG with transparent background
element_image.save("element_image.png")

# Show the result
element_image.show()

# Quit the driver
driver.quit()
