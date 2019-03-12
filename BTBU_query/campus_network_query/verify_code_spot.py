"""
二维码orc识别模块

需提前安装tesseract-ocr包
sudo apt install tesseract-ocr

"""

from PIL import Image
import uuid, os, re
from io import BytesIO
import pytesseract

class verifyCode:
    """
    实现图片保存和验证码识别功能

    """
    def __init__(self, ImgBytes, size = (62, 22)):
        self.ImgPath = os.path.dirname(os.path.realpath(__file__)) + '/veri_code/'
        self.ImgSize = size
        self.ImgBytes = ImgBytes
        self.codeImg = Image.open(BytesIO(self.ImgBytes))

    # 随机存储文件
    def saveImg(self):
        self.ImgName = uuid.uuid4().hex + '.jpeg'
        self.codeImg.save(self.ImgPath + self.ImgName)

    # 二值化图片、去边框、独立点
    def _convertImage(self, standard=127.5):
        binaryImage = self.codeImg.convert('L')
        pixels = binaryImage.load()

        for x in range(binaryImage.width):
            for y in range(binaryImage.height):

                if pixels[x, y] > standard:
                    pixels[x, y] = 255
                else:
                    pixels[x, y] = 0

                if x <= 1 or x >= binaryImage.width - 2:
                    pixels[x, y] = 255
                elif y <= 1 or y >= binaryImage.height - 2:
                    pixels[x, y] = 255
        # binaryImage.show()

        for x in range(binaryImage.width):
            for y in range(binaryImage.height):
                if x <= 1 or x >= binaryImage.width - 2 or y <= 1 or y >= binaryImage.height - 2:
                    continue

                if pixels[x, y] == 255:
                    continue
                dependence = 0
                if pixels[x-1, y] == 255:
                    dependence += 1
                if pixels[x+1, y] == 255:
                    dependence += 1
                if pixels[x, y-1] == 255:
                    dependence += 1
                if pixels[x, y+1] == 255:
                    dependence += 1

                if dependence >= 3:
                    pixels[x, y] = 255

        # binaryImage.show()
        return binaryImage


    # OCR识别
    def ImageToText(self):
        '''
        如果出现找不到训练库的位置, 需要我们手动自动
        语法: tessdata_dir_config = '--tessdata-dir "<replace_with_your_tessdata_dir_path>"'
        '''

        BWImage = self._convertImage(standard= 120)

        textCode = pytesseract.image_to_string(BWImage, lang='eng')
        # 去掉非法字符，只保留字母数字
        textCode = re.sub("\W", "", textCode)
        return textCode.lower()
