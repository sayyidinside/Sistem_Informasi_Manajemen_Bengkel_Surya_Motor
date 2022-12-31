from django.core.exceptions import ValidationError


def validate_image_size(value):
    image_size = value.size

    if image_size > 1048576:  # 1 MB
        raise ValidationError('Gambar yang diupload tidak bisa lebih dari 1MB')
    else:
        return value
