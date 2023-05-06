import shutil
import subprocess
import sys
from os import listdir
from os.path import join
import os
import SimpleITK as sitk
import numpy as np

def is_image_file(filename):
    return any(filename.endswith(extension) for extension in [".nrrd"])

def AffBsp(fix, mov_aff, out_aff, mov_bsp, out_bsp, out_setting):

    new_rigid_dir = join(out_setting, 'rigid.txt')
    new_bspline_dir = join(out_setting, 'bspline.txt')

    if not os.path.exists(out_aff):
        os.makedirs(out_aff)
    cmd = "elastix\elastix.exe -f " + fix + " -m " + mov_aff + " -out " + out_aff + " -p "+new_rigid_dir
    subprocess.call(cmd, shell=True)

    if not os.path.exists(out_bsp):
        os.makedirs(out_bsp)
    cmd = "elastix\elastix.exe -f " + fix + " -m " + mov_bsp + " -out " + out_bsp + " -p "+new_bspline_dir
    subprocess.call(cmd, shell=True)

def Filling(mov_dir, out_setting, init_rigid_dir, init_bspline_dir):
    img = sitk.ReadImage(mov_dir)
    img = sitk.GetArrayFromImage(img)
    val = np.min(img)
    t = img.dtype.name

    find_str_type = "(ResultImagePixelType \"unsigned short\")"
    if t == 'int16':
        replace_str_type = "(ResultImagePixelType \"short\")"
    elif t == 'uint16':
        replace_str_type = "(ResultImagePixelType \"unsigned short\")"
    elif t == 'int32':
        replace_str_type = "(ResultImagePixelType \"long\")"
    elif t == 'uint32':
        replace_str_type = "(ResultImagePixelType \"unsigned long\")"
    elif t == 'float32':
        replace_str_type = "(ResultImagePixelType \"float\")"
    elif t == 'float64':
        replace_str_type = "(ResultImagePixelType \"double\")"
    else:
        replace_str_type = "(ResultImagePixelType \"unsigned short\")"


    replace_str = "(DefaultPixelValue " + str(val) + ')'
    find_str = "(DefaultPixelValue 32769)"


    if not os.path.exists(out_setting):
        os.makedirs(out_setting)

    new_rigid_dir = join(out_setting, 'rigid.txt')
    new_bspline_dir = join(out_setting, 'bspline.txt')

    # 设置仿射配准参数
    f_rigid_init = open(init_rigid_dir, "r")
    f_rigid_new = open(new_rigid_dir, "w")
    for line in f_rigid_init:
        if find_str in line:
            line = line.replace(find_str, replace_str)
        if find_str_type in line:
            line = line.replace(find_str_type, replace_str_type)
        f_rigid_new.writelines(line)
    f_rigid_init.close()
    f_rigid_new.close()

    # 设置弹性形变参数
    f_bspline_init = open(init_bspline_dir, "r")
    f_bspline_new = open(new_bspline_dir, "w")
    for line in f_bspline_init:
        if find_str in line:
            line = line.replace(find_str, replace_str)
        if find_str_type in line:
            line = line.replace(find_str_type, replace_str_type)
        f_bspline_new.writelines(line)
    f_bspline_init.close()
    f_bspline_new.close()

if __name__ == '__main__':
    fix_dir = 'A2B/fixed'
    mov_dir = 'A2B/mov'
    warp_dir = 'A2B/warp'

    tmp_dir = 'A2B/_tmp/tmp_log'
    init_rigid_dir = 'elastix/rigid.txt'
    init_bspline_dir = 'elastix/bspline.txt'

    patient_filenames = listdir(fix_dir)

    for patientname in patient_filenames:
        fix_filenames = [x for x in listdir(join(fix_dir, patientname)) if is_image_file(x)]
        mov_filenames = [x for x in listdir(join(mov_dir, patientname)) if is_image_file(x)]
        for fix_filename in fix_filenames:
            fix = join(fix_dir, patientname, fix_filename)
            for mov_filename in mov_filenames:
                mov_aff = join(mov_dir, patientname, mov_filename)
                out_aff = join(tmp_dir, patientname, fix_filename[:-5], mov_filename[:-5]+'_aff')
                mov_bsp = join(out_aff, 'result.0.nrrd')
                out_bsp = join(tmp_dir, patientname, fix_filename[:-5], mov_filename[:-5]+'_bsp')
                out_setting = join(tmp_dir, patientname, fix_filename[:-5], mov_filename[:-5]+'_setting')
                out_save = join(warp_dir, patientname, fix_filename[:-5], mov_filename)
                if not os.path.exists(join(warp_dir, patientname, fix_filename[:-5])):
                    os.makedirs(join(warp_dir, patientname, fix_filename[:-5]))

                # 设置参数文件
                Filling(mov_aff, out_setting, init_rigid_dir, init_bspline_dir)
                # Affine-Deform 配准
                AffBsp(fix, mov_aff, out_aff, mov_bsp, out_bsp, out_setting)
                shutil.move(join(out_bsp,'result.0.nrrd'), out_save)