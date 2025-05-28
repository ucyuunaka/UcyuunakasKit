from PIL import Image
import os

# 定义函数，将PNG图片转换为PDF
def png_to_pdf(png_path, pdf_path):
    # 打开PNG图片
    image = Image.open(png_path)
    # 如果图片不是RGBA模式，转换为RGBA模式
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    # 创建一个白色背景的新图片
    new_image = Image.new('RGBA', image.size, 'white')  # "white" 是背景颜色
    # 将原始图片粘贴到新图片上，透明部分会变为白色
    new_image.paste(image, (0, 0), image)
    # 将新图片转换为RGB模式
    new_image = new_image.convert('RGB')
    # 保存为PDF
    new_image.save(pdf_path, "PDF")

# 遍历指定目录下的所有PNG文件转为pdf然后保存在当前文件夹中
for file in os.listdir('figure'):
    if file.endswith('.png'):
        # 使用函数
        png_to_pdf('figure\\'+file, file[:-4] + '.pdf')

