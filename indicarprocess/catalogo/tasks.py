## -*- coding: utf-8 -*-
from createhdr.createhdr import ReadTif
from celery import shared_task

from os.path import join
from subprocess import call

from .models import CatalogoLandsat


@shared_task
def make_tms(image):
    """Generate the TMS of an Image."""

    if (image.type == 'r6g5b4' and image.scene.sat == 'L8') or \
        (image.type == 'r5g4b3' and image.scene.sat in ['L5', 'L7']):

        if CatalogoLandsat.objects.filter(image=image.name).count() == 0:
            call(['make_tms.sh', image.file_path()])
            CatalogoLandsat.objects.create(
                image=image.name,
                path=join('/mnt/csr/imagens/landsat%s' % image.scene.sat[-1],
                    image.scene.name),
                shape=image.scene.geom,
                data=image.scene.date,
                url_tms=join('http://10.1.25.66/imagens/tms/landsat',
                    '%s_%s_tms.xml' % (image.scene.name, image.type)
                    )
            )
        else:
            print(('%s already has TMS' % image.name))
    else:
        print('Image is not a Landsat 8 of r6g5b4 type or a Landsat 5/7 of r5g4b3 type.')


@shared_task
def create_hdr(image):

    if (image.type == 'r6g5b4' and image.scene.sat == 'L8') or \
        (image.type == 'r5g4b3' and image.scene.sat in ['L5', 'L7']):

        tif = ReadTif(image.file_path())
        tif.write_hdr()