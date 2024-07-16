from PIL import Image, ImageDraw


class OP:
    def cropp_image(self,input_image_path, output_image_path, points):
        input_image = Image.open(input_image_path)
        mask = Image.new('L', input_image.size, 0)

        mask_draw = ImageDraw.Draw(mask)
        mask_draw.polygon(points, fill=255)

        output_image = Image.new('RGB', input_image.size)
        output_image.paste(input_image, mask=mask)
        output_image.save(output_image_path)





