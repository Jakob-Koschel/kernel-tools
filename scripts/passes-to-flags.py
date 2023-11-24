#!/usr/bin/env python3

import sys
import os

import argparse

def main():
    parser = argparse.ArgumentParser(description='convert passes to the necessary compile/link flags')
    parser.add_argument('--passes', dest='passes', required=True, type=str)
    parser.add_argument('--compile-flags', dest='compile_flags', action=argparse.BooleanOptionalAction)
    parser.add_argument('--lto-flags', dest='lto_flags', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    passes_array = args.passes.split(' ')
    repos = os.getenv('REPOS', '').split()
    repos = [r[:-1] if r.endswith('/') else r for r in repos]

    flags = ""

    for pass_item in passes_array:
        compile_pass = False
        lto_pass = False

        if pass_item.startswith("compile:") and args.compile_flags:
            pass_item = pass_item[len("compile:"):]
            compile_pass = True
        if pass_item.startswith("lto:") and args.lto_flags:
            pass_item = pass_item[len("lto:"):]
            lto_pass = True

        if not compile_pass and not lto_pass:
            continue

        pass_array = pass_item.split(':')
        if len(pass_array) == 1:
            # if there is only a single repo, specifying it can be ommited
            if len(repos) == 1:
                pass_repo = os.path.basename(repos[0])
            else:
                print("With multiple REPOS, it needs to be specified")
                sys.exit(1)
        else:
            pass_repo = pass_array[0]
            pass_item = pass_array[1]

        # find correct repo
        repo = next((repo_path for repo_path in repos if os.path.basename(repo_path) == pass_repo), None)

        if not repo:
            print("Couldn't find correct REPO")
            sys.exit(1)

        tmp_pass_name = pass_item.split('(')[0]
        arguments = pass_item[len(tmp_pass_name):]
        pass_item = tmp_pass_name

        arguments = arguments.strip('()')
        pass_arguments = ""
        for arg in arguments.split():
            pass_arguments += f" -mllvm {arg}"

        camel_case_pass = pass_item
        if '-' in camel_case_pass:
            camel_case_pass = ''.join(word.capitalize() for word in pass_item.split('-'))

        pass_path = f"{repo}/build/passes/{pass_item}/LLVM{camel_case_pass}Pass.so"
        if not os.path.isfile(pass_path):
            pass_path = f"{repo}/build/{pass_item}/LLVM{camel_case_pass}Pass.so"
            if not os.path.isfile(pass_path):
                print("[KERNEL TOOLS] couldn't find PASS :(")
                sys.exit(1)

        if compile_pass:
            flags += f" -Xclang -load -Xclang {pass_path} -fpass-plugin={pass_path} {pass_arguments}"
        if lto_pass:
            flags += f" -mllvm=-load={pass_path}"

    if args.lto_flags:
        old_pm = os.getenv('PASS_MANAGER', None)
        if old_pm:
            flags += " -plugin-opt=legacy-pass-manager"

    print(flags)

if __name__ == '__main__':
    main()

