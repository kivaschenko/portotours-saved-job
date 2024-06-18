from celery import shared_task


@shared_task()
def set_read_public_for_new_images_in_uploads_folder():
    from service_layer.s3_utils import adjust_time_expires_for_image
    adjust_time_expires_for_image()
