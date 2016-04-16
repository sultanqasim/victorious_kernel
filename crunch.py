#!/usr/bin/python3
from sys import argv, exit
from os import system, environ

SUPPORTED_DEVICES = ["condor", "otus", "falcon", "peregrine", "titan", "victara"]
MODULE_DEVICES = ["condor", "otus"]

if len(argv) < 2:
    print("Target device not specified.")
    exit(-2)
elif not argv[1] in SUPPORTED_DEVICES:
    print("Device %s is not supported." % argv[1])
    exit(-3)

OUT_FILE_NAME = "arch/arm/boot/octopus_kernel-" + argv[1] + ".zip"

def clean():
    system("rm -f arch/arm/boot/dts/*.dtb")
    system("rm -f arch/arm/boot/dt.img")
    system("rm -rf squid_install")
    system("rm -rf cwm_flash_zip/system/lib/modules")
    system("rm -rf " + OUT_FILE_NAME)

def build_core():
    system("make " + argv[1] + "_defconfig")
    if system("make -j5 zImage"):
        print("zImage build failed")
        exit(-1)
    if system("make -j5 dtimage"):
        print("dtb build failed")
        exit(-1)
    system("cp arch/arm/boot/zImage cwm_flash_zip/tools/")
    system("cp arch/arm/boot/dt.img cwm_flash_zip/tools/")

def build_modules():
    system("mkdir -p squid_install")
    if system("make -j5 modules"):
        print("module build failed")
        exit(-1)
    system("make -j5 modules_install INSTALL_MOD_PATH=squid_install INSTALL_MOD_STRIP=1")
    system("mkdir -p cwm_flash_zip/system/lib/modules/pronto")
    system("find squid_install/ -name '*.ko' -type f -exec cp '{}' cwm_flash_zip/system/lib/modules/ \;")
    system("mv cwm_flash_zip/system/lib/modules/wlan.ko cwm_flash_zip/system/lib/modules/pronto/pronto_wlan.ko")

def create_zip():
    system("cd cwm_flash_zip && zip -r ../" + OUT_FILE_NAME + " ./")
    print()
    print("kernel zip created:", OUT_FILE_NAME)

environ["ARCH"] = "arm"
clean()
build_core()
if argv[1] in MODULE_DEVICES:
    build_modules()
create_zip()
