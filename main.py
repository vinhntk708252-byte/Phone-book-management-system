import tkinter as tk

def main():
    # Khởi tạo cửa sổ chính
    root = tk.Tk()
    root.title("Hệ thống Quản lý Danh bạ - Nhóm Trưởng Khánh Vinh")
    root.geometry("600x400")
    
    # Hiển thị một dòng chữ test
    label = tk.Label(root, text="LÀM LẸ ĐI MẤY CON VỢ!", font=("Arial", 16))
    label.pack(pady=100)
    
    # Giữ cửa sổ luôn mở
    root.mainloop()

if __name__ == "__main__":
    main()