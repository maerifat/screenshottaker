import boto3
import os
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from botocore.exceptions import ClientError
import json
from PIL import Image, ImageDraw, ImageFont
import cv2

session = boto3.Session(profile_name='dev')
ec2 = session.resource('ec2')

def take_screenshot(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')
    
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    driver = webdriver.Chrome(options=options, desired_capabilities=caps)
    
    print(f'https://{url}')
    try:
        driver.get(f'https://{url}')
        #time.sleep(5)
        page_width = driver.execute_script("return Math.max(document.body.scrollWidth, document.documentElement.scrollWidth, document.body.offsetWidth, document.documentElement.offsetWidth, document.documentElement.clientWidth);")
        page_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight, document.documentElement.clientHeight);")
        print("The width of the webpage is:", page_width)
        print("The height of the webpage is:", page_height)

        # Set the window size to match the calculated page width and height
        driver.set_window_size(page_width, page_height)

        #time.sleep(5)
        driver.save_screenshot(f'screenshots/{url}.png')
        driver.quit()

        # Load the screenshot image
        image = cv2.imread(f'screenshots/{url}.png')

        # Define the text, font, and color for the watermark
        text = f'https://{url}'
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        thickness = 10
        color = (80,80,80)
        color2 = (213, 213, 80)

        # Get the size of the text
        size = cv2.getTextSize(text, font, font_scale, thickness)[0]

        # Set the position of the text in the image
        x = 10
        y = 10 + size[1]

        rectangle_position = (10, 10)
        rectangle_size = (size[0] + 20, size[1] + 20)

        cv2.rectangle(image, rectangle_position, (rectangle_position[0] + rectangle_size[0], rectangle_position[1] + rectangle_size[1]), color, -1)
        # Add the text as a watermark to the image
        cv2.putText(image, text, (x, y), font, 2, color2, 2)

        # Save the watermarked image
        cv2.imwrite(f'screenshots/{url}.png', image)

    except Exception as e:
        print(e)

def main():
    with open('subs.txt','r') as file:
        for domain in file:
            take_screenshot(domain.strip())
            print("Screenshots saved successfully")

if __name__ == '__main__':
    try:
        main()
    except ClientError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
    except Exception as e:
        print(f"Error: {e}")
