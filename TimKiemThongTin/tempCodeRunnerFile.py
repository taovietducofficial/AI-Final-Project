def bfs(self):
        """
        Hàm thực hiện thuật toán Best First Search để tìm đường đi ngắn nhất từ đầu rắn đến thức ăn.
        
        Cách hoạt động:
        1. Khởi tạo:
           - Điểm bắt đầu là đầu rắn
           - Điểm đích là vị trí thức ăn
           - Hàng đợi queue lưu các vị trí cần xét và đường đi tới đó
           - Set visited lưu các ô đã thăm
        
        2. Lặp cho đến khi tìm được đường đi hoặc hết khả năng:
           - Lấy vị trí hiện tại và đường đi từ queue
           - Nếu đến đích thì trả về đường đi
           - Thử các hướng di chuyển có thể (UP/DOWN/LEFT/RIGHT)
           - Thêm các vị trí hợp lệ vào queue và visited
        
        3. Trả về:
           - Danh sách các hướng đi nếu tìm thấy đường
           - Danh sách rỗng nếu không tìm được đường đi
        """
        start = self.snake[0]  # Điểm bắt đầu là đầu rắn
        goal = self.food  # Điểm đích là thức ăn

        directions = [UP, DOWN, LEFT, RIGHT]  # Các hướng có