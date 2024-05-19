import os
import cv2
import numpy as np
import pandas as pd

# Đường dẫn tới thư mục chứa ảnh
folder_path = r'F:\Data\gray80+2+'

# Hàm chuyển đổi kích thước ảnh
def resize_image(image_path, new_size):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    resized_img = cv2.resize(img, (new_size, new_size))
    return resized_img

# Lấy danh sách các file trong thư mục
image_files = os.listdir(folder_path)

# Số lượng ảnh
num_images = len(image_files)

# Khởi tạo mảng để lưu dữ liệu ảnh
image_data = np.zeros((num_images, 96 * 96), dtype=np.uint8)

# Chuyển đổi kích thước ảnh và lưu vào mảng
for idx, file_name in enumerate(image_files):
    image_path = os.path.join(folder_path, file_name)
    resized_img = resize_image(image_path, 96)
    image_data[idx, :] = resized_img.flatten()

# Tạo DataFrame từ mảng dữ liệu ảnh
df = pd.DataFrame(image_data)

# Lưu DataFrame thành file CSV
csv_path = r'F:\Data\gray80_2.csv'
df.to_csv(csv_path, index=False, header=False)

print(f"{num_images} ảnh đã được chuyển đổi và lưu thành công dưới dạng file CSV tại đường dẫn: {csv_path}")
