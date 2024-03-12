# kernel-tools

This repository *should* make it easy to run LLVM LTO passes on the Linux kernel for dynamic and static analysis.

To run it you need to set the following environment variables in your shell or in a `.env` file:

* `LLVMPREFIX`: by default points to the `llvm-project` directory (created with `task llvm:clone`), you can overwrite it with your own or for example `/usr/lib/llvm-12`.
* `KERNEL`: should point to the Linux kernel repo.
* `REPOS` should point to the directories holding the LLVM LTO passes and runtimes (space separated).

For convenience you can add `kernel-tools/bin` to your PATH and run any command executable with `task ...` from within the kernel repo.
This is useful to for example start the kernel you are in directly in qemu.

## Dependencies
Install [go-task](https://taskfile.dev/#/installation) as a task-runner.
```
sudo sh -c "$(curl -ssL https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin
```
or on Ubuntu:
```
sudo snap install task --classic
```

Install a recent [golang](https://go.dev/doc/install) (the apt one is usually too old).
or on Ubuntu:
```
sudo snap install go --classic
```

Install the usual dependencies:
```
sudo apt install cmake gdb
# llvm-project
sudo apt install build-essential clang-12 lld-12 ninja-build ccache
# linux
sudo apt install bison flex libelf-dev libssl-dev
# syzkaller
sudo apt install debootstrap libguestfs-tools
# qemu
sudo apt install qemu-system-x86
```

**NOTE**: The project now requires ar (binutils 2.38) which is one (not the only) reason why you shouldn't use this on an Ubuntu version before 22.04.

## Compile LLVM
To compile your `llvm-project` you can simply run:

```
task llvm:create llvm:config llvm:build
```

## Compile your passes
```
task build
```

## Compile and configure your kernel
To compile your kernel with CLANG/LLVM and set the necessary config you can run:
```
task kernel:config kernel:bzImage
```

## Run your kernel with QEMU
To run your kernel in QEMU you need to first create a initramfs if you don't have one yet:
```
task initramfs:create
```

Then running it with QEMU:
```
task qemu
task qemu:qemu-gdb # waiting to attach gdb
```
or from the kernel directory:
```
kernel-tools qemu
```

gdb can automatically be attached with:
```
task gdb
```

QEMU's escape character has been remapped to CTRL-Q, you can stop the running QEMU instance after the boot with:
```CTRL-Q x```

## Run syzkaller
To fuzz the kernel with syzkaller you need to compile it first and create the necessary image:
```
task syzkaller:create syzkaller:build syzkaller:config syzkaller:create-image
```

If you want to use your own syzkaller repository (located somewhere else) you need to overwrite both `SYZKALLER_PREFIX` and `SYZKALLER_BIN`.

then running the kernel with that image to have a full userspace with SSH:
```
task qemu:syzkaller
```
or from the kernel directory:
```
kernel-tools qemu:syzkaller
```

To start syzkaller for fuzzing just run:
```
task syzkaller:run
```

## Run LTO passes on the kernel
```
task passes:run -- pass1:pass2
```

The directories `REPOS` are pointing to need to follow a certain pattern right now:
The compiled .so of the pass with the name <pass-name1> will be expected in:
```
${REPO}/build/passes/pass-name1/LLVMPassName1Pass.so
```

If you only want to link in the runtime component (for example to run your own code with `__initcall` at boot time)
you can simply run:
```
task passes:run -- .
```

You can get inspired by [kernel-tools-template-repo](https://github.com/Jakob-Koschel/kernel-tools-template-repo) on how such a repository can be setup.

## Share files with the VM

You can set `QEMU_9P_SHARED_FOLDER` to share a directory with the VM.
