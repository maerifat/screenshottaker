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

def take_screenshot(instance, ip_address, port):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920x1080")
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    print("error10")
    driver = webdriver.Chrome(options=options, desired_capabilities=caps)
    print("error11")
    driver.set_page_load_timeout(5)
    try:
        if port == 443:
            driver.get(f'https://{ip_address}:{port}')
        else:
            driver.get(f'http://{ip_address}:{port}')
        print(f'http://{ip_address}:{port}')
        time.sleep(1)
        driver.save_screenshot(f'screenshots/{ip_address}_{port}.png')
        


        # Load the screenshot image
        image = cv2.imread("screenshots/" + str(ip_address) + "_" + str(port) + ".png")

        # Define the text, font, and color for the watermark
        text = f'https://{ip_address}:{port}'
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
        cv2.imwrite("screenshots/" + str(ip_address) + "_" + str(port) + ".png", image)

        driver.quit()

    except Exception as e:
    # handle other exceptions
        print(e)

def main():
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')
    for instance in instances:
        public_ip = instance.public_ip_address
        if not public_ip:
            continue
        sg_ids = [sg['GroupId'] for sg in instance.security_groups]
        for sg_id in sg_ids:
            sg = ec2.SecurityGroup(sg_id)
            ports = set()
            response = sg.ip_permissions
            #print(response)
            json_str = json.dumps(response)
            print("error1")
            data = json.loads(json_str)
            print("error2")
            for rule in data:
                if rule['IpProtocol'] != 'tcp':
                    continue
                if rule["FromPort"] == 22:
                    continue
                    print("error3")
                for port_range in rule['IpRanges']:
                    print("error4")
                    if 'FromPort' not in rule or 'ToPort' not in rule or rule['FromPort'] == rule['ToPort']:
                        print("error5")
                        port = int(rule['FromPort'])
                        print("error6")
                        if port not in ports:
                            print("error7")
                            ports.add(port)
                            print("error8")
                            take_screenshot(instance, public_ip, port)
                            print("error9")
                    else:
                        print(f"Ignoring port range from {rule['FromPort']} to {rule['ToPort']} for security group {sg_id}")
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
