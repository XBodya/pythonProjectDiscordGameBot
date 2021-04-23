from PIL import Image
from discord import File


class ImageBuilder:
    def __init__(self):
        self.image_board = Image.open("images/board.png").convert("RGBA")
        self.image_square = Image.open("images/square.png").convert("RGBA")
        self.image_cross = Image.open("images/cross.png").convert("RGBA")
        self.image_shot = Image.open("images/shot_area.png").convert("RGBA")

        self.step_h, self.step_v = self.image_board.size
        self.step_h //= 11
        self.step_v //= 11

    def build_image(self, board) -> File:
        image = Image.new("RGBA", self.image_board.size)
        image.paste(self.image_board)

        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] != 0 or len(str(board[i][j])) == 2:
                    image.paste(
                        self.image_square,
                        (j * self.step_v + self.step_v - 1,
                         i * self.step_h + self.step_h - 1),
                        self.image_square
                    )
                    print("PASTE")

        for i in range(len(board)):
            for j in range(len(board[0])):
                if str(board[i][j])[0] == "*" and len(str(board[i][j])) >= 3:
                    image.paste(
                        self.image_cross,
                        (j * self.step_v + self.step_v - 1,
                         i * self.step_h + self.step_h - 1),
                        self.image_cross
                    )
                elif str(board[i][j])[0] == "*":
                    image.paste(
                        self.image_shot,
                        (j * self.step_v + self.step_v - 1,
                         i * self.step_h + self.step_h - 1),
                        self.image_shot
                    )

        image.save("images/area.png")

        with open("images/area.png", "rb") as file:
            picture = File(file)

            return picture
