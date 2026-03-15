import re

class SentenceSplitter:
    def __init__(self):
        self.buffer = ""
        # Regex này tìm các ký tự kết thúc câu (. ! ? \n) có khoảng trắng hoặc kết thúc chuỗi theo sau
        self.sentence_end_regex = re.compile(r'(.*?[.!?;])(\s+|$)', re.DOTALL)

    def append_token(self, token: str) -> str:
        """
        Thêm một token vào buffer và kiểm tra xem có tạo thành câu hoàn chỉnh không.
        Nếu có, trả về câu đó và xóa khỏi buffer.
        """
        self.buffer += token
        match = self.sentence_end_regex.search(self.buffer)
        if match:
            sentence = match.group(1).strip()
            # Cập nhật buffer bằng phần còn lại sau khi đã tách câu
            self.buffer = self.buffer[match.end():]
            return sentence
        return None

    def get_remaining(self) -> str:
        """
        Trả về phần văn bản còn lại trong buffer nếu chưa được tách thành câu.
        """
        remaining = self.buffer.strip()
        self.buffer = ""
        return remaining if remaining else None
