import cloudinary
import cloudinary.uploader

# Replace these with your actual Cloudinary account info
cloudinary.config(
    cloud_name='your_cloud_name',
    api_key='your_api_key',
    api_secret='your_api_secret',
    secure=True  # ensures HTTPS URLs
)
